from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from .models import WantToRead, CurrentlyReading, Read, Favorites, Book


class AddToReadingListView(LoginRequiredMixin, View):
    VALID_LIST_TYPES = {
        'want_to_read': WantToRead,
        'currently_reading': CurrentlyReading,
        'read': Read,
        'favorites': Favorites
    }

    @transaction.atomic
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})

        book_id = request.POST.get('book_id')
        list_type = request.POST.get('list_type')

        if list_type not in self.VALID_LIST_TYPES:
            return JsonResponse({'success': False, 'message': 'Invalid list type.'})

        try:
            with transaction.atomic():
                book = get_object_or_404(Book, pk=book_id)

                lists_to_clear = [WantToRead, CurrentlyReading]
                if list_type != 'favorites':
                    lists_to_clear.extend([Read, Favorites])

                for model in lists_to_clear:
                    model.objects.filter(user=request.user, book=book).delete()

                if list_type == 'favorites':
                    Favorites.objects.get_or_create(user=request.user, book=book)
                    Read.objects.get_or_create(user=request.user, book=book)
                else:
                    self.VALID_LIST_TYPES[list_type].objects.get_or_create(user=request.user, book=book)

                return JsonResponse({
                    'success': True,
                    'message': f'Book added to {list_type} list.',
                    'book_id': book_id,
                    'list_type': list_type
                })

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


class RemoveFromReadingListView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated.'})

        book_id = request.POST.get('book_id')
        book = get_object_or_404(Book, pk=book_id)

        WantToRead.objects.filter(user=request.user, book=book).delete()
        CurrentlyReading.objects.filter(user=request.user, book=book).delete()
        Read.objects.filter(user=request.user, book=book).delete()
        Favorites.objects.filter(user=request.user, book=book).delete()

        return JsonResponse({'success': True, 'message': 'Book removed from all lists.'})
