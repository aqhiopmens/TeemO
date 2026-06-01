import json
import unittest
from unittest.mock import patch, MagicMock

from llm import solar
from llm.solar import _parse_first_json, get_recommendations


class TestParseFirstJson(unittest.TestCase):
    def test_plain_object(self):
        self.assertEqual(_parse_first_json('{"a": 1}'), {"a": 1})

    def test_ignores_trailing_extra_object(self):
        # Solar sometimes appends a second object → json.loads raises 'Extra data'.
        doubled = '{"recommendations": [1]}\n{"recommendations": [2]}'
        self.assertEqual(_parse_first_json(doubled), {"recommendations": [1]})

    def test_strips_code_fence(self):
        fenced = '```json\n{"recommendations": []}\n```'
        self.assertEqual(_parse_first_json(fenced), {"recommendations": []})

    def test_skips_leading_prose(self):
        self.assertEqual(_parse_first_json('자, 추천이야: {"x": 2} 끝!'), {"x": 2})

    def test_no_object_raises(self):
        with self.assertRaises(json.JSONDecodeError):
            _parse_first_json('표지가 없어요')


def _doubled_recs_response():
    """Solar response whose content is a valid object followed by extra data."""
    recs = [{"title": f"추천{i}", "author": "저자", "genre": "소설", "reason": "이유"}
            for i in range(5)]
    content = json.dumps({"recommendations": recs}, ensure_ascii=False) + "\n설명을 덧붙입니다."
    resp = MagicMock()
    resp.json.return_value = {"choices": [{"message": {"content": content}}]}
    resp.raise_for_status.return_value = None
    return resp


@patch.dict("os.environ", {"UPSTAGE_API_KEY": "test-key"})
class TestRecommendationsTolerantParse(unittest.TestCase):
    def setUp(self):
        solar._cache.clear()

    @patch("llm.solar.requests.post")
    def test_recommendations_parsed_despite_trailing_text(self, mock_post):
        mock_post.return_value = _doubled_recs_response()
        result = get_recommendations(
            [{"title": "데미안", "author": "헤세", "genre": "소설", "rating": 5}],
            ["소설"], {"소설": 1.0},
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)

    @patch("llm.solar.requests.post")
    def test_retries_once_on_unparseable_then_succeeds(self, mock_post):
        # First response has no JSON (e.g. truncated / prose); retry returns valid.
        mock_post.side_effect = [_unparseable_response(), _doubled_recs_response()]
        result = get_recommendations(
            [{"title": "데미안", "author": "헤세", "genre": "소설", "rating": 5}],
            ["소설"], {"소설": 1.0},
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertEqual(mock_post.call_count, 2)  # one retry

    @patch("llm.solar.requests.post")
    def test_two_failures_return_error_dict(self, mock_post):
        mock_post.side_effect = [_unparseable_response(), _unparseable_response()]
        result = get_recommendations(
            [{"title": "데미안", "author": "헤세", "genre": "소설", "rating": 5}],
            ["소설"], {"소설": 1.0},
        )
        self.assertEqual(result, {"error": "응답 형식 오류"})
        self.assertEqual(mock_post.call_count, 2)


def _unparseable_response():
    """A Solar response whose content has no JSON object at all."""
    resp = MagicMock()
    resp.json.return_value = {"choices": [{"message": {"content": "죄송, 추천을 못 만들었어요"}}]}
    resp.raise_for_status.return_value = None
    return resp


if __name__ == "__main__":
    unittest.main()
