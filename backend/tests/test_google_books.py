import unittest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations.google_books import fetch_cover_url


def _mock_response(payload):
    """Build a MagicMock standing in for a requests.Response."""
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


def _volume(thumbnail):
    return {'items': [{'volumeInfo': {'imageLinks': {'thumbnail': thumbnail}}}]}


class TestFetchCoverUrl(unittest.TestCase):
    @patch('integrations.google_books.requests.get')
    def test_extracts_thumbnail_from_normal_response(self, mock_get):
        mock_get.return_value = _mock_response(
            _volume('https://books.google.com/cover.jpg')
        )
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_rewrites_http_to_https(self, mock_get):
        mock_get.return_value = _mock_response(
            _volume('http://books.google.com/cover.jpg')
        )
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg',
        )

    @patch('integrations.google_books.requests.get')
    def test_strips_edge_curl_param(self, mock_get):
        mock_get.return_value = _mock_response(
            _volume('http://books.google.com/cover.jpg?id=1&edge=curl')
        )
        self.assertEqual(
            fetch_cover_url('1984', '조지 오웰'),
            'https://books.google.com/cover.jpg?id=1',
        )

    @patch('integrations.google_books.requests.get')
    def test_no_items_returns_none(self, mock_get):
        # Both the ko-restricted call and the retry return no items.
        mock_get.return_value = _mock_response({'totalItems': 0})
        self.assertIsNone(fetch_cover_url('테스트책zzz', '가짜저자'))

    @patch('integrations.google_books.requests.get')
    def test_network_error_returns_none(self, mock_get):
        mock_get.side_effect = requests_exception()
        # Must not raise — best-effort returns None.
        self.assertIsNone(fetch_cover_url('1984', '조지 오웰'))

    @patch.dict(os.environ, {'GOOGLE_BOOKS_API_KEY': 'secret-key'})
    @patch('integrations.google_books.requests.get')
    def test_api_key_passed_when_set(self, mock_get):
        mock_get.return_value = _mock_response(
            _volume('https://books.google.com/cover.jpg')
        )
        fetch_cover_url('1984', '조지 오웰')
        # Key must be forwarded as the `key` query param.
        self.assertEqual(mock_get.call_args.kwargs['params'].get('key'), 'secret-key')

    @patch.dict(os.environ, {}, clear=True)
    @patch('integrations.google_books.requests.get')
    def test_no_api_key_omits_key_param(self, mock_get):
        mock_get.return_value = _mock_response(
            _volume('https://books.google.com/cover.jpg')
        )
        fetch_cover_url('1984', '조지 오웰')
        # No key configured → no `key` param (anonymous call).
        self.assertNotIn('key', mock_get.call_args.kwargs['params'])


def requests_exception():
    import requests
    return requests.exceptions.ConnectionError('boom')


if __name__ == '__main__':
    unittest.main()
