from django.db import migrations, models
import uuid


def populate_more_keys(apps, schema_editor):
    Message = apps.get_model('portfolio', 'Message')
    Tag = apps.get_model('portfolio', 'Tag')
    ExperienceItem = apps.get_model('portfolio', 'ExperienceItem')
    EducationItem = apps.get_model('portfolio', 'EducationItem')
    CertificationItem = apps.get_model('portfolio', 'CertificationItem')
    AwardItem = apps.get_model('portfolio', 'AwardItem')
    AchievementItem = apps.get_model('portfolio', 'AchievementItem')
    SkillItem = apps.get_model('portfolio', 'SkillItem')
    SiteSettings = apps.get_model('portfolio', 'SiteSettings')
    for Model in (Message, Tag, ExperienceItem, EducationItem, CertificationItem, AwardItem, AchievementItem, SkillItem, SiteSettings):
        for obj in Model.objects.all():
            if not getattr(obj, 'key', None):
                obj.key = uuid.uuid4()
                obj.save(update_fields=['key'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0031_auto_add_keys'),
    ]

    operations = [
        # 1) Add nullable fields first
        migrations.AddField(
            model_name='message',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='tag',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='experienceitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='educationitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='certificationitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='awarditem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='achievementitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='skillitem',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='key',
            field=models.UUIDField(null=True, editable=False),
        ),
        # 2) Populate
        migrations.RunPython(populate_more_keys, migrations.RunPython.noop),
        # 3) Enforce default+unique
        migrations.AlterField(
            model_name='message',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='tag',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='experienceitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='educationitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='certificationitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='awarditem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='achievementitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='skillitem',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='key',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False),
        ),
    ]
