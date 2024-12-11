from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from book_nexus.accounts.models import Follow
from book_nexus.books.models import Book, Review
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user = UserModel.objects.create_user(
            email="testuser@example.com", password="pass123", full_name="Test User"
        )

        cls.other_user = UserModel.objects.create_user(
            email="other@example.com", password="otherpass", full_name="Other User"
        )

        cls.book = Book.objects.create(
            title="Followed User Book",
            genre="Fiction",
            pages=100,
            publication_date=timezone.now(),
        )
        cls.review = Review.objects.create(
            user=cls.other_user,
            book=cls.book,
            content="Great book!",
        )

    def setUp(self):
        self.client = Client()

    def test_home_view_not_logged_in(self):
        url = reverse("home")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("reviews", [])), 0)
        self.assertTemplateUsed(response, "common/home-no-profile.html")

    def test_home_view_logged_in_following_user_with_reviews(self):
        self.client.login(email="testuser@example.com", password="pass123")
        Follow.objects.create(follower=self.user, followed_user=self.other_user)

        url = reverse("home")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        reviews = response.context["reviews"]
        self.assertEqual(len(reviews), 1)
        self.assertEqual(reviews[0], self.review)

        self.assertTemplateUsed(response, "common/home-with-profile.html")
