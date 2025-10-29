from django.db import migrations
from django.db.models import Q


OPTION4_TEXT = (
    "I’m Denis Lokwo, a full‑stack engineer who enjoys solving hard problems with simple, elegant solutions. "
    "Over the past years I’ve built APIs, dashboards, and data‑heavy interfaces using Django, React, and TypeScript—always with an eye for performance and accessibility. "
    "I care about maintainable code, clear documentation, and great UX. "
    "Whether I’m refining a query, designing a component system, or mentoring a teammate, my goal is the same: ship useful software that feels great to use."
)


def forwards(apps, schema_editor):
    Profile = apps.get_model('portfolio', 'Profile')
    # Prefill summary only where it's empty or null so admins keep control
    for p in Profile.objects.filter(Q(summary__isnull=True) | Q(summary__exact='')):
        p.summary = OPTION4_TEXT
        p.save(update_fields=['summary'])


def backwards(apps, schema_editor):
    Profile = apps.get_model('portfolio', 'Profile')
    # Only clear if it matches the exact text we set, to avoid nuking user edits
    for p in Profile.objects.filter(summary=OPTION4_TEXT):
        p.summary = ''
        p.save(update_fields=['summary'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0012_awarditem_certificationitem_educationitem_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
