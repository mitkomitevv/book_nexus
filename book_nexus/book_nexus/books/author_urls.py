from django.urls import path
from .views import AuthorDetailView, AuthorCreateView

urlpatterns = [
    path('create/', AuthorCreateView.as_view(), name='author-create'),
    path('show/<int:pk>/', AuthorDetailView.as_view(), name='author-details'),
]
