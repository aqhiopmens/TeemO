import json
import unittest
from unittest.mock import patch, MagicMock

from llm import solar
from llm.solar import get_recommendations


def _rec_response():
    """5개짜리 정상 recommendations 리스트를 반환하는 가짜 Solar 응답."""
    recs = [
        {"title": f"추천{i}", "author": "저자", "genre": "소설", "reason": "이유"}
        for i in range(5)
    ]
    resp = MagicMock()
    resp.json.return_value = {
        "choices": [{"message": {"content": json.dumps(
            {"recommendations": recs}, ensure_ascii=False)}}]
    }
    resp.raise_for_status.return_value = None
    return resp


def _books(title="데미안", author="헤세", rating=5):
    return [{"title": title, "author": author, "genre": "소설", "rating": rating}]


@patch.dict("os.environ", {"UPSTAGE_API_KEY": "test-key"})
class TestRecommendationCache(unittest.TestCase):
    def setUp(self):
        # 모듈 전역 캐시는 테스트 간 공유되므로 매 테스트 초기화.
        solar._cache.clear()

    @patch("llm.solar.requests.post")
    def test_same_input_served_from_cache(self, mock_post):
        mock_post.return_value = _rec_response()
        books = _books()
        first = get_recommendations(books, ["소설"], {"소설": 1.0})
        second = get_recommendations(books, ["소설"], {"소설": 1.0})
        # 두 번째 호출은 캐시 히트 → API 미호출, 동일 결과.
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(first, second)

    @patch("llm.solar.requests.post")
    def test_different_input_calls_api_again(self, mock_post):
        mock_post.return_value = _rec_response()
        get_recommendations(_books(title="데미안"), ["소설"], {"소설": 1.0})
        get_recommendations(_books(title="1984"), ["소설"], {"소설": 1.0})
        # 입력이 다르면 캐시 미스 → API 두 번 호출.
        self.assertEqual(mock_post.call_count, 2)

    @patch("llm.solar.requests.post")
    def test_exclude_busts_cache_and_calls_api_again(self, mock_post):
        mock_post.return_value = _rec_response()
        books = _books()
        # 같은 책이라도 exclude가 다르면 다른 캐시 키 → API 재호출 ("다시 추천").
        get_recommendations(books, ["소설"], {"소설": 1.0})
        get_recommendations(books, ["소설"], {"소설": 1.0}, exclude=["추천0", "추천1"])
        self.assertEqual(mock_post.call_count, 2)
        # 같은 exclude로 다시 부르면 캐시 히트 → 추가 호출 없음.
        get_recommendations(books, ["소설"], {"소설": 1.0}, exclude=["추천1", "추천0"])
        self.assertEqual(mock_post.call_count, 2)

    @patch("llm.solar.requests.post")
    def test_excluded_titles_appear_in_prompt(self, mock_post):
        mock_post.return_value = _rec_response()
        get_recommendations(_books(), ["소설"], {"소설": 1.0}, exclude=["멋진 신세계"])
        prompt = mock_post.call_args.kwargs["json"]["messages"][1]["content"]
        self.assertIn("멋진 신세계", prompt)
        self.assertIn("이미 추천", prompt)

    @patch("llm.solar.requests.post")
    def test_error_result_not_cached(self, mock_post):
        import requests
        mock_post.side_effect = requests.ConnectionError()
        result = get_recommendations(_books(), ["소설"], {"소설": 1.0})
        # 실패는 error dict이며 캐시에 저장되지 않는다.
        self.assertIn("error", result)
        self.assertEqual(len(solar._cache), 0)

    @patch("llm.solar.requests.post")
    def test_lru_eviction_after_max(self, mock_post):
        mock_post.return_value = _rec_response()
        # 첫 입력을 캐싱하고 그 키를 기록.
        get_recommendations(_books(title="책0"), ["소설"], {"소설": 1.0})
        first_key = next(iter(solar._cache))
        # 서로 다른 입력으로 _CACHE_MAX(50)개를 채우도록 50번 더 호출 (총 51개).
        for i in range(1, solar._CACHE_MAX + 1):
            get_recommendations(_books(title=f"책{i}"), ["소설"], {"소설": 1.0})
        # 가장 오래된(첫) 항목이 제거되고 크기는 상한을 유지.
        self.assertNotIn(first_key, solar._cache)
        self.assertEqual(len(solar._cache), solar._CACHE_MAX)


if __name__ == "__main__":
    unittest.main()
