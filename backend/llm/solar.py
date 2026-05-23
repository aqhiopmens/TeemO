import os
import requests

SOLAR_API_URL = "https://api.upstage.ai/v1/chat/completions"


def get_recommendations(books, top_genres, preference_scores):
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise ValueError("UPSTAGE_API_KEY not set in environment")

    book_list = "\n".join(
        f"- {b['title']} by {b['author']} (Rating: {b['rating']}/5, Genre: {b['genre']})"
        for b in books
    )
    genre_str = ", ".join(top_genres) if top_genres else "various"
    score_str = ", ".join(f"{g}: {s}" for g, s in preference_scores.items())

    prompt = (
        "You are a book recommendation expert.\n\n"
        f"The user has read and rated the following books:\n{book_list}\n\n"
        f"Top preferred genres: {genre_str}\n"
        f"Preference scores by genre: {score_str}\n\n"
        "Based on this reading history and preferences, recommend 5 books the user would love next.\n"
        "For each book provide: title, author, genre, and a brief reason (1-2 sentences) "
        "why it matches their taste. Format as a numbered list.\n\n"
        "Respond in Korean."  # Owner override: align output language with the Korean UI
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
        "max_tokens": 1024,
    }

    response = requests.post(SOLAR_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def classify_genre(title: str, author: str) -> str:
    """Classify a book into a single Korean genre word via Solar.

    Returns one Korean word (e.g. "판타지"). Any failure — missing API key,
    network error, timeout, or malformed response — yields "Unknown" instead
    of raising, so the book-add flow is never blocked by the LLM call.

    Owner override (LLM track): temporary auto-classification prompt added
    before 박병진 is set up; revisit as prompt v2.
    """
    try:
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            return "Unknown"

        prompt = (
            "Classify this book into a single genre word in Korean. "
            f"Title: {title}, Author: {author}. "
            "Respond with ONE Korean word only, no explanation."
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
        return genre or "Unknown"
    except Exception:
        return "Unknown"
