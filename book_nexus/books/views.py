from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.db.models import Avg, Count, Prefetch, Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from book_nexus.books.decorators import librarian_required
from book_nexus.books.forms import BookCreateForm, AuthorCreateForm, BookUpdateForm, ReviewForm, AuthorUpdateForm
from book_nexus.books.mixins import BookQuerysetMixin
from book_nexus.books.models import Book, Rating, Author, Review, Comment, Series
from book_nexus.mixins import LibrariansPermission, ModeratorsPermission
from book_nexus.reading_list.mixins import UserReadingListMixin


class BookCreateView(LoginRequiredMixin, LibrariansPermission, CreateView):
    model = Book
    form_class = BookCreateForm
    template_name = 'books/book-create.html'
    success_url = reverse_lazy('home')


class BookEditView(LoginRequiredMixin, LibrariansPermission, UpdateView):
    model = Book
    form_class = BookUpdateForm
    template_name = 'books/book-edit.html'
    success_url = reverse_lazy('show-all-books')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.publication_date:
            form.fields['publication_date'].initial = self.object.publication_date

        return form


@librarian_required
def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect('show-all-books')


class BookListView(BookQuerysetMixin ,UserReadingListMixin, ListView):
    model = Book
    template_name = 'books/all-books.html'
    context_object_name = 'books'
    paginate_by = 10


class BookDetailsView(UserReadingListMixin, DetailView):
    model = Book
    template_name = 'books/book-details.html'
    context_object_name = 'book'
    reviews_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        # Combine average and count aggregation into a single query
        aggregate_data = book.ratings.aggregate(
            average_rating=Avg('rating'),
            rating_count=Count('rating')
        )

        context['average_rating'] = aggregate_data['average_rating']
        context['rating_count'] = aggregate_data['rating_count']
        context['review_count'] = book.reviews.count()

        # Prefetch related objects to reduce queries
        reviews_queryset = Review.objects.filter(book=book).select_related('user').prefetch_related(
            'user__profile',
            Prefetch('comments', queryset=Comment.objects.order_by('-created_at'))
        ).order_by('-created_at')

        page = self.request.GET.get('page', 1)
        paginator = Paginator(reviews_queryset, self.reviews_per_page)
        try:
            paginated_reviews = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            paginated_reviews = paginator.page(1)

        user_ids = [review.user_id for review in paginated_reviews.object_list]

        ratings = Rating.objects.filter(user_id__in=user_ids, book=book)
        ratings_dict = {rating.user_id: rating for rating in ratings}

        context['reviews_with_comments'] = []
        for review in paginated_reviews.object_list:
            comments = list(review.comments.all()[:5])
            comments.reverse()
            context['reviews_with_comments'].append({
                'review': review,
                'profile': getattr(review.user, 'profile', None),
                'rating': ratings_dict.get(review.user_id),
                'comments': comments,
                'total_comments_count': review.comments.count(),
            })

        context['paginated_reviews'] = paginated_reviews

        user = self.request.user
        if user.is_authenticated:
            user_review = Review.objects.filter(book=book, user=user).first()
            context['user_review'] = user_review
            context['review_form'] = None if user_review else ReviewForm()
            user_rating = Rating.objects.filter(book=book, user=user).first()
            context['user_rating'] = user_rating.rating if user_rating else None
        else:
            context['user_review'] = None
            context['review_form'] = None
            context['user_rating'] = None

        return context


class AddReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.book = get_object_or_404(Book, pk=self.kwargs['pk'])
        messages.success(self.request, 'Your review has been submitted.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error submitting your review.')
        return redirect('book-details', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('book-details', kwargs={'pk': self.kwargs['pk']})


class EditReviewView(LoginRequiredMixin, ModeratorsPermission, View):
    def test_func(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        return (
                super().test_func() or
                self.request.user == review.user
        )

    def post(self, request, review_pk):
        review = get_object_or_404(Review, pk=review_pk)

        if not self.test_func():
            return JsonResponse({'success': False, 'message': 'Permission denied.'})

        content = request.POST.get('content')
        if content:
            review.content = content
            review.save()
            return JsonResponse({'success': True, 'message': 'Review updated successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Content cannot be empty.'})


class DeleteReviewView(LoginRequiredMixin, ModeratorsPermission, View):
    def test_func(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        return (
                super().test_func() or
                self.request.user == review.user
        )

    def post(self, request, review_pk):
        review = get_object_or_404(Review, pk=review_pk)

        if not self.test_func():
            return JsonResponse({'success': False, 'message': 'Permission denied.'})

        review.delete()
        return JsonResponse({'success': True, 'message': 'Review deleted successfully.'})


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, review_pk):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})

        content = request.POST.get('content')
        if not content:
            return JsonResponse({'success': False, 'message': 'Comment content cannot be empty.'})

        review = get_object_or_404(Review, pk=review_pk)
        comment = Comment.objects.create(review=review, user=request.user, content=content)

        if hasattr(request.user, 'profile') and request.user.profile.profile_picture:
            user_profile_picture = request.user.profile.profile_picture.url
        else:
            user_profile_picture = None

        response_data = {
            'success': True,
            'message': 'Comment added successfully.',
            'comment_content': comment.content,
            'comment_created_at': timezone.localtime(comment.created_at).strftime('%B %d, %Y %H:%M'),
            'user_full_name': request.user.full_name,
            'user_profile_picture': user_profile_picture,
        }

        return JsonResponse(response_data)


