
import os
import requests
import json
from urllib.parse import quote
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


def build_core_search_url(title: str, author: str, limit: int = 100, offset: int = 0) -> str:
    """
    Формирует URL для запроса к API CORE с точным названием статьи и автором.
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"

    # Экранируем параметры
    safe_title = quote(title.replace('"', '\\"'))
    safe_author = quote(author.replace('"', '\\"'))

    # Формируем запрос с использованием AND для точного названия и автора
    query = f'title:"{safe_title}" AND authors:"{safe_author}"'

    return (
        f"{base_url}?q={query}"
        f"&limit={limit}"
        f"&offset={offset}"
        f"&apiKey={api_key}"
    )


def fetch_articles(title: str, author: str):
    """
    Получает статьи из API CORE по точному названию и автору.
    """
    url = build_core_search_url(title=title, author=author)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None


if __name__ == "__main__":
    title = "Physics"  # Точное название статьи
    author = "Wang"  # Точное имя автора
    articles_data = fetch_articles(title, author)

    if articles_data:
        print(json.dumps(articles_data, indent=4, ensure_ascii=False))
    else:
        print("Failed to fetch articles.")


