from django.views.generic.base import ContextMixin
from .models import WantToRead, CurrentlyReading, Read, Favorites


class UserReadingListMixin(ContextMixin):
    def get_user_reading_list_status(self):
        if not self.request.user.is_authenticated:
            return {}

        user = self.request.user
        read_books = Read.objects.filter(user=user).values_list("book_id", flat=True)
        want_to_read_books = WantToRead.objects.filter(user=user).values_list(
            "book_id", flat=True
        )
        currently_reading_books = CurrentlyReading.objects.filter(
            user=user
        ).values_list("book_id", flat=True)
        favorites_books = Favorites.objects.filter(user=user).values_list(
            "book_id", flat=True
        )

        return {
            "read_books": read_books,
            "want_to_read_books": want_to_read_books,
            "currently_reading_books": currently_reading_books,
            "favorites_books": favorites_books,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_user_reading_list_status())
        return context