class EditCommentView(LoginRequiredMixin, ModeratorsPermission, UpdateView):
    model = Comment
    fields = ['content']
    pk_url_kwarg = 'comment_pk'

    def test_func(self):
        comment = self.get_object()
        return (
                super().test_func() or
                self.request.user == comment.user
        )

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'content': self.object.content})
        else:
            return redirect('some-success-url')

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': context['form'].errors}, status=400)
        else:
            return super().render_to_response(context, **response_kwargs)


class DeleteCommentView(LoginRequiredMixin, ModeratorsPermission, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_pk'
    success_url = reverse_lazy('show-all-books')

    def test_func(self):
        comment = self.get_object()
        return (
                super().test_func() or
                self.request.user == comment.user

        )

    def post(self, request, *args, **kwargs):
        comment_pk = kwargs.get(self.pk_url_kwarg)
        comment = get_object_or_404(Comment, pk=comment_pk)
        comment.delete()
        return JsonResponse({'success': True})


class ReviewCommentsModalView(View):
    def get(self, request, review_pk):
        try:
            review = Review.objects.select_related('user', 'user__profile').get(pk=review_pk)
        except Review.DoesNotExist:
            raise Http404("No Review matches the given query.")

        comments = review.comments.select_related('user', 'user__profile').order_by('created_at')

        # Pagination
        page_number = request.GET.get('page', 1)
        paginator = Paginator(comments, 10)
        paginated_comments = paginator.get_page(page_number)

        rating = Rating.objects.filter(user=review.user, book=review.book).first()

        context = {
            'review': review,
            'rating': rating,
            'paginated_comments': paginated_comments,
            'user': request.user,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('reviews/modal_comments.html', context, request=request)
            return JsonResponse({'html': html})
        else:
            return render(request, 'reviews/modal_comments.html', context)


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)

            rating_value = request.POST.get('rating')
            if rating_value:
                rating_value = float(rating_value)

                _, _ = Rating.objects.update_or_create(
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


class AuthorCreateView(LoginRequiredMixin, LibrariansPermission, CreateView):
    model = Author
    form_class = AuthorCreateForm
    template_name = 'authors/author-create.html'
    success_url = reverse_lazy('home')


class AuthorDetailsView(DetailView):
    model = Author
    template_name = 'authors/author-details.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['series_list'] = self.object.series.prefetch_related('series_books__book')
        return context


class AuthorUpdateView(LoginRequiredMixin,LibrariansPermission, UpdateView):
    model = Author
    form_class = AuthorUpdateForm
    template_name = 'authors/author-edit.html'

    def get_success_url(self):
        return reverse_lazy('author-details', kwargs={'pk': self.object.pk})

class AuthorDeleteView(LoginRequiredMixin, LibrariansPermission, DeleteView):
    model = Author
    success_url = reverse_lazy('show-all-books')

    def delete(self, request, *args, **kwargs):
        if not self.test_func():
            messages.error(request, 'You do not have permission to delete this author.')
            return redirect('author-details', pk=self.kwargs['pk'])
        messages.success(request, 'Author deleted successfully.')
        return super().delete(request, *args, **kwargs)

class ShowAuthorBooksView(BookQuerysetMixin, UserReadingListMixin, ListView):
    model = Book
    template_name = 'authors/author-books.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('pk')
        return queryset.filter(authors__id=author_id).prefetch_related('authors')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('pk')

        author = get_object_or_404(Author, pk=author_id)
        context['author'] = author
        return context


class BookSearchView(BookQuerysetMixin, UserReadingListMixin, ListView):
    model = Book
    template_name = 'books/search.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q', '')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(authors__name__icontains=query) |
                Q(series_books__series__name__icontains=query)
            ).distinct()

        self.extra_context = {'query': query}
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'extra_context'):
            context.update(self.extra_context)
        return context


class SeriesDetailView(UserReadingListMixin, DetailView):
    model = Series
    template_name = 'books/series-details.html'
    context_object_name = 'series'
    paginate_by = 10

    def get_books_queryset(self):
        mixin = BookQuerysetMixin()
        mixin.request = self.request
        return (
            mixin.get_queryset()
            .filter(series_books__series=self.object)
            .order_by('series_books__number')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_books_queryset()

        paginator = Paginator(books, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['books'] = page_obj.object_list
        return context
