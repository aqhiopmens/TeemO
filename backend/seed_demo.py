"""Seed the running TeemO backend with a demo library.

POSTs ~20 well-known books across diverse genres to the live API so the
recommendation pipeline (Solar genre classification + Google Books cover
lookup + Merge Sort / Hashing / Greedy) has realistic data for a demo.

Run the backend first (``cd backend && python app.py``), then:

    python seed_demo.py                 # default http://localhost:5000
    python seed_demo.py http://host:port

Notes
-----
- Each POST triggers a real Solar ``classify_genre`` call and a Google Books
  cover lookup, so seeding 20 books takes a little while.
- The backend stores books in memory; restarting it clears everything, so
  re-run this script after a restart.
- Duplicates are rejected by the backend (HTTP 409) and reported as skipped,
  so re-running is safe.
"""

import sys

import requests

# (title, author, rating) — diverse genres + a 3~5 rating spread so the stats
# dashboard and rating-sort look realistic. Genre is classified by Solar, not
# set here. Mostly well-known titles for high Google Books cover hit-rate.
DEMO_BOOKS = [
    ("1984", "조지 오웰", 5),
    ("사피엔스", "유발 하라리", 5),
    ("해리 포터와 마법사의 돌", "J.K. 롤링", 5),
    ("채식주의자", "한강", 4),
    ("코스모스", "칼 세이건", 5),
    ("셜록 홈즈의 모험", "아서 코난 도일", 4),
    ("어린 왕자", "생텍쥐페리", 5),
    ("데미안", "헤르만 헤세", 4),
    ("반지의 제왕", "J.R.R. 톨킨", 5),
    ("듄", "프랭크 허버트", 4),
    ("그리고 아무도 없었다", "애거사 크리스티", 5),
    ("미움받을 용기", "기시미 이치로", 4),
    ("총, 균, 쇠", "재레드 다이아몬드", 5),
    ("나미야 잡화점의 기적", "히가시노 게이고", 5),
    ("살인자의 기억법", "김영하", 4),
    ("정의란 무엇인가", "마이클 샌델", 4),
    ("노르웨이의 숲", "무라카미 하루키", 4),
    ("위대한 개츠비", "F. 스콧 피츠제럴드", 3),
    ("침묵의 봄", "레이첼 카슨", 4),
    ("호밀밭의 파수꾼", "J.D. 샐린저", 3),
]


def _out(line):
    """Print UTF-8 safely even on a cp949 Windows console."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    endpoint = base.rstrip("/") + "/api/books"

    _out(f"Seeding {len(DEMO_BOOKS)} books → {endpoint}\n")
    added = skipped = failed = with_cover = 0

    for title, author, rating in DEMO_BOOKS:
        try:
            resp = requests.post(
                endpoint,
                json={"title": title, "author": author, "rating": rating},
                timeout=60,
            )
        except requests.RequestException as e:
            failed += 1
            _out(f"  ✗ {title} — 요청 실패: {e}")
            continue

        if resp.status_code == 201:
            book = resp.json().get("book", {})
            genre = book.get("genre", "?")
            has_cover = bool(book.get("cover_url"))
            with_cover += 1 if has_cover else 0
            added += 1
            _out(f"  ✓ {title} / {author}  [{genre}] {'📕표지' if has_cover else '⬜커버없음'}")
        elif resp.status_code == 409:
            skipped += 1
            _out(f"  ↷ {title} — 이미 등록됨, 건너뜀")
        else:
            failed += 1
            msg = resp.json().get("error", resp.text) if resp.content else resp.status_code
            _out(f"  ✗ {title} — {resp.status_code}: {msg}")

    _out(f"\n완료: 추가 {added} · 건너뜀 {skipped} · 실패 {failed} · 표지있음 {with_cover}/{added}")


if __name__ == "__main__":
    main()
