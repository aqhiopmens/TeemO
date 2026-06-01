import unittest
from unittest.mock import patch, MagicMock

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integrations import kakao_books


def _resp(documents):
    resp = MagicMock()
    resp.json.return_value = {'documents': documents}
    resp.raise_for_status = MagicMock()
    return resp


def _doc(title, authors, thumbnail=''):
    return {'title': title, 'authors': authors, 'thumbnail': thumbnail}


class TestKakaoFetchCoverUrl(unittest.TestCase):
    @patch.dict(os.environ, {'KAKAO_REST_API_KEY': 'k'})
    @patch('integrations.kakao_books.requests.get')
    def test_returns_thumbnail_for_matching_doc(self, mock_get):
        mock_get.return_value = _resp([
            _doc('불편한 편의점', ['김호연'], 'https://img.kakao/c.jpg'),
        ])
        self.assertEqual(
            kakao_books.fetch_cover_url('불편한 편의점', '김호연'),
            'https://img.kakao/c.jpg',
        )
        # Auth header carries the REST key.
        self.assertEqual(
            mock_get.call_args.kwargs['headers']['Authorization'], 'KakaoAK k')

    @patch.dict(os.environ, {'KAKAO_REST_API_KEY': 'k'})
    @patch('integrations.kakao_books.requests.get')
    def test_skips_doc_without_thumbnail(self, mock_get):
        mock_get.return_value = _resp([
            _doc('아몬드', ['손원평'], ''),                       # no thumbnail
            _doc('아몬드 (리커버)', ['손원평'], 'https://img/2.jpg'),
        ])
        self.assertEqual(
            kakao_books.fetch_cover_url('아몬드', '손원평'),
            'https://img/2.jpg',
        )

    @patch.dict(os.environ, {'KAKAO_REST_API_KEY': 'k'})
    @patch('integrations.kakao_books.requests.get')
    def test_rejects_wrong_author(self, mock_get):
        mock_get.return_value = _resp([
            _doc('살인자의 기억법 해설', ['윤지한'], 'https://img/wrong.jpg'),
        ])
        self.assertIsNone(kakao_books.fetch_cover_url('살인자의 기억법', '김영하'))

    @patch.dict(os.environ, {}, clear=True)
    @patch('integrations.kakao_books.requests.get')
    def test_no_key_returns_none_without_request(self, mock_get):
        self.assertIsNone(kakao_books.fetch_cover_url('아몬드', '손원평'))
        mock_get.assert_not_called()

    @patch.dict(os.environ, {'KAKAO_REST_API_KEY': 'k'})
    @patch('integrations.kakao_books.requests.get')
    def test_network_error_returns_none(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError('boom')
        self.assertIsNone(kakao_books.fetch_cover_url('아몬드', '손원평'))


if __name__ == '__main__':
    unittest.main()
