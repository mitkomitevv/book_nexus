from datetime import date
from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.db import models


UserModel = get_user_model()


class Book(models.Model):
    title = models.CharField(
        max_length=50
    )

    genre = models.CharField(
        max_length=30
    )


    summary = models.TextField(
        blank=True,
        null=True
    )

    publication_date = models.DateField(
        default=date.today
    )

    cover = CloudinaryField('image', blank=True, null=True)

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
        'Book',
        related_name='authors'
    )

    picture = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.name


class Rating(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    book = models.ForeignKey(
        'Book',
        related_name='ratings',
        on_delete=models.CASCADE
    )

    rating = models.FloatField()

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user} - {self.book}: {self.rating}"


class Series(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SeriesBook(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_books')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, related_name='series_books')
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('series', 'number')
        ordering = ['number']

    def __str__(self):
        return f"{self.series.name} - {self.number}: {self.book.title}"


class Review(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        'Book',
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
        'Review',
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
