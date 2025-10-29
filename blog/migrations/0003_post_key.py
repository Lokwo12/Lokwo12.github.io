from django.db import migrations, models
import uuid


def populate_post_keys(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for p in Post.objects.all():
        if not getattr(p, 'key', None):
            p.key = uuid.uuid4()
            p.save(update_fields=['key'])


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_post_category_tags_thumbnail'),
    ]

    operations = [
        # 1) Add nullable, non-unique field
        migrations.AddField(
            model_name='post',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        # 2) Populate values for existing rows
        migrations.RunPython(populate_post_keys, migrations.RunPython.noop),
        # 3) Enforce uniqueness and non-null going forward
        migrations.AlterField(
            model_name='post',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]