from django.views.generic import ListView
from book_nexus.books.models import Review


class HomeView(ListView):
    model = Review
    template_name = 'common/home-with-profile.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.is_authenticated:
            followed_user_ids = self.request.user.following.values_list('followed_user_id', flat=True)
            return Review.objects.filter(user_id__in=followed_user_ids).exclude(user=self.request.user).select_related('book', 'user', 'user__profile').order_by('-created_at')
        else:
            return Review.objects.none()

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['common/home-with-profile.html']
        return ['common/home-no-profile.html']
