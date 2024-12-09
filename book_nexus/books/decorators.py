# your_app/decorators.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib import messages


def librarian_required(view_func):

    @login_required(login_url='login')  # Ensure 'login' URL is defined
    def wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_superuser or user.groups.filter(name='Librarians').exists():
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You do not have permission to access this page.")
            return render(request, '403.html')

    return wrapped_view
