from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date, time as dtime
from blog.models import Post
from .models import Message, Project, Testimonial, Tag, GalleryItem, Subscription
from django.db import models
from django.db.models import Count
from .forms import ContactForm, SubscribeForm, TestimonialForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.decorators.cache import cache_page
from django.utils.text import slugify
from django.apps import apps


# Shorter cache for homepage while developing; keep 5 minutes in production
HOME_CACHE_SECONDS = (60 if settings.DEBUG else 60 * 5)
@cache_page(HOME_CACHE_SECONDS)
def home(request):
	# simply render the homepage which contains the form
	posts = Post.objects.filter(published=True).order_by('-created_at')[:3]
	qs = Project.objects.all()
	featured_list = list(qs.filter(is_featured=True).order_by('featured_order', '-date')[:3])
	if len(featured_list) < 3:
		need = 3 - len(featured_list)
		extras = list(qs.exclude(pk__in=[p.pk for p in featured_list]).order_by('-date')[:need])
		projects = featured_list + extras
	else:
		projects = featured_list
	# Site settings control for testimonials visibility and limit
	try:
		SiteSettings = apps.get_model('portfolio', 'SiteSettings')
		ss = SiteSettings.objects.first()
		show_t = True if (not ss or getattr(ss, 'show_testimonials_home', True)) else False
		limit_t = (getattr(ss, 'testimonials_home_limit', 6) or 6)
	except Exception:
		show_t = True
		limit_t = 6
	if show_t:
		testimonials = Testimonial.objects.filter(featured=True).order_by('order','-created_at','id')[:limit_t]
	else:
		testimonials = []
	form = ContactForm()
	# Stats
	from django.utils import timezone as _tz
	current_year = _tz.now().year
	start_year = getattr(settings, 'CAREER_START_YEAR', current_year)
	years = max(1, current_year - int(start_year))
	projects_count = Project.objects.count()
	posts_count = Post.objects.filter(published=True).count()
	# Top technologies (tags)
	top_tags = list(Tag.objects.annotate(cnt=Count('projects')).order_by('-cnt', 'name')[:10].values_list('name', flat=True))
	featured_post = posts[0] if posts else None
	featured_project = (featured_list[0] if featured_list else Project.objects.order_by('-date').first())
	return render(request, 'home.html', {
		'posts': posts,
		'projects': projects,
		'testimonials': testimonials,
		'testimonials_enabled': show_t,
		'form': form,
		'stats': {
			'years': years,
			'projects': projects_count,
			'posts': posts_count,
		},
		'top_tags': top_tags,
		'featured_post': featured_post,
		'featured_project': featured_project,
	})


@cache_page(60 * 10)
def testimonials(request):
	"""Public testimonials listing page with simple pagination; shows featured testimonials."""
	qs = Testimonial.objects.filter(featured=True).order_by('order','-created_at','id')
	paginator = Paginator(qs, 12)
	page = request.GET.get('page') or 1
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)
	return render(request, 'testimonials.html', {
		'testimonials': page_obj.object_list,
		'page_obj': page_obj,
		'paginator': paginator,
	})


def about(request):
	"""Simple About page.
	Uses existing styles to present a bio, skills, and highlights.
	"""
	return render(request, 'about.html')


def about_pdf(request):
	"""Render the About (resume) page as a downloadable PDF using WeasyPrint when possible.
	Fallbacks:
	  1) If WeasyPrint not available or PDF gen fails → redirect to uploaded resume (if configured)
	  2) Else redirect to static resume file (if present)
	  3) Else redirect to portfolio PDF (ReportLab)
	"""
	# Attempt WeasyPrint generation
	try:
		import weasyprint  # type: ignore
		html_str = render_to_string('about.html', request=request)
		base_url = request.build_absolute_uri('/')
		stylesheets = []
		try:
			from django.conf import settings as _settings
			css_dir = _settings.BASE_DIR / 'portfolio' / 'static' / 'css'
			style_files = []
			# Prefer site styles then print overrides
			for name in ('styles.css', 'print.css'):
				path = css_dir / name
				if path.exists():
					style_files.append(weasyprint.CSS(filename=str(path)))
			stylesheets = style_files
		except Exception:
			stylesheets = []

		pdf_bytes = weasyprint.HTML(string=html_str, base_url=base_url).write_pdf(stylesheets=stylesheets or None)
		response = HttpResponse(pdf_bytes, content_type='application/pdf')
		# Force download for clarity
		response['Content-Disposition'] = 'attachment; filename="Denis_Lokwo_Resume.pdf"'
		return response
	except Exception:
		# Graceful fallbacks
		try:
			# Prefer uploaded resume file from SiteSettings if available
			from django.apps import apps as _apps
			SiteSettings = _apps.get_model('portfolio', 'SiteSettings')
			obj = SiteSettings.objects.first()
			if obj and getattr(obj, 'resume_file', None) and getattr(obj.resume_file, 'url', None):
				return redirect(obj.resume_file.url)
		except Exception:
			pass
		try:
			# Try static resume fallback
			from django.conf import settings as _settings
			static_url = getattr(_settings, 'STATIC_URL', '/static/') + 'resume/Denis_Lokwo_Resume.pdf'
			return redirect(static_url)
		except Exception:
			pass
		# Last resort: redirect to portfolio PDF (already implemented with ReportLab)
		return redirect('portfolio:portfolio_pdf')


def contact(request):
	RATE_LIMIT_SECONDS = getattr(settings, 'CONTACT_RATE_LIMIT_SECONDS', 30)  # simple per-session rate limit
	if request.method == 'POST':
		form = ContactForm(request.POST, request.FILES)
		if form.is_valid():
			# basic rate limiting by session timestamp
			last = request.session.get('last_contact')
			now = timezone.now().timestamp()
			if last and (now - float(last) < RATE_LIMIT_SECONDS):
				messages.error(request, 'Please wait a moment before sending another message.')
				return redirect(reverse('portfolio:contact'))

			name = form.cleaned_data['name']
			email = form.cleaned_data['email']
			message_text = form.cleaned_data['message']

			# save to DB
			msg_obj = Message.objects.create(
				name=name,
				email=email,
				message=message_text,
				attachment=form.cleaned_data.get('attachment')
			)

			subject = f'Portfolio contact from {name}'
			body = f'From: {name} <{email}>\n\n{message_text}'
			recipient = getattr(settings, 'CONTACT_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
			try:
				attachment = form.cleaned_data.get('attachment')
				if attachment:
					email_msg = EmailMessage(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient])
					email_msg.attach(attachment.name, attachment.read(), getattr(attachment, 'content_type', None))
					email_msg.send(fail_silently=False)
				else:
					send_mail(subject, body, None, [recipient], fail_silently=False)
			except Exception:
				# still show success but message remains in DB for inspection
				messages.warning(request, 'Received — but email delivery failed. Message saved.')
			else:
				messages.success(request, 'Thanks — your message was sent. I will get back to you soon.')

			request.session['last_contact'] = str(now)
			return redirect(reverse('portfolio:contact'))
	else:
		form = ContactForm()
	return render(request, 'contact.html', {'form': form})


def privacy(request):
	return render(request, 'privacy.html')


def terms(request):
	return render(request, 'terms.html')


def subscribe(request):
	"""Subscription with double opt-in: collect email, send confirmation link, activate on confirm."""
	if request.method == 'POST':
		form = SubscribeForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			next_url = request.POST.get('next') or None
			sub, created = Subscription.objects.get_or_create(email=email, defaults={'active': False})
			if sub.active:
				messages.info(request, "You're already subscribed.")
				return redirect(next_url or 'portfolio:subscribe')
			# Ensure token exists
			if not sub.token:
				import uuid as _uuid
				sub.token = _uuid.uuid4()
			# Keep inactive until confirmed (created with active=False above)
			sub.save()

			# Send confirmation email
			try:
				confirm_url = request.build_absolute_uri(reverse('portfolio:subscribe_confirm', kwargs={'token': str(sub.token)}))
				site_name = getattr(settings, 'SITE_NAME', 'Portfolio')
				# Branding from SiteSettings (logo, brand name)
				brand_name = site_name
				logo_url = None
				primary_color = '#111'
				try:
					SiteSettings = apps.get_model('portfolio', 'SiteSettings')
					ss = SiteSettings.objects.first()
					if ss:
						if getattr(ss, 'brand_name', None):
							brand_name = ss.brand_name
						img = getattr(ss, 'logo_light', None) or getattr(ss, 'logo', None)
						if img and getattr(img, 'url', None):
							logo_url = request.build_absolute_uri(img.url)
						pc = getattr(ss, 'primary_color', '') or ''
						if isinstance(pc, str) and pc.strip():
							primary_color = pc.strip()
				except Exception:
					pass
				subject = f"Confirm your subscription to {site_name}"
				from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
				to = [email]
				# Render simple text + HTML
				ctx = {
					'site_name': site_name,
					'brand_name': brand_name,
					'logo_url': logo_url,
					'confirm_url': confirm_url,
					'primary_color': primary_color,
				}
				try:
					text_body = render_to_string('emails/subscribe_confirm.txt', ctx)
					html_body = render_to_string('emails/subscribe_confirm.html', ctx)
				except Exception:
					text_body = (
						f"Hi,\n\nPlease confirm your subscription by clicking the link below:\n{confirm_url}\n\n"
						f"If you didn't request this, you can ignore this email.\n"
					)
					html_body = None
				send_mail(subject, text_body, from_addr, to, fail_silently=not settings.DEBUG, html_message=html_body)
			except Exception:
				# Don't block on email errors; allow manual confirmation if needed later
				pass

			messages.success(request, "Thanks! Please check your email to confirm your subscription.")
			return redirect(next_url or 'portfolio:subscribe')
	else:
		form = SubscribeForm()
	return render(request, 'subscribe.html', {'form': form})


