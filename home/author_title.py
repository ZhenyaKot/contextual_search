import os
import requests
from urllib.parse import quote
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def build_core_search_url(title: str, author: str, year_start: int = None, year_end: int = None, limit: int = 100, offset: int = 0) -> str:
    """
    Формирует URL для запроса к API CORE с точным названием статьи, автором и диапазоном годов публикации.
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"

    # Экранируем параметры
    safe_title = quote(title.replace('"', '\\"'))
    safe_author = quote(author.replace('"', '\\"'))

    # Формируем запрос с использованием AND для точного названия и автора
    query = f'title:"{safe_title}" AND authors:"{safe_author}"'

    if year_start and year_end:
        query += f' AND yearPublished>={year_start} AND yearPublished<={year_end}'
    elif year_start:
        query += f' AND yearPublished>={year_start}'
    elif year_end:
        query += f' AND yearPublished<={year_end}'

    return (
        f"{base_url}?q={query}"
        f"&limit={limit}"
        f"&offset={offset}"
        f"&apiKey={api_key}"
    )


def fetch_articles(title: str, author: str, year_start: int = None, year_end: int = None):
    """
    Получает статьи из API CORE по точному названию, автору и диапазону годов публикации.
    """
    url = build_core_search_url(title=title, author=author, year_start=year_start, year_end=year_end)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


def extract_article_info(articles_data):
    """
    Извлекает title, authors, year, source, link из данных статей и выводит в консоль.
    """
    if articles_data and 'results' in articles_data:
        for article in articles_data['results']:
            title = article.get('title', 'Без названия')
            authors = [author.get('name', '') for author in article.get('authors', [])]
            year = article.get('yearPublished', '') or (article.get('createdDate', '')[:4] if article.get('createdDate') else '')
            source = article.get('publisher', 'Неизвестен')
            link = article.get('downloadUrl', '')

            print("------------------------------")
            print(f"Title: {title}")
            print(f"Authors: {', '.join(authors)}")
            print(f"Year: {year}")
            print(f"Source: {source}")
            print(f"Link: {link}")
            print("------------------------------")
    else:
        print("No articles found or invalid data format.")


if __name__ == "__main__":
    title = "математика"  # Точное название статьи
    author = "Головчанська"  # Точное имя автора
    year_start = None  # Начальный год диапазона
    year_end = None

    articles_data = fetch_articles(title, author, year_start, year_end)
    if articles_data:
        extract_article_info(articles_data)
    else:
        print("Failed to fetch articles.")