import os
import requests
from urllib.parse import quote
from dotenv import find_dotenv, load_dotenv
import spacy
from collections import defaultdict

load_dotenv(find_dotenv())

# Load English model with word vectors
nlp = spacy.load("en_core_web_lg")


def build_core_search_url(title: str, author: str, fields: list = None,
                          limit: int = 50, offset: int = 0) -> str:
    """
    Optimized search URL with field restrictions (no year filters)
    """
    api_key = os.getenv('API_CORE')
    base_url = "https://api.core.ac.uk/v3/search/works"

    safe_title = quote(title.replace('"', '\\"'))
    safe_author = quote(author.replace('"', '\\"'))

    # Basic search query without year restrictions
    query = f'(title:"{safe_title}"^2 OR abstract:"{safe_title}"^1.5) AND authors:"{safe_author}"'

    params = {
        "q": query,
        "limit": limit,
        "offset": offset,
        "apiKey": api_key,
    }

    if fields:
        params["fields"] = ",".join(fields)

    return f"{base_url}?" + "&".join(f"{k}={v}" for k, v in params.items())


def fetch_relevant_articles(title: str, author: str, search_query: str,
                            batch_size: int = 50):
    """
    Fetch all relevant articles without early termination
    """
    relevant_articles = []
    seen_dois = set()
    offset = 0

    fields = ["title", "authors", "yearPublished", "publisher",
              "downloadUrl", "abstract", "doi"]

    while True:
        url = build_core_search_url(
            title=title,
            author=author,
            fields=fields,
            limit=batch_size,
            offset=offset
        )

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if not data.get('results'):
                break  # No more results

            new_articles = 0
            for article in data['results']:
                doi = article.get('doi')
                if doi and doi in seen_dois:
                    continue
                if doi:
                    seen_dois.add(doi)

                text_to_analyze = article.get('abstract', '')[:1000]
                if not text_to_analyze:
                    continue

                relevance = calculate_relevance(search_query, text_to_analyze)

                # Keep all articles regardless of relevance score
                article['relevance'] = relevance
                relevant_articles.append(article)
                new_articles += 1

            offset += batch_size

            # Stop if we didn't get any new articles in this batch
            if new_articles == 0:
                break

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            break

    return sorted(relevant_articles, key=lambda x: x['relevance'], reverse=True)


def calculate_relevance(query: str, text: str) -> float:
    """
    Calculate relevance score
    """
    query = " ".join(query.lower().split()[:20])
    text = " ".join(text.lower().split()[:500])

    doc1 = nlp(query)
    doc2 = nlp(text)
    return doc1.similarity(doc2)


def display_results(articles, search_query, max_display=None):
    """
    Display results (show all if max_display is None)
    """
    print(f"\nFound {len(articles)} articles for '{search_query}':")
    print("=" * 80)

    display_count = len(articles) if max_display is None else min(max_display, len(articles))

    for i, article in enumerate(articles[:display_count]):
        print(f"\n#{i + 1} | Relevance: {article['relevance']:.3f}")
        print(f"Title: {article.get('title', 'No title')}")
        print(f"Authors: {', '.join(a.get('name', '') for a in article.get('authors', []))}")
        print(f"Year: {article.get('yearPublished', 'Unknown')}")
        print(f"Source: {article.get('publisher', 'Unknown')}")
        if article.get('abstract'):
            print(f"Abstract: {article['abstract'][:200]}...")
        print(f"Link: {article.get('downloadUrl', 'Not available')}")
        print("-" * 60)


if __name__ == "__main__":
    # Parameters
    title = "Physics"
    author = "Wang"
    search_query = "quantum mechanics and material science applications"

    # Fetch and display all results
    articles = fetch_relevant_articles(
        title=title,
        author=author,
        search_query=search_query
    )

    # Display all found articles
    display_results(articles, search_query, max_display=None)