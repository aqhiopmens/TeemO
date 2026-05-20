# TeemO — Project Context for Claude Code

## Project Overview
- **Name**: TeemO
- **What it does**: Web app that analyzes a user's reading preferences (book list + ratings) and recommends books via Upstage Solar LLM
- **Course context**: 2026-1 Algorithms team project (Korea University). Final presentation on 2026-06-09 or 06-11 (in English).
- **Key grading criterion**: "The more course algorithm concepts applied, the better." Already applied: Merge Sort, Hashing, Greedy, KMP. Planning to add 1–2 more (BST / DP / Graph).

## Tech Stack
- **Backend**: Python 3 + Flask 3.0 + flask-cors
- **Frontend**: Vanilla HTML/CSS/JavaScript (no framework)
- **LLM**: Upstage Solar (`solar-pro` model) via REST API
- **Storage**: In-memory (Python list) — persistence is a future consideration

## Repository Structure

```
TeemO/
├── backend/
│   ├── app.py                  # Flask REST API (4 endpoints)
│   ├── algorithms/
│   │   ├── merge_sort.py       # Sort books by rating (descending, stable)
│   │   ├── hashing.py          # BookHashTable, Separate Chaining
│   │   ├── greedy.py           # Genre preference scoring with rank-bonus
│   │   └── kmp.py              # KMP string matching with LPS table
│   ├── llm/
│   │   └── solar.py            # Upstage Solar API client
│   └── requirements.txt
├── frontend/
│   ├── index.html              # 4 sections: add / search / list / recommendations
│   ├── style.css               # Indigo tone, CSS variables
│   └── script.js               # apiFetch helper, escapeHtml (XSS), renderStars
├── .env                        # UPSTAGE_API_KEY (gitignored)
└── README.md
```


## Team Structure & Collaboration Model

### Roles
| Role | Member | Responsibility |
|---|---|---|
| Backend / Server (Lead) | 김강민 | Algorithms, REST API, server logic |
| Frontend | 서은빈 | UI/UX, screen implementation |
| LLM / Prompt | 박병진 | Solar API integration, prompt engineering |
| PM | 오세준 | Schedule, docs, meetings, deliverables |

### Two Development Tracks

We work in **two parallel tracks** to minimize merge conflicts and keep concerns separated:

#### Track 1: App (Frontend + Backend combined)
- **Branch prefix**: `feature/app-*`
- **Owners**: 김강민 (BE) + 서은빈 (FE)
- **Working style**: Both members push directly to the **same** `feature/app-*` branch (no separate FE/BE branches). Always run `git pull --rebase origin <branch>` before each push to avoid conflicts and accidental force pushes.
- **Rationale**: UI and API changes are tightly coupled — pairing them in one branch keeps integration smooth
- **File ownership**: BE owns `backend/` (excluding `backend/llm/`), FE owns `frontend/`. Don't edit the other person's files in the same session without telling them in chat.
- **Example branches**:
  - `feature/app-add-validation`
  - `feature/app-search-ui-polish`
  - `feature/app-bst-genre-index`

#### Track 2: LLM (isolated)
- **Branch prefix**: `feature/llm-*`
- **Owner**: 박병진
- **File ownership**: `backend/llm/` and prompt-related changes only
- **Rationale**: Prompt experimentation needs isolation; integration into App track happens via PR after results are good
- **Example branches**:
  - `feature/llm-prompt-v2`
  - `feature/llm-response-cache`
  - `feature/llm-few-shot-examples`

### Git Workflow
1. Create branch from `main`: `git checkout -b feature/app-xyz`
2. Commit frequently with clear messages
3. Before pushing: `git pull --rebase origin main` to avoid conflicts
4. Open PR to `main` — **requires 1 reviewer approval** from the other track before merge
5. After merge, delete the feature branch

### When Working on Code
- **API contract changes**: If you modify a REST API endpoint's request/response shape, announce it in the team chat BEFORE merging, so the other track can adapt
- **Cross-track changes**: If LLM track needs a new API field (e.g., for caching), open a PR or issue requesting the BE change rather than modifying `backend/app.py` directly
- **Tests first when possible**: For algorithms, write a small test script in `backend/tests/` (pytest or standalone)

## Coding Conventions

### Python (Backend)
- Follow PEP 8
- Type hints encouraged but not mandatory
- Docstrings for public functions, especially in `algorithms/` (include time complexity)
- Input validation in `app.py` route handlers, not in algorithm modules
- Algorithm modules should be pure functions where possible (easier to test)

### JavaScript (Frontend)
- Vanilla JS, no framework
- Always use `escapeHtml()` when inserting user input into the DOM
- API calls go through the `apiFetch()` helper
- Keep CSS in `style.css`, use CSS variables for theming

### Prompts (LLM)
- All prompts live in `backend/llm/solar.py` (or new files under `backend/llm/`)
- Document prompt versions: v1, v2, etc., with the rationale for changes
- Test prompts against these input cases:
  - 1 book only (minimal data)
  - All same genre (biased input)
  - 5+ different genres (diverse input)
  - All 5-star or all 1-star (extreme ratings)

## API Endpoints (Current)
| Method | Path | Purpose |
|---|---|---|
| GET | `/api/books` | List books sorted by rating (Merge Sort) |
| POST | `/api/books` | Add a book (validates: title/author/genre required, rating 1–5 int) |
| GET | `/api/search?q=<query>` | Search book titles using KMP |
| GET | `/api/recommendations` | Pipeline: Merge Sort → Hashing (top genres) → Greedy (scores) → Solar LLM |

## Current Status (as of Week 11)
- ✅ All 4 algorithms implemented
- ✅ REST API endpoints working
- ✅ Frontend UI complete (4 sections)
- ✅ Solar API integration working end-to-end (verified on web)
- ⏳ Next: 1–2 more algorithms (BST/DP/Graph), LLM quality testing, UI polish

## When in Doubt
- **Code style questions**: Match existing patterns in the repo
- **Architecture questions**: Keep it simple — this is a course project, not production
- **Algorithm choice**: Prefer ones explicitly taught in class (sorting, divide & conquer, greedy, DP, graph, hashing, BST/RBT/B-Tree)
- **Always**: Explain your changes clearly in PR descriptions so non-coding teammates (PM) can follow
