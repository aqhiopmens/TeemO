"""Google Books API integration — fetch a book cover thumbnail URL.

Best-effort enrichment: any failure (network, timeout, missing fields, no
results) resolves to ``None`` rather than raising, so the add-book flow never
breaks because the cover lookup failed.
"""

import os

import requests

_ENDPOINT = "https://www.googleapis.com/books/v1/volumes"
_TIMEOUT = 5


def _query_thumbnail(title: str, author: str, lang_restrict: bool):
    """Single Google Books lookup. Returns raw thumbnail URL or None.

    Raises requests exceptions to the caller — wrapped by fetch_cover_url.
    Time complexity: O(1) (one HTTP round-trip, fixed-size parse).
    """
    # Use a space (not a literal '+') between query terms: requests URL-encodes
    # the value, and a literal '+' becomes '%2B' which Google treats as a
    # literal plus character rather than the AND/space separator.
    params = {
        "q": f"intitle:{title} inauthor:{author}",
        "maxResults": 1,
    }
    if lang_restrict:
        params["langRestrict"] = "ko"

    # Optional API key: without it, anonymous calls share a low global quota
    # per IP (HTTP 429 once exhausted). With a free key, quota is per-project
    # (~1000/day). Read at call time so .env loaded by app.py is picked up.
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if api_key:
        params["key"] = api_key

    resp = requests.get(_ENDPOINT, params=params, timeout=_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items")
    if not items:
        return None
    image_links = items[0].get("volumeInfo", {}).get("imageLinks")
    if not image_links:
        return None
    return image_links.get("thumbnail")


def _normalize_url(url: str) -> str:
    """Force https and drop the &edge=curl page-curl effect parameter."""
    url = url.replace("http://", "https://")
    url = url.replace("&edge=curl", "").replace("?edge=curl", "")
    return url


def fetch_cover_url(title: str, author: str):
    """Return a cover thumbnail URL for (title, author), or None.

    Tries a Korean-restricted query first; if that yields no result, retries
    once without the language restriction. Never raises — any error → None.
    Time complexity: O(1) (at most two fixed HTTP round-trips).
    """
    try:
        thumb = _query_thumbnail(title, author, lang_restrict=True)
        if thumb is None:
            thumb = _query_thumbnail(title, author, lang_restrict=False)
        if thumb is None:
            return None
        return _normalize_url(thumb)
    except Exception:
        # Best-effort: swallow network/timeout/parse errors and any other issue.
        return None
