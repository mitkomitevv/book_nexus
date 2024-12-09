from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Avg, Count, Subquery, OuterRef
from book_nexus.books.models import Book, Rating


class BookQuerysetMixin:
    def get_queryset(self):
        queryset = Book.objects.annotate(
            average_rating=Avg('ratings__rating'),
            rating_count=Count('ratings__rating')
        )

        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(user=self.request.user, book=OuterRef('pk'))
            queryset = queryset.annotate(user_rating=Subquery(user_ratings.values('rating')[:1]))

        return queryset.order_by('-created_at')


class LibrariansPermission(UserPassesTestMixin):
    permission_denied_message = "You do not have permission to access this page."

    def test_func(self):
        return (
                self.request.user.is_superuser or
                self.request.user.groups.filter(name='Librarians').exists()
        )

class ModeratorsPermission(UserPassesTestMixin):
    permission_denied_message = "You do not have permission to access this page."

    def test_func(self):
        return (
                self.request.user.is_superuser or
                self.request.user.groups.filter(name='Moderators').exists()
        )