"""Shared title/author matching for cover lookups (Google Books, Kakao).

Keeps cover lookups precise: a candidate volume is accepted only if the
search title is contained in the candidate title AND (when an author is
given) at least one author token overlaps in either direction. This rejects
same-keyword-but-different books and works *about* a book by another author,
while tolerating spelling/spacing/order differences across editions.
"""

import re


def norm(s: str) -> str:
    """Lowercase and strip whitespace/punctuation for loose comparison."""
    return re.sub(r"[\s\W_]+", "", (s or "").lower())


def tokens(s: str):
    """Name tokens (length >= 2) for cross-spelling overlap checks."""
    return [t for t in re.split(r"[\s,/.]+", (s or "").lower()) if len(t) >= 2]


def matches(cand_title: str, cand_authors, title: str, author: str) -> bool:
    """Whether a candidate (title, authors) plausibly is the requested book.

    cand_authors may be a list (Google/Kakao ``authors``) or a string.
    Time complexity: O(len(title) + len(authors)).
    """
    if norm(title) not in norm(cand_title):
        return False
    if not author:
        return True
    if isinstance(cand_authors, (list, tuple)):
        cand_authors = " ".join(cand_authors)
    cand_norm = norm(cand_authors)
    # Our token appears in candidate authors...
    if any(norm(t) in cand_norm for t in tokens(author)):
        return True
    # ...or a candidate token appears in our author string (handles spacing/
    # ordering differences across editions).
    author_norm = norm(author)
    return any(norm(t) in author_norm for t in tokens(cand_authors))
