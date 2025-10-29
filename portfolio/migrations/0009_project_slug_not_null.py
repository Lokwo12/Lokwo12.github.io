from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0008_populate_project_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(max_length=220, unique=True),
        ),
    ]