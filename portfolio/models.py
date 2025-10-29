from django.db import models
import uuid
from django.urls import reverse


class Message(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} <{self.email}> on {self.created_at:%Y-%m-%d}"


class MessageAttachment(models.Model):
    message = models.ForeignKey(Message, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='messages/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        try:
            return f"Attachment for {self.message_id}: {self.file.name}"
        except Exception:
            return self.file.name or 'Attachment'


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    description = models.TextField()
    technologies = models.CharField(max_length=200, help_text="Comma-separated list of technologies", blank=True)
    category = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    url = models.URLField(blank=True)
    # Admin-managed featured selection and ordering
    is_featured = models.BooleanField(default=False, help_text="Show on homepage featured section")
    featured_order = models.PositiveIntegerField(default=0, help_text="Lower = earlier in featured list")
    
    # New: normalized tags for stronger queries/admin
    # Keep the legacy 'technologies' field for backward compatibility and migration
    
    
    

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.title

    def tech_list(self):
        # Prefer normalized tags if available, else fallback to legacy comma-separated field
        if hasattr(self, 'tags') and self.tags.exists():
            return list(self.tags.values_list('name', flat=True))
        return [tech.strip() for tech in (self.technologies or '').split(',') if tech.strip()]

    def get_absolute_url(self):
        return reverse('portfolio:project_detail', args=[self.slug])


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    created_at = models.DateField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first on listings")

    class Meta:
        ordering = ['order', '-created_at', 'id']

    def __str__(self):
        return f"{self.name} ({self.role})"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# Add the ManyToMany at end to avoid circular reference in editors
Project.add_to_class('tags', models.ManyToManyField('Tag', related_name='projects', blank=True))


class Profile(models.Model):
    """Editable profile content for About page and global use."""
    name = models.CharField(max_length=150, default='Denis Lokwo')
    title = models.CharField(max_length=220, blank=True)
    intro = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='profile/', blank=True, null=True)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)

    # JSON content
    skills = models.JSONField(blank=True, null=True, help_text='List of skills')
    tools = models.JSONField(blank=True, null=True, help_text='List of tools/technologies')
    languages = models.JSONField(blank=True, null=True, help_text='List of languages')
    interests = models.JSONField(blank=True, null=True, help_text='List of interests')
    links = models.JSONField(blank=True, null=True, help_text='Dict of external links')
    experience = models.JSONField(blank=True, null=True, help_text='List of experience items')
    education = models.JSONField(blank=True, null=True, help_text='List of education items')
    certifications = models.JSONField(blank=True, null=True)
    awards = models.JSONField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Profile: {self.name}" 


