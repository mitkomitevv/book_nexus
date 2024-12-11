from django.contrib import admin
from django.contrib.auth.hashers import make_password
from book_nexus.accounts.models import Profile, Follow, CustomUser


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


@admin.register(CustomUser)
class UserModelAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ("email", "full_name", "is_active", "is_staff", "is_superuser", "date_joined")
    search_fields = ("email", "full_name")
    list_filter = ("is_active", "is_staff", "date_joined")
    ordering = ("-date_joined",)

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get("password"):
            obj.password = make_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed_user", "created_at")
    search_fields = ("follower__email", "followed_user__email")
    list_filter = ("created_at",)