from django.contrib import admin
from .models import Message, Project, Testimonial, Tag, Profile, ExperienceItem, EducationItem, CertificationItem, AwardItem, SiteSettings, AchievementItem, SkillItem, GalleryItem, Subscription
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import path
from django.template.response import TemplateResponse
from django import forms
from django.utils.html import format_html


class ReplyForm(forms.Form):
	subject = forms.CharField(max_length=200, initial='Re: Thanks for reaching out')
	body = forms.CharField(widget=forms.Textarea, initial='Thanks for contacting me. I will reply shortly.')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
	list_display = ('name', 'email', 'created_at', 'processed')
	list_filter = ('processed', 'created_at')
	search_fields = ('name', 'email', 'message')
	readonly_fields = ('created_at','key')
	actions = ['mark_processed']

	def get_urls(self):
		urls = super().get_urls()
		custom = [
			path('<int:message_id>/reply/', self.admin_site.admin_view(self.reply_view), name='portfolio_message_reply'),
		]
		return custom + urls

	def reply_view(self, request, message_id, *args, **kwargs):
		message = self.get_object(request, message_id)
		if request.method == 'POST':
			form = ReplyForm(request.POST)
			if form.is_valid():
				subject = form.cleaned_data['subject']
				body = form.cleaned_data['body']
				send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [message.email])
				message.processed = True
				message.save()
				self.message_user(request, 'Reply sent and message marked processed.')
				return redirect('..')
		else:
			form = ReplyForm()
		context = dict(self.admin_site.each_context(request), form=form, message=message)
		return TemplateResponse(request, 'admin/portfolio/reply.html', context)

	def mark_processed(self, request, queryset):
		updated = queryset.update(processed=True)
		self.message_user(request, f'{updated} message(s) marked processed')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	def thumb(self, obj):
		if getattr(obj, 'image', None):
			try:
				url = obj.image.url
				return format_html('<img src="{}" alt="" style="width:48px;height:auto;border-radius:6px;box-shadow:0 1px 6px rgba(0,0,0,.2)">', url)
			except Exception:
				return ''
		return ''
	thumb.short_description = 'Image'

	list_display = ('thumb','title', 'category', 'date', 'is_featured', 'featured_order', 'slug', 'key')
	list_display_links = ('title',)
	search_fields = ('title', 'description', 'technologies', 'category', 'tags__name')
	list_filter = ('category', 'date', 'tags', 'is_featured')
	prepopulated_fields = { 'slug': ('title',) }
	list_editable = ('is_featured','featured_order')
	ordering = ('-date', 'featured_order')
	readonly_fields = ('key',)
	autocomplete_fields = ('tags',)

	def get_queryset(self, request):
		qs = super().get_queryset(request)
		# Prefetch tags to reduce queries on changelist
		return qs.prefetch_related('tags')
	fieldsets = (
		(None, {'fields': ('title','slug','category','date','image','url','description')}),
		('Tech', {'fields': ('technologies','tags')}),
		('Featured', {'fields': ('is_featured','featured_order')}),
		('Meta', {'fields': ('key',)}),
	)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
	search_fields = ('name',)
	list_display = ('name',)
	readonly_fields = ('key',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ('name', 'role', 'email', 'featured', 'order', 'created_at')
	search_fields = ('name', 'role', 'email', 'content')
	list_filter = ('featured', 'created_at')
	readonly_fields = ('key',)
	list_editable = ('featured','order')

	actions = ['notify_selected_featured']

	def save_model(self, request, obj, form, change):
		# Detect if 'featured' changed to True and notify user if email provided
		notify = False
		if change:
			try:
				old = Testimonial.objects.get(pk=obj.pk)
				if not old.featured and obj.featured:
					notify = True
			except Testimonial.DoesNotExist:
				pass
		else:
			# On create, don't notify; only on approval/feature
			notify = False
		super().save_model(request, obj, form, change)
		if notify and getattr(obj, 'email', ''):
			try:
				site_name = getattr(settings, 'SITE_NAME', 'Portfolio')
				subject = f"Your recommendation was featured on {site_name}!"
				body = (
					f"Hi {obj.name},\n\n"
					f"Thanks again for your kind words. Your recommendation has just been featured on my portfolio.\n\n"
					f"Best regards,\nDenis"
				)
				send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [obj.email], fail_silently=True)
				self.message_user(request, f"Notified {obj.email} about featuring.")
			except Exception:
				self.message_user(request, f"Could not notify {obj.email}.", level='warning')

	def notify_selected_featured(self, request, queryset):
		count = 0
		for t in queryset:
			if t.featured and getattr(t, 'email', ''):
				try:
					site_name = getattr(settings, 'SITE_NAME', 'Portfolio')
					subject = f"Your recommendation was featured on {site_name}!"
					body = (
						f"Hi {t.name},\n\n"
						f"Thanks again for your kind words. Your recommendation has just been featured on my portfolio.\n\n"
						f"Best regards,\nDenis"
					)
					send_mail(subject, body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [t.email], fail_silently=True)
					count += 1
				except Exception:
					pass
		self.message_user(request, f"Sent notifications to {count} user(s).")
	notify_selected_featured.short_description = "Notify users for selected featured testimonials"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("name", "title", "location", "updated_at")
	search_fields = ("name", "title", "location", "email")
	readonly_fields = ("about_preview", "created_at", "updated_at", "key")
	fieldsets = (
		(None, {
			'fields': ('name','title','intro','summary','avatar','about_preview')
		}),
		('Contact', {
			'fields': ('location','email','phone','whatsapp')
		}),
		('Meta JSON', {
			'fields': ('skills','tools','languages','interests','links','achievements'),
			'classes': ('collapse',)
		}),
		('Legacy JSON (optional)', {
			'fields': ('experience','education','certifications','awards'),
			'classes': ('collapse',)
		}),
		('Timestamps', {
			'fields': ('key','created_at','updated_at')
		}),
	)

	def about_preview(self, obj):
		try:
			from django.urls import reverse
			url = reverse('portfolio:about')
			return format_html('<a href="{}" target="_blank" rel="noopener">Open About page</a>', url)
		except Exception:
			return ''
	about_preview.short_description = "Preview"

