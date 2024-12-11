from django.contrib import admin

from book_nexus.reading_list.models import CurrentlyReading, Read, Favorites, WantToRead


# Register your models here.
@admin.register(WantToRead)
class WantToReadAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "added_at")
    search_fields = ("user__email", "book__title")
    list_filter = ("added_at",)


@admin.register(CurrentlyReading)
class CurrentlyReadingAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "started_at")
    search_fields = ("user__email", "book__title")
    list_filter = ("started_at",)


@admin.register(Read)
class ReadAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "completed_at")
    search_fields = ("user__email", "book__title")
    list_filter = ("completed_at",)


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "added_at")
    search_fields = ("user__email", "book__title")
    list_filter = ("added_at",)
