"""Seed the running TeemO backend with a randomized demo library.

Each run picks a random subset of well-known books from BOOK_POOL and assigns
each a random rating from a realistic distribution, then POSTs them to the live
API. This exercises the full pipeline (Solar genre classification + Google
Books cover lookup + Merge Sort / Hashing / Greedy) with fresh-looking data.

Run the backend first (``cd backend && python app.py``), then:

    python seed_demo.py                 # 20 random books, default localhost:5000
    python seed_demo.py 15              # 15 random books
    python seed_demo.py http://host:port 25
    python seed_demo.py --seed 42       # reproducible selection (fixed RNG seed)

Rating distribution (weighted random):
    1★ 2% · 2★ 8% · 3★ 20% · 4★ 30% · 5★ 40%

Notes
-----
- Each POST triggers a real Solar ``classify_genre`` call and a Google Books
  cover lookup, so seeding takes a little while.
- The backend stores books in memory; restarting it clears everything, so
  re-run this script after a restart.
- Duplicates are rejected by the backend (HTTP 409) and reported as skipped.
"""

import random
import sys

import requests

# Curated pool of recognizable titles across diverse genres. Every entry was
# verified to resolve a Google Books cover via fetch_cover_url, so any random
# subset shows 100% covers (titles that didn't resolve were dropped).
BOOK_POOL = [
    # 소설
    ("채식주의자", "한강"),
    ("소년이 온다", "한강"),
    ("노르웨이의 숲", "무라카미 하루키"),
    ("1Q84", "무라카미 하루키"),
    ("데미안", "헤르만 헤세"),
    ("어린 왕자", "생텍쥐페리"),
    ("위대한 개츠비", "F. 스콧 피츠제럴드"),
    ("호밀밭의 파수꾼", "J.D. 샐린저"),
    ("나미야 잡화점의 기적", "히가시노 게이고"),
    ("파친코", "이민진"),
    ("작은 아씨들", "루이자 메이 올컷"),
    ("오만과 편견", "제인 오스틴"),
    ("죄와 벌", "도스토옙스키"),
    ("안나 카레니나", "레프 톨스토이"),
    ("변신", "프란츠 카프카"),
    ("82년생 김지영", "조남주"),
    # SF
    ("1984", "조지 오웰"),
    ("듄", "프랭크 허버트"),
    ("멋진 신세계", "올더스 헉슬리"),
    ("우리가 빛의 속도로 갈 수 없다면", "김초엽"),
    ("삼체", "류츠신"),
    # 판타지
    ("해리 포터와 마법사의 돌", "J.K. 롤링"),
    ("반지의 제왕", "J.R.R. 톨킨"),
    ("호빗", "J.R.R. 톨킨"),
    ("나니아 연대기", "C.S. 루이스"),
    # 추리
    ("그리고 아무도 없었다", "애거사 크리스티"),
    ("오리엔트 특급 살인", "애거사 크리스티"),
    ("셜록 홈즈의 모험", "아서 코난 도일"),
    ("화차", "미야베 미유키"),
    # 인문
    ("사피엔스", "유발 하라리"),
    ("호모 데우스", "유발 하라리"),
    ("총, 균, 쇠", "재레드 다이아몬드"),
    ("정의란 무엇인가", "마이클 샌델"),
    ("군주론", "마키아벨리"),
    # 과학
    ("코스모스", "칼 세이건"),
    ("이기적 유전자", "리처드 도킨스"),
    ("침묵의 봄", "레이첼 카슨"),
    ("시간의 역사", "스티븐 호킹"),
    # 자기계발
    ("미움받을 용기", "기시미 이치로"),
    ("아주 작은 습관의 힘", "제임스 클리어"),
    # 역사
    ("로마인 이야기 1", "시오노 나나미"),
]

# Rating value → selection weight (%). Skews high, like real "books I rated".
_RATINGS = [1, 2, 3, 4, 5]
_WEIGHTS = [2, 8, 20, 30, 40]

DEFAULT_COUNT = 20


def _random_rating():
    """A rating in 1..5 drawn from the weighted distribution above."""
    return random.choices(_RATINGS, weights=_WEIGHTS, k=1)[0]


def _parse_args(argv):
    """Parse [base_url] [count] and optional --seed <n> (order-insensitive)."""
    base = "http://localhost:5000"
    count = DEFAULT_COUNT
    seed = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--seed" and i + 1 < len(argv):
            seed = int(argv[i + 1]); i += 2; continue
        if a.startswith("http"):
            base = a
        elif a.isdigit():
            count = int(a)
        i += 1
    return base, min(count, len(BOOK_POOL)), seed


def _out(line):
    """Print UTF-8 safely even on a cp949 Windows console."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def main():
    base, count, seed = _parse_args(sys.argv[1:])
    if seed is not None:
        random.seed(seed)
    endpoint = base.rstrip("/") + "/api/books"

    chosen = random.sample(BOOK_POOL, count)
    selection = [(t, a, _random_rating()) for t, a in chosen]

    _out(f"Seeding {count} random books (of {len(BOOK_POOL)}) → {endpoint}")
    _out("rating dist: 1★2% 2★8% 3★20% 4★30% 5★40%"
         + (f"  (seed={seed})" if seed is not None else "") + "\n")
    added = skipped = failed = with_cover = 0

    for title, author, rating in selection:
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
            stars = "★" * rating + "☆" * (5 - rating)
            _out(f"  ✓ {title} / {author}  {stars} [{genre}] {'📕표지' if has_cover else '⬜커버없음'}")
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