class ExperienceInline(admin.TabularInline):
	class ExperienceItemForm(forms.ModelForm):
		technologies_csv = forms.CharField(
			label='Technologies', required=False,
			help_text="Comma-separated list, e.g. Python, Django, React, PostgreSQL"
		)

		class Meta:
			model = ExperienceItem
			exclude = ('technologies','key')

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			inst = self.instance or None
			if inst and inst.pk:
				vals = getattr(inst, 'technologies', None)
				if isinstance(vals, (list, tuple)):
					self.fields['technologies_csv'].initial = ", ".join([str(x) for x in vals if str(x).strip()])
				elif isinstance(vals, str):
					self.fields['technologies_csv'].initial = vals

		def clean(self):
			cleaned = super().clean()
			text = cleaned.get('technologies_csv')
			if text:
				items = [i.strip() for i in str(text).split(',') if i.strip()]
			else:
				items = []
			self.instance.technologies = items
			return cleaned

	model = ExperienceItem
	form = ExperienceItemForm
	extra = 0
	fields = (
		'order','role','company','company_url',
		'start_year','end_year','is_current','period',
		'location','employment_type','work_mode','technologies_csv',
		'summary','logo'
	)
	ordering = ('order', 'id')
	show_change_link = True
	readonly_fields = ('key',)

class EducationInline(admin.TabularInline):
	class EducationItemForm(forms.ModelForm):
		courses_csv = forms.CharField(
			label='Courses offered', required=False,
			help_text="Comma-separated list, e.g. Algorithms, Databases, Operating Systems"
		)
		technologies_csv = forms.CharField(
			label='Technologies', required=False,
			help_text="Comma-separated list, e.g. Python, Django, SQL"
		)
		activities_csv = forms.CharField(
			label='Activities', required=False,
			help_text="Comma-separated list, e.g. Programming Club President, Hackathon Winner"
		)

		class Meta:
			model = EducationItem
			exclude = ('courses','technologies','activities','key')

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			# Initialize CSV fields from JSON/list fields
			def join_list(val):
				if not val:
					return ''
				if isinstance(val, (list, tuple)):
					return ", ".join([str(x) for x in val if str(x).strip()])
				if isinstance(val, str):
					return val
				return ''
			inst = self.instance or None
			if inst and inst.pk:
				self.fields['courses_csv'].initial = join_list(getattr(inst, 'courses', None))
				self.fields['technologies_csv'].initial = join_list(getattr(inst, 'technologies', None))
				self.fields['activities_csv'].initial = join_list(getattr(inst, 'activities', None))

		def clean(self):
			cleaned = super().clean()
			# Parse CSVs into lists; ensure empty lists not None
			def split_csv(text):
				if not text:
					return []
				items = [i.strip() for i in str(text).split(',')]
				return [i for i in items if i]
			self.instance.courses = split_csv(cleaned.get('courses_csv'))
			self.instance.technologies = split_csv(cleaned.get('technologies_csv'))
			self.instance.activities = split_csv(cleaned.get('activities_csv'))
			return cleaned

	model = EducationItem
	form = EducationItemForm
	extra = 0
	fields = (
		'order','degree','field_of_study','institution','institution_url',
		'period','study_mode','location','duration_years',
		'gpa','honors','summary','courses_csv','technologies_csv','thesis_title','activities_csv','logo'
	)
	ordering = ('order', 'id')
	show_change_link = True
	readonly_fields = ('key',)

