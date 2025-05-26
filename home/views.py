import logging
import math

import requests
from django.shortcuts import render, redirect
from dotenv import find_dotenv, load_dotenv

from .core_url import build_core_search_url
from .forms import SearchForm

load_dotenv(find_dotenv())

logger = logging.getLogger('core_search')


def process_articles(results, authors_filter=None):
    """
    Обрабатывает сырые результаты из API CORE и преобразует в нужный формат
    :param results: Список статей из API
    :param authors_filter: Список авторов для фильтрации
    :return: Список обработанных статей
    """
    processed = []
    for article in results:
        # Получаем всех авторов статьи
        authors = []
        other_names = []
        for author in article.get('authors', []):
            if author.get('name'):
                authors.append(author['name'])
            if author.get('otherNames'):
                other_names.extend(author['otherNames'])
        # Применяем фильтр по авторам, если он задан
        if authors_filter:
            authors_filter_lower = [author.lower() for author in authors_filter]
            has_author = False
            for author_filter in authors_filter_lower:
                if (any(author_filter in a.lower() for a in authors) or
                        any(author_filter in n.lower() for n in other_names)):
                    has_author = True
                    break
            if not has_author:
                continue  # Пропускаем статьи без нужного автора
        # Формируем данные статьи
        processed_article = {
            'title': article.get('title', 'Без названия'),
            'link': article.get('downloadUrl', ''),
            'authors': authors,
            'year': article.get('createdDate', '')[:4] if article.get('createdDate') else '',
            'abstract': article.get('abstract', 'Аннотация не предоставлена'),
            'source': article.get('publisher', 'Неизвестен')
        }
        processed.append(processed_article)
    return processed


def search_core(title, authors=None, limit=100, offset=0):
    """Основная логика обработки API-запроса"""
    url = build_core_search_url(title, authors, limit, offset)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return {
            'articles': process_articles(data.get('results', []), authors),  # Передаем authors как фильтр
            'total': data.get('totalHits', 0)
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed | Error: {str(e)}")
        return {'error': True, 'message': f"Ошибка API: {str(e)}"}
    except Exception as e:
        return {'error': True, 'message': f"Неожиданная ошибка: {str(e)}"}


def search_view(request):
    form = SearchForm(request.POST or None)
    error = None
    search_query = request.GET.get('q', '').strip()
    authors = request.GET.getlist('authors')
    page = request.GET.get('page', '1')
    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
        logger.warning(f"Invalid page number received: {page} | Defaulting to 1")
    articles = []
    total_results = 0
    if search_query:
        offset = (page_number - 1) * 10
        api_response = search_core(
            search_query,
            authors=authors,
            limit=10,
            offset=offset
        )
        if not api_response.get('error'):
            articles = api_response['articles']
            total_results = api_response['total']
            logger.debug(
                f"API results processed | "
                f"Articles: {len(articles)} | "
                f"Total: {total_results}"
            )
            if not articles and page_number > 1:
                logger.warning(
                    f"No articles found | "
                    f"Redirecting to page 1 | "
                    f"Original page: {page_number}"
                )
                return redirect(f'/?q={search_query}&page=1')
        else:
            error = api_response
            logger.error(f"API error: {error.get('message')}")
    total_pages = max(1, math.ceil(total_results / 10)) if total_results else 1
    logger.debug(
        f"Rendering template | "
        f"Query: '{search_query}' | "
        f"Articles: {len(articles)} | "
        f"Total results: {total_results}"
    )
    return render(request, 'home/home.html', {
        'form': form,
        'articles': articles,
        'current_page': page_number,
        'total_results': total_results,
        'authors': authors,
        'error': error,
        'search_query': search_query,
        'has_previous': page_number > 1,
        'has_next': (page_number * 10) < total_results,
        'next_page': page_number + 1,
        'prev_page': page_number - 1,
        'total_pages': total_pages,
        'request': request,
    })
