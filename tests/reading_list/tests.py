from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from book_nexus.books.models import Book
from book_nexus.reading_list.models import WantToRead, CurrentlyReading, Read, Favorites

UserModel = get_user_model()

class ReadingListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserModel.objects.create_user(
            email='user@example.com',
            password='pass123',
            full_name='Test User'
        )
        cls.book = Book.objects.create(
            title='Test Book',
            genre='Fiction',
            pages=100,
            publication_date=timezone.now()
        )

    def setUp(self):
        self.client = Client()

    def test_add_to_want_to_read_without_login(self):
        url = reverse('add-to-reading-list')
        response = self.client.post(url, {'book_id': self.book.pk, 'list_type': 'want_to_read'})

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertFalse(data['success'])
        self.assertIn('User not authenticated', data['message'])
        self.assertFalse(WantToRead.objects.filter(user=self.user, book=self.book).exists())

    def test_add_to_want_to_read_logged_in(self):
        self.client.login(email='user@example.com', password='pass123')
        url = reverse('add-to-reading-list')
        response = self.client.post(url, {'book_id': self.book.pk, 'list_type': 'want_to_read'})

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data['success'])
        self.assertIn('want_to_read', data['message'])
        self.assertTrue(WantToRead.objects.filter(user=self.user, book=self.book).exists())

    def test_add_to_favorites_also_adds_to_read(self):
        self.client.login(email='user@example.com', password='pass123')
        add_url = reverse('add-to-reading-list')
        self.client.post(add_url, {'book_id': self.book.pk, 'list_type': 'want_to_read'})

        self.assertTrue(WantToRead.objects.filter(user=self.user, book=self.book).exists())

        response = self.client.post(add_url, {'book_id': self.book.pk, 'list_type': 'favorites'})
        data = response.json()

        self.assertTrue(data['success'])
        self.assertIn('favorites', data['message'])

        self.assertTrue(Favorites.objects.filter(user=self.user, book=self.book).exists())
        self.assertTrue(Read.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(WantToRead.objects.filter(user=self.user, book=self.book).exists())

    def test_remove_from_all_lists(self):
        self.client.login(email='user@example.com', password='pass123')
        add_url = reverse('add-to-reading-list')
        self.client.post(add_url, {'book_id': self.book.pk, 'list_type': 'read'})

        self.assertTrue(Read.objects.filter(user=self.user, book=self.book).exists())

        remove_url = reverse('remove-from-reading-list')
        response = self.client.post(remove_url, {'book_id': self.book.pk})
        data = response.json()

        self.assertTrue(data['success'])
        self.assertIn('Book removed from all lists', data['message'])

        self.assertFalse(Read.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(WantToRead.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(CurrentlyReading.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(Favorites.objects.filter(user=self.user, book=self.book).exists())

    def test_add_with_invalid_list_type(self):
        self.client.login(email='user@example.com', password='pass123')
        url = reverse('add-to-reading-list')
        response = self.client.post(url, {'book_id': self.book.pk, 'list_type': 'invalid_type'})

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertFalse(data['success'])
        self.assertIn('Invalid list type', data['message'])

        self.assertFalse(WantToRead.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(CurrentlyReading.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(Read.objects.filter(user=self.user, book=self.book).exists())
        self.assertFalse(Favorites.objects.filter(user=self.user, book=self.book).exists())
