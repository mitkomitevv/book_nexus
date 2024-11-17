from django.contrib import admin
from django.contrib.auth import get_user_model
from book_nexus.accounts.models import Profile


UserModel = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)


