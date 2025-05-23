import logging
import math
import os

import requests
from django.shortcuts import render, redirect
from dotenv import find_dotenv, load_dotenv

from .cached import get_cached_articles, set_articles_cache
from .forms import SearchForm

load_dotenv(find_dotenv())

logger = logging.getLogger('core_search')


def search_core(title, limit=100, offset=0):
    api_key = os.getenv('API_CORE')
    url = f"https://api.core.ac.uk/v3/search/works?q=title:\"{title}\"&limit={limit}&offset={offset}&apiKey={api_key}"

    try:
        logger.debug(f"API request started | URL: {url} | Title: '{title}'")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        logger.info(
            f"API response | Total: {data.get('totalHits')} | "
            f"Returned: {len(data.get('results', []))} | "
            f"Query: '{title}'"
        )

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

        logger.debug(f"Successfully processed {len(articles)} articles")
        return {
            'articles': articles,
            'total': data.get('totalHits', 0)
        }

    except requests.exceptions.RequestException as e:
        logger.error(
            f"API request failed | URL: {url} | "
            f"Error: {str(e)} | "
            f"Status: {getattr(e.response, 'status_code', 'NO_RESPONSE')}"
        )
        return {
            'error': True,
            'message': f"Ошибка API: {str(e)}"
        }
    except Exception as e:
        logger.exception(f"Unexpected error during API processing: {str(e)}")
        return {
            'error': True,
            'message': f"Неожиданная ошибка: {str(e)}"
        }


def search_view(request):
    form = SearchForm(request.POST or None)
    error = None
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', '1')

    try:
        page_number = int(page)
    except ValueError:
        page_number = 1
        logger.warning(f"Invalid page number received: {page} | Defaulting to 1")

    if request.method == 'POST' and form.is_valid():
        search_query = form.cleaned_data['search_request']
        logger.info(f"Search form submitted | Query: '{search_query}'")
        return redirect(f'/?q={search_query}&page=1')

    articles = []
    total_results = 0

    if search_query:
        cached_data = get_cached_articles(search_query, page_number)
        if cached_data:
            logger.debug(
                f"Cache hit | Query: '{search_query}' | "
                f"Page: {page_number} | "
                f"Results: {len(cached_data['articles'])}"
            )
            articles = cached_data['articles']
            total_results = cached_data['total']
        else:
            offset = (page_number - 1) * 10
            logger.info(
                f"New API search | Query: '{search_query}' | "
                f"Page: {page_number} | "
                f"Offset: {offset}"
            )

            api_response = search_core(search_query, limit=10, offset=offset)

            if not api_response.get('error'):
                articles = api_response['articles']
                total_results = api_response['total']
                logger.debug(
                    f"API results processed | "
                    f"Articles: {len(articles)} | "
                    f"Total: {total_results}"
                )

                set_articles_cache(search_query, page_number, {
                    'articles': articles,
                    'total': total_results
                })

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
        'error': error,
        'search_query': search_query,
        'has_previous': page_number > 1,
        'has_next': (page_number * 10) < total_results,
        'next_page': page_number + 1,
        'prev_page': page_number - 1,
        'total_pages': total_pages,
        'request': request,
    })
