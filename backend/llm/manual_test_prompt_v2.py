"""Manual (real-API) check for Prompt v2 — NOT part of the unittest suite.

Exercises the full recommendation pipeline (Merge Sort → Hashing → Greedy →
Solar LLM) across the 4 standard input cases, plus a quick classify_genre
candidate-enforcement check. Requires a live UPSTAGE_API_KEY in .env.

Run from backend/:  python llm/manual_test_prompt_v2.py
"""
from dotenv import load_dotenv

from algorithms.merge_sort import merge_sort
from algorithms.hashing import BookHashTable
from algorithms.greedy import greedy_preference_score
from llm.solar import get_recommendations, classify_genre, GENRE_CANDIDATES

load_dotenv()

# 모델 응답에 마크다운 토큰이 섞였는지 검사 (평문 응답 강제 확인용).
MARKDOWN_TOKENS = ["**", "##", "`", "- "]


def build_recommendation(books):
    """app.py /api/recommendations 와 동일한 파이프라인."""
    sorted_books = merge_sort(books.copy(), key="rating")
    table = BookHashTable()
    for b in sorted_books:
        table.insert(b["genre"], b)
    top_genres = table.get_top_genres(3)
    scores = greedy_preference_score(sorted_books)
    return get_recommendations(sorted_books, top_genres, scores)


def b(title, author, genre, rating):
    return {"title": title, "author": author, "genre": genre, "rating": rating}


CASES = {
    "1) 책 1권만": [
        b("나미야 잡화점의 기적", "히가시노 게이고", "소설", 5),
    ],
    "2) 같은 장르 5권 (판타지)": [
        b("해리포터와 마법사의 돌", "J.K. 롤링", "판타지", 5),
        b("반지의 제왕", "J.R.R. 톨킨", "판타지", 4),
        b("나니아 연대기", "C.S. 루이스", "판타지", 4),
        b("어스시의 마법사", "어슐러 르 귄", "판타지", 3),
        b("미스트본", "브랜던 샌더슨", "판타지", 5),
    ],
    "3) 다양한 장르 5권": [
        b("코스모스", "칼 세이건", "과학", 5),
        b("총, 균, 쇠", "재레드 다이아몬드", "역사", 4),
        b("미움받을 용기", "기시미 이치로", "자기계발", 3),
        b("셜록 홈즈", "코난 도일", "추리", 5),
        b("듄", "프랭크 허버트", "SF", 4),
    ],
    "4) 별점 모두 5점": [
        b("데미안", "헤르만 헤세", "소설", 5),
        b("사피엔스", "유발 하라리", "인문", 5),
        b("1984", "조지 오웰", "소설", 5),
        b("코스모스", "칼 세이건", "과학", 5),
        b("호빗", "J.R.R. 톨킨", "판타지", 5),
    ],
}


def report_markdown(text):
    hits = [tok for tok in MARKDOWN_TOKENS if tok in text]
    return ("⚠️ 마크다운 토큰 발견: " + ", ".join(repr(t) for t in hits)) if hits \
        else "✅ 평문(마크다운 없음)"


def main():
    for name, books in CASES.items():
        print("\n" + "=" * 70)
        print(f"[{name}]  ({len(books)}권)")
        print("=" * 70)
        out = build_recommendation(books)
        print(out)
        print("-" * 70)
        print(report_markdown(out))

    # classify_genre 후보 강제 확인
    print("\n" + "=" * 70)
    print("[classify_genre 후보 강제 확인]")
    print("=" * 70)
    samples = [
        ("코스모스", "칼 세이건"),
        ("해리포터와 마법사의 돌", "J.K. 롤링"),
        ("총, 균, 쇠", "재레드 다이아몬드"),
        ("죽은 시인의 사회", "N.H. 클라인바움"),
    ]
    for title, author in samples:
        g = classify_genre(title, author)
        ok = "✅" if g in GENRE_CANDIDATES else "❌(후보 밖!)"
        print(f"  {title:<22} → {g}  {ok}")


if __name__ == "__main__":
    main()
