import re
from django import forms
from django.core.validators import RegexValidator


class SearchForm(forms.Form):
    QUALIFICATION_CHOICES = [
        ('', 'Выберите квалификацию'),
        ('aspirant', 'Аспирант'),
        ('candidate', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
        ('authority', 'Признанный авторитет'),
    ]

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

    dateRange = forms.CharField(
        max_length=20,
        label='Годы публикации',
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Например: 2020-2023',
            'class': 'form-control'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{4}-\d{4}$|^$',
            )
        ]
    )

    authorQualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        label='Квалификация авторов',
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get('dateRange')

        if date_range:
            start_year, end_year = map(int, date_range.split('-'))
            if start_year > end_year:
                self.add_error('dateRange', 'Начальный год должен быть меньше конечного')
            if end_year > 2025:  # Текущий год + 1
                self.add_error('dateRange', 'Год не может быть больше текущего')

        return cleaned_data

    def clean_authors(self):
        authors = self.cleaned_data.get('authors', '')
        if authors:
            # Удаляем лишние пробелы и пустые значения
            authors_list = [a.strip() for a in authors.split(',') if a.strip()]
            return ', '.join(authors_list)
        return authors
