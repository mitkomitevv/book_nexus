# Generated by Django 5.1.3 on 2024-11-23 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0012_alter_book_options_book_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="pages",
            field=models.PositiveIntegerField(default=400),
            preserve_default=False,
        ),
    ]