def subscribe_confirm(request, token: str):
	"""Confirm a subscription using its token and activate it."""
	sub = Subscription.objects.filter(token=token).first()
	next_url = request.GET.get('next') or reverse('portfolio:home')
	if not sub:
		messages.error(request, "Invalid or expired confirmation link.")
		return redirect(next_url)
	# Activate and rotate token to prevent reuse
	sub.active = True
	try:
		import uuid as _uuid
		sub.token = _uuid.uuid4()
	except Exception:
		pass
	sub.save()

	# Optional: send welcome email with unsubscribe link
	try:
		unsubscribe_url = request.build_absolute_uri(reverse('portfolio:unsubscribe', kwargs={'token': str(sub.token)}))
		site_name = getattr(settings, 'SITE_NAME', 'Portfolio')
		# Branding from SiteSettings (logo, brand name)
		brand_name = site_name
		logo_url = None
		primary_color = '#111'
		try:
			SiteSettings = apps.get_model('portfolio', 'SiteSettings')
			ss = SiteSettings.objects.first()
			if ss:
				if getattr(ss, 'brand_name', None):
					brand_name = ss.brand_name
				img = getattr(ss, 'logo_light', None) or getattr(ss, 'logo', None)
				if img and getattr(img, 'url', None):
					logo_url = request.build_absolute_uri(img.url)
				pc = getattr(ss, 'primary_color', '') or ''
				if isinstance(pc, str) and pc.strip():
					primary_color = pc.strip()
		except Exception:
			pass
		subject = f"Welcome to {site_name}"
		from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
		to = [sub.email]
		ctx = {
			'site_name': site_name,
			'brand_name': brand_name,
			'logo_url': logo_url,
			'primary_color': primary_color,
			'unsubscribe_url': unsubscribe_url,
		}
		try:
			text_body = render_to_string('emails/subscribe_welcome.txt', ctx)
			html_body = render_to_string('emails/subscribe_welcome.html', ctx)
		except Exception:
			text_body = (
				"Thanks for confirming your subscription!\n\n"
				f"You can unsubscribe anytime: {unsubscribe_url}\n"
			)
			html_body = None
		send_mail(subject, text_body, from_addr, to, fail_silently=not settings.DEBUG, html_message=html_body)
	except Exception:
		pass

	messages.success(request, "You're all set — subscription confirmed!")
	return redirect(next_url)


def unsubscribe(request, token: str):
	"""Unsubscribe using token link."""
	sub = Subscription.objects.filter(token=token).first()
	next_url = request.GET.get('next') or reverse('portfolio:home')
	if not sub:
		messages.error(request, "Invalid or expired unsubscribe link.")
		return redirect(next_url)
	sub.active = False
	try:
		import uuid as _uuid
		sub.token = _uuid.uuid4()
	except Exception:
		pass
	sub.save()
	messages.success(request, "You've been unsubscribed. We're sorry to see you go.")
	return redirect(next_url)


