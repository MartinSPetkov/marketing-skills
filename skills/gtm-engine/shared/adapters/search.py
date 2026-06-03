"""
Optional URL discovery adapter.

Default: returns the URLs the caller supplies manually. No external call, no key needed.
Optional: hook for a search API (SerpAPI, Brave Search, etc.) — set SEARCH_API_KEY.

Usage:
    from shared.adapters.search import discover_urls

    # Manual default — always works:
    urls = discover_urls(query="contract testing tools", manual_urls=["https://example.com"])

    # With a search API configured, manual_urls are merged with search results.
"""

import os


def discover_urls(
    query: str,
    manual_urls: list[str] | None = None,
    max_results: int = 5,
) -> list[str]:
    """
    Return a list of URLs relevant to query.

    Manual URLs are always included first. If a search API key is present,
    additional results are appended up to max_results.

    Args:
        query:       The search query for optional API lookup.
        manual_urls: URLs the user has explicitly provided. Returned first.
        max_results: Max additional URLs to add from a search API.
    """
    urls = list(manual_urls or [])

    api_results = _search_api(query, max_results=max_results)
    if api_results:
        for url in api_results:
            if url not in urls:
                urls.append(url)

    return urls


# ── Optional search API hook ──────────────────────────────────────────────────
# TODO: implement by setting SEARCH_API_KEY and choosing a provider.
# Suggested providers:
#   - SerpAPI (serpapi.com)       — set SEARCH_API_KEY + SEARCH_PROVIDER=serpapi
#   - Brave Search API            — set SEARCH_API_KEY + SEARCH_PROVIDER=brave
#   - Exa (exa.ai, semantic)     — set SEARCH_API_KEY + SEARCH_PROVIDER=exa
# The function returns [] when no key is set, so the tool degrades to manual URLs.

def _search_api(query: str, max_results: int = 5) -> list[str]:
    key = os.environ.get("SEARCH_API_KEY")
    provider = os.environ.get("SEARCH_PROVIDER", "").lower()

    if not key:
        return []

    if provider == "brave":
        return _brave_search(query, key, max_results)
    elif provider == "exa":
        return _exa_search(query, key, max_results)
    elif provider == "serpapi":
        return _serpapi_search(query, key, max_results)
    else:
        print(
            f"[search] SEARCH_API_KEY is set but SEARCH_PROVIDER is not recognised "
            f"(got '{provider}'). Set SEARCH_PROVIDER to 'brave', 'exa', or 'serpapi'. "
            f"Falling back to manual URLs."
        )
        return []


def _brave_search(query: str, key: str, max_results: int) -> list[str]:
    # TODO: implement Brave Search API (https://api.search.brave.com)
    print("[search] Brave Search adapter not yet implemented. Skipping.")
    return []


def _exa_search(query: str, key: str, max_results: int) -> list[str]:
    # TODO: `pip install exa-py` and implement Exa semantic search.
    print("[search] Exa adapter not yet implemented. Skipping.")
    return []


def _serpapi_search(query: str, key: str, max_results: int) -> list[str]:
    # TODO: `pip install google-search-results` and implement SerpAPI.
    # Never pass 'site:google.com' or LinkedIn queries to this adapter.
    print("[search] SerpAPI adapter not yet implemented. Skipping.")
    return []
