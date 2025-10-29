from django.db import migrations
from django.utils.text import slugify


def gen_unique_slug(model, base, existing):
    slug = slugify(base) or 'project'
    original = slug
    idx = 2
    while slug in existing:
        slug = f"{original}-{idx}"
        idx += 1
    existing.add(slug)
    return slug


def forwards(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    existing = set(
        x for x in Project.objects.exclude(slug__isnull=True).exclude(slug='').values_list('slug', flat=True)
    )
    for p in Project.objects.all():
        if not p.slug:
            p.slug = gen_unique_slug(Project, p.title, existing)
            p.save(update_fields=['slug'])


def backwards(apps, schema_editor):
    # No-op: keep slugs
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0007_project_slug'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
