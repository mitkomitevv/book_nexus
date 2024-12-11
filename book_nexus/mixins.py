from django.contrib.auth.mixins import UserPassesTestMixin


class LibrariansPermission(UserPassesTestMixin):
    permission_denied_message = "You do not have permission to access this page."

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Librarians").exists()
        )


class ModeratorsPermission(UserPassesTestMixin):
    permission_denied_message = "You do not have permission to access this page."

    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.groups.filter(name="Moderators").exists()
        )
