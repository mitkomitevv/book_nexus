from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import WantToRead, CurrentlyReading, Read, Favorites, Book


# class AddToReadingListView(LoginRequiredMixin, View):
#     def post(self, request):
#         book_id = request.POST.get('book_id')
#         list_type = request.POST.get('list_type')
#
#         book = get_object_or_404(Book, pk=book_id)
#
#         try:
#             if list_type == 'want_to_read':
#                 WantToRead.objects.get_or_create(user=request.user, book=book)
#             elif list_type == 'currently_reading':
#                 CurrentlyReading.objects.get_or_create(user=request.user, book=book)
#             elif list_type == 'read':
#                 Read.objects.get_or_create(user=request.user, book=book)
#             elif list_type == 'favorites':
#                 Favorites.objects.get_or_create(user=request.user, book=book)
#             else:
#                 return JsonResponse({'success': False, 'message': 'Invalid list type.'})
#             return JsonResponse({'success': True})
#         except Exception as e:
#             return JsonResponse({'success': False, 'message': str(e)})
#
#
# class RemoveFromReadingListView(View):
#     def post(self, request):
#         book_id = request.POST.get('book_id')
#         user = request.user
#
#         if not book_id:
#             return JsonResponse({'success': False, 'message': 'Invalid book ID'})
#
#         # Remove the book from all the user's reading lists
#         WantToRead.objects.filter(user=user, book_id=book_id).delete()
#         CurrentlyReading.objects.filter(user=user, book_id=book_id).delete()
#         Read.objects.filter(user=user, book_id=book_id).delete()
#         Favorites.objects.filter(user=user, book_id=book_id).delete()
#
#         return JsonResponse({'success': True, 'message': 'Book removed from all reading lists.'})


class AddToReadingListView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})

        book_id = request.POST.get('book_id')
        list_type = request.POST.get('list_type')
        book = get_object_or_404(Book, pk=book_id)

        try:
            WantToRead.objects.filter(user=request.user, book=book).delete()
            CurrentlyReading.objects.filter(user=request.user, book=book).delete()

            if list_type == 'want_to_read':
                WantToRead.objects.create(user=request.user, book=book)
            elif list_type == 'currently_reading':
                CurrentlyReading.objects.create(user=request.user, book=book)
            elif list_type == 'read':
                Read.objects.get_or_create(user=request.user, book=book)
            elif list_type == 'favorites':
                Favorites.objects.get_or_create(user=request.user, book=book)
                Read.objects.get_or_create(user=request.user, book=book)


            return JsonResponse({'success': True, 'message': f'Book added to {list_type} list.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

class RemoveFromReadingListView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})

        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, pk=book_id)

        # Remove the book from all user's lists
        WantToRead.objects.filter(user=request.user, book=book).delete()
        CurrentlyReading.objects.filter(user=request.user, book=book).delete()
        Read.objects.filter(user=request.user, book=book).delete()
        Favorites.objects.filter(user=request.user, book=book).delete()

        return JsonResponse({'success': True, 'message': 'Book removed from all lists.'})
