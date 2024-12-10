from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.forms import PasswordInput
from django.forms.widgets import EmailInput

from book_nexus.accounts.models import Profile

UserModel = get_user_model()

class CustomUserBaseForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ['full_name', 'email', 'password1', 'password2']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
                'autocomplete': 'email',
            }),
        }

        #TODO: Find out why these aren't working
        #
        #     'password1': forms.PasswordInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Enter your password',
        #         'autocomplete': 'new-password',
        #     }),
        #     'password2': forms.PasswordInput(attrs={
        #         'class': 'form-control',
        #         'placeholder': 'Re-enter your password',
        #         'autocomplete': 'new-password',
        #     }),
        # }

class CustomUserCreationForm(CustomUserBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['full_name'].label = 'Your Name'
        self.fields['email'].label = 'Email'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

        self.fields['password1'].widget = PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget = PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
        })

        for field_name, field in self.fields.items():
            field.help_text = ''


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Your email or password is incorrect. Please try again.",
        'inactive': "This account is inactive.",
    }

    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )

    def clean_username(self):
        email = self.cleaned_data.get('username')
        if email:
            return email.lower()
        return email

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data


class ProfileEditForm(forms.ModelForm):
    full_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Profile
        exclude = ('user',)
        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.date_of_birth:
            formatted_date = self.instance.date_of_birth.strftime('%Y-%m-%d')
            self.initial['date_of_birth'] = formatted_date

        if self.instance and hasattr(self.instance, 'user') and self.instance.user:
            self.fields['full_name'].initial = self.instance.user.full_name

    def save(self, commit=True):
        profile = super().save(commit=False)

        if profile.user:
            profile.user.full_name = self.cleaned_data['full_name']
            profile.user.save()

        if commit:
            profile.save()

        return profile