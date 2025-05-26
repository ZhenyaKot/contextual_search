import os
from urllib.parse import quote_plus


def build_core_search_url(title: str, authors: list = None, limit: int = 100, offset: int = 0) -> str:
    """
    Формирует URL для запроса к API CORE с поддержкой нескольких авторов
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"
    # Экранируем параметры
    safe_title = quote_plus(title.replace('"', '\\"'))
    # Формируем запрос
    query = f'title:"{safe_title}"'
    if authors:
        safe_authors = [quote_plus(author.replace('"', '\\"')) for author in authors]
        authors_query = ' AND '.join([f'authors:"{author}"' for author in safe_authors])
        query += f' AND ({authors_query})'
    return (
        f"{base_url}?q={query}"
        f"&limit={limit}"
        f"&offset={offset}"
        f"&apiKey={api_key}"
    )