"""Kakao Book Search integration — fetch a book cover thumbnail URL.

Kakao's catalogue has far better coverage of Korean domestic books than Google
Books, so this is used as the primary cover source (see book_covers.py).
Best-effort: any failure (no key, network, timeout, no match) → None.

Requires KAKAO_REST_API_KEY in the environment (the app's REST API key from
https://developers.kakao.com). Without it, returns None (caller falls back).
"""

import os

import requests

from integrations._match import matches

_ENDPOINT = "https://dapi.kakao.com/v3/search/book"
_TIMEOUT = 5
_SIZE = 10


def fetch_cover_url(title: str, author: str):
    """Return a Kakao cover thumbnail URL for (title, author), or None.

    Searches by title (relevance-ranked) and returns the first result that has
    a thumbnail and whose title/author match. Never raises.
    Time complexity: O(1) (one HTTP round-trip, bounded result scan).
    """
    api_key = os.environ.get("KAKAO_REST_API_KEY")
    if not api_key:
        return None
    try:
        resp = requests.get(
            _ENDPOINT,
            headers={"Authorization": f"KakaoAK {api_key}"},
            params={"query": title, "target": "title", "size": _SIZE},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        for doc in resp.json().get("documents", []):
            thumb = doc.get("thumbnail")
            if thumb and matches(doc.get("title", ""), doc.get("authors", []), title, author):
                return thumb
        return None
    except Exception:
        # Best-effort: swallow network/timeout/parse errors and any other issue.
        return None
