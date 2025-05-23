from django.core.cache import cache


def get_cached_articles(search_query, page_number):
    cache_key = f"articles_{search_query}_{page_number}"
    return cache.get(cache_key)


def set_articles_cache(search_query, page_number, data):
    cache_key = f"articles_{search_query}_{page_number}"
    cache.set(cache_key, data, timeout=300)  # 5 минут (300 секунд)
