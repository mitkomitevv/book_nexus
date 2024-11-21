from django import forms

from book_nexus.books.models import Book, Author


class BookBaseForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'


class AuthorBaseForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'


class BookCreateForm(BookBaseForm):
    class Meta(BookBaseForm.Meta):

        widgets = {
            'summary': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'publication_date': forms.DateInput(attrs={'type': 'date'})
        }


class AuthorCreateForm(AuthorBaseForm):
    class Meta(AuthorBaseForm.Meta):
        pass