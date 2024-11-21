from django.urls import path
from book_nexus.reading_list.views import AddToReadingListView, RemoveFromReadingListView

urlpatterns = [
    path('add-to-reading-list/', AddToReadingListView.as_view(), name='add-to-reading-list'),
    path('remove-from-reading-list/', RemoveFromReadingListView.as_view(), name='remove-from-reading-list'),
]