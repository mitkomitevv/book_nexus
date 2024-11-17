from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('book_nexus.common.urls')),
    path('user/', include('book_nexus.accounts.urls')),
    path('books/', include('book_nexus.books.urls')),
    path('reading-list/', include('book_nexus.reading_list.urls')),
    path('api/', include('book_nexus.api.urls')),
]
