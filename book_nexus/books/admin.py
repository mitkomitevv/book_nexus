from django.contrib import admin
from .models import Book, Author, Rating, Series, SeriesBook, Review, Comment


class AuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "pages", "publication_date", "created_at")
    search_fields = ("title", "genre", "authors__name")
    list_filter = ("genre", "publication_date", "created_at")
    inlines = [AuthorInline]
    autocomplete_fields = ["authors"]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [AuthorInline]


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "rating")
    search_fields = ("user__email", "book__title")
    list_filter = ("rating",)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "authors__name")
    autocomplete_fields = ["authors"]


@admin.register(SeriesBook)
class SeriesBookAdmin(admin.ModelAdmin):
    list_display = ("series", "number", "book")
    search_fields = ("series__name", "book__title")
    list_filter = ("series",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "created_at", "updated_at")
    search_fields = ("user__email", "book__title", "content")
    list_filter = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("review", "user", "created_at", "updated_at")
    search_fields = ("user__email", "review__content", "content")
    list_filter = ("created_at", "updated_at")

