# Generated by Django 5.1.3 on 2024-11-25 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0016_alter_book_authors"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="seriesbook",
            unique_together={("series", "book"), ("series", "number")},
        ),
    ]
