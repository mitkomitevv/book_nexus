# Generated by Django 5.1.3 on 2024-11-17 18:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0003_author_picture_book_cover"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="publication_date",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
