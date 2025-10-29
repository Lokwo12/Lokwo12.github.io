# Denis Lokwo — Portfolio (Django)

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2%2B-092E20?logo=django&logoColor=white)

A full‑featured, production‑ready portfolio and blog built with Django 5.x. It showcases projects, blog posts, and a curated visual gallery; includes a polished contact flow (file uploads + email), SEO and sitemaps, dark/light themes, PDF exports, and a brandable header with logo and favicon variants. Most content is admin‑editable.

## Highlights

- Projects
	- Slugged detail pages with related projects and hero thumbnails (16:9 responsive sizing)
	- Tags, categories, pagination, and “Selected/Featured” projects for the homepage

- Blog
	- List and detail pages, categories and tags with pretty URLs, and RSS at `/blog/rss.xml`
	- Thumbnails on list/detail and in the Gallery

- Gallery
	- Unified visual gallery that aggregates project images, blog thumbnails, and admin‑managed custom items
	- Source filter chips (All, Projects, Blog, Custom)
	- 4‑column responsive grid, hover effects, and an accessible lightbox with next/prev and an “Open” button
	- Captions/descriptions visible under thumbnails; full description in the lightbox
	- Dedicated alt text per image for screen readers (improves a11y/SEO)

- About & Resume
	- Rich About page driven by a Profile model (experience, education, awards, skills/tools)
	- Resume downloads and a printable Portfolio PDF at `/portfolio.pdf` (ReportLab)
	- About page PDF generation via WeasyPrint at `/about.pdf` (with robust fallbacks)

- Contact & Scheduling
	- Contact form with file attachment support (saved and emailed)
	- Inline Calendly embed (configurable)

- Admin experience
	- Site Settings: brand name, logos (default + light/dark variants), favicon, hero texts/roles, contact info, socials, GA4 id, consent
	- Active Profile selection: choose which Profile powers the site (name/avatar/links)
	- Optional homepage avatar override via Site Settings (doesn’t affect About)
	- GalleryItem admin with thumbnails, filters, bulk publish/unpublish, ordering, and caption/description
	- Friendly admin styling with sticky headers and thumbnails

- SEO, a11y, and performance
	- Meta descriptions, OpenGraph/Twitter tags, JSON‑LD (breadcrumbs, person, article)
	- XML sitemap and robots.txt; optional HTML sitemap page
	- Caching: home and list views (5–15 mins), sitemap/robots/RSS (24h)
	- Responsive images, lazy loading, accessible landmarks and aria attributes
	- Theme‑aware logos (light/dark)

## Data model overview

- `Project`: title, slug, description, category, tags, image, featured flags
- `Post` (blog): title, slug, content, category, tags, thumbnail, published timestamps
- `Profile`: name, title, intro/summary, location, contact, avatar; related items:
	- `ExperienceItem`, `EducationItem`, `CertificationItem`, `AwardItem`, `AchievementItem`, `SkillItem`
- `SiteSettings`: brand name, logo variants (default/light/dark), favicon, hero texts/roles, socials, contact, GA4 id/consent, Calendly URL, resume file, active_profile, optional homepage avatar override
- `GalleryItem`: title, image, caption, description, optional link to Project or Post (or external URL), publish flag, order
	- Also: `alt_text` for accessible alternative text

## Requirements

- Python 3.11+
- Django 5.2+

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment

