import unittest
from unittest.mock import patch, MagicMock

from llm.solar import classify_genre


def _mock_response(content):
    """Build a fake Solar HTTP response whose JSON yields ``content``."""
    resp = MagicMock()
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    resp.raise_for_status.return_value = None
    return resp


class TestClassifyGenre(unittest.TestCase):
    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_returns_korean_word_on_success(self, mock_post):
        mock_post.return_value = _mock_response('판타지')
        self.assertEqual(classify_genre('호빗', 'J.R.R. 톨킨'), '판타지')

    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_strips_surrounding_whitespace(self, mock_post):
        mock_post.return_value = _mock_response('  추리\n')
        self.assertEqual(classify_genre('셜록 홈즈', '아서 코난 도일'), '추리')

    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_passes_timeout_to_request(self, mock_post):
        mock_post.return_value = _mock_response('소설')
        classify_genre('제목', '저자')
        self.assertEqual(mock_post.call_args.kwargs.get('timeout'), 30)

    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_api_error_returns_unknown(self, mock_post):
        mock_post.side_effect = Exception('network down')
        self.assertEqual(classify_genre('제목', '저자'), 'Unknown')

    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_empty_content_returns_unknown(self, mock_post):
        mock_post.return_value = _mock_response('   ')
        self.assertEqual(classify_genre('제목', '저자'), 'Unknown')

    @patch.dict('os.environ', {'UPSTAGE_API_KEY': 'test-key'})
    @patch('llm.solar.requests.post')
    def test_off_candidate_word_collapses_to_etc(self, mock_post):
        # Prompt v2: 후보 목록(GENRE_CANDIDATES) 밖의 단어는 "기타"로 흡수된다.
        mock_post.return_value = _mock_response('로맨스')
        self.assertEqual(classify_genre('제목', '저자'), '기타')

    @patch.dict('os.environ', {}, clear=True)
    def test_missing_api_key_returns_unknown(self):
        # No network call should happen when the key is absent.
        self.assertEqual(classify_genre('제목', '저자'), 'Unknown')


if __name__ == '__main__':
    unittest.main()
