from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0021_backfill_experience_years'),
    ]

    operations = [
        migrations.AddField(
            model_name='experienceitem',
            name='location',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='employment_type',
            field=models.CharField(blank=True, choices=[('full-time', 'Full‑time'), ('part-time', 'Part‑time'), ('contract', 'Contract'), ('freelance', 'Freelance'), ('internship', 'Internship'), ('temporary', 'Temporary')], max_length=20),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='work_mode',
            field=models.CharField(blank=True, choices=[('remote', 'Remote'), ('hybrid', 'Hybrid'), ('on-site', 'On‑site')], max_length=10),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='technologies',
            field=models.JSONField(blank=True, help_text='List of key technologies for this role', null=True),
        ),
    ]
