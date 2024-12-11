from django.db.models import Avg, Count, Subquery, OuterRef
from book_nexus.books.models import Book, Rating


class BookQuerysetMixin:
    def get_queryset(self):
        queryset = Book.objects.annotate(
            average_rating=Avg("ratings__rating"), rating_count=Count("ratings__rating")
        )

        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(
                user=self.request.user, book=OuterRef("pk")
            )
            queryset = queryset.annotate(
                user_rating=Subquery(user_ratings.values("rating")[:1])
            )

        return queryset.order_by("-created_at")
