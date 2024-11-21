from django.urls import path, include
from book_nexus.books.views import BookCreateView, BookListView, BookDetailsView, RateBookView

urlpatterns = [
    path('show-books/', BookListView.as_view(), name='show-all-books'),
    path('create/', BookCreateView.as_view(), name='create-book'),
    path('<int:pk>/', include([
        path('details/', BookDetailsView.as_view(), name='book-details'),
        path('add-rate/', RateBookView.as_view(), name='rate-book'),
    ])),
]