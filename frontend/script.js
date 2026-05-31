'use strict';

/* ──────────────────────────────────────────────────────────
   Mock backend — same apiFetch(path, options) contract as the
   live frontend. Used only when USE_MOCK = true (offline design
   preview / demo without a running backend). The real app runs
   against the Flask backend (USE_MOCK = false).
────────────────────────────────────────────────────────── */
const SEED_BOOKS = [
  { title: '해리포터와 마법사의 돌', author: 'J.K. 롤링',             genre: '판타지',   rating: 5 },
  { title: '사피엔스',              author: '유발 하라리',            genre: '인문',     rating: 4 },
  { title: '1984',                  author: '조지 오웰',              genre: 'SF',       rating: 5 },
  { title: '노르웨이의 숲',          author: '무라카미 하루키',         genre: '소설',     rating: 4 },
  { title: '셜록 홈즈의 모험',       author: '코난 도일',              genre: '추리',     rating: 5 },
  { title: '어린 왕자',             author: '생텍쥐페리',             genre: '소설',     rating: 4 },
  { title: '코스모스',              author: '칼 세이건',              genre: '과학',     rating: 3 },
  { title: '데미안',                author: '헤르만 헤세',            genre: '소설',     rating: 5 },
  { title: '반지의 제왕',           author: 'J.R.R. 톨킨',            genre: '판타지',   rating: 5 },
  { title: '듄',                    author: '프랭크 허버트',           genre: 'SF',       rating: 4 },
  { title: '그리고 아무도 없었다',    author: '애거사 크리스티',         genre: '추리',     rating: 5 },
  { title: '미움받을 용기',          author: '기시미 이치로·고가 후미타케', genre: '자기계발', rating: 4 },
  { title: '총, 균, 쇠',            author: '재레드 다이아몬드',        genre: '인문',     rating: 5 },
  { title: '나미야 잡화점의 기적',    author: '히가시노 게이고',         genre: '소설',     rating: 5 },
  { title: '채식주의자',            author: '한강',                   genre: '소설',     rating: 4 },
  { title: '살인자의 기억법',        author: '김영하',                 genre: '추리',     rating: 4 },
  { title: '로마인 이야기 1',        author: '시오노 나나미',           genre: '역사',     rating: 4 },
  { title: '7년의 밤',              author: '정유정',                 genre: '추리',     rating: 5 },
  { title: '위대한 개츠비',          author: 'F. 스콧 피츠제럴드',       genre: '소설',     rating: 4 },
  { title: '안나 카레니나',          author: '톨스토이',               genre: '소설',     rating: 5 },
];

const REC_POOL = [
  { title: '멋진 신세계',       author: '올더스 헉슬리',    genre: 'SF',
    reason: '1984 재밌게 봤다면 이것도 좋아할 거예요. 이번엔 통제된 행복이라는 다른 결의 디스토피아예요.' },
  { title: '총, 균, 쇠',        author: '재레드 다이아몬드', genre: '인문',
    reason: '사피엔스 다음에 보기 딱 좋은 책. 문명의 운명이 왜 갈렸는지를 지리로 풀어내요.' },
  { title: '반지의 제왕',       author: 'J.R.R. 톨킨',      genre: '판타지',
    reason: '해리포터 세계관을 즐겼다면, 모든 판타지의 원형이 된 대서사시로 넘어갈 차례.' },
  { title: '그리고 아무도 없었다', author: '애거사 크리스티',   genre: '추리',
    reason: '셜록 홈즈 추리가 짜릿했다면, 미스터리 여왕의 완벽한 밀실 한 편을 추천해요.' },
  { title: '해변의 카프카',      author: '무라카미 하루키',   genre: '소설',
    reason: '노르웨이의 숲 여운이 남았다면, 무라카미 특유의 몽환적인 이야기를 한 번 더.' },
  { title: '시간의 역사',        author: '스티븐 호킹',       genre: '과학',
    reason: '코스모스에서 우주에 빠졌다면, 빅뱅부터 블랙홀까지 더 깊이 들어가 볼 차례예요.' },
];

const GENRE_KEYWORDS = [
  [/(마법|판타지|반지|마녀|드래곤|용)/, '판타지'],
  [/(우주|로봇|미래|행성|sf|에이아이)/i, 'SF'],
  [/(살인|탐정|추리|미스터리|사건|범죄)/, '추리'],
  [/(과학|물리|진화|생물)/, '과학'],
  [/(역사|로마|왕조|전쟁사)/, '역사'],
  [/(철학|인간|문명|사회|심리)/, '인문'],
  [/(습관|성공|부자|마인드|성장|일잘|용기)/, '자기계발'],
];
function classifyGenre(title, author) {
  const hay = (title + ' ' + author);
  for (const [re, g] of GENRE_KEYWORDS) if (re.test(hay)) return g;
  return '소설';
}

function levenshtein(a, b) {
  a = a.toLowerCase(); b = b.toLowerCase();
  const m = a.length, n = b.length;
  const d = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
  for (let j = 0; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      d[i][j] = Math.min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + (a[i-1] === b[j-1] ? 0 : 1));
  return d[m][n];
}

const MOCK = {
  books: SEED_BOOKS.map(b => ({ ...b })),
  recCursor: 0,
  delay(ms) { return new Promise(r => setTimeout(r, ms)); },
  async handle(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const [route, query] = path.split('?');
    await this.delay(method === 'GET' && route === '/recommendations' ? 800 : 160);

    if (route === '/books' && method === 'GET') return this.books.map(b => ({ ...b }));

    if (route === '/books' && method === 'POST') {
      const body = JSON.parse(options.body || '{}');
      const title = (body.title || '').trim();
      const author = (body.author || '').trim();
      if (this.books.some(b => b.title === title)) { const e = new Error('이미 등록된 책입니다'); e.status = 409; throw e; }
      const book = { title, author, genre: classifyGenre(title, author), rating: body.rating };
      this.books.unshift(book);
      // Match the live backend response shape: { message, book, ... }.
      return { message: '책이 추가되었습니다', book: { ...book }, genre_auto_classified: true };
    }

    if (route.startsWith('/books/') && method === 'DELETE') {
      const idx = parseInt(route.split('/')[2], 10);
      if (!Number.isNaN(idx)) this.books.splice(idx, 1);
      return { ok: true };
    }

    if (route === '/search' && method === 'GET') {
      const q = decodeURIComponent((query || '').replace(/^q=/, '')).trim();
      const exact = this.books.filter(b => b.title.toLowerCase().includes(q.toLowerCase()));
      if (exact.length) return { results: exact, matched_by: 'exact', did_you_mean: null };
      let best = null, bestD = Infinity;
      for (const b of this.books) { const d = levenshtein(q, b.title); if (d < bestD) { bestD = d; best = b; } }
      if (best && bestD <= Math.max(2, Math.ceil(best.title.length * 0.5)))
        return { results: [best], matched_by: 'fuzzy', did_you_mean: best.title };
      return { results: [], matched_by: 'none', did_you_mean: null };
    }

    if (route === '/recommendations' && method === 'GET') {
      const counts = {};
      for (const b of this.books) counts[b.genre] = (counts[b.genre] || 0) + 1;
      const top = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3).map(e => e[0]);
      const picks = [];
      for (let i = 0; i < 4; i++) picks.push(REC_POOL[(this.recCursor + i) % REC_POOL.length]);
      this.recCursor = (this.recCursor + 4) % REC_POOL.length;
      return { recommendations: picks.map(r => ({ ...r })), top_genres: top.length ? top : ['소설'] };
    }

    const e = new Error('알 수 없는 요청입니다'); e.status = 404; throw e;
  }
};

/* ── API layer ──────────────────────────────────────────── */
// USE_MOCK=true 면 내장 mock 데이터로 동작합니다 (백엔드 없이 바로 미리보기).
// 실제 백엔드(Flask, localhost:5000)에 연결하려면 USE_MOCK 를 false 로 둡니다.
const API_BASE = 'http://localhost:5000/api';
const USE_MOCK = false;

async function apiFetch(path, options = {}) {
  if (USE_MOCK) return MOCK.handle(path, options);
  const res = await fetch(API_BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}
function escapeHtml(str) {
  return String(str).replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}
function renderStars(rating) { return '★'.repeat(rating) + '☆'.repeat(5 - rating); }

/* ── Genre colour coding ── */
const GENRE_HUE = { '판타지': 290, 'SF': 250, '소설': 160, '추리': 350, '인문': 40, '과학': 210, '자기계발': 130, '역사': 25, '에세이': 80, '기타': 60 };
function genreStyle(genre) {
  const h = GENRE_HUE[genre] != null ? GENRE_HUE[genre] : 60;
  return { cover: `oklch(0.64 0.13 ${h})`, chipBg: `oklch(0.95 0.035 ${h})`, chipFg: `oklch(0.45 0.11 ${h})` };
}

/* ── Per-book cover colour — hashed so all spines differ
   (wide hue range + mixed pastel / medium lightness & chroma).
   Used as the fallback when a book has no Google Books cover. ── */
function hashStr(s) { let h = 0; for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) | 0; return Math.abs(h); }
function coverColor(book) {
  const h = hashStr(book.title + '·' + book.author);
  const hue = h % 360;
  const light = [0.60, 0.66, 0.72, 0.78][(h >> 3) % 4];
  const chroma = [0.055, 0.085, 0.115, 0.145][(h >> 6) % 4];
  return `oklch(${light} ${chroma} ${hue})`;
}

function renderBookCard(book, index) {
  const gs = genreStyle(book.genre);
  const del = (typeof index === 'number')
    ? `<button class="del-btn" data-index="${index}" aria-label="삭제"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14"/></svg></button>`
    : '';
  // Google Books cover (cover_url) overlays the colour block. If the image
  // fails to load, onerror removes it and the colour block shows through.
  const coverImg = book.cover_url
    ? `<img class="cover-img" src="${escapeHtml(book.cover_url)}" alt="" loading="lazy" onerror="this.remove()">`
    : '';
  return `
    <article class="book-item">
      <div class="cover" style="--cv:${coverColor(book)}">${coverImg}</div>
      <div class="bi-body">
        <div class="bi-title">${escapeHtml(book.title)}</div>
        <div class="bi-author">${escapeHtml(book.author)}</div>
        <div class="bi-meta">
          <span class="chip" style="--chip-bg:${gs.chipBg};--chip-fg:${gs.chipFg}">${escapeHtml(book.genre)}</span>
          <span class="stars">${renderStars(book.rating)}</span>
        </div>
      </div>
      ${del}
    </article>`;
}

/* ── Toast ── */
function toast(message, type = 'ok') {
  const host = document.getElementById('toast-host');
  const el = document.createElement('div');
  el.className = 'toast' + (type === 'warn' ? ' warn' : '');
  el.innerHTML = `<span class="mk"></span><span>${escapeHtml(message)}</span>`;
  host.appendChild(el);
  setTimeout(() => { el.classList.add('out'); el.addEventListener('animationend', () => el.remove(), { once: true }); }, 2500);
}

/* ── Stats ── */
function updateStats(books) {
  const countEl = document.getElementById('stat-count');
  const avgEl = document.getElementById('stat-avg');
  const genreEl = document.getElementById('stat-genre');
  const listCount = document.getElementById('list-count');
  if (!books || !books.length) {
    countEl.textContent = '0'; avgEl.textContent = '—'; genreEl.textContent = '—';
    if (listCount) listCount.textContent = '0'; return;
  }
  countEl.textContent = books.length;
  avgEl.textContent = (books.reduce((s, b) => s + b.rating, 0) / books.length).toFixed(1);
  const counts = {};
  for (const b of books) counts[b.genre] = (counts[b.genre] || 0) + 1;
  let topGenre = '—', best = 0;
  for (const [genre, n] of Object.entries(counts)) if (n > best) { best = n; topGenre = genre; }
  genreEl.textContent = topGenre;
  if (listCount) listCount.textContent = books.length;
}

/* ──────────────────────────────────────────────────────────
   Shelf: genre filters + sort + progressive (8-at-a-time)
   loading via IntersectionObserver inside a bounded scroll box.
────────────────────────────────────────────────────────── */
const PAGE = 8;
const GENRE_ORDER = ['판타지', 'SF', '소설', '추리', '인문', '과학', '자기계발', '역사', '에세이', '기타'];
let ALL = [];                 // canonical books, each tagged with _idx
let activeGenres = new Set(); // empty = 전체
let sortKey = 'recent';
let shown = PAGE;
let shelfObserver = null;

function filteredSorted() {
  let arr = ALL.slice();
  if (activeGenres.size) arr = arr.filter(b => activeGenres.has(b.genre));
  if (sortKey === 'rating') arr.sort((a, b) => b.rating - a.rating || a._idx - b._idx);
  else if (sortKey === 'title') arr.sort((a, b) => a.title.localeCompare(b.title, 'ko'));
  else arr.sort((a, b) => a._idx - b._idx); // recent: canonical front = newest
  return arr;
}

function buildFilterChips() {
  const host = document.getElementById('genre-filters');
  const present = new Set(ALL.map(b => b.genre));
  const ordered = GENRE_ORDER.filter(g => present.has(g));
  for (const g of present) if (!ordered.includes(g)) ordered.push(g);
  // drop any active filters no longer present
  for (const g of [...activeGenres]) if (!present.has(g)) activeGenres.delete(g);
  const chips = [`<button class="gchip${activeGenres.size === 0 ? ' active' : ''}" data-genre="__all">전체</button>`]
    .concat(ordered.map(g => `<button class="gchip${activeGenres.has(g) ? ' active' : ''}" data-genre="${escapeHtml(g)}">${escapeHtml(g)}</button>`));
  host.innerHTML = chips.join('');
}

function renderShelf() {
  const listEl = document.getElementById('book-list');
  const endEl = document.getElementById('shelf-end');
  const sentinel = document.getElementById('scroll-sentinel');
  const arr = filteredSorted();
  const slice = arr.slice(0, shown);
  listEl.innerHTML = slice.length
    ? slice.map(b => renderBookCard(b, b._idx)).join('')
    : '<div class="empty-state"><b>해당하는 책이 없어요</b>다른 장르를 골라보세요</div>';

  const done = shown >= arr.length;
  if (done && arr.length) {
    endEl.hidden = false;
    endEl.textContent = `📚 모든 책을 다 봤어요 (총 ${arr.length}권)`;
    sentinel.style.display = 'none';
  } else {
    endEl.hidden = true;
    sentinel.style.display = arr.length ? 'block' : 'none';
  }
}

function resetShelf() {
  shown = PAGE;
  const sc = document.getElementById('book-scroll');
  if (sc) sc.scrollTop = 0;
  renderShelf();
}

function setupObserver() {
  if (shelfObserver) return;
  const root = document.getElementById('book-scroll');
  const sentinel = document.getElementById('scroll-sentinel');
  shelfObserver = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (!e.isIntersecting) continue;
      const total = filteredSorted().length;
      if (shown < total) { shown = Math.min(shown + PAGE, total); renderShelf(); }
    }
  }, { root, rootMargin: '0px 0px 140px 0px', threshold: 0 });
  shelfObserver.observe(sentinel);

  // Fallback: some embedded webviews don't fire IO on programmatic
  // scroll, so also watch the scroll container directly.
  root.addEventListener('scroll', () => {
    if (root.scrollTop + root.clientHeight >= root.scrollHeight - 140) {
      const total = filteredSorted().length;
      if (shown < total) { shown = Math.min(shown + PAGE, total); renderShelf(); }
    }
  });
}

// filter chip clicks
document.getElementById('genre-filters').addEventListener('click', (e) => {
  const chip = e.target.closest('.gchip');
  if (!chip) return;
  const g = chip.dataset.genre;
  if (g === '__all') activeGenres.clear();
  else { activeGenres.has(g) ? activeGenres.delete(g) : activeGenres.add(g); }
  buildFilterChips();
  resetShelf();
});
// sort change
document.getElementById('sort-select').addEventListener('change', (e) => {
  sortKey = e.target.value;
  resetShelf();
});
// delete (delegated on the scroll container so it survives re-renders)
document.getElementById('book-scroll').addEventListener('click', async (e) => {
  const btn = e.target.closest('.del-btn');
  if (!btn) return;
  const idx = parseInt(btn.dataset.index, 10);
  if (Number.isNaN(idx)) return;
  try { await apiFetch('/books/' + idx, { method: 'DELETE' }); await loadBooks(); toast('책장에서 뺐어요'); }
  catch (err) { toast('삭제 실패: ' + err.message, 'warn'); }
});

async function loadBooks(opts = {}) {
  try {
    const books = await apiFetch('/books');
    // Prefer the backend's _idx (original storage index) so deletes hit the
    // right book even though GET returns a rating-sorted list. Fall back to
    // the array position only if the backend didn't supply it (e.g. mock).
    ALL = books.map((b, i) => ({ ...b, _idx: b._idx ?? i }));
    updateStats(books);
    buildFilterChips();
    if (opts.reset) shown = PAGE;
    renderShelf();
    setupObserver();
  } catch (e) {
    document.getElementById('book-list').innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
    updateStats([]);
  }
}

/* ── Star rating ── */
const starPicker = document.getElementById('star-picker');
const ratingInput = document.getElementById('rating');
const starButtons = starPicker ? Array.from(starPicker.querySelectorAll('.star')) : [];
function paintStars(value) { starButtons.forEach(s => s.classList.toggle('filled', Number(s.dataset.value) <= value)); }
function selectedRating() { return parseInt(ratingInput.value, 10) || 0; }
function resetStarPicker() { ratingInput.value = ''; paintStars(0); }
starButtons.forEach(star => {
  const v = Number(star.dataset.value);
  star.addEventListener('mouseenter', () => paintStars(v));
  star.addEventListener('focus', () => paintStars(v));
  star.addEventListener('click', () => { ratingInput.value = String(v); paintStars(v); });
});
if (starPicker) {
  starPicker.addEventListener('mouseleave', () => paintStars(selectedRating()));
  starPicker.addEventListener('blur', () => paintStars(selectedRating()), true);
}

/* ── Add book ── */
document.getElementById('book-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const rating = selectedRating();
  if (!rating) { toast('별점을 먼저 골라주세요', 'warn'); return; }
  const body = { title: document.getElementById('title').value.trim(), author: document.getElementById('author').value.trim(), rating };
  try {
    const res = await apiFetch('/books', { method: 'POST', body: JSON.stringify(body) });
    const saved = res.book || res;  // live backend wraps in { book }; mock returns same shape
    e.target.reset(); resetStarPicker();
    await loadBooks({ reset: true });
    toast(`${saved.genre} · '${saved.title}' 추가 완료`);
  } catch (err) {
    if (err.message === '이미 등록된 책입니다') toast('이미 책장에 있는 책이에요', 'warn');
    else toast('오류: ' + err.message, 'warn');
  }
});

/* ── Search ── */
document.getElementById('search-btn').addEventListener('click', async () => {
  const q = document.getElementById('search-input').value.trim();
  const resultsEl = document.getElementById('search-results');
  if (!q) { resultsEl.innerHTML = ''; return; }
  try {
    const data = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
    const cards = data.results.map(b => renderBookCard(b)).join('');
    if (data.matched_by === 'fuzzy')
      resultsEl.innerHTML = `<div class="did-you-mean">혹시 <strong>'${escapeHtml(data.did_you_mean)}'</strong> 찾으세요?</div>` + cards;
    else if (data.matched_by === 'exact') resultsEl.innerHTML = cards;
    else resultsEl.innerHTML = `<div class="empty-state"><b>검색 결과가 없어요</b>'${escapeHtml(q)}'와 비슷한 책을 못 찾았어요</div>`;
  } catch (e) { resultsEl.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`; }
});
document.getElementById('search-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') document.getElementById('search-btn').click();
});

/* ── Recommendations ── */
function scrollToRecs() {
  const el = document.getElementById('recommendations-section');
  const y = el.getBoundingClientRect().top + window.scrollY - 16;
  window.scrollTo({ top: y, behavior: 'smooth' });
}
async function loadRecs() {
  const recsEl = document.getElementById('recommendations');
  recsEl.className = 'loading'; recsEl.textContent = '추천 고르는 중…';
  scrollToRecs();
  try {
    const data = await apiFetch('/recommendations');
    recsEl.className = '';
    // The live backend returns { recommendations: [...] } on success, but
    // { recommendations: { error: "..." } } when the LLM call fails (PR #21),
    // and a top-level { error } for empty libraries (surfaced via apiFetch throw).
    const recs = data.recommendations;
    if (data.error || !Array.isArray(recs)) {
      const msg = data.error || (recs && recs.error) || '추천을 받지 못했어요. 잠시 후 다시 시도해주세요.';
      recsEl.innerHTML = `<p class="error">${escapeHtml(msg)}</p>` +
        `<button class="btn btn-mini recs-again" id="recs-again">🔄 다시 추천 받기</button>`;
      return;
    }
    const tags = (data.top_genres || []).map(g => `<span class="tg">${escapeHtml(g)}</span>`).join('');
    const cards = recs.map((r) => {
      const gs = genreStyle(r.genre);
      return `
        <div class="rec-card">
          <div class="rec-top">
            <span class="rec-title">${escapeHtml(r.title)}</span>
            <span class="rec-author">${escapeHtml(r.author)}</span>
            <span class="chip" style="--chip-bg:${gs.chipBg};--chip-fg:${gs.chipFg}">${escapeHtml(r.genre)}</span>
          </div>
          <p class="rec-reason">${escapeHtml(r.reason)}</p>
        </div>`;
    }).join('');
    recsEl.innerHTML =
      `<div class="rec-intro">요즘 ${tags} 많이 보셨네요. 이런 책 어때요?</div>` +
      `<div class="rec-list">${cards}</div>` +
      `<button class="btn btn-mini recs-again" id="recs-again">🔄 다시 추천 받기</button>`;
  } catch (e) { recsEl.className = 'error'; recsEl.textContent = '오류: ' + e.message; }
}
document.getElementById('get-recs-btn').addEventListener('click', loadRecs);
document.getElementById('recommendations').addEventListener('click', (e) => {
  if (e.target.closest('#recs-again')) loadRecs();
});

loadBooks();
