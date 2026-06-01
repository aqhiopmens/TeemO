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


if __name__ == "__main__":
    unittest.main()
