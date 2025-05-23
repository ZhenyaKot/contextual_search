import math
import requests
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import SearchForm
from pprint import pprint


def search_core(title, limit=100, offset=0):
    api_key = "L6tE1T7OhQ80dzijFu9kqygBMfwPWAlI"
    url = f"https://api.core.ac.uk/v3/search/works?q=title:\"{title}\"&limit={limit}&offset={offset}&apiKey={api_key}"

    try:
        print(f"\nMaking API request to: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        print(f"API response - total: {data.get('totalHits')}, returned: {len(data.get('results', []))}")

        articles = []
        for result in data.get('results', []):
            article_data = {
                'title': result.get('title') or 'Без названия',
                'link': result.get('downloadUrl') or '',
                'authors': [a.get('name', '') for a in result.get('authors', [])],
                'year': result.get('createdDate', '')[:4] if result.get('createdDate') else '',
                'abstract': result.get('abstract') or 'Аннотация не предоставлена',
                'source': result.get('publisher') or 'Неизвестен'
            }
            articles.append(article_data)

        return {
            'articles': articles,
            'total': data.get('totalHits', 0)
        }

    except Exception as e:
        print(f"API error: {str(e)}")
        return {
            'error': True,
            'message': f"Ошибка API: {str(e)}"
        }


def get_cached_articles(search_query, page_number):
    cache_key = f"articles_{search_query}_{page_number}"
    return cache.get(cache_key)


def set_articles_cache(search_query, page_number, data):
    cache_key = f"articles_{search_query}_{page_number}"
    cache.set(cache_key, data, timeout=300)  # 5 минут (300 секунд)


def search_view(request):
    form = SearchForm(request.POST or None)
    error = None
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', '1')

    try:
        page_number = int(page)
    except ValueError:
        page_number = 1

    if request.method == 'POST' and form.is_valid():
        search_query = form.cleaned_data['search_request']
        return redirect(f'/?q={search_query}&page=1')

    articles = []
    total_results = 0

    if search_query:
        # Проверяем кэш перед запросом к API
        cached_data = get_cached_articles(search_query, page_number)
        if cached_data:
            print(f"Using cached data for page {page_number}")
            articles = cached_data['articles']
            total_results = cached_data['total']
        else:
            offset = (page_number - 1) * 10
            print(f"\n=== API Request: Page {page_number} ===")
            print(f"Query: {search_query}")
            print(f"Offset: {offset}")

            api_response = search_core(search_query, limit=10, offset=offset)

            if not api_response.get('error'):
                articles = api_response['articles']
                total_results = api_response['total']
                print(f"Received {len(articles)} articles")

                # Сохраняем в кэш
                set_articles_cache(search_query, page_number, {
                    'articles': articles,
                    'total': total_results
                })

                if not articles and page_number > 1:
                    print("No articles, redirecting to page 1")
                    return redirect(f'/?q={search_query}&page=1')
            else:
                error = api_response
                print(f"API Error: {error.get('message')}")

    # Для отладки
    print(f"Articles to template: {len(articles)}")
    print(f"Total results: {total_results}")

    total_pages = max(1, math.ceil(total_results / 10)) if total_results else 1

    return render(request, 'home/home.html', {
        'form': form,
        'articles': articles,
        'current_page': page_number,
        'total_results': total_results,
        'error': error,
        'search_query': search_query,
        'has_previous': page_number > 1,
        'has_next': (page_number * 10) < total_results,
        'next_page': page_number + 1,
        'prev_page': page_number - 1,
        'total_pages': total_pages,
        'request': request,
    })