import os
from urllib.parse import quote_plus, quote


def build_core_search_url(title: str, authors: list = None, limit: int = 100, offset: int = 0,
                          year_start: int = None, year_end: int = None) -> str:
    """
    Формирует URL для запроса к API CORE с точным названием статьи, авторами и диапазоном годов публикации.
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"
    safe_title = quote(title)
    query = f'title:"{safe_title}"'
    if authors:
        safe_authors = [quote(author) for author in authors]
        authors_query = ' AND '.join([f'authors:"{author}"' for author in safe_authors])
        query += f' AND ({authors_query})'
    if year_start and year_end:
        query += f' AND (yearPublished>={year_start} AND yearPublished<={year_end})'
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