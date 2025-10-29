from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0034_subscription_alter_galleryitem_key_alter_profile_key_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
