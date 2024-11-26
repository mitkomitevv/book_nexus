from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg, Subquery, OuterRef, Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from book_nexus.accounts.models import Profile
from book_nexus.books.forms import BookCreateForm, AuthorCreateForm, BookUpdateForm, ReviewForm
from book_nexus.books.models import Book, Rating, Author, Review, Comment
from book_nexus.reading_list.mixins import UserReadingListMixin


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookCreateForm
    template_name = 'books/book-create.html'
    success_url = reverse_lazy('home')


class BookEditView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookUpdateForm
    template_name = 'books/book-edit.html'
    success_url = reverse_lazy('show-all-books')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.object.publication_date:
            form.fields['publication_date'].initial = self.object.publication_date
        return form


def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, f'"{book.title}" has been deleted.')  # optional
    return redirect('book-list')


class BookListView(UserReadingListMixin, ListView):
    model = Book
    template_name = 'books/all-books.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            average_rating=Avg('ratings__rating'),
            rating_count=Count('ratings__rating')
        )

        if self.request.user.is_authenticated:
            user_ratings = Rating.objects.filter(user=self.request.user, book=OuterRef('pk'))
            queryset = queryset.annotate(user_rating=Subquery(user_ratings.values('rating')[:1]))

        return queryset.order_by('-created_at')


class BookDetailsView(UserReadingListMixin, DetailView):
    model = Book
    template_name = 'books/book-details.html'
    context_object_name = 'book'
    reviews_per_page = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()

        context['average_rating'] = book.ratings.aggregate(Avg('rating'))['rating__avg']
        context['rating_count'] = book.ratings.aggregate(Count('rating'))['rating__count']
        # TODO: Remove this if i dont have the time to fix the reading list button
        context['is_details_view'] = True

        reviews = Review.objects.filter(book=self.object).select_related('user').order_by('-created_at')

        page = self.request.GET.get('page', 1)
        paginator = Paginator(reviews, self.reviews_per_page)

        try:
            paginated_reviews = paginator.page(page)
        except PageNotAnInteger:
            paginated_reviews = paginator.page(1)
        except EmptyPage:
            paginated_reviews = paginator.page(paginator.num_pages)

        context['reviews'] = [
            {
                'review': review,
                'profile': Profile.objects.filter(user=review.user).first(),
                'rating': Rating.objects.filter(user=review.user, book=book).first(),
            }
            for review in paginated_reviews.object_list
        ]

        reviews_with_comments = []
        for review in context['reviews']:
            comments = review.review.comments.order_by('-created_at')[:5]
            reviews_with_comments.append({
                'review': review.review,
                'comments': comments,
            })

        context['reviews_with_comments'] = reviews_with_comments

        context['paginated_reviews'] = paginated_reviews

        user = self.request.user
        if user.is_authenticated:
            user_review = Review.objects.filter(book=self.object, user=user).first()
            context['user_review'] = user_review
            if not user_review:
                context['review_form'] = ReviewForm()
        else:
            context['user_review'] = None
            context['review_form'] = None

        # Get the user's rating if logged in
        if user.is_authenticated:
            user_rating = book.ratings.filter(user=user).first()
            context['user_rating'] = user_rating.rating if user_rating else None
        else:
            context['user_rating'] = None

        return context


class AddReviewView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('login')

        book = get_object_or_404(Book, pk=pk)
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Your review has been submitted.')
        else:
            messages.error(request, 'There was an error submitting your review.')

        return redirect('book-details', pk=pk)


class EditReviewView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        return (self.request.user == review.user
                or self.request.user.is_staff
                or self.request.user.is_superuser)

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


class DeleteReviewView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        review = get_object_or_404(Review, pk=self.kwargs['review_pk'])
        return (self.request.user == review.user
                or self.request.user.is_staff
                or self.request.user.is_superuser)

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
        Comment.objects.create(review=review, user=request.user, content=content)

        return JsonResponse({'success': True, 'message': 'Comment added successfully.'})


class LoadMoreCommentsView(View):
    def get(self, request, review_pk):
        page = int(request.GET.get('page', 1))
        review = get_object_or_404(Review, pk=review_pk)
        comments = review.comments.order_by('-created_at')
        paginator = Paginator(comments, 5)
        page_obj = paginator.get_page(page)

        comments_data = [
            {
                'user': comment.user.full_name,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%B %d, %Y')
            }
            for comment in page_obj
        ]

        return JsonResponse({'comments': comments_data, 'has_next': page_obj.has_next()})


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            book = get_object_or_404(Book, pk=pk)

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
