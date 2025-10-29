from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0006_message_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='slug',
            field=models.SlugField(max_length=220, unique=True, null=True, blank=True),
        ),
    ]
