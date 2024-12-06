from django.urls import path, include
from .views import AuthorDetailsView, AuthorCreateView, ShowAuthorBooksView

urlpatterns = [
    path('create/', AuthorCreateView.as_view(), name='author-create'),
    path('<int:pk>/', include([
        path('details/', AuthorDetailsView.as_view(), name='author-details'),
        path('show-books/', ShowAuthorBooksView.as_view(), name='author-show-books'),
    ])),
]
