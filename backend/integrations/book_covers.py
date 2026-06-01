"""Unified book-cover lookup.

Tries Kakao first (best coverage for Korean domestic books), then falls back
to Google Books (best for international titles / classics). Best-effort —
returns None if neither source yields a matching cover, so the add-book flow
is never blocked by cover lookup.
"""

from integrations import google_books, kakao_books


def fetch_cover_url(title: str, author: str):
    """Return a cover thumbnail URL for (title, author), or None.

    Kakao → Google Books fallback. Each source is best-effort (returns None on
    any failure), so this never raises.
    Time complexity: O(1) (a bounded number of HTTP round-trips).
    """
    return (
        kakao_books.fetch_cover_url(title, author)
        or google_books.fetch_cover_url(title, author)
    )
