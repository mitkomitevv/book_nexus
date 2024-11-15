from django.contrib.auth import get_user_model
from django.db import models

class Book(models.Model):
    title = models.CharField(
        max_length=50
    )

    genre = models.CharField(
        max_length=30
    )

    isbn = models.CharField(
        max_length=13,
        unique=True
    )

    summary = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title


class Author(models.Model):
    name = models.CharField(
        max_length=50
    )

    bio = models.TextField(
        blank=True
    )

    books = models.ManyToManyField(
        Book,
        related_name='authors'
    )

    def __str__(self):
        return self.name

UserModel = get_user_model()

class Review(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    content = models.TextField()
    rating = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