class ExperienceItem(models.Model):
    profile = models.ForeignKey(Profile, related_name='experience_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    period = models.CharField(max_length=100, blank=True)
    # New structured period fields
    start_year = models.CharField(max_length=4, blank=True, help_text="Start year, e.g. 2021")
    end_year = models.CharField(max_length=4, blank=True, help_text="End year, e.g. 2024 (leave blank if current)")
    is_current = models.BooleanField(default=False, help_text="Mark if this role is ongoing")
    # Extra metadata
    location = models.CharField(max_length=150, blank=True)
    EMPLOYMENT_CHOICES = (
        ('full-time','Full‑time'),
        ('part-time','Part‑time'),
        ('contract','Contract'),
        ('freelance','Freelance'),
        ('internship','Internship'),
        ('temporary','Temporary'),
    )
    employment_type = models.CharField(max_length=20, blank=True, choices=EMPLOYMENT_CHOICES)
    WORK_MODE_CHOICES = (
        ('remote','Remote'),
        ('hybrid','Hybrid'),
        ('on-site','On‑site'),
    )
    work_mode = models.CharField(max_length=10, blank=True, choices=WORK_MODE_CHOICES)
    technologies = models.JSONField(blank=True, null=True, help_text='List of key technologies for this role')
    summary = models.TextField(blank=True)
    company_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='companies/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.role} @ {self.company}" if self.company else self.role


class EducationItem(models.Model):
    profile = models.ForeignKey(Profile, related_name='education_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200, blank=True, help_text="Major or specialization, e.g. Computer Science")
    institution = models.CharField(max_length=200, blank=True)
    institution_url = models.URLField(blank=True)
    period = models.CharField(max_length=100, blank=True)
    STUDY_MODE_CHOICES = (
        ('on-campus','On‑campus'),
        ('online','Online'),
        ('hybrid','Hybrid'),
    )
    study_mode = models.CharField(max_length=20, blank=True, choices=STUDY_MODE_CHOICES)
    location = models.CharField(max_length=150, blank=True)
    duration_years = models.PositiveSmallIntegerField(blank=True, null=True, help_text="Approximate program duration in years")
    gpa = models.CharField(max_length=50, blank=True)
    honors = models.CharField(max_length=120, blank=True)
    summary = models.TextField(blank=True)
    courses = models.JSONField(blank=True, null=True)
    technologies = models.JSONField(blank=True, null=True, help_text="Technologies/skills covered (list)")
    thesis_title = models.CharField(max_length=300, blank=True)
    activities = models.JSONField(blank=True, null=True, help_text="Clubs, leadership, notable activities (list)")
    logo = models.ImageField(upload_to='universities/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.degree} - {self.institution}" if self.institution else self.degree


class CertificationItem(models.Model):
    profile = models.ForeignKey(Profile, related_name='certification_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class AwardItem(models.Model):
    profile = models.ForeignKey(Profile, related_name='award_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class AchievementItem(models.Model):
    profile = models.ForeignKey(Profile, related_name='achievement_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    text = models.CharField(max_length=300)
    metric = models.CharField(max_length=120, blank=True, help_text="Optional quantified metric, e.g. +30% performance")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text


class SkillItem(models.Model):
    CATEGORY_CHOICES = (
        ('skill', 'Skill'),
        ('tool', 'Tool/Tech'),
    )
    profile = models.ForeignKey(Profile, related_name='skill_items', on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=80)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='skill')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']
        unique_together = ('profile', 'name', 'category')

    def __str__(self):
        return f"{self.name} ({self.category})"

# Extra: Achievements on profile (optional quantified highlights)
Profile.add_to_class('achievements', models.JSONField(blank=True, null=True, help_text='List of quantified achievements'))


class SiteSettings(models.Model):
    """Global site settings manageable via admin.
    Keep it to a single row; admin will restrict adding more.
    """
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    brand_name = models.CharField(max_length=120, blank=True, help_text="Header brand text; falls back to Profile.name")
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Default logo (used if variants not set)")
    logo_light = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Logo for light theme (optional)")
    logo_dark = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Logo for dark theme (optional)")
    primary_color = models.CharField(max_length=9, blank=True, help_text="Primary brand color (e.g. #111111 or #0F172A)")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Favicon (PNG/SVG) shown in browser tab")
    default_og_image = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Default OpenGraph/Twitter image")
    hero_heading = models.CharField(max_length=200, blank=True)
    hero_subheading = models.CharField(max_length=300, blank=True)
    home_eyebrow = models.CharField(max_length=120, blank=True, help_text="Short label above hero, e.g. role")
    home_roles = models.TextField(blank=True, help_text="Pipe-separated roles for home typing effect, e.g. React Developer|Django Developer|Open Source Contributor")
    resume_file = models.FileField(upload_to='resume/', blank=True, null=True)
    contact_title = models.CharField(max_length=200, blank=True, help_text="Contact page title heading")
    contact_subtitle = models.CharField(max_length=300, blank=True, help_text="Contact page subtitle/lead")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=150, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    calendly_url = models.URLField(blank=True)
    analytics_measurement_id = models.CharField(max_length=40, blank=True, help_text="Google Analytics 4 Measurement ID")
    consent_required = models.BooleanField(default=True)
    # Explicitly choose which Profile powers the site (avatar/name/etc.)
    active_profile = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='site_settings', help_text="Select the Profile to use for homepage avatar and global profile data.")
    # Optional override: homepage avatar image directly from Site Settings
    home_avatar = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Override homepage avatar; if set, used instead of Profile.avatar")
    # Testimonials section controls
    show_testimonials_home = models.BooleanField(default=True, help_text="Show the 'What clients say' section on the homepage")
    testimonials_home_limit = models.PositiveSmallIntegerField(default=6, help_text="Max number of testimonials to show on the homepage")

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


class Service(models.Model):
    """Services offered, editable via admin and displayed on Services page."""
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL slug; auto-generated from title if left blank")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, blank=True, help_text="Optional emoji or CSS icon class, e.g. 🚀 or lucide-code")
    price = models.CharField(max_length=60, blank=True, help_text="Optional price text, e.g. $499+ or Custom")
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if getattr(self, 'slug', None):
            return reverse('portfolio:service_detail', args=[self.slug])
        # Fallback to listing if slug not set yet
        return reverse('portfolio:services')

    def save(self, *args, **kwargs):
        # Auto-generate slug from title if missing
        if (not getattr(self, 'slug', None)) and getattr(self, 'title', None):
            from django.utils.text import slugify
            base = slugify(self.title)[:190] or None
            if base:
                slug = base
                i = 2
                # ensure uniqueness
                while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    suffix = f"-{i}"
                    slug = (base[: (190 - len(suffix))] + suffix)
                    i += 1
                self.slug = slug
        return super().save(*args, **kwargs)


class GalleryItem(models.Model):
    """Admin-managed gallery item for showcasing images not tied strictly to a single Project or Blog Post.
    Optionally link to a Project or Post; otherwise provide a standalone image (with optional caption and link).
    """
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)
    alt_text = models.CharField(max_length=255, blank=True, help_text="Accessible alternative text for screen readers.")
    caption = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True, help_text="Optional longer description shown in the lightbox.")
    # Optional relations
    project = models.ForeignKey('Project', blank=True, null=True, on_delete=models.SET_NULL, related_name='gallery_items')
    post = models.ForeignKey('blog.Post', blank=True, null=True, on_delete=models.SET_NULL, related_name='gallery_items')
    # Optional external link when not using relations above
    external_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Gallery Item'
        verbose_name_plural = 'Gallery Items'

    def __str__(self):
        return self.title

    def source_label(self):
        if self.project_id:
            return 'Project'
        if self.post_id:
            return 'Blog'
        return 'Custom'

    def link_url(self):
        if self.project_id and hasattr(self.project, 'get_absolute_url'):
            return self.project.get_absolute_url()
        if self.post_id and hasattr(self.post, 'get_absolute_url'):
            return self.post.get_absolute_url()
        return self.external_url or ''


class Subscription(models.Model):
    """Simple newsletter/update subscription list."""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({'active' if self.active else 'inactive'})"