```powershell
py -3 -m venv venv
venv\Scripts\Activate
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Migrate and create a superuser

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4) Run the server

```powershell
python manage.py runserver
```

Open http://127.0.0.1:8000 and the admin at http://127.0.0.1:8000/admin

## Initial admin setup

1) Site settings
	 - Set Brand name
	 - Upload brand logos (default + light/dark) and a favicon (SVG/PNG)
	 - Enter email/phone/location, social links, GA4 ID (optional), Calendly URL (optional)
	 - Optionally upload a Resume file (used by About/Downloads)

2) Profile and homepage avatar
	 - Create/edit a Profile and upload an Avatar
	 - In Site settings, choose the Active profile used across the site
	 - Optionally upload a “Home avatar” in Site settings to override the homepage avatar only

3) Projects & blog
	 - Add Projects with images and tags; mark featured ones to appear on the homepage
	 - Add Blog posts with thumbnails, categories, and tags

4) Gallery (optional)
	 - Add Gallery items (title, image) and optionally link them to a Project or Blog post (or provide an external URL)
	 - Provide alt text (for accessibility), a caption, and a longer description; set published and order

## Caching & performance

- Home and list pages are cached for 5–15 minutes
- Sitemap, robots, and RSS cached for 24 hours
- In development: the homepage cache is shortened to 60 seconds to reflect admin changes faster. You can also add a querystring like `?refresh=1` or restart the server to bypass cache quickly.

## Deployment

Production checklist:

1) Configure environment

- `DEBUG=False`
- `ALLOWED_HOSTS` set to your domain(s)
- Email settings (SMTP) if using the contact form for real emails
- Storage for media uploads (local volume or cloud storage)

2) Static files

```powershell
python manage.py collectstatic --noinput
```

`WhiteNoise` serves static assets when `DEBUG=False`. Ensure your reverse proxy caches static files aggressively.

3) WSGI/ASGI server

- WSGI: `gunicorn myportfolio.wsgi:application --bind 0.0.0.0:8000`
- ASGI: `uvicorn myportfolio.asgi:application --host 0.0.0.0 --port 8000`

Behind Nginx/Traefik/Caddy with HTTPS. Set security headers/toggles (HSTS, secure cookies) as noted above.

4) Media

Keep `/media/` persisted. If deploying to containers, mount a volume or use a cloud bucket for uploads (avatars, project images, gallery, etc.).

## Routes

- Home: `/`
- Projects: `/projects/` and `/projects/<slug>/`
- Blog: `/blog/`, `/blog/<slug>/`, RSS at `/blog/rss.xml`
- Gallery: `/gallery/`
- About: `/about/` (+ PDF at `/about.pdf`)
- Contact: `/contact/`
- Portfolio PDF: `/portfolio.pdf`
- Sitemap: `/sitemap.xml` (plus optional HTML sitemap page)
- Robots: `/robots.txt`

## Environment variables (recommended)

- `DEBUG` = True | False
- `ALLOWED_HOSTS` = example.com,www.example.com
- `CSRF_TRUSTED_ORIGINS` = https://example.com,https://www.example.com
- `DEFAULT_FROM_EMAIL` = no-reply@example.com
- `CONTACT_EMAIL` = owner@example.com
- `EMAIL_BACKEND` or SMTP settings: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`
- `GA_MEASUREMENT_ID` = G-XXXXXXX (enables analytics after consent)
- `CALENDLY_URL` = https://calendly.com/your-link (optional)
- `CAREER_START_YEAR` = 2020 (for experience years on About)

Media & static

- Static URL: `/static/`; WhiteNoise is used automatically when `DEBUG=False`
- Media URL: `/media/` for uploads (avatars, project images, gallery, etc.)

Collect static for production:

```powershell
python manage.py collectstatic --noinput
```

Security toggles (HTTPS):

- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS=31536000`

## WeasyPrint notes (About PDF)

WeasyPrint is used to generate `/about.pdf`. On Windows, it may require additional system libraries for full CSS/Font support. If missing, the app gracefully falls back to a pre‑uploaded resume or a static PDF.

## Tests

```powershell
python manage.py test
```

## Tips

- Default social image: `static/images/og-default.svg`. Project/blog pages use their own images where available.
- Theme‑aware brand logo: upload both light and dark variants for crisp rendering on each theme.
- To adjust the homepage hero intro/roles, edit `portfolio/templates/home.html` or update Site Settings (hero fields).