class CertificationInline(admin.TabularInline):
	model = CertificationItem
	extra = 0
	fields = ('order','name','issuer','year')
	ordering = ('order', 'id')
	show_change_link = True
	readonly_fields = ('key',)

class AwardInline(admin.TabularInline):
	model = AwardItem
	extra = 0
	fields = ('order','name','issuer','year')
	ordering = ('order', 'id')
	show_change_link = True
	readonly_fields = ('key',)

class AchievementInline(admin.TabularInline):
	model = AchievementItem
	extra = 0
	fields = ('order','text','metric')
	ordering = ('order','id')
	show_change_link = True
	readonly_fields = ('key',)

class SkillInline(admin.TabularInline):
	model = SkillItem
	extra = 0
	fields = ('order','name','category')
	ordering = ('category','order','name')
	show_change_link = True
	readonly_fields = ('key',)

ProfileAdmin.inlines = [ExperienceInline, EducationInline, CertificationInline, AwardInline, AchievementInline, SkillInline]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
	fieldsets = (
	(None, {'fields': ('brand_name','active_profile')}),
	('Brand', {'fields': ('logo','logo_light','logo_dark','primary_color','favicon','default_og_image')}),
		('Homepage', {'fields': ('home_avatar','show_testimonials_home','testimonials_home_limit')}),
		('Hero', {'fields': ('home_eyebrow','hero_heading','hero_subheading','home_roles','resume_file')}),
		('Contact', {'fields': ('contact_title','contact_subtitle','email','phone','location','calendly_url')}),
	('Social', {'fields': ('github_url','linkedin_url','twitter_url','youtube_url')}),
		('Analytics', {'fields': ('analytics_measurement_id','consent_required')}),
		('Timestamps', {'fields': ('key','created_at','updated_at')}),
	)
	autocomplete_fields = ('active_profile',)
	list_select_related = ('active_profile',)
	readonly_fields = ('key','created_at','updated_at')

	def has_add_permission(self, request):
		# Allow only a single instance
		return not SiteSettings.objects.exists()

# Admin branding
admin.site.site_header = "Portfolio Admin"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Site Management"


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
	class SourceFilter(admin.SimpleListFilter):
		title = 'Source'
		parameter_name = 'source'

		def lookups(self, request, model_admin):
			return (
				('project', 'Project'),
				('blog', 'Blog'),
				('custom', 'Custom'),
			)

		def queryset(self, request, queryset):
			val = self.value()
			if val == 'project':
				return queryset.exclude(project__isnull=True)
			if val == 'blog':
				return queryset.exclude(post__isnull=True)
			if val == 'custom':
				return queryset.filter(project__isnull=True, post__isnull=True)
			return queryset

	def thumb(self, obj):
		if getattr(obj, 'image', None):
			try:
				return format_html('<img src="{}" alt="" style="width:64px;height:48px;object-fit:cover;border-radius:6px;box-shadow:0 1px 6px rgba(0,0,0,.2)">', obj.image.url)
			except Exception:
				return ''
		return ''
	thumb.short_description = 'Image'

	def source(self, obj):
		return obj.source_label()
	source.short_description = 'Source'

	list_display = ('thumb','title','source','is_published','order','created_at')
	list_display_links = ('title',)
	search_fields = ('title','alt_text','caption','description')
	list_filter = ('is_published','created_at', SourceFilter)
	ordering = ('order','-created_at')
	readonly_fields = ('created_at','key')
	autocomplete_fields = ('project','post')
	list_select_related = ('project','post')
	list_editable = ('is_published','order')
	fieldsets = (
		(None, {'fields': ('title','image')}),
		('Text', {'fields': ('alt_text','caption','description')}),
		('Link', {'fields': ('project','post','external_url')}),
		('Meta', {'fields': ('key','is_published','order','created_at')}),
	)

	actions = ['publish_selected','unpublish_selected']

	def publish_selected(self, request, queryset):
		updated = queryset.update(is_published=True)
		self.message_user(request, f"{updated} item(s) published.")

	def unpublish_selected(self, request, queryset):
		updated = queryset.update(is_published=False)
		self.message_user(request, f"{updated} item(s) unpublished.")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
	list_display = ('email','active','created_at')
	list_filter = ('active','created_at')
	search_fields = ('email',)
	readonly_fields = ('created_at','token')

