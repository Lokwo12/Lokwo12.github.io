from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0019_sitesettings_youtube_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='experienceitem',
            name='start_year',
            field=models.CharField(blank=True, help_text='Start year, e.g. 2021', max_length=4),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='end_year',
            field=models.CharField(blank=True, help_text='End year, e.g. 2024 (leave blank if current)', max_length=4),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='is_current',
            field=models.BooleanField(default=False, help_text='Mark if this role is ongoing'),
        ),
    ]
