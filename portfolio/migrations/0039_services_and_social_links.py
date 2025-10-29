from django.db import migrations, models
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0038_messageattachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='facebook_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='instagram_url',
            field=models.URLField(blank=True),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Optional emoji or CSS icon class, e.g. 🚀 or lucide-code', max_length=60)),
                ('price', models.CharField(blank=True, help_text='Optional price text, e.g. $499+ or Custom', max_length=60)),
                ('is_published', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Service',
                'verbose_name_plural': 'Services',
                'ordering': ['order', 'title'],
            },
        ),
    ]
