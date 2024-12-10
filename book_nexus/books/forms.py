from django import forms
from django.db.models import Max
from django.db import transaction

from book_nexus.books.models import Book, Author, Series, SeriesBook, Review
from django_select2.forms import Select2MultipleWidget, Select2Widget



class BookBaseForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        required=False,
        widget=Select2MultipleWidget(attrs={'class': 'form-control django-select2'}),
        label="Select Existing Authors",
    )

    new_authors = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter new authors, separated by commas',
            'class': 'form-control',
        }),
        label="Add New Authors",
    )

    series = forms.ModelChoiceField(
        queryset=Series.objects.all(),
        required=False,
        widget=Select2Widget(attrs={'class': 'form-control django-select2'}),
        label="Select Existing Series",
    )

    new_series_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a new series name',
            'class': 'form-control',
        }),
        label="Add New Series",
    )

    series_number = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Book Number in Series",
    )

    class Meta:
        model = Book
        exclude = ['created_at']

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter Book Title'}),
            'genre': forms.TextInput(attrs={'placeholder': "Enter the Book's Genre"}),
            'summary': forms.Textarea(attrs={'placeholder': 'Book summary'}),
            'publication_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'cover': 'Cover Image',
        }

    def save(self, commit=True):

        with transaction.atomic():
            instance = super().save(commit=False)
            if commit:
                instance.save()

            existing_authors = self.cleaned_data.get('authors', [])
            new_authors_set = set(existing_authors)
            instance.authors.set(new_authors_set)

            new_authors = self.cleaned_data.get('new_authors', '')
            if new_authors:
                author_names = [name.strip() for name in new_authors.split(',') if name.strip()]
                for name in author_names:
                    author, created = Author.objects.get_or_create(name=name)
                    instance.authors.add(author)
                    new_authors_set.add(author)

            current_authors = set(instance.authors.all())

            series = self.cleaned_data.get('series')
            new_series_name = self.cleaned_data.get('new_series_name')
            series_number = self.cleaned_data.get('series_number')

            if new_series_name:
                series, created = Series.objects.get_or_create(name=new_series_name)
            elif series:
                pass
            else:
                SeriesBook.objects.filter(book=instance).delete()
                series = None

            if series is not None:
                if not series_number:
                    last_number = SeriesBook.objects.filter(series=series).aggregate(
                        max_number=Max('number')
                    )['max_number'] or 0
                    series_number = last_number + 1

                SeriesBook.objects.filter(series=series, book=instance).delete()
                SeriesBook.objects.create(series=series, book=instance, number=series_number)

                for author in current_authors:
                    series.authors.add(author)

                previous_authors = set(instance.authors.all())
                authors_to_remove = previous_authors - current_authors
                for author in authors_to_remove:
                    if not author.books.filter(series_books__series=series).exists():
                        series.authors.remove(author)

            return instance


class BookCreateForm(BookBaseForm):
    pass


class BookUpdateForm(BookBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo: make the form auto populate image, upload it only if it doesnt already exists and show preview
        if self.instance and self.instance.pk:
            series_books = self.instance.series_books.all()
            if series_books.exists():
                series_book = series_books.first()
                self.fields['series'].initial = series_book.series
                self.fields['series_number'].initial = series_book.number
                print(f"Form initialized with series '{series_book.series}' and number {series_book.number}")
            else:
                print("No series associated with this book.")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control','rows': 5, 'placeholder': 'Write your review here...'}),
        }
        labels = {
            'content': '',
        }


class AuthorBaseForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AuthorCreateForm(AuthorBaseForm):
        pass


class AuthorUpdateForm(AuthorBaseForm):
        pass
