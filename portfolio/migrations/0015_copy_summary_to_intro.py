from django.db import migrations


def forwards(apps, schema_editor):
    Profile = apps.get_model('portfolio', 'Profile')
    for p in Profile.objects.all():
        intro = getattr(p, 'intro', '') or ''
        if not intro and (p.summary or '').strip():
            p.intro = p.summary
            p.save(update_fields=['intro'])


def backwards(apps, schema_editor):
    # Non-destructive: don't clear intro on rollback
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0014_profile_intro'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
