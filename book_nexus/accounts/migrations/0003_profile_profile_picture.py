# Generated by Django 5.1.3 on 2024-11-16 18:52

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_profile_country_profile_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="profile_picture",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True, verbose_name="image"
            ),
        ),
    ]
