from django.db import migrations
import re


def forwards(apps, schema_editor):
    ExperienceItem = apps.get_model('portfolio', 'ExperienceItem')
    year_pat = re.compile(r"(?i)(\d{4}).*?(\d{4}|present|current|ongoing)?")

    for item in ExperienceItem.objects.all():
        # Only backfill when structured fields are empty
        if (item.start_year or item.end_year or item.is_current):
            continue
        text = (item.period or '').strip()
        if not text:
            continue
        m = year_pat.search(text)
        if not m:
            continue
        start = m.group(1)
        end = m.group(2) or ''
        cur = False
        if end:
            if end.lower() in ('present', 'current', 'ongoing'):
                cur = True
                end = ''
            elif not re.fullmatch(r"\d{4}", end):
                end = ''
        # Save only if we have something meaningful
        changed = False
        if start and not item.start_year:
            item.start_year = start
            changed = True
        if end and not item.end_year:
            item.end_year = end
            changed = True
        if cur and not item.is_current:
            item.is_current = True
            changed = True
        if changed:
            item.save(update_fields=['start_year','end_year','is_current'])


def backwards(apps, schema_editor):
    # Non-destructive; leave structured fields as-is on reverse
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0020_experienceitem_period_fields'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
