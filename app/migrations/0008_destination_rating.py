# Generated by Django 5.0.3 on 2024-04-17 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_userprofile_prefered_destination_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]