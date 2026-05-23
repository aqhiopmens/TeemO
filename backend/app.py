from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from algorithms.merge_sort import merge_sort
from algorithms.hashing import BookHashTable
from algorithms.greedy import greedy_preference_score
from algorithms.kmp import kmp_search
from llm.solar import get_recommendations, classify_genre

load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory book store (keyed by session; single-user for now)
user_books = []


@app.route('/api/books', methods=['GET'])
def get_books():
    return jsonify(merge_sort(user_books.copy(), key='rating'))


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

    # Genre is no longer entered by the user — Solar classifies it automatically.
    genre = classify_genre(title, author)

    book = {'title': title, 'author': author, 'genre': genre, 'rating': rating}
    user_books.append(book)
    return jsonify({
        'message': '책이 추가되었습니다',
        'book': book,
        'genre_auto_classified': True,
    }), 201


@app.route('/api/search', methods=['GET'])
def search_books():
    query = (request.args.get('q') or '').lower()
    results = [b for b in user_books if kmp_search(b['title'].lower(), query) != -1]
    return jsonify(results)


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

    recs = get_recommendations(sorted_books, top_genres, preference_scores)
    return jsonify({'recommendations': recs, 'top_genres': top_genres})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
