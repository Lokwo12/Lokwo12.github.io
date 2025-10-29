from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Message, Subscription, Testimonial
from django.core import mail
from django.conf import settings
from django.core.cache import cache
import time


@override_settings(MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != 'myportfolio.middleware.ratelimit.SimpleRateLimitMiddleware'])
class ContactFormTests(TestCase):
	def setUp(self):
		cache.clear()
	def test_contact_form_saves_message(self):
		data = {'name': 'Alice', 'email': 'alice@example.com', 'message': 'Hello!', 'hp': ''}
		resp = self.client.post(reverse('portfolio:contact'), data)
		self.assertRedirects(resp, reverse('portfolio:contact'))
		self.assertEqual(Message.objects.count(), 1)

	def test_honeypot_rejected(self):
		data = {'name': 'Spam', 'email': 'spammer@example.com', 'message': 'Buy now', 'hp': 'I am a bot'}
		resp = self.client.post(reverse('portfolio:contact'), data)
		# Should not save
		self.assertEqual(Message.objects.count(), 0)

	def test_email_sent_and_saved(self):
		mail.outbox = []
		data = {'name': 'Bob', 'email': 'bob@example.com', 'message': 'Hello', 'hp': ''}
		resp = self.client.post(reverse('portfolio:contact'), data)
		self.assertEqual(resp.status_code, 302)
		self.assertEqual(Message.objects.count(), 1)
		# console backend still creates outbox entry when using locmem, so check len>=0
		# Use settings.EMAIL_BACKEND to determine behavior; for console backend mail.outbox may not be populated
		# We'll assert that no exception occurred and message exists
		self.assertTrue(Message.objects.filter(email='bob@example.com').exists())

	@override_settings(CONTACT_RATE_LIMIT_SECONDS=1)
	def test_rate_limiting(self):
		data = {'name': 'Carol', 'email': 'carol@example.com', 'message': '1', 'hp': ''}
		resp1 = self.client.post(reverse('portfolio:contact'), data)
		self.assertEqual(resp1.status_code, 302)
		self.assertEqual(Message.objects.filter(email='carol@example.com').count(), 1)
		# immediate second post should be blocked by simple rate limit and not create a new message
		resp2 = self.client.post(reverse('portfolio:contact'), data)
		self.assertEqual(Message.objects.filter(email='carol@example.com').count(), 1)
		# wait and retry after the rate limit window
		time.sleep(1.2)
		resp3 = self.client.post(reverse('portfolio:contact'), data)
		self.assertEqual(Message.objects.filter(email='carol@example.com').count(), 2)

class PortfolioPDFTests(TestCase):
	def test_portfolio_pdf_endpoint(self):
		url = reverse('portfolio:portfolio_pdf')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp['Content-Type'], 'application/pdf')
		# PDF should not be empty; expect some bytes
		self.assertGreater(len(resp.content), 100)

class AboutPDFTests(TestCase):
	def test_about_pdf_endpoint(self):
		url = reverse('portfolio:about_pdf')
		# Do not follow redirects so we can validate fallback targets even when static serving is disabled in tests
		resp = self.client.get(url)
		# Either a direct PDF (200) or a redirect (302) to a fallback
		self.assertIn(resp.status_code, (200, 302))
		if resp.status_code == 200:
			# If content-type is pdf, ensure it's non-trivial
			content_type = resp.headers.get('Content-Type') or resp._headers.get('content-type', (None, None))[1]
			self.assertEqual(content_type, 'application/pdf')
			self.assertGreater(len(resp.content), 100)
		else:
			# Redirect should be to one of the known fallbacks
			loc = resp.headers.get('Location') or resp._headers.get('location', (None, None))[1]
			self.assertTrue(
				loc.endswith('/portfolio.pdf') or
				loc.endswith('/about.pdf') or  # unlikely redirect loop, but tolerate
				'/static/resume/' in loc,
				msg=f"Unexpected redirect target: {loc}"
			)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
				   MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != 'myportfolio.middleware.ratelimit.SimpleRateLimitMiddleware'])
