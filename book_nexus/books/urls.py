from django.urls import path, include
from book_nexus.books.views import (
    BookCreateView,
    BookListView,
    BookDetailsView,
    RateBookView,
    BookEditView,
    AddReviewView,
    EditReviewView,
    DeleteReviewView,
    AddCommentView,
    ReviewCommentsModalView,
    DeleteCommentView,
    EditCommentView,
    BookSearchView,
    SeriesDetailView,
    book_delete_view,
)

urlpatterns = [
    path("show-all-books/", BookListView.as_view(), name="show-all-books"),
    path("create/", BookCreateView.as_view(), name="create-book"),
    path(
        "<int:pk>/",
        include(
            [
                path("details/", BookDetailsView.as_view(), name="book-details"),
                path("add-rate/", RateBookView.as_view(), name="rate-book"),
                path("edit-book/", BookEditView.as_view(), name="book-edit"),
                path("delete-book/", book_delete_view, name="book-delete"),
                path("add-review/", AddReviewView.as_view(), name="add-review"),
            ]
        ),
    ),
    path("edit-review/<int:review_pk>/", EditReviewView.as_view(), name="edit-review"),
    path(
        "delete-review/<int:review_pk>/",
        DeleteReviewView.as_view(),
        name="delete-review",
    ),
    path("add-comment/<int:review_pk>/", AddCommentView.as_view(), name="add-comment"),
    path(
        "review-comments/<int:review_pk>/",
        ReviewCommentsModalView.as_view(),
        name="review-comments",
    ),
    path(
        "edit-comment/<int:comment_pk>/", EditCommentView.as_view(), name="edit-comment"
    ),
    path(
        "delete-comment/<int:comment_pk>/",
        DeleteCommentView.as_view(),
        name="delete-comment",
    ),
    path("search/", BookSearchView.as_view(), name="search-books"),
    path("series/<int:pk>/", SeriesDetailView.as_view(), name="series-detail"),
]
