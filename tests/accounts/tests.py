from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.contrib.auth.models import Group
from book_nexus.accounts.models import Profile, Follow
from book_nexus.books.models import Book
from django.utils import timezone
from django.urls import reverse

UserModel = get_user_model()


class AccountsViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserModel.objects.create_user(
            email='normal@example.com', password='pass123', full_name='Normal User'
        )

        cls.librarian = UserModel.objects.create_user(
            email='librarian@example.com', password='libpass', full_name='Librarian User', is_staff=True
        )
        librarians_group, _ = Group.objects.get_or_create(name='Librarians')
        librarians_group.user_set.add(cls.librarian)

        cls.moderator = UserModel.objects.create_user(
            email='moderator@example.com', password='modpass', full_name='Moderator User'
        )
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        moderators_group.user_set.add(cls.moderator)

        cls.book = Book.objects.create(
            title='Test Book',
            genre='Fiction',
            pages=100,
            publication_date=timezone.now()
        )

    def setUp(self):
        self.client = Client()

    def test_user_registration_view(self):
        url = reverse('register')
        response = self.client.post(url, {
            'full_name': 'New User',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))

        messages_list = list(response.wsgi_request._messages)

        self.assertIn('Your account has been created successfully.', str(messages_list[0]))
        self.assertTrue(UserModel.objects.filter(email='newuser@example.com').exists())

    def test_user_login_view(self):
        url = reverse('login')
        response = self.client.post(url, {
            'username': 'normal@example.com',
            'password': 'pass123'
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_user_details_view(self):
        profile = Profile.objects.get(user=self.user)
        profile.date_of_birth = date(1990, 1, 1)
        profile.save()

        self.client.login(email='normal@example.com', password='pass123')
        url = reverse('profile_details', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('age', response.context)
        self.assertIsNotNone(response.context['age'])

    def test_user_edit_view(self):
        UserModel.objects.create_user(
            email='another@example.com', password='pass123', full_name='Another User'
        )

        self.client.login(email='another@example.com', password='pass123')
        url = reverse('profile_edit', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertTemplateUsed(response, '403.html')

        self.client.login(email='normal@example.com', password='pass123')
        response = self.client.post(url, {'full_name': 'Updated Name', 'country': 'Newland'})

        self.assertRedirects(response, reverse('profile_details', kwargs={'pk': self.user.pk}))
        self.user.refresh_from_db()

        self.assertEqual(self.user.full_name, 'Updated Name')

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.country, 'Newland')

    def test_follow_unfollow_user(self):
        other_user = UserModel.objects.create_user(
            email='other@example.com', password='otherpass', full_name='Other User'
        )
        self.client.login(email='normal@example.com', password='pass123')
        follow_url = reverse('follow_user', kwargs={'user_pk': other_user.pk})
        unfollow_url = reverse('unfollow_user', kwargs={'user_pk': other_user.pk})

        response = self.client.post(follow_url)
        self.assertRedirects(response, reverse('profile_details', kwargs={'pk': other_user.pk}))
        self.assertTrue(Follow.objects.filter(follower=self.user, followed_user=other_user).exists())

        response = self.client.post(unfollow_url)
        self.assertRedirects(response, reverse('profile_details', kwargs={'pk': other_user.pk}))
        self.assertFalse(Follow.objects.filter(follower=self.user, followed_user=other_user).exists())
