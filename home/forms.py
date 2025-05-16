import re

from django import forms


class SearchForm(forms.Form):
    QUALIFICATION_CHOICES = [
        ('', 'Выберите квалификацию'),
        ('aspirant', 'Аспирант'),
        ('candidate', 'Кандидат наук'),
        ('doctor', 'Доктор наук'),
        ('authority', 'Признанный авторитет'),
    ]

    search_request = forms.CharField(max_length=255, label='поиск статьи', required=True,
                                     widget=forms.TextInput(attrs={'placeholder': 'Введите данные поиска'}))
    keywords = forms.CharField(max_length=255, label='Ключевые слова', required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Введите ключевые слова'}))

    # Делаем аннотацию необязательной
    abstract = forms.CharField(required=False, label='Аннотация',
                               widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Введите аннотацию'}))

    # Делаем интервал времени с регулярным выражением
    dateRange = forms.CharField(
        max_length=20,
        label='Интервал времени',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Например: 2020-2023'})
    )

    # Добавляем валидацию для интервала времени
    def clean_dateRange(self):
        date_range = self.cleaned_data.get('dateRange', '').strip()  # Получение значения с обрезкой пробелов

        if date_range:
            # Если поле не пустое, проверяем формат
            if not re.match(r'^\d{4}-\d{4}$', date_range):
                raise forms.ValidationError("Введите интервал времени в формате ГГГГ-ГГГГ, например: 2020-2023.")

    authorQualification = forms.ChoiceField(choices=QUALIFICATION_CHOICES, label='Квалификация авторов',
                                            required=False)  # Сделаем необязательным
