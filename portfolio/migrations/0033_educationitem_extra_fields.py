from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0032_more_auto_keys'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationitem',
            name='field_of_study',
            field=models.CharField(blank=True, help_text='Major or specialization, e.g. Computer Science', max_length=200),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='study_mode',
            field=models.CharField(blank=True, choices=[('on-campus', 'On‑campus'), ('online', 'Online'), ('hybrid', 'Hybrid')], max_length=20),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='duration_years',
            field=models.PositiveSmallIntegerField(blank=True, help_text='Approximate program duration in years', null=True),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='technologies',
            field=models.JSONField(blank=True, help_text='Technologies/skills covered (list)', null=True),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='thesis_title',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='activities',
            field=models.JSONField(blank=True, help_text='Clubs, leadership, notable activities (list)', null=True),
        ),
    ]