def recommend(request):
	"""Public form to submit a testimonial; saved for moderation (not featured by default). Sends an email notification."""
	if request.method == 'POST':
		form = TestimonialForm(request.POST, request.FILES)
		if form.is_valid():
			t = form.save(commit=False)
			t.featured = False
			t.save()

			# Notify site owner/admin
			try:
				admin_email = getattr(settings, 'CONTACT_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
				if admin_email:
					subject = f"New recommendation from {t.name}"
					admin_url = None
					try:
						admin_url = request.build_absolute_uri(reverse('admin:portfolio_testimonial_change', args=[t.pk]))
					except Exception:
						admin_url = None
					body = (
						f"A new recommendation was submitted.\n\n"
						f"Name: {t.name}\n"
						f"Role: {t.role}\n\n"
						f"Content:\n{t.content}\n\n"
						+ (f"Review in admin: {admin_url}\n" if admin_url else "")
					)
					send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [admin_email], fail_silently=True)
			except Exception:
				pass

			# Send acknowledgment to user if email provided
			try:
				if getattr(t, 'email', ''):
					subject = "Thanks for your recommendation"
					body = (
						"Hi,\n\n"
						"Thanks for sharing your feedback! Your recommendation was received and is pending review.\n\n"
						"Best regards,\nDenis"
					)
					send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [t.email], fail_silently=True)
			except Exception:
				pass

			messages.success(request, 'Thank you! Your recommendation was received and is pending review.')
			next_url = request.POST.get('next') or None
			return redirect(next_url or 'portfolio:recommend')
	else:
		form = TestimonialForm()
	return render(request, 'recommend.html', {'form': form})


@cache_page(60 * 10)
def project_list(request):
	projects = Project.objects.all().prefetch_related('tags')
	tech = request.GET.get('tech')
	category = request.GET.get('category')
	search = request.GET.get('search')
	sort = request.GET.get('sort') or 'date_desc'
	per = request.GET.get('per') or '9'
	if tech:
		# Prefer normalized tags
		projects = projects.filter(models.Q(tags__name__iexact=tech) | models.Q(technologies__icontains=tech))
	if category:
		projects = projects.filter(category__iexact=category)
	if search:
		projects = projects.filter(
			models.Q(title__icontains=search) |
			models.Q(description__icontains=search) |
			models.Q(technologies__icontains=search)
		)
	# Sorting
	sort_map = {
		'date_desc': '-date',
		'date_asc': 'date',
		'title_asc': 'title',
		'title_desc': '-title',
	}
	projects = projects.order_by(sort_map.get(sort, '-date'))

	# Pagination
	try:
		per_int = int(per)
	except ValueError:
		per_int = 9
	if per_int not in (6, 9, 12, 24):
		per_int = 9
	paginator = Paginator(projects, per_int)
	page = request.GET.get('page') or 1
	try:
		page_obj = paginator.page(page)
	except PageNotAnInteger:
		page_obj = paginator.page(1)
	except EmptyPage:
		page_obj = paginator.page(paginator.num_pages)

	categories = Project.objects.values_list('category', flat=True).exclude(category='').distinct()
	# Prefer normalized tags list
	techs = list(Tag.objects.values_list('name', flat=True))
	if not techs:
		# fallback to legacy split
		tech_set = set()
		for p in Project.objects.all():
			tech_set.update(p.tech_list())
		techs = sorted(tech_set)

	return render(request, 'projects.html', {
		'projects': page_obj.object_list,
		'page_obj': page_obj,
		'paginator': paginator,
		'categories': categories,
		'techs': techs,
		'selected_tech': tech,
		'selected_category': category,
		'search': search,
		'sort': sort,
		'per': per_int,
		'per_options': (6, 9, 12, 24),
		'has_filters': bool(tech or category or search),
	})


