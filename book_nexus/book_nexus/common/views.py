from django.views.generic import ListView
from book_nexus.books.models import Book


class HomeView(ListView):
    model = Book
    context_object_name = 'posts'

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['common/home-with-profile.html']
        return ['common/home-no-profile.html']
