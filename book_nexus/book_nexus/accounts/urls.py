from django.urls import path
from book_nexus.accounts.views import UserRegistrationView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register')
]