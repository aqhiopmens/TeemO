import json
import os
from collections import OrderedDict

import requests

SOLAR_API_URL = "https://api.upstage.ai/v1/chat/completions"

# get_recommendations 응답 LRU 캐시. 같은 독서 이력으로 반복 호출 시
# Solar API 호출을 아껴 공유 rate limit 부담을 줄인다.
_cache = OrderedDict()
_CACHE_MAX = 50

# 자동 장르 분류가 사용할 수 있는 유일한 후보 집합.
# classify_genre 는 이 목록 밖의 값을 절대 반환하지 않는다.
GENRE_CANDIDATES = [
    "소설", "판타지", "SF", "추리", "자기계발",
    "역사", "에세이", "인문", "과학", "기타",
]

# 두 프롬프트 공통: 평문 응답 강제(마크다운 금지)
_NO_MARKDOWN = "마크다운(**, #, `, -) 사용 금지, 평문으로만 응답."


def _parse_first_json(content):
    """응답에서 첫 JSON 객체만 파싱한다.

    Solar가 가끔 코드펜스를 두르거나, 유효한 JSON 뒤에 설명/중복 객체를
    덧붙여 ``json.loads`` 가 'Extra data' 로 실패하는 경우가 있다(특히 exclude
    프롬프트). 코드펜스를 벗기고 첫 '{' 부터 ``raw_decode`` 로 한 객체만 읽어
    뒤의 여분은 무시한다. 파싱 불가 시 JSONDecodeError 를 그대로 올린다.
    """
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text[:4].lower() == "json":
            text = text[4:]
    start = text.find("{")
    if start == -1:
        raise json.JSONDecodeError("no JSON object found", text or "", 0)
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def get_recommendations(books, top_genres, preference_scores, exclude=None):
    """Solar에 추천을 요청하고 recommendations 리스트를 반환한다.

    ``exclude``: 이미 추천해 제외할 책 제목들(iterable). "다시 추천 받기"가
    매번 새로운 책을 받도록, 제외 목록을 프롬프트에 반영하고 캐시 키에도
    포함한다(같은 제외셋끼리만 캐시 공유).

    모든 실패는 예외로 전파하지 않고 ``{"error": <한국어 메시지>}`` dict로
    돌려준다 — 호출부(app.py)와 프론트가 항상 dict/list만 다루면 되도록.
    """
    try:
        # 제외 목록 정규화: 공백 제거 + 중복 제거 + 정렬(캐시 키 안정화).
        exclude_titles = tuple(sorted(
            {(t or "").strip() for t in (exclude or []) if (t or "").strip()}
        ))
        # 캐시 키: 책의 (제목, 저자, 평점) 집합 + 제외 목록 — 순서 무관(sorted).
        cache_key = hash((
            tuple(sorted((b["title"], b["author"], b["rating"]) for b in books)),
            exclude_titles,
        ))
        if cache_key in _cache:
            _cache.move_to_end(cache_key)  # 최근 사용으로 갱신 (LRU)
            return _cache[cache_key]

        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("UPSTAGE_API_KEY not set in environment")

        book_list = "\n".join(
            f"{b['title']} / {b['author']} (평점 {b['rating']}/5, 장르 {b['genre']})"
            for b in books
        )
        genre_str = ", ".join(top_genres) if top_genres else "다양함"
        score_str = ", ".join(f"{g}: {s}" for g, s in preference_scores.items())

        # "다시 추천 받기"용 제외 절: 이미 보여준 책을 다시 추천하지 않도록.
        exclude_clause = ""
        if exclude_titles:
            exclude_clause = (
                f"\n\n단, 다음 책들은 이미 추천했으니 절대 다시 추천하지 마: "
                f"{', '.join(exclude_titles)}.\n"
                "이 목록과 겹치지 않는 완전히 새로운 책 4권으로 추천해줘."
            )

        # Prompt v2 + JSON 구조화: 한국어 친근체 + 추천 사유 2~3문장
        # + 응답을 JSON 형식으로 강제 (프론트 카드 UI 렌더용)
        prompt = (
            "너는 책을 잘 아는 친한 친구 같은 책 추천 도우미야. 편하고 다정한 말투로 이야기해줘.\n\n"
            f"내가 지금까지 읽고 평점을 매긴 책들이야:\n{book_list}\n\n"
            f"내가 가장 좋아하는 장르: {genre_str}\n"
            f"장르별 선호 점수: {score_str}\n\n"
            "이 독서 이력과 취향을 바탕으로, 내가 다음에 읽으면 좋아할 책 4권을 추천해줘.\n"
            "각 책마다 제목, 저자, 장르를 알려주고, 왜 내 취향에 맞는지 추천 사유를 "
            "2~3문장으로 친근하게 설명해줘."
            f"{exclude_clause}\n\n"
            "응답은 정확히 다음 JSON 형식으로만 해줘 — 다른 텍스트, 설명, 코드펜스, 마크다운 절대 금지. "
            "배열에는 정확히 4개 책:\n"
            '{"recommendations": [{"title": "책제목", "author": "저자", '
            '"genre": "장르", "reason": "추천사유"}, ...]}\n\n'
            f"{_NO_MARKDOWN}"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "solar-pro",
            "messages": [
                {"role": "system", "content": "You are a helpful book recommendation assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            # 추천 사유가 길어도 JSON이 잘리지 않도록 충분히 (이전 1024는 가끔 잘려
            # 파싱 실패 → "응답 형식 오류"가 났다).
            "max_tokens": 1500,
        }

        # Solar가 가끔 비-JSON이거나 잘린 응답을 준다(특히 exclude로 여러 번 호출 시).
        # 파싱 실패하면 1회 재요청한다 — temperature>0라 재요청은 보통 정상 JSON.
        parse_error = None
        result = None
        for _ in range(2):
            response = requests.post(SOLAR_API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            try:
                result = _parse_first_json(content)["recommendations"]
                break
            except (json.JSONDecodeError, KeyError) as e:
                parse_error = e  # 다음 루프에서 재요청
        if result is None:
            raise parse_error  # 두 번 모두 실패 → 바깥 except에서 error dict 반환

        # 성공(리스트) 결과만 캐시에 저장. error dict는 저장하지 않는다.
        if isinstance(result, list):
            if len(_cache) >= _CACHE_MAX:
                _cache.popitem(last=False)  # 가장 오래된 항목 제거 (LRU eviction)
            _cache[cache_key] = result
        return result

    except requests.Timeout:
        return {"error": "응답 시간 초과"}
    except requests.RequestException:
        return {"error": "LLM 서버 연결 실패"}
    except json.JSONDecodeError:
        return {"error": "응답 형식 오류"}
    except (KeyError, IndexError):
        return {"error": "응답 형식 오류"}
    except Exception:
        return {"error": "알 수 없는 오류가 발생했습니다."}


def classify_genre(title: str, author: str) -> str:
    """Classify a book into one of GENRE_CANDIDATES via Solar.

    Returns exactly one of the predefined Korean genres (e.g. "판타지").
    The model is constrained by the prompt to pick from the candidate list,
    and the response is validated against it — anything off-list collapses
    to "기타". Any failure — missing API key, network error, timeout, or
    malformed response — yields "Unknown" instead of raising, so the
    book-add flow is never blocked by the LLM call.

    Prompt v2 (LLM track, 박병진): 후보 장르 강제 + 평문 응답.
    """
    try:
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            return "Unknown"

        candidates = "/".join(GENRE_CANDIDATES)
        prompt = (
            "다음 책을 아래 장르 후보 중 단 하나로 분류해줘.\n"
            f"장르 후보: {candidates}\n"
            f"제목: {title}, 저자: {author}\n"
            "반드시 위 후보 중 하나의 단어로만 답하고, 후보에 없는 단어는 쓰지 마.\n"
            "애매하면 '기타'로 답해. 설명 없이 장르 단어 하나만 출력해.\n"
            f"{_NO_MARKDOWN}"
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "solar-pro",
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": 20,
        }

        response = requests.post(SOLAR_API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        genre = response.json()["choices"][0]["message"]["content"].strip()
        if not genre:
            return "Unknown"  # 빈 응답 = 분류 실패 신호 (오류와 동일 취급)
        # 내용은 있으나 후보 밖인 경우만 "기타"로 흡수해 후보 집합을 강제한다.
        return genre if genre in GENRE_CANDIDATES else "기타"
    except Exception:
        return "Unknown"
