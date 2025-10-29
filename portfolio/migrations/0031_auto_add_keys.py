from django.db import migrations, models
import uuid


def populate_portfolio_keys(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    Testimonial = apps.get_model('portfolio', 'Testimonial')
    Profile = apps.get_model('portfolio', 'Profile')
    GalleryItem = apps.get_model('portfolio', 'GalleryItem')
    for Model in (Project, Testimonial, Profile, GalleryItem):
        for obj in Model.objects.all():
            if not getattr(obj, 'key', None):
                obj.key = uuid.uuid4()
                obj.save(update_fields=['key'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0030_galleryitem_alt_text'),
    ]

    operations = [
        # 1) Add nullable non-unique fields
        migrations.AddField(
            model_name='project',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='galleryitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        # 2) Populate keys for existing rows
        migrations.RunPython(populate_portfolio_keys, migrations.RunPython.noop),
        # 3) Enforce uniqueness and default for new rows
        migrations.AlterField(
            model_name='project',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='galleryitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
