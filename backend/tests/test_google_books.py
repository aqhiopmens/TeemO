import unittest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.google_books import fetch_cover_url


def _resp(items):
    """Build a MagicMock standing in for a requests.Response."""
    resp = MagicMock()
    resp.json.return_value = {'items': items}
    resp.raise_for_status = MagicMock()
    return resp


def _item(title, authors, thumbnail=None):
    """A Google Books volume; omit thumbnail to simulate a cover-less result."""
    vi = {'title': title, 'authors': authors}
    if thumbnail is not None:
        vi['imageLinks'] = {'thumbnail': thumbnail}
    return {'volumeInfo': vi}


class TestFetchCoverUrl(unittest.TestCase):
    @patch('integrations.google_books.requests.get')
    def test_returns_thumbnail_for_matching_volume(self, mock_get):
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰'], 'https://books.google.com/cover.jpg'),
        ])
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_rewrites_http_to_https(self, mock_get):
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰'], 'http://books.google.com/cover.jpg'),
        ])
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_strips_edge_curl_param(self, mock_get):
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰'], 'http://books.google.com/cover.jpg?id=1&edge=curl'),
        ])
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg?id=1',
        )

    @patch('integrations.google_books.requests.get')
    def test_skips_coverless_result_and_picks_matching_one_with_image(self, mock_get):
        # First (exact) result has no imageLinks; a later same-book edition does.
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰']),  # no cover
            _item('1984 (한글판)', ['조지 오웰'], 'https://books.google.com/c2.jpg'),
        ])
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/c2.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_rejects_wrong_author_even_with_image(self, mock_get):
        # A commentary that contains the title but is by a different author must
        # NOT be accepted (precision). With no other candidate → None.
        mock_get.return_value = _resp([
            _item('저는 김영하의 살인자의 기억법 이렇게 읽었습니다', ['윤지한'],
                  'https://books.google.com/wrong.jpg'),
        ])
        self.assertIsNone(fetch_cover_url('살인자의 기억법', '김영하'))

    @patch('integrations.google_books.requests.get')
    def test_accepts_author_spelling_variant(self, mock_get):
        # 애거사 vs 애거서 — token "크리스티" overlaps, so it's accepted.
        mock_get.return_value = _resp([
            _item('그리고 아무도 없었다', ['애거서 크리스티'],
                  'https://books.google.com/c.jpg'),
        ])
        self.assertEqual(
            fetch_cover_url('그리고 아무도 없었다', '애거사 크리스티'),
            'https://books.google.com/c.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_no_results_returns_none(self, mock_get):
        mock_get.return_value = _resp([])
        self.assertIsNone(fetch_cover_url('존재하지않는책zzz', '가짜저자'))

    @patch('integrations.google_books.requests.get')
    def test_network_error_returns_none(self, mock_get):
        mock_get.side_effect = requests_exception()
        # Must not raise — best-effort returns None.
        self.assertIsNone(fetch_cover_url('1984', '조지 오웰'))

    @patch.dict(os.environ, {'GOOGLE_BOOKS_API_KEY': 'secret-key'})
    @patch('integrations.google_books.requests.get')
    def test_api_key_passed_when_set(self, mock_get):
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰'], 'https://books.google.com/cover.jpg'),
        ])
        fetch_cover_url('1984', '조지 오웰')
        self.assertEqual(mock_get.call_args.kwargs['params'].get('key'), 'secret-key')

    @patch.dict(os.environ, {}, clear=True)
    @patch('integrations.google_books.requests.get')
    def test_no_api_key_omits_key_param(self, mock_get):
        mock_get.return_value = _resp([
            _item('1984', ['조지 오웰'], 'https://books.google.com/cover.jpg'),
        ])
        fetch_cover_url('1984', '조지 오웰')
        self.assertNotIn('key', mock_get.call_args.kwargs['params'])


def requests_exception():
    import requests
    return requests.exceptions.ConnectionError('boom')


if __name__ == '__main__':
    unittest.main()
