from django.contrib.auth import get_user_model
from django.db import models
from book_nexus.books.models import Book

UserModel = get_user_model()


class WantToRead(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


class CurrentlyReading(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)


class Read(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)


class Favorites(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
