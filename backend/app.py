from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from algorithms.merge_sort import merge_sort
from algorithms.hashing import BookHashTable
from algorithms.greedy import greedy_preference_score
from algorithms.kmp import kmp_search
from llm.solar import get_recommendations

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
    genre = (data.get('genre') or '').strip()
    rating = data.get('rating')

    if not title or not author or not genre:
        return jsonify({'error': 'title, author, and genre are required'}), 400
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({'error': 'rating must be an integer between 1 and 5'}), 400

    book = {'title': title, 'author': author, 'genre': genre, 'rating': rating}
    user_books.append(book)
    return jsonify({'message': 'Book added', 'book': book}), 201


@app.route('/api/search', methods=['GET'])
def search_books():
    query = (request.args.get('q') or '').lower()
    results = [b for b in user_books if kmp_search(b['title'].lower(), query) != -1]
    return jsonify(results)


@app.route('/api/recommendations', methods=['GET'])
def recommendations():
    if not user_books:
        return jsonify({'error': 'No books added yet'}), 400

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