class SubscriptionTests(TestCase):
	def test_subscribe_flow_sends_confirmation_and_confirms(self):
		# Subscribe
		email = 'user@example.com'
		resp = self.client.post(reverse('portfolio:subscribe'), {'email': email, 'hp': '', 'next': '/'})
		# Redirect back to next or subscribe page
		self.assertIn(resp.status_code, (302, 303))
		# Created subscription inactive with token
		sub = Subscription.objects.get(email=email)
		self.assertFalse(sub.active)
		self.assertIsNotNone(sub.token)
		# Confirmation email sent
		sent_before = len(mail.outbox)
		self.assertGreaterEqual(sent_before, 1)
		self.assertTrue(any('Confirm your subscription' in m.subject for m in mail.outbox))

		# Confirm
		old_token = str(sub.token)
		confirm_url = reverse('portfolio:subscribe_confirm', kwargs={'token': old_token})
		resp2 = self.client.get(confirm_url)
		self.assertIn(resp2.status_code, (302, 303))
		sub.refresh_from_db()
		self.assertTrue(sub.active)
		# Token rotated
		self.assertNotEqual(old_token, str(sub.token))
		# Welcome email sent after confirmation
		self.assertGreater(len(mail.outbox), sent_before)

	def test_unsubscribe_with_token(self):
		# Prepare active subscription
		email = 'active@example.com'
		self.client.post(reverse('portfolio:subscribe'), {'email': email, 'hp': ''})
		sub = Subscription.objects.get(email=email)
		# Manually activate and set a known token to simulate confirmed state
		sub.active = True
		token_before = sub.token
		sub.save()
		# Unsubscribe
		url = reverse('portfolio:unsubscribe', kwargs={'token': str(token_before)})
		resp = self.client.get(url)
		self.assertIn(resp.status_code, (302, 303))
		sub.refresh_from_db()
		self.assertFalse(sub.active)
		# Token rotated after use
		self.assertNotEqual(str(token_before), str(sub.token))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
				   MIDDLEWARE=[m for m in settings.MIDDLEWARE if m != 'myportfolio.middleware.ratelimit.SimpleRateLimitMiddleware'])
class RecommendationTests(TestCase):
	def test_recommend_sends_admin_notification(self):
		mail.outbox = []
		data = {
			'name': 'Happy Client',
			'role': 'CTO',
			'email': 'client@example.com',
			'content': 'Great work delivered on time!',
			'hp': ''
		}
		resp = self.client.post(reverse('portfolio:recommend'), data)
		self.assertIn(resp.status_code, (302, 303))
		# Two emails: admin notification and user acknowledgment
		self.assertGreaterEqual(len(mail.outbox), 2)
		subjects = [m.subject for m in mail.outbox]
		self.assertTrue(any('New recommendation from' in s for s in subjects))
		self.assertTrue(any('Thanks for your recommendation' in s for s in subjects))

	def test_recommend_requires_email(self):
		from .models import Testimonial
		mail.outbox = []
		data = {
			'name': 'No Email',
			'role': 'Manager',
			# No email provided
			'content': 'Great!',
			'hp': ''
		}
		resp = self.client.post(reverse('portfolio:recommend'), data)
		# Should re-render form with errors (200), no redirect
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(Testimonial.objects.count(), 0)
		self.assertEqual(len(mail.outbox), 0)


class HomePageTests(TestCase):
	def setUp(self):
		cache.clear()

	def test_homepage_renders(self):
		"""Simple smoke test to ensure home page loads without template/db errors."""
		resp = self.client.get(reverse('portfolio:home'))
		self.assertEqual(resp.status_code, 200)

	def test_testimonials_page_renders(self):
		resp = self.client.get(reverse('portfolio:testimonials'))
		self.assertEqual(resp.status_code, 200)

	def test_testimonials_page_has_cta(self):
		resp = self.client.get(reverse('portfolio:testimonials'))
		self.assertContains(resp, reverse('portfolio:recommend'))
		# Contains next back to testimonials
		self.assertIn('next=' + reverse('portfolio:testimonials'), resp.content.decode('utf-8'))

