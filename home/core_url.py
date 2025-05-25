import os
from urllib.parse import quote_plus


def build_core_search_url(title: str, author: str = None, limit: int = 100, offset: int = 0) -> str:
    """
    Формирует URL для запроса к API CORE с поддержкой автора
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"
    # Экранируем параметры
    safe_title = quote_plus(title.replace('"', '\\"'))
    safe_author = quote_plus(author.replace('"', '\\"')) if author else None
    # Формируем запрос
    query = f'title:"{safe_title}"'
    if safe_author:
        query += f' AND authors:"{safe_author}"'
    return (
        f"{base_url}?q={query}"
        f"&limit={limit}"
        f"&offset={offset}"
        f"&apiKey={api_key}"
    )
