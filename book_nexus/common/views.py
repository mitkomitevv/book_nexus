from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery, Prefetch
from django.views.generic import ListView

from book_nexus.books.models import Review, Rating, Comment
from book_nexus.reading_list.mixins import UserReadingListMixin


class HomeView(UserReadingListMixin, ListView):
    model = Review
    context_object_name = "reviews"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            followed_user_ids = self.request.user.following.values_list(
                "followed_user_id", flat=True
            )

            user_rating_subquery = Rating.objects.filter(
                user=OuterRef("user"), book=OuterRef("book")
            ).values("rating")[:1]

            return (
                Review.objects.filter(user_id__in=followed_user_ids)
                .exclude(user=self.request.user)
                .select_related("book", "user", "user__profile")
                .annotate(user_rating=Subquery(user_rating_subquery))
                .prefetch_related(
                    Prefetch(
                        "comments",
                        queryset=Comment.objects.select_related("user").order_by(
                            "-created_at"
                        ),
                    )
                )
                .order_by("-created_at")
            )
        else:
            return Review.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            book_ids = [review.book_id for review in context["reviews"]]

            user_ratings = Rating.objects.filter(
                user=self.request.user, book_id__in=book_ids
            ).values("book_id", "rating")

            user_rating_map = {
                rating["book_id"]: rating["rating"] for rating in user_ratings
            }

            for review in context["reviews"]:
                review.book.user_rating = user_rating_map.get(review.book_id, None)
                comments = review.comments.all()
                paginator = Paginator(comments, 10)
                review.paginated_comments = paginator.page(1)

            return context

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ["common/home-with-profile.html"]
        return ["common/home-no-profile.html"]
