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

## Team Operating Environment (claude.ai 웹 + Claude Code 병행)

본 팀은 두 가지 Claude 표면을 병행 사용합니다.

### Claude Code (이 환경)
- 모든 **코드 작업**: 파일 편집, 실행, 테스트, 디버깅, 커밋
- 본 `CLAUDE.md` + 본인의 `CLAUDE.local.md`를 컨텍스트로 사용
- 4명이 김강민 Claude 계정 공유 (각자 본인 노트북에서 `claude` 실행)

### claude.ai 웹 채팅 — Project 5개
| Project | 용도 | 주 사용자 |
|---|---|---|
| TeemO - 공유 | 공유 문서 작성·갱신 (개발 프로세스 문서, 회의록, 주간 보고, README) | 김강민 |
| TeemO - 김강민 (Backend) | 알고리즘 설계 논의, 코드 리뷰 상담 | 김강민 |
| TeemO - 서은빈 (Frontend) | UI/UX 설계, Artifacts 디자인 프리뷰 | 서은빈 |
| TeemO - 박병진 (LLM) | 프롬프트 설계, 응답 품질 분석 | 박병진 |
| TeemO - 오세준 (PM) | 일정 관리, 전체 진행 점검 | 오세준 |

각 Project에는 Google Drive sync로 개발 프로세스 문서가 연결되어 있어, 웹에서 작업 시 최신 진행 상황을 항상 참조 가능.

### 역할 분담 보강
- **공유 문서 작업** (개발 프로세스 문서, 회의록, 주간 보고, README): 김강민
- **발표 슬라이드·기술 보고서** (영문, 6/4~6/8): 팀 전원이 함께 작업
- **코드 작업**은 위 표의 본인 담당 폴더에 한정, Claude Code로 진행

### 어디서 뭘 할지
| 작업 | 어디서 |
|---|---|
| 파일 직접 수정·실행·테스트 | Claude Code |
| 알고리즘 설계 논의, 복잡도 분석 | 웹 (본인 Project) |
| UI 시안 빠른 프리뷰 | 웹 (서은빈 Project, Artifacts) |
| 프롬프트 v2 설계·응답 비교 | 웹 (박병진 Project) |
| 회의록·주간 보고 작성 | 웹 (공유 Project, 김강민) |
| 영문 발표 슬라이드 | 웹 (공유 또는 오세준 Project, 팀 전원) |

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

### Owner Override (김강민 only)

As repo owner and BE Lead, 김강민 may directly modify any file — including those in another track's ownership — when **all** of these apply:

- The change is small (typically 1–3 lines) and blocking other work
- The track owner is **unavailable or not yet set up** with Claude Code / GitHub
- It's a clear bug fix or trivial config change, **not a design decision**

**Procedure when overriding**:
1. Branch must use the appropriate track prefix for the file being touched
   - LLM file → `feature/llm-*` (not `feature/app-*`)
2. PR title or description must include `Owner override:` and a one-line reason
3. @mention the track owner so they review retroactively when set up
4. Notify on team chat before opening the PR

**Never override on**:
- Prompt design changes (LLM track core work)
- Architecture decisions or refactors
- Ongoing work in someone else's open branch
- Files in `frontend/` while 서은빈 is actively editing (check chat first)

The override exists to **unblock progress**, not to bypass collaboration. When in doubt, ask in team chat first — it's almost always faster than the override.

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

## Common Patterns (Templates)

### Adding a new algorithm module
1. Create `backend/algorithms/<name>.py` — pure functions / classes, **no Flask imports**
2. Top of file: docstring describing purpose, method, and **time complexity**
3. Create `backend/tests/test_<name>.py` mirroring existing test files (stdlib `unittest`, see `test_kmp.py` as reference)
4. Wire into `backend/app.py` only if it serves a user-facing endpoint
5. Update `README.md` "Algorithm Concepts Applied" section
6. Run `cd backend && python -m unittest discover -s tests` — all green

### Adding a new REST endpoint
1. Add route in `backend/app.py` with explicit validation (mirror the `add_book` POST handler)
2. Return `{'error': '...'}` with proper HTTP status on bad input (400, 404, etc.)
3. Document in README's `## API Endpoints` table AND update the same table in `CLAUDE.md`
4. If the endpoint changes existing response shape, **announce in team chat before merging** (frontend will break)
5. Frontend code (`script.js`) calls it through the existing `apiFetch()` helper

### Adding a frontend feature
1. New section in `frontend/index.html` follows the `<section id="...">` + `<h2>` pattern
2. Event handlers at bottom of `script.js`, always go through `apiFetch()`
3. **Any user-input rendered into DOM MUST pass through `escapeHtml()`** — no exceptions
4. CSS in `style.css`, reuse existing CSS variables (don't hardcode colors)
5. Test by opening `frontend/index.html` in browser with backend running on `localhost:5000`

### Adding/changing an LLM prompt (박병진)
1. Versioned in `backend/llm/solar.py` (or new file under `backend/llm/`) with comment `# Prompt v2: <rationale>`
2. Test against the 4 input cases (1 book / single genre / 5+ genres / extreme ratings)
3. Include before/after example outputs in PR description
4. If response shape changes (e.g., now returns JSON instead of markdown), coordinate with App track

## Testing Conventions

- **Framework**: stdlib `unittest` only — no pytest, no third-party deps
- **Location**: `backend/tests/test_<module>.py`
- **Per algorithm, cover at minimum**:
  - Empty / single-element edge case
  - Happy path (typical input)
  - Invariants (e.g. "sort is stable", "scores sum to ~1.0")
  - Boundary (smallest valid, largest practical)
- **Naming**: `test_<behavior_in_snake_case>` — describe the assertion, not the function
- **Run**: `cd backend && python -m unittest discover -s tests`
- **Required before merging algorithm PRs**: all tests pass locally + author has added at least one test for any new function

## Common Pitfalls

| Pitfall | Prevention |
|---|---|
| Korean text shows as `???` in Windows terminal | Run `chcp 65001` once per shell, or use VS Code terminal |
| Frontend can't reach backend (CORS error in console) | Verify `CORS(app)` is still present in `app.py` and backend is running on port 5000 |
| `UPSTAGE_API_KEY not set` error on `/api/recommendations` | `.env` must be in project root (not `backend/`); `load_dotenv()` walks up to find it |
| Algorithm module accidentally imports Flask | Algorithms must be pure — move any Flask logic into `app.py` |
| Two people push to same `feature/app-*` branch and one's commit disappears | Run `git pull --rebase origin <branch>` **before every push** |
| LLM call hangs forever | `solar.py` should pass `timeout=30` to `requests.post` |
| `.env` accidentally committed | Already gitignored. If a key leaks, rotate on Upstage immediately and force-push to remove from history |

## Definition of Done

A task is "done" when:

| Task type | Done means |
|---|---|
| **New algorithm** | Module + docstring with complexity + tests (4+ cases) + README mention + all tests green |
| **New API endpoint** | Route + input validation + README API table updated + manual curl test passes |
| **Frontend feature** | UI works in browser + `escapeHtml()` on user input + no console errors |
| **LLM prompt change** | Tested against the 4 input cases + before/after examples in PR description |
| **Bug fix** | Failing test added that reproduces the bug + fix makes it pass |
| **Refactor** | All existing tests still green + no behavior change + 1-line PR description explaining "why" |
| **Docs** | A teammate could follow the new instructions cold without asking questions |

**Universally required**:
- PR description explains the "why" in 1–3 sentences
- No new runtime dependencies without team agreement
- Branch follows naming convention (`feature/app-*`, `feature/llm-*`, `docs/*`, `fix/*`)

## Working with Ralph-style Loops

When using `/loop` or autonomous iteration (e.g. "keep working until X"):

- **Always include an explicit stop condition** — "stop when all tests pass", "stop when README updated", etc. Never open-ended.
- **Scope the goal narrowly** — one feature per loop. Don't say "build the whole BST module + 5 endpoints + UI" in one shot.
- **Reference this CLAUDE.md sections** in the goal — e.g. "follow the 'Adding a new algorithm module' pattern in CLAUDE.md"
- **Heavy loops eat shared rate limit** — coordinate in team chat before kicking off
- **Verify the result yourself** — read the diff, don't just trust "Claude said it's done"

## When in Doubt
- **Code style questions**: Match existing patterns in the repo
- **Architecture questions**: Keep it simple — this is a course project, not production
- **Algorithm choice**: Prefer ones explicitly taught in class (sorting, divide & conquer, greedy, DP, graph, hashing, BST/RBT/B-Tree)
- **Always**: Explain your changes clearly in PR descriptions so non-coding teammates (PM) can follow