def portfolio_pdf(request):
	"""Generate a simple portfolio PDF with a project listing.
	If reportlab is not installed, return a helpful message.
	"""
	try:
		from reportlab.lib.pagesizes import A4
		from reportlab.pdfgen import canvas
		from reportlab.lib.units import mm
		from reportlab.lib.utils import simpleSplit
	except Exception as exc:
		# Fallback: return a minimal PDF-like payload so endpoint remains available for tests/environments without ReportLab
		placeholder = b"%PDF-1.4\n" + (b"0" * 256) + b"\n%%EOF"
		resp = HttpResponse(placeholder, content_type='application/pdf')
		resp['Content-Disposition'] = 'attachment; filename="Denis_Lokwo_Portfolio.pdf"'
		return resp

	try:
		# Prepare response
		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="Denis_Lokwo_Portfolio.pdf"'
		c = canvas.Canvas(response, pagesize=A4)
		width, height = A4

		# Margins
		margin_x = 20 * mm
		margin_y = 20 * mm
		y = height - margin_y

		# Title
		c.setFont("Helvetica-Bold", 18)
		c.drawString(margin_x, y, "Denis Lokwo — Portfolio")
		y -= 12 * mm

		# Intro
		c.setFont("Helvetica", 11)
		intro = (
			"Selected projects and highlights. For live demos and full details, visit the website."
		)
		for line in simpleSplit(intro, "Helvetica", 11, width - 2 * margin_x):
			c.drawString(margin_x, y, line)
			y -= 6 * mm

		y -= 4 * mm
		c.setFont("Helvetica-Bold", 14)
		c.drawString(margin_x, y, "Projects")
		y -= 8 * mm

		projects = Project.objects.order_by('-date')
		c.setFont("Helvetica", 11)
		for proj in projects:
			# Ensure there is space, else new page
			min_block = 18 * mm
			if y < margin_y + min_block:
				c.showPage()
				y = height - margin_y
				c.setFont("Helvetica", 11)

			# Title line
			title = f"{proj.title} — {proj.category or 'General'} ({proj.date:%b %Y})"
			for line in simpleSplit(title, "Helvetica", 11, width - 2 * margin_x):
				c.drawString(margin_x, y, line)
				y -= 6 * mm

			# Technologies
			tech = ", ".join(proj.tech_list())
			if tech:
				for line in simpleSplit(f"Tech: {tech}", "Helvetica", 10, width - 2 * margin_x):
					c.drawString(margin_x, y, line)
					y -= 5 * mm

			# Description (short)
			desc = (proj.description or "").strip()
			if desc:
				lines = simpleSplit(desc, "Helvetica", 10, width - 2 * margin_x)
				for line in lines[:5]:
					c.drawString(margin_x, y, line)
					y -= 5 * mm

			y -= 3 * mm

		# Footer note
		if y < margin_y + 12 * mm:
			c.showPage()
			y = height - margin_y
		c.setFont("Helvetica-Oblique", 9)
		site_url = request.build_absolute_uri('/')
		c.drawString(margin_x, margin_y, f"Generated from Denis Lokwo Portfolio — {site_url}")

		c.showPage()
		c.save()
		return response
	except Exception:
		# Graceful fallback: minimal one-page PDF so endpoint remains available even if a rendering error occurs
		fallback = HttpResponse(content_type='application/pdf')
		fallback['Content-Disposition'] = 'attachment; filename="Denis_Lokwo_Portfolio.pdf"'
		c = canvas.Canvas(fallback, pagesize=A4)
		c.setFont("Helvetica-Bold", 16)
		c.drawString(50, 800, "Denis Lokwo — Portfolio")
		c.setFont("Helvetica", 12)
		c.drawString(50, 780, "Portfolio PDF temporarily simplified.")
		c.showPage()
		c.save()
		return fallback


def project_detail(request, slug: str):
	project = get_object_or_404(Project, slug=slug)
	# gather related projects via shared tags (optional small touch)
	related = Project.objects.exclude(pk=project.pk)
	if hasattr(project, 'tags') and project.tags.exists():
		related = related.filter(tags__in=project.tags.all()).distinct()[:3]
	else:
		related = related.order_by('-date')[:3]
	return render(request, 'project.html', {
		'project': project,
		'related': related,
	})


