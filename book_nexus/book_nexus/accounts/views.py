from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from book_nexus.accounts.forms import CustomUserCreationForm, ProfileEditForm
from book_nexus.accounts.models import Profile, Follow
from book_nexus.reading_list.models import WantToRead, CurrentlyReading, Read, Favorites

UserModel = get_user_model()


class UserRegistrationView(CreateView):
    model = UserModel
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'


class UserDetailsView(LoginRequiredMixin, DetailView):
    model = UserModel
    template_name = 'accounts/profile-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        if user.profile.date_of_birth:
            today = date.today()
            birthday = user.profile.date_of_birth
            context['age'] = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        else:
            context['age'] = None

        print([context['age']])

        context['want_to_read_count'] = WantToRead.objects.filter(user=user).count()
        context['currently_reading_count'] = CurrentlyReading.objects.filter(user=user).count()
        context['read_count'] = Read.objects.filter(user=user).count()
        context['favorites_count'] = Favorites.objects.filter(user=user).count()

        context['favorites'] = Favorites.objects.filter(user=user).all()

        return context


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'accounts/profile-edit.html'
    success_url = reverse_lazy('profile_details')

    def test_func(self):
        profile = get_object_or_404(Profile, pk=self.kwargs['pk'])
        return (
                self.request.user == profile.user or
                self.request.user.is_superuser or
                self.request.user.groups.filter(name='Moderators').exists()
        )

    def get_success_url(self):
        return reverse_lazy(
            'profile_details',
            kwargs={
                'pk': self.object.pk,
            }
        )

@login_required
def follow_user(request, user_pk):
    followed_user = get_object_or_404(UserModel, pk=user_pk)
    if followed_user != request.user:
        Follow.objects.get_or_create(follower=request.user, followed_user=followed_user)
    return redirect('profile_details', pk=user_pk)


@login_required
def unfollow_user(request, user_pk):
    followed_user = get_object_or_404(UserModel, pk=user_pk)
    Follow.objects.filter(follower=request.user, followed_user=followed_user).delete()
    return redirect('profile_details', pk=user_pk)
