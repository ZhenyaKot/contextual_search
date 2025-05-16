# views.py
import requests
from django.shortcuts import render
from .forms import SearchForm

from pprint import pprint  # Для красивого вывода ошибок в консоль


def search_core(title, limit=100):
    api_key = "L6tE1T7OhQ80dzijFu9kqygBMfwPWAlI"
    url = f"https://api.core.ac.uk/v3/search/works?q=title:\"{title}\"&limit={limit}&apiKey={api_key}"

    try:
        print(f"\n=== Делаем запрос к API ===")
        print(f"URL: {url}")

        response = requests.get(url)
        print(f"Статус ответа: {response.status_code}")

        # Выводим полный ответ API в консоль для отладки
        print("\nПолный ответ API:")
        pprint(response.json())

        response.raise_for_status()  # Вызовет исключение для 4XX/5XX статусов

        data = response.json()

        articles = []
        for result in data.get('results', []):
            # Извлекаем год из даты (если дата есть)
            created_date = result.get('createdDate', '')
            year = created_date[:4] if created_date else ''

            article_data = {
                'title': result.get('title', 'Без названия'),
                'link': result.get('downloadUrl', ''),
                'authors': [author.get('name', '') for author in result.get('authors', [])],
                'year': year,
                'abstract': result.get('abstract', 'Аннотация не предоставлена'),
                'source': result.get('publisher', 'Неизвестен')
            }
            articles.append(article_data)

        print(f"\nУспешно получили {len(articles)} статей")
        return articles

    except Exception as e:
        # Выводим подробную информацию об ошибке в консоль
        print("\n=== ПРОИЗОШЛА ОШИБКА ===")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")

        if 'response' in locals():
            print(f"HTTP статус: {response.status_code}")
            try:
                print("Тело ответа:", response.text)
            except:
                pass

        # Возвращаем информацию об ошибке пользователю
        return {
            'error': True,
            'type': type(e).__name__,
            'message': str(e),
            'status_code': response.status_code if 'response' in locals() else None
        }


def search_view(request):
    form = SearchForm()
    results = []
    error = None

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_request = form.cleaned_data['search_request']
            print(f"\n=== Пользователь ищет: '{search_request}' ===")

            api_response = search_core(search_request)

            if isinstance(api_response, list):
                results = api_response
            else:
                error = api_response
                print(f"\nОшибка для пользователя: {error}")

    return render(request, 'home/home.html', {
        'form': form,
        'results': results,
        'error': error
    })