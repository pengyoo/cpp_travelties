# Generated by Django 5.0.3 on 2024-04-17 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_comment_post_alter_post_user_favor'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='prefered_destination_type',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
