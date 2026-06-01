# TeemO

[![CI](https://github.com/aqhiopmens/TeemO/actions/workflows/ci.yml/badge.svg)](https://github.com/aqhiopmens/TeemO/actions/workflows/ci.yml)

2026-1 Algorithm Project — AI-based Book Preference Analysis & Recommendation

## Overview

Users input books they have read along with ratings (1–5).  
The backend analyzes reading preferences using classic algorithms, then calls the  
Upstage Solar LLM to generate personalized book recommendations.

## Project Structure

```
TeemO/
├── backend/
│   ├── app.py                  # Flask REST API
│   ├── algorithms/
│   │   ├── merge_sort.py       # Sort books by rating
│   │   ├── hashing.py          # Genre-keyed hash table
│   │   ├── greedy.py           # Preference score weighting
│   │   ├── kmp.py              # Title search (KMP, exact)
│   │   └── levenshtein.py      # Edit distance (DP) — fuzzy title search fallback
│   ├── llm/
│   │   └── solar.py            # Upstage Solar API client
│   ├── integrations/
│   │   ├── book_covers.py     # Unified cover lookup: Kakao → Google Books fallback
│   │   ├── kakao_books.py     # Kakao Book Search (best for Korean books)
│   │   ├── google_books.py    # Google Books (best for international/classics)
│   │   └── _match.py          # Shared title/author match check (precision)
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .env                        # (not committed) UPSTAGE_API_KEY=..., KAKAO_REST_API_KEY=..., GOOGLE_BOOKS_API_KEY=...
└── README.md
```

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Create .env in the project root
echo UPSTAGE_API_KEY=your_key_here > .env
# (optional) book covers — covers are looked up via Kakao first (best Korean
# coverage), then Google Books. Both are free; without them covers just fall
# back to a colour block. Kakao: developers.kakao.com → REST API key.
# Google: Google Cloud → enable "Books API" → API key (raises the daily quota).
echo KAKAO_REST_API_KEY=your_key_here >> .env
echo GOOGLE_BOOKS_API_KEY=your_key_here >> .env

# 4. Run the backend
cd backend
python app.py
```

Open `frontend/index.html` in a browser (or serve it with any static server).

## Running Tests

Unit tests for the algorithm modules use the Python standard library `unittest` framework — no extra dependencies required.

```bash
cd backend
python -m unittest discover -s tests
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/books` | List all books sorted by rating. Each book carries `_idx` (its original storage index) so the client can delete the right book despite the sorted order |
| POST | `/api/books` | Add a book `{title, author, rating}` — genre is auto-classified by the Solar LLM (response adds `genre_auto_classified: true`). A best-effort cover image is looked up via Kakao (Korean books) then Google Books, returned as `cover_url` (`null` if not found) |
| GET | `/api/search?q=<query>` | Search titles — KMP exact match, else Levenshtein fuzzy fallback (≤3). Returns `{results, matched_by, did_you_mean}` |
| GET | `/api/recommendations` | Get Solar LLM recommendations. Optional repeated `exclude` params (`?exclude=A&exclude=B`) skip already-shown titles so "다시 추천 받기" returns fresh books |

## Algorithm Concepts Applied

### 1. Merge Sort (`algorithms/merge_sort.py`)
- **Purpose:** Sort the user's book list by rating in descending order before analysis
- **Method:** Divide & Conquer — recursively splits the list, merges in sorted order
- **Complexity:** O(n log n) guaranteed; stable sort preserves insertion order for equal ratings

### 2. Hash Table with Separate Chaining (`algorithms/hashing.py`)
- **Purpose:** Group books by genre and compute top preferred genres in O(1) average time
- **Hash function:** `sum(ord(c) for c in genre) % table_size`
- **Collision resolution:** Separate chaining (list of entries per slot)
- **Complexity:** O(1) average for insert and lookup

### 3. Greedy Preference Scoring (`algorithms/greedy.py`)
- **Purpose:** Assign a normalized preference weight to each genre
- **Method:** Greedily accumulates rating × rank-bonus per genre, then normalizes
- **Complexity:** O(n) — single pass over the sorted book list

### 4. KMP String Search (`algorithms/kmp.py`)
- **Purpose:** Efficient substring title search across the book list
- **Method:** Knuth–Morris–Pratt with LPS (Longest Proper Prefix-Suffix) table
- **Complexity:** O(n + m) where n = text length, m = pattern length

### 5. Levenshtein Distance (Dynamic Programming) (`algorithms/levenshtein.py`)
- **Purpose:** Typo-tolerant title search — when the KMP exact search finds nothing,
  fall back to fuzzy matching so a misspelled query still surfaces the right book
  (a "did you mean…?" suggestion)
- **Method:** Bottom-up 2D DP table; `dp[i][j]` = edit distance between the prefixes
  `s1[:i]` and `s2[:j]`, minimizing insertion / deletion / substitution
- **Complexity:** O(m × n) time and space, where m, n are the string lengths
