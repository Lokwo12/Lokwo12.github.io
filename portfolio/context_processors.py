from django.conf import settings
from django.apps import apps

def analytics(request):
    # Keep backward compatibility for templates still referencing CALENDLY_URL
    cal = getattr(settings, 'CALENDLY_URL', '')
    try:
        SiteSettings = apps.get_model('portfolio', 'SiteSettings')
        obj = SiteSettings.objects.first()
        if obj and getattr(obj, 'calendly_url', ''):
            cal = obj.calendly_url
    except Exception:
        pass
    return {
        'GA_MEASUREMENT_ID': getattr(settings, 'GA_MEASUREMENT_ID', None),
        'CALENDLY_URL': cal,
    }

def profile(request):
    """Expose profile data to templates from settings.PROFILE with safe defaults."""
    profile = getattr(settings, 'PROFILE', {}) or {}
    # Try to load DB Profile if available
    try:
        Profile = apps.get_model('portfolio', 'Profile')
        SiteSettings = apps.get_model('portfolio', 'SiteSettings')
        # Prefer explicitly selected active_profile when set
        db_obj = None
        ss = SiteSettings.objects.first()
        if ss and getattr(ss, 'active_profile_id', None):
            db_obj = ss.active_profile
        else:
            # Fallback heuristic: most content, then latest updated
            profiles = list(Profile.objects.all())
            if profiles:
                def score(p):
                    try:
                        return (
                            (getattr(p, 'experience_items').count() if hasattr(p, 'experience_items') else 0)
                            + (getattr(p, 'education_items').count() if hasattr(p, 'education_items') else 0)
                            + (getattr(p, 'certification_items').count() if hasattr(p, 'certification_items') else 0)
                            + (getattr(p, 'award_items').count() if hasattr(p, 'award_items') else 0),
                            p.updated_at
                        )
                    except Exception:
                        return (0, getattr(p, 'updated_at', None))
                db_obj = sorted(profiles, key=score, reverse=True)[0]
    except Exception:
        db_obj = None
    if db_obj:
        # Build dict from model fields, preferring DB values when present
        db_data = {
            'name': db_obj.name,
            'title': db_obj.title,
            'intro': getattr(db_obj, 'intro', '') or '',
            'summary': db_obj.summary,
            'location': db_obj.location,
            'email': db_obj.email,
            'phone': db_obj.phone,
            'whatsapp': db_obj.whatsapp,
            'updated_at': db_obj.updated_at,
            'skills': db_obj.skills or [],
            'tools': db_obj.tools or [],
            'languages': db_obj.languages or [],
            'interests': db_obj.interests or [],
            'links': db_obj.links or {},
            'experience': db_obj.experience or [],
            'education': db_obj.education or [],
            'certifications': db_obj.certifications or [],
            'awards': db_obj.awards or [],
            # Avatar URL (if set)
            'avatar_url': (db_obj.avatar.url if db_obj.avatar else None),
        }
        # Merge settings fallback for any missing fields
        for k, v in (profile or {}).items():
            db_data.setdefault(k, v)
        profile = db_data

        # If related items exist, override arrays with relational data for better admin UX
        using_db_related = False
        exp_count = edu_count = cert_count = award_count = 0
        try:
            exp_qs = getattr(db_obj, 'experience_items').all()
            if exp_qs.exists():
                using_db_related = True
                exp_count = exp_qs.count()
                def fmt_period(e):
                    try:
                        sy = (getattr(e, 'start_year', '') or '').strip()
                        ey = (getattr(e, 'end_year', '') or '').strip()
                        cur = bool(getattr(e, 'is_current', False))
                        if sy or ey or cur:
                            left = sy
                            right = 'Present' if cur or not ey else ey
                            return f"{left} — {right}" if left or right else ''
                    except Exception:
                        pass
                    return e.period or ''

                def as_list(x):
                    if not x:
                        return []
                    if isinstance(x, (list, tuple)):
                        return list(x)
                    if isinstance(x, str):
                        return [i.strip() for i in x.split(',') if i.strip()]
                    return []

                # Compute a simple duration label per experience (years only)
                import datetime
                now_year = datetime.date.today().year
                def compute_duration_label(e):
                    try:
                        sy = (getattr(e, 'start_year', '') or '').strip()
                        ey = (getattr(e, 'end_year', '') or '').strip()
                        cur = bool(getattr(e, 'is_current', False))
                        if sy.isdigit() and len(sy) == 4:
                            start = int(sy)
                            end = now_year if (cur or not ey.isdigit()) else int(ey)
                            if end >= start:
                                years = end - start
                                if years <= 0:
                                    return '<1 yr'
                                return f"{years} yr" if years == 1 else f"{years} yrs"
                    except Exception:
                        pass
                    return ''

                profile['experience'] = [
                    {
                        'role': e.role,
                        'company': e.company,
                        'period': fmt_period(e),
                        'summary': e.summary,
                        'start_year': (getattr(e, 'start_year', '') or ''),
                        'end_year': (getattr(e, 'end_year', '') or ''),
                        'is_current': bool(getattr(e, 'is_current', False)),
                        'location': getattr(e, 'location', '') or '',
                        'employment_type': getattr(e, 'employment_type', '') or '',
                        'work_mode': getattr(e, 'work_mode', '') or '',
                        'technologies': as_list(getattr(e, 'technologies', [])),
                        'company_url': getattr(e, 'company_url', '') or '',
                        'logo_url': (e.logo.url if getattr(e, 'logo', None) else None),
                        'duration_label': compute_duration_label(e),
                    } for e in exp_qs
                ]
            edu_qs = getattr(db_obj, 'education_items').all()
            if edu_qs.exists():
                using_db_related = True
                edu_count = edu_qs.count()
                profile['education'] = [
                    {
                        'degree': ed.degree,
                        'field_of_study': getattr(ed, 'field_of_study', '') or '',
                        'institution': ed.institution,
                        'institution_url': getattr(ed, 'institution_url', '') or '',
                        'period': ed.period,
                        'study_mode': getattr(ed, 'study_mode', '') or '',
                        'location': ed.location,
                        'duration_years': getattr(ed, 'duration_years', None),
                        'gpa': ed.gpa,
                        'honors': ed.honors,
                        'summary': ed.summary,
                        'courses': (ed.courses or []),
                        'technologies': (ed.technologies or []),
                        'thesis_title': getattr(ed, 'thesis_title', '') or '',
                        'activities': (ed.activities or []),
                        'logo_url': (ed.logo.url if getattr(ed, 'logo', None) else None),
                    } for ed in edu_qs
                ]
            cert_qs = getattr(db_obj, 'certification_items').all()
            if cert_qs.exists():
                using_db_related = True
                cert_count = cert_qs.count()
                # Rich structured list for detailed rendering
                certs_full = []
                certs = []
                for c in cert_qs.order_by('order','id'):
                    item = {
                        'name': c.name,
                        'issuer': c.issuer,
                        'year': c.year,
                    }
                    certs_full.append(item)
                    parts = [c.name]
                    meta = ", ".join([p for p in [c.issuer, c.year] if p])
                    if meta:
                        parts.append(f"({meta})")
                    certs.append(" ".join(parts))
                profile['certifications_full'] = certs_full
                profile['certifications'] = certs
            award_qs = getattr(db_obj, 'award_items').all()
            if award_qs.exists():
                using_db_related = True
                award_count = award_qs.count()
                awards_full = []
                awards = []
                for a in award_qs.order_by('order','id'):
                    item = {
                        'name': a.name,
                        'issuer': a.issuer,
                        'year': a.year,
                    }
                    awards_full.append(item)
                    parts = [a.name]
                    meta = ", ".join([p for p in [a.issuer, a.year] if p])
                    if meta:
                        parts.append(f"({meta})")
                    awards.append(" ".join(parts))
                profile['awards_full'] = awards_full
                profile['awards'] = awards
        except Exception:
            pass
        # Debug info to help diagnose selection/rendering issues (only surfaced when DEBUG is true in template)
    # Internal diagnostics removed from template; keep data minimal
    # Normalize common list-like fields
    def as_list(value):
        if not value:
            return []
        if isinstance(value, (list, tuple)):
            return list(value)
        if isinstance(value, str):
            return [x.strip() for x in value.split(',') if x.strip()]
        return []

    profile.setdefault('name', 'Denis Lokwo')
    profile.setdefault('title', 'Full‑stack Developer — Django, React, TypeScript')
    # If no intro is set, leave it empty (we avoid copying summary here to prevent duplicate rendering)
    profile.setdefault('intro', profile.get('intro', ''))
    profile.setdefault('summary', "I'm a full‑stack developer passionate about building fast, accessible, and elegant web applications. I enjoy solving hard problems, mentoring, and delivering production‑ready systems.")
    profile.setdefault('location', 'L’Aquila, Abruzzi, Italy')
    profile.setdefault('email', 'denis.lokwo@example.com')
    profile.setdefault('phone', '+39 123 456 7890')
    profile.setdefault('whatsapp', '+39 123 456 7890')
    # Derived fields
    import re
    profile['whatsapp_link'] = re.sub(r'[^0-9]', '', str(profile.get('whatsapp') or ''))
    profile['skills'] = as_list(profile.get('skills') or ['Python','Django','DRF','PostgreSQL','JavaScript','TypeScript','React','Tailwind','Docker','CI/CD'])
    profile['tools'] = as_list(profile.get('tools') or ['Git','Pytest','Poetry','Celery','Redis'])
    profile['languages'] = as_list(profile.get('languages') or ['English','Italian'])
    profile['interests'] = as_list(profile.get('interests') or ['Open Source','AI','Developer Experience'])
    profile.setdefault('links', {
        'linkedin': 'https://linkedin.com/in/denislokwo',
        'github': 'https://github.com/Lokwo12',
    })
    # Structured sections
    profile.setdefault('experience', [
        {'role':'Senior Full‑stack Developer','company':'Company Name','period':'2023 — Present','summary':'Leading delivery of scalable web apps, improving performance and developer productivity, mentoring juniors, and collaborating cross‑functionally.'},
        {'role':'Software Engineer','company':'Company Name','period':'2021 — 2023','summary':'Built APIs, dashboards, and automation for data‑heavy workflows. Focused on testing, typing, and reliable deploys.'},
    ])
    profile.setdefault('education', [
        {
            'degree':'BSc, Computer Science',
            'institution':'University of Example',
            'period':'2017 — 2021',
            'location':'L’Aquila, Italy',
            'gpa':'3.7/4.0',
            'honors':'Magna Cum Laude',
            'summary':'Strong foundation in algorithms, data structures, databases, and HCI.',
            'courses':['Algorithms','Operating Systems','Computer Networks','Databases','Human‑Computer Interaction']
        },
    ])
    profile['certifications'] = as_list(profile.get('certifications'))
    profile['awards'] = as_list(profile.get('awards'))
    profile['achievements'] = as_list(profile.get('achievements'))

    # Aggregate courses across education into a single flat, de-duplicated list
    try:
        courses_all = []
        seen = set()
        for ed in (profile.get('education') or []):
            courses = ed.get('courses') if isinstance(ed, dict) else None
            # Normalize courses into list of strings
            items = []
            if courses:
                if isinstance(courses, (list, tuple)):
                    items = [str(x).strip() for x in courses if str(x).strip()]
                elif isinstance(courses, str):
                    items = [x.strip() for x in courses.split(',') if x.strip()]
            for c in items:
                if c not in seen:
                    courses_all.append(c)
                    seen.add(c)
        if courses_all:
            profile['courses_all'] = courses_all
    except Exception:
        pass

    # If admin-managed Skills/Tools exist via SkillItem, override
    try:
        SkillItem = apps.get_model('portfolio', 'SkillItem')
        skill_qs = SkillItem.objects.filter(profile=db_obj) if db_obj else SkillItem.objects.none()
        if skill_qs.exists():
            profile['skills'] = list(skill_qs.filter(category='skill').order_by('order','name').values_list('name', flat=True))
            profile['tools'] = list(skill_qs.filter(category='tool').order_by('order','name').values_list('name', flat=True))
    except Exception:
        pass

    # If AchievementItem exist, override achievements list
    try:
        AchievementItem = apps.get_model('portfolio', 'AchievementItem')
        ach_qs = AchievementItem.objects.filter(profile=db_obj).order_by('order','id') if db_obj else AchievementItem.objects.none()
        if ach_qs.exists():
            profile['achievements'] = [
                (f"{a.text} — {a.metric}" if a.metric else a.text)
                for a in ach_qs
            ]
    except Exception:
        pass

    # Compute total experience years (rough estimate: earliest start_year to current/end)
    try:
        import datetime
        years = []
        now_year = datetime.date.today().year
        for job in (profile.get('experience') or []):
            sy = str(job.get('start_year') or '').strip()
            ey = str(job.get('end_year') or '').strip()
            cur = bool(job.get('is_current'))
            if sy.isdigit() and len(sy) == 4:
                start = int(sy)
                end = (now_year if (cur or not ey.isdigit()) else int(ey))
                if end >= start:
                    years.append((start, end))
        if years:
            earliest = min(y[0] for y in years)
            latest = max(y[1] for y in years) or now_year
            total = max(0, latest - earliest)
            profile['experience_years_total'] = total
        else:
            profile['experience_years_total'] = None
    except Exception:
        profile['experience_years_total'] = None

    return {'PROFILE': profile}


