from django.contrib.auth.views import LogoutView
from django.urls import path, include
from book_nexus.accounts.forms import CustomAuthenticationForm
from book_nexus.accounts.views import UserRegistrationView, UserLoginView, UserDetailsView, UserEditView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<int:pk>/', include([
        path('details/', UserDetailsView.as_view(), name='profile_details'),
        path('edit/', UserEditView.as_view(), name='profile_edit'),

    ]))
]