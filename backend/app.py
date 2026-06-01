import threading

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from algorithms.merge_sort import merge_sort
from algorithms.hashing import BookHashTable
from algorithms.greedy import greedy_preference_score
from algorithms.kmp import kmp_search
from algorithms.levenshtein import levenshtein_distance
from llm.solar import get_recommendations, classify_genre
from integrations.book_covers import fetch_cover_url

load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory book store (keyed by session; single-user for now)
user_books = []

# Guards the duplicate-check-then-append so concurrent identical POSTs can't
# both slip through (the dev server is threaded and the cover/genre lookups
# between the check and the append open a race window).
_add_lock = threading.Lock()


def _normalize(s):
    """Normalize title/author for duplicate detection — case- and space-insensitive."""
    return (s or "").lower().replace(" ", "").strip()


def _find_duplicate(title, author):
    """Return the existing book matching (title, author) by normalized key, or None."""
    new_key = (_normalize(title), _normalize(author))
    for existing in user_books:
        if (_normalize(existing['title']), _normalize(existing['author'])) == new_key:
            return existing
    return None


@app.route('/api/books', methods=['GET'])
def get_books():
    # Tag each book with its original position in user_books (_idx) BEFORE
    # sorting, so the client can delete by storage index rather than by the
    # sorted display position (which would otherwise target the wrong book).
    indexed = [{**b, '_idx': i} for i, b in enumerate(user_books)]
    return jsonify(merge_sort(indexed, key='rating'))


@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json(force=True)
    title = (data.get('title') or '').strip()
    author = (data.get('author') or '').strip()
    rating = data.get('rating')

    if not title or not author:
        return jsonify({'error': '제목과 저자는 필수 입력 항목입니다'}), 400
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({'error': '평점은 1~5 사이의 정수여야 합니다'}), 400

    # Fast pre-check: reject obvious duplicates before the slow LLM/cover calls.
    dup = _find_duplicate(title, author)
    if dup is not None:
        return jsonify({'error': '이미 등록된 책입니다', 'existing': dup}), 409

    # Genre is no longer entered by the user — Solar classifies it automatically.
    genre = classify_genre(title, author)

    # Best-effort cover lookup via Google Books — None if not found / on error.
    cover_url = fetch_cover_url(title, author)

    book = {'title': title, 'author': author, 'genre': genre,
            'rating': rating, 'cover_url': cover_url}

    # Authoritative check + append under a lock: the slow calls above open a
    # race window where two concurrent identical POSTs both pass the pre-check.
    # Re-checking here (atomically with the append) guarantees no duplicates.
    with _add_lock:
        dup = _find_duplicate(title, author)
        if dup is not None:
            return jsonify({'error': '이미 등록된 책입니다', 'existing': dup}), 409
        user_books.append(book)

    return jsonify({
        'message': '책이 추가되었습니다',
        'book': book,
        'genre_auto_classified': True,
    }), 201


@app.route('/api/books/<int:index>', methods=['DELETE'])
def delete_book(index):
    if index < 0 or index >= len(user_books):
        return jsonify({'error': 'book not found'}), 404
    deleted = user_books.pop(index)
    return jsonify({'message': 'deleted', 'book': deleted}), 200


FUZZY_DISTANCE_THRESHOLD = 3


@app.route('/api/search', methods=['GET'])
def search_books():
    query = (request.args.get('q') or '').strip().lower()

    # Stage 1: exact substring match via KMP — on title OR author.
    exact = [
        b for b in user_books
        if kmp_search(b['title'].lower(), query) != -1
        or kmp_search(b['author'].lower(), query) != -1
    ]
    if exact:
        return jsonify({'results': exact, 'matched_by': 'exact', 'did_you_mean': None})

    # Stage 2: fuzzy fallback — Levenshtein distance against each book's title
    # AND author; keep the smaller distance per book, within threshold, closest
    # first. `did_you_mean` is the closest-matching field (title or author).
    scored = []
    for b in user_books:
        dt = levenshtein_distance(query, b['title'].lower())
        da = levenshtein_distance(query, b['author'].lower())
        best_str = b['title'] if dt <= da else b['author']
        scored.append((min(dt, da), best_str, b))
    near = sorted(
        (item for item in scored if item[0] <= FUZZY_DISTANCE_THRESHOLD),
        key=lambda item: item[0],
    )
    if near:
        return jsonify({
            'results': [b for _, _, b in near],
            'matched_by': 'fuzzy',
            'did_you_mean': near[0][1],
        })

    return jsonify({'results': [], 'matched_by': 'none', 'did_you_mean': None})


@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    if not user_books:
        return jsonify({'error': '아직 추가된 책이 없습니다'}), 400

    sorted_books = merge_sort(user_books.copy(), key='rating')

    hash_table = BookHashTable()
    for book in sorted_books:
        hash_table.insert(book['genre'], book)

    top_genres = hash_table.get_top_genres(3)
    preference_scores = greedy_preference_score(sorted_books)

    # "다시 추천 받기": already-shown titles to avoid. Repeated query params
    # (?exclude=A&exclude=B) so titles containing commas stay intact.
    exclude = request.args.getlist('exclude')

    recs = get_recommendations(sorted_books, top_genres, preference_scores, exclude=exclude)

    # Belt-and-suspenders: the LLM occasionally re-suggests an excluded title
    # despite the prompt, so filter them out server-side too (guarantees
    # "다시 추천 받기" never repeats a shown book; may yield <5 in rare cases).
    if isinstance(recs, list) and exclude:
        excluded = {t.strip() for t in exclude}
        recs = [r for r in recs if (r.get('title') or '').strip() not in excluded]

    return jsonify({'recommendations': recs, 'top_genres': top_genres})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
