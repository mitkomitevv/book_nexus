# Generated by Django 5.1.3 on 2024-11-23 20:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0013_book_pages"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="rating",
        ),
    ]