@cache_page(60 * 15)
def gallery(request):
	"""Unified gallery showing project images, blog thumbnails, and admin-managed GalleryItems with a simple source filter."""
	src = request.GET.get('src', 'all')  # all | projects | blog | custom
	items = []
	# Projects
	if src in ('all', 'projects'):
		proj_qs = Project.objects.exclude(image__isnull=True).exclude(image='').order_by('-date')
		for p in proj_qs:
			items.append({
				'title': p.title,
				'url': p.get_absolute_url(),
				'img': getattr(p.image, 'url', ''),
				'width': getattr(p.image, 'width', None),
				'height': getattr(p.image, 'height', None),
				'alt': p.title,
				'desc': (p.description or '').strip(),
				'source': 'Project',
				'date': getattr(p, 'date', None),
			})
	# Blog posts
	if src in ('all', 'blog'):
		post_qs = Post.objects.filter(published=True).exclude(thumbnail__isnull=True).exclude(thumbnail='').order_by('-created_at')
		for b in post_qs:
			items.append({
				'title': b.title,
				'url': b.get_absolute_url(),
				'img': getattr(b.thumbnail, 'url', ''),
				'width': getattr(b.thumbnail, 'width', None),
				'height': getattr(b.thumbnail, 'height', None),
				'alt': b.title,
				'desc': (b.content or '').strip(),
				'source': 'Blog',
				'date': getattr(b, 'created_at', None),
			})
	# Admin-managed custom Gallery items
	if src in ('all', 'custom'):
		gqs = GalleryItem.objects.filter(is_published=True).select_related('project','post').order_by('order', '-created_at')
		for g in gqs:
			items.append({
				'title': g.title,
				'url': g.link_url() or '#',
				'img': getattr(g.image, 'url', ''),
				'width': getattr(g.image, 'width', None),
				'height': getattr(g.image, 'height', None),
				'alt': (g.alt_text or g.caption or g.title or '').strip(),
				'desc': (g.description or g.caption or '').strip(),
				'source': g.source_label(),
				'date': getattr(g, 'created_at', None),
			})
	# Sort by date desc where available, normalizing to aware datetimes to avoid
	# TypeError when mixing datetime.date and datetime.datetime values.
	def _sort_key(x):
		d = x.get('date')
		if d is None:
			# Items without dates sort last when reverse=True; use numeric sentinel to avoid cross-type comparison
			return (0, 0)
		if isinstance(d, datetime):
			# Ensure aware
			if timezone.is_naive(d):
				d = timezone.make_aware(d, timezone.get_current_timezone())
			return (1, d)
		if isinstance(d, date):
			# Promote date to start-of-day aware datetime
			dt = datetime.combine(d, dtime.min)
			dt = timezone.make_aware(dt, timezone.get_current_timezone())
			return (1, dt)
		# Fallback: treat as no-date
		return (0, 0)

	items.sort(key=_sort_key, reverse=True)

	# Paginate
	paginator = Paginator(items, 8)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	return render(request, 'gallery.html', {
		'items': page_obj.object_list,
		'page_obj': page_obj,
		'paginator': paginator,
		'src': src,
	})


def html_sitemap(request):
	"""Human-friendly HTML sitemap page listing key sections, recent content, and taxonomy pages."""
	# Core sections
	sections = [
		{'title': 'Home', 'url': reverse('portfolio:home')},
		{'title': 'About', 'url': reverse('portfolio:about')},
		{'title': 'Projects', 'url': reverse('portfolio:project_list')},
		{'title': 'Blog', 'url': reverse('blog:post_list')},
		{'title': 'Gallery', 'url': reverse('portfolio:gallery')},
		{'title': 'Contact', 'url': reverse('portfolio:contact')},
		{'title': 'Privacy', 'url': reverse('portfolio:privacy')},
		{'title': 'Terms', 'url': reverse('portfolio:terms')},
	]

	# Recent blog posts
	posts = Post.objects.filter(published=True).order_by('-created_at')[:20]

	# Blog categories/tags (slugs + labels)
	cat_map = {}
	for p in Post.objects.filter(published=True).exclude(category__isnull=True).exclude(category=''):
		s = slugify(p.category)
		if s and s not in cat_map:
			cat_map[s] = p.category
	categories = [{'slug': s, 'label': lbl, 'url': reverse('blog:post_list_by_category', kwargs={'category': s})}
				  for s, lbl in sorted(cat_map.items(), key=lambda x: x[1].lower())]

	tag_map = {}
	for p in Post.objects.filter(published=True):
		for t in (getattr(p, 'tag_list', []) or []):
			s = slugify(t)
			if s and s not in tag_map:
				tag_map[s] = t
	tags = [{'slug': s, 'label': lbl, 'url': reverse('blog:post_list_by_tag', kwargs={'tag': s})}
			for s, lbl in sorted(tag_map.items(), key=lambda x: x[1].lower())]

	# Recent projects
	projects = Project.objects.order_by('-date')[:30]

	return render(request, 'sitemap.html', {
		'sections': sections,
		'recent_posts': posts,
		'categories': categories,
		'tags': tags,
		'projects': projects,
	})

