# Generated by Django 5.0.3 on 2024-03-12 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_destination_city_destination_continent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='summary',
            field=models.CharField(default='This is a summary', max_length=255),
            preserve_default=False,
        ),
    ]
