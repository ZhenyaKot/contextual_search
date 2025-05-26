import re
from django import forms
from django.core.validators import RegexValidator


class SearchForm(forms.Form):
    search_request = forms.CharField(
        max_length=255,
        label='Поиск статей',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите название статьи или тему',
            'class': 'form-control'
        }),
    )

    authors = forms.CharField(
        max_length=500,
        label='авторы',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите фамилии авторов через запятую',
            'class': 'form-control'
        }),
        validators=[
            RegexValidator(
                regex=r'^[а-яА-ЯёЁa-zA-Z\s,]+$',
                message='Используйте только буквы и запятые для разделения авторов'
            )
        ]
    )

    keywords = forms.CharField(
        max_length=255,
        label='Ключевые слова',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите ключевые слова через запятую',
            'class': 'form-control'
        }),
    )

    abstract = forms.CharField(
        required=False,
        label='Поиск по аннотации',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Введите фрагменты текста для поиска в аннотациях',
            'class': 'form-control'
        }),
    )

    year_start = forms.IntegerField(
        label='Год начала публикации',
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Начальный год',
            'class': 'form-control'
        }),
        min_value=1000,  # Минимальный год
        max_value=2025   # Максимальный год
    )

    year_end = forms.IntegerField(
        label='Год окончания публикации',
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Конечный год',
            'class': 'form-control'
        }),
        min_value=1000,  # Минимальный год
        max_value=2025   # Максимальный год
    )

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get('year_start')
        end_year = cleaned_data.get('year_end')

        if start_year and end_year:
            if start_year > end_year:
                self.add_error('year_start', 'Начальный год должен быть меньше или равен конечному году')
            if end_year > 2025:  # Текущий год + 1
                self.add_error('year_end', 'Год не может быть больше текущего')
        elif start_year and start_year > 2025:
            self.add_error('year_start', 'Год не может быть больше текущего')
        elif end_year and end_year > 2025:
            self.add_error('year_end', 'Год не может быть больше текущего')

        return cleaned_data

    def clean_authors(self):
        authors = self.cleaned_data.get('authors', '')
        if authors:
            # Удаляем лишние пробелы и пустые значения
            authors_list = [a.strip() for a in authors.split(',') if a.strip()]
            return ', '.join(authors_list)
        return authors