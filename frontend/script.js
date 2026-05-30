const API_BASE = 'http://localhost:5000/api';

async function apiFetch(path, options = {}) {
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

function renderStars(rating) {
  return '★'.repeat(rating) + '☆'.repeat(5 - rating);
}

function renderBookCard(book, index) {
  // Delete button is only shown when an index is provided — search results
  // pass no index so users can't delete the wrong book via stale list position.
  const deleteBtn = (typeof index === 'number')
    ? `<button class="delete-btn" data-index="${index}" aria-label="삭제">×</button>`
    : '';
  return `
    <div class="book-card">
      ${deleteBtn}
      <div class="title">${escapeHtml(book.title)}</div>
      <div class="meta">
        <span class="author">${escapeHtml(book.author)}</span>
        <span class="genre-badge">${escapeHtml(book.genre)}</span>
        <span class="stars">${renderStars(book.rating)}</span>
      </div>
    </div>`;
}

// ── Stats dashboard ──────────────────────────────────────────
// Computes count / average rating / most-frequent genre on the
// frontend from the same /api/books payload the list already uses.
function updateStats(books) {
  const countEl = document.getElementById('stat-count');
  const avgEl = document.getElementById('stat-avg');
  const genreEl = document.getElementById('stat-genre');

  if (!books || !books.length) {
    countEl.textContent = '—';
    avgEl.textContent = '—';
    genreEl.textContent = '—';
    return;
  }

  countEl.textContent = books.length;
  avgEl.textContent = (books.reduce((s, b) => s + b.rating, 0) / books.length).toFixed(1);

  const counts = {};
  for (const b of books) {
    counts[b.genre] = (counts[b.genre] || 0) + 1;
  }
  let topGenre = '—';
  let best = 0;
  for (const [genre, n] of Object.entries(counts)) {
    if (n > best) { best = n; topGenre = genre; }
  }
  genreEl.textContent = topGenre;
}

async function loadBooks() {
  const listEl = document.getElementById('book-list');
  try {
    const books = await apiFetch('/books');
    listEl.innerHTML = books.length
      ? books.map((b, i) => renderBookCard(b, i)).join('')
      : '<p class="empty-state">아직 추가된 책이 없어요.<br>위에서 첫 책을 추가해보세요!</p>';
    updateStats(books);

    // One-time event delegation for delete buttons.
    if (!listEl.dataset.bound) {
      listEl.addEventListener('click', async (e) => {
        const btn = e.target.closest('.delete-btn');
        if (!btn) return;
        const idx = parseInt(btn.dataset.index, 10);
        if (Number.isNaN(idx)) return;
        if (!confirm('이 책을 삭제할까요?')) return;
        try {
          await apiFetch('/books/' + idx, { method: 'DELETE' });
          await loadBooks();
        } catch (err) {
          alert('삭제 실패: ' + err.message);
        }
      });
      listEl.dataset.bound = '1';
    }
  } catch (e) {
    listEl.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
    updateStats([]);
  }
}

// ── Clickable star rating input ──────────────────────────────
const starPicker = document.getElementById('star-picker');
const ratingInput = document.getElementById('rating');
const starButtons = starPicker ? Array.from(starPicker.querySelectorAll('.star')) : [];

function paintStars(value) {
  starButtons.forEach(s => s.classList.toggle('filled', Number(s.dataset.value) <= value));
}

function selectedRating() {
  return parseInt(ratingInput.value, 10) || 0;
}

function resetStarPicker() {
  ratingInput.value = '';
  paintStars(0);
}

starButtons.forEach(star => {
  const v = Number(star.dataset.value);
  star.addEventListener('mouseenter', () => paintStars(v));
  star.addEventListener('focus', () => paintStars(v));
  star.addEventListener('click', () => {
    ratingInput.value = String(v);
    paintStars(v);
  });
});
if (starPicker) {
  starPicker.addEventListener('mouseleave', () => paintStars(selectedRating()));
  starPicker.addEventListener('blur', () => paintStars(selectedRating()), true);
}

// ── Add book ─────────────────────────────────────────────────
document.getElementById('book-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const rating = selectedRating();
  if (!rating) {
    alert('별점을 선택해주세요 ⭐');
    return;
  }
  const body = {
    title: document.getElementById('title').value.trim(),
    author: document.getElementById('author').value.trim(),
    rating,
  };
  try {
    await apiFetch('/books', { method: 'POST', body: JSON.stringify(body) });
    e.target.reset();
    resetStarPicker();
    await loadBooks();
  } catch (err) {
    if (err.message === '이미 등록된 책입니다') {
      alert('📚 ' + err.message);
    } else {
      alert('오류: ' + err.message);
    }
  }
});

// ── Search books ─────────────────────────────────────────────
document.getElementById('search-btn').addEventListener('click', async () => {
  const q = document.getElementById('search-input').value.trim();
  const resultsEl = document.getElementById('search-results');
  if (!q) { resultsEl.innerHTML = ''; return; }
  try {
    const data = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
    // No index passed → no delete button on search-result cards
    // (their position doesn't match the underlying user_books index).
    const cards = data.results.map(b => renderBookCard(b)).join('');
    if (data.matched_by === 'fuzzy') {
      resultsEl.innerHTML =
        `<div class="did-you-mean">혹시 <strong>'${escapeHtml(data.did_you_mean)}'</strong>를 찾으셨나요?</div>` + cards;
    } else if (data.matched_by === 'exact') {
      resultsEl.innerHTML = cards;
    } else {
      resultsEl.innerHTML = `<p class="empty-state">'${escapeHtml(q)}'에 대한 검색 결과가 없어요</p>`;
    }
  } catch (e) {
    resultsEl.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
  }
});

// Enter key triggers search too
document.getElementById('search-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') document.getElementById('search-btn').click();
});

// ── AI recommendations ───────────────────────────────────────
document.getElementById('get-recs-btn').addEventListener('click', async () => {
  const recsEl = document.getElementById('recommendations');
  recsEl.className = 'loading';
  recsEl.textContent = 'AI가 취향을 분석 중이에요…';
  try {
    const data = await apiFetch('/recommendations');
    recsEl.className = '';
    recsEl.innerHTML = `
      <div class="rec-card">
        <div class="rec-header">✨ AI가 골라드린 책</div>
        <div class="rec-body">
          <p class="rec-genres"><span>선호 장르</span> ${escapeHtml(data.top_genres.join(', '))}</p>
          <div class="rec-text">${escapeHtml(data.recommendations)}</div>
        </div>
      </div>`;
  } catch (e) {
    recsEl.className = 'error';
    recsEl.textContent = '오류: ' + e.message;
  }
});

loadBooks();