def site_settings(request):
    """Expose global site settings from DB with sensible fallbacks.
    Provides SITE dict: brand_name, logo_url, og_image_url, hero texts, resume_url, contact and socials, GA ID and consent flag.
    """
    data = {}
    try:
        SiteSettings = apps.get_model('portfolio', 'SiteSettings')
        obj = SiteSettings.objects.first()
    except Exception:
        obj = None
    if obj:
        data = {
            'brand_name': obj.brand_name or None,
            'logo_url': (obj.logo.url if obj.logo else None),
            'logo_light_url': (obj.logo_light.url if obj.logo_light else None),
            'logo_dark_url': (obj.logo_dark.url if obj.logo_dark else None),
            'favicon_url': (obj.favicon.url if obj.favicon else None),
            'home_avatar_url': (obj.home_avatar.url if getattr(obj, 'home_avatar', None) else None),
            'og_image_url': (obj.default_og_image.url if obj.default_og_image else None),
            'hero_heading': obj.hero_heading or None,
            'hero_subheading': obj.hero_subheading or None,
            'home_eyebrow': obj.home_eyebrow or None,
            'home_roles': obj.home_roles or None,
            'resume_url': (obj.resume_file.url if obj.resume_file else None),
            'email': obj.email or None,
            'phone': obj.phone or None,
            'location': obj.location or None,
            'contact_title': getattr(obj, 'contact_title', None) or None,
            'contact_subtitle': getattr(obj, 'contact_subtitle', None) or None,
            'github_url': obj.github_url or None,
            'linkedin_url': obj.linkedin_url or None,
            'twitter_url': obj.twitter_url or None,
            'youtube_url': obj.youtube_url or None,
            'facebook_url': getattr(obj, 'facebook_url', None) or None,
            'instagram_url': getattr(obj, 'instagram_url', None) or None,
            'calendly_url': obj.calendly_url or None,
            'analytics_measurement_id': obj.analytics_measurement_id or getattr(settings, 'GA_MEASUREMENT_ID', None),
            'consent_required': obj.consent_required,
            'primary_color': getattr(obj, 'primary_color', None) or None,
    }
    else:
        data = {
            'brand_name': None,
            'logo_url': None,
            'logo_light_url': None,
            'logo_dark_url': None,
            'favicon_url': None,
            'home_avatar_url': None,
            'og_image_url': None,
            'hero_heading': None,
            'hero_subheading': None,
            'home_eyebrow': None,
            'home_roles': None,
            'resume_url': None,
            'email': None,
            'phone': None,
            'location': None,
            'contact_title': None,
            'contact_subtitle': None,
            'github_url': None,
            'linkedin_url': None,
            'twitter_url': None,
            'youtube_url': None,
            'facebook_url': None,
            'instagram_url': None,
            'calendly_url': None,
            'analytics_measurement_id': getattr(settings, 'GA_MEASUREMENT_ID', None),
            'consent_required': True,
            'primary_color': None,
        }
    return {'SITE': data}
