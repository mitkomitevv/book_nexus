from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Subquery, OuterRef, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView
from book_nexus.books.forms import BookCreateForm, AuthorCreateForm
from book_nexus.books.models import Book, Rating, Author
from book_nexus.reading_list.mixins import UserReadingListMixin


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookCreateForm
    template_name = 'books/book-create.html'
    success_url = reverse_lazy('home')


class BookListView(UserReadingListMixin, ListView):
    model = Book
    template_name = 'books/all-books.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().annotate(average_rating=Avg('ratings__rating'), rating_count=Count('ratings__rating'))

        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(user=self.request.user, book=OuterRef('pk'))
            queryset = queryset.annotate(user_rating=Subquery(user_ratings.values('rating')[:1]))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BookDetailsView(UserReadingListMixin, DetailView):
    model = Book
    template_name = 'books/book-details.html'
    context_object_name = 'book'


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)

            # Extract rating from POST data
            rating_value = request.POST.get('rating')
            if rating_value:
                rating_value = float(rating_value)

                rating, created = Rating.objects.update_or_create(
                    user=request.user,
                    book=book,
                    defaults={'rating': rating_value}
            )

                return JsonResponse({'success': True, 'message': 'Rating submitted successfully.'})

            return JsonResponse({'success': False, 'message': 'Invalid rating value.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    def delete(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)

            rating = Rating.objects.filter(user=request.user, book=book)
            if rating.exists():
                rating.delete()
                return JsonResponse({'success': True, 'message': 'Rating cleared successfully.'})
            return JsonResponse({'success': False, 'message': 'Rating not found.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorCreateForm
    template_name = 'authors/author-create.html'
    success_url = reverse_lazy('home')


class AuthorDetailView(ListView):
    model = Author
    template_name = 'authors/show-author.html'
    context_object_name = 'author'
