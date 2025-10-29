from django.db import migrations


def forwards(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    Tag = apps.get_model('portfolio', 'Tag')
    for project in Project.objects.all():
        techs = (project.technologies or '')
        names = [t.strip() for t in techs.split(',') if t.strip()]
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            project.tags.add(tag)


def backwards(apps, schema_editor):
    Project = apps.get_model('portfolio', 'Project')
    # Optional: keep technologies as comma-separated union of tags
    for project in Project.objects.all():
        names = list(project.tags.values_list('name', flat=True))
        project.technologies = ', '.join(names)
        project.save(update_fields=['technologies'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0004_tag_alter_project_technologies_project_tags'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
