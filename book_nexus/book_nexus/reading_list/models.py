from django.contrib.auth import get_user_model
from django.db import models
from book_nexus.books.models import Book

UserModel = get_user_model()

class ReadingList(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    books = models.ManyToManyField(
        Book,
        related_name='reading_lists'
    )

    name = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )
