import unittest
from unittest.mock import patch

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations import book_covers


class TestBookCoversFallback(unittest.TestCase):
    @patch('integrations.book_covers.google_books.fetch_cover_url')
    @patch('integrations.book_covers.kakao_books.fetch_cover_url')
    def test_kakao_hit_short_circuits_google(self, mock_kakao, mock_google):
        mock_kakao.return_value = 'https://kakao/cover.jpg'
        self.assertEqual(
            book_covers.fetch_cover_url('불편한 편의점', '김호연'),
            'https://kakao/cover.jpg',
        )
        mock_google.assert_not_called()

    @patch('integrations.book_covers.google_books.fetch_cover_url')
    @patch('integrations.book_covers.kakao_books.fetch_cover_url')
    def test_falls_back_to_google_when_kakao_misses(self, mock_kakao, mock_google):
        mock_kakao.return_value = None
        mock_google.return_value = 'https://google/cover.jpg'
        self.assertEqual(
            book_covers.fetch_cover_url('1984', '조지 오웰'),
            'https://google/cover.jpg',
        )
        mock_google.assert_called_once()

    @patch('integrations.book_covers.google_books.fetch_cover_url')
    @patch('integrations.book_covers.kakao_books.fetch_cover_url')
    def test_returns_none_when_both_miss(self, mock_kakao, mock_google):
        mock_kakao.return_value = None
        mock_google.return_value = None
        self.assertIsNone(book_covers.fetch_cover_url('존재안함zzz', '가짜저자'))


if __name__ == '__main__':
    unittest.main()
