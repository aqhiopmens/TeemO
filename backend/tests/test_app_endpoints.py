"""End-to-end tests for /api/books endpoints using Flask test_client.

Covers:
  - Duplicate prevention via normalized (title, author) keys
  - DELETE /api/books/<index> happy path + out-of-range + negative index
"""
import os
import sys
import unittest
from unittest.mock import patch

# Make `backend/` importable when tests run from project root or backend/.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app  # noqa: E402
from app import user_books  # noqa: E402


class BookEndpointsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        user_books.clear()
        # Block real Solar API calls — classify_genre always returns "Unknown".
        patcher = patch('app.classify_genre', return_value='Unknown')
        self.mock_classify = patcher.start()
        self.addCleanup(patcher.stop)
        # Block real Google Books calls — cover lookup always returns None.
        cover_patcher = patch('app.fetch_cover_url', return_value=None)
        self.mock_cover = cover_patcher.start()
        self.addCleanup(cover_patcher.stop)

    def _add(self, title, author, rating=4):
        return self.client.post(
            '/api/books',
            json={'title': title, 'author': author, 'rating': rating},
        )

    # ── Duplicate prevention ────────────────────────────────────
    def test_duplicate_identical_returns_409(self):
        self.assertEqual(self._add('해리포터', '롤링').status_code, 201)
        res = self._add('해리포터', '롤링')
        self.assertEqual(res.status_code, 409)
        body = res.get_json()
        self.assertIn('이미 등록된', body['error'])
        self.assertEqual(body['existing']['title'], '해리포터')

    def test_duplicate_whitespace_difference_returns_409(self):
        self.assertEqual(self._add('해리포터', '롤링').status_code, 201)
        self.assertEqual(self._add('해리 포터', '롤링').status_code, 409)

    def test_duplicate_case_difference_returns_409(self):
        self.assertEqual(self._add('Harry Potter', 'Rowling').status_code, 201)
        self.assertEqual(self._add('harry potter', 'Rowling').status_code, 409)

    def test_different_book_returns_201(self):
        self.assertEqual(self._add('해리포터', '롤링').status_code, 201)
        self.assertEqual(self._add('반지의 제왕', '톨킨').status_code, 201)
        self.assertEqual(len(user_books), 2)

    def test_same_title_different_author_returns_201(self):
        self.assertEqual(self._add('동명소설', '저자A').status_code, 201)
        self.assertEqual(self._add('동명소설', '저자B').status_code, 201)
        self.assertEqual(len(user_books), 2)

    # ── Delete ──────────────────────────────────────────────────
    def test_delete_existing_book_returns_200(self):
        self._add('지울책', '저자')
        self.assertEqual(len(user_books), 1)
        res = self.client.delete('/api/books/0')
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body['message'], 'deleted')
        self.assertEqual(body['book']['title'], '지울책')
        self.assertEqual(len(user_books), 0)

    def test_delete_out_of_range_returns_404(self):
        res = self.client.delete('/api/books/99')
        self.assertEqual(res.status_code, 404)

    def test_delete_negative_index_returns_404(self):
        # Flask's <int:index> converter rejects negatives at the routing layer,
        # so this 404s before reaching the handler — still 404, which is what we want.
        self._add('책', '저자')
        res = self.client.delete('/api/books/-1')
        self.assertEqual(res.status_code, 404)


if __name__ == '__main__':
    unittest.main()
