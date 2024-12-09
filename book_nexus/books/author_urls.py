from django.urls import path, include
from .views import AuthorDetailsView, AuthorCreateView, ShowAuthorBooksView, AuthorUpdateView, AuthorDeleteView

urlpatterns = [
    path('create/', AuthorCreateView.as_view(), name='author-create'),
    path('<int:pk>/', include([
        path('details/', AuthorDetailsView.as_view(), name='author-details'),
        path('show-books/', ShowAuthorBooksView.as_view(), name='author-show-books'),
        path('edit/', AuthorUpdateView.as_view(), name='author-edit'),
        path('delete/', AuthorDeleteView.as_view(), name='author-delete'),
    ])),
]
