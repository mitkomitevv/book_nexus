from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.messages import get_messages

from book_nexus.books.models import Book, Author, Review, Comment

UserModel = get_user_model()


class ViewsTestsWithCustomUser(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = UserModel.objects.create_user(
            email='user@example.com', password='userpass', full_name='Normal User'
        )

        # Create librarian
        self.librarian = UserModel.objects.create_user(
            email='lib@example.com', password='libpass', full_name='Librarian User'
        )
        librarians_group, _ = Group.objects.get_or_create(name='Librarians')
        librarians_group.user_set.add(self.librarian)

        self.moderator = UserModel.objects.create_user(
            email='mod@example.com', password='modpass', full_name='Moderator User'
        )
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')
        moderators_group.user_set.add(self.moderator)

        self.book = Book.objects.create(
            title='Test Book',
            genre='Fiction',
            pages=100,
            publication_date=timezone.now()
        )
        self.author = Author.objects.create(name='Test Author')
        self.book.authors.add(self.author)

        self.review = Review.objects.create(
            book=self.book,
            user=self.user,
            content='Great book!'
        )

    def test_book_create_requires_librarian(self):
        url = reverse('create-book')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        self.client.login(email='user@example.com', password='userpass')

        self.assertTemplateUsed('403.html')

        self.client.login(email='lib@example.com', password='libpass')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book-create.html')

    def test_book_edit_as_librarian(self):
        self.client.login(email='lib@example.com', password='libpass')
        url = reverse('book-edit', kwargs={'pk': self.book.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book-edit.html')

    def test_book_delete_view_as_librarian(self):
        self.client.login(email='lib@example.com', password='libpass')
        url = reverse('book-delete', kwargs={'pk': self.book.pk})
        response = self.client.post(url)

        self.assertRedirects(response, reverse('show-all-books'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_book_list_view_pagination(self):
        for i in range(15):
            Book.objects.create(
                title=f'Book{i}',
                genre='Fiction',
                pages=200,
                publication_date=timezone.now()
            )

        url = reverse('show-all-books')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['books']), 10)  # default paginate_by=10

    def test_book_details_view_user_review(self):
        self.client.login(email='user@example.com', password='userpass')
        url = reverse('book-details', kwargs={'pk': self.book.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_review'], self.review)
        self.assertIsNone(response.context['review_form'])

    def test_add_review_view(self):
        self.client.login(email='user@example.com', password='userpass')
        url = reverse('add-review', kwargs={'pk': self.book.pk})
        response = self.client.post(url, {'content': 'Another review!'})

        self.assertRedirects(response, reverse('book-details', kwargs={'pk': self.book.pk}))

        messages_list = list(get_messages(response.wsgi_request))

        self.assertIn('Your review has been submitted.', str(messages_list[0]))
        self.assertTrue(Review.objects.filter(book=self.book, user=self.user, content='Another review!').exists())

    def test_edit_review_view_as_moderator(self):
        self.client.login(email='mod@example.com', password='modpass')
        url = reverse('edit-review', kwargs={'review_pk': self.review.pk})
        response = self.client.post(url, {'content': 'Updated content!'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        self.review.refresh_from_db()

        self.assertEqual(self.review.content, 'Updated content!')

    def test_delete_review_view_as_owner(self):
        self.client.login(email='user@example.com', password='userpass')
        url = reverse('delete-review', kwargs={'review_pk': self.review.pk})
        response = self.client.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Review.objects.filter(pk=self.review.pk).exists())

    def test_add_comment_view(self):
        self.client.login(email='user@example.com', password='userpass')
        url = reverse('add-comment', kwargs={'review_pk': self.review.pk})
        response = self.client.post(url, {'content': 'Nice comment!'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data['success'])
        self.assertTrue(Comment.objects.filter(review=self.review, user=self.user, content='Nice comment!').exists())

    def test_review_comments_modal_view(self):
        url = reverse('review-comments', kwargs={'review_pk': self.review.pk})
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn('comments-modal', data['html'])
