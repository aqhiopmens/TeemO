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

function renderBookCard(book) {
  return `
    <div class="book-card">
      <div class="title">${escapeHtml(book.title)}</div>
      <div class="meta">
        ${escapeHtml(book.author)} &middot; ${escapeHtml(book.genre)}
        <span class="stars">${renderStars(book.rating)}</span>
      </div>
    </div>`;
}

async function loadBooks() {
  const listEl = document.getElementById('book-list');
  try {
    const books = await apiFetch('/books');
    listEl.innerHTML = books.length
      ? books.map(renderBookCard).join('')
      : '<p class="loading">아직 추가된 책이 없습니다.</p>';
  } catch (e) {
    listEl.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
  }
}

// Add book
document.getElementById('book-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const body = {
    title: document.getElementById('title').value.trim(),
    author: document.getElementById('author').value.trim(),
    rating: parseInt(document.getElementById('rating').value, 10),
  };
  try {
    await apiFetch('/books', { method: 'POST', body: JSON.stringify(body) });
    e.target.reset();
    await loadBooks();
  } catch (err) {
    alert('오류: ' + err.message);
  }
});

// Search books
document.getElementById('search-btn').addEventListener('click', async () => {
  const q = document.getElementById('search-input').value.trim();
  const resultsEl = document.getElementById('search-results');
  if (!q) { resultsEl.innerHTML = ''; return; }
  try {
    const data = await apiFetch(`/search?q=${encodeURIComponent(q)}`);
    const cards = data.results.map(renderBookCard).join('');
    if (data.matched_by === 'fuzzy') {
      resultsEl.innerHTML =
        `<p class="loading">혹시 '${escapeHtml(data.did_you_mean)}'를 찾으셨나요?</p>` + cards;
    } else if (data.matched_by === 'exact') {
      resultsEl.innerHTML = cards;
    } else {
      resultsEl.innerHTML = '<p class="loading">결과 없음</p>';
    }
  } catch (e) {
    resultsEl.innerHTML = `<p class="error">${escapeHtml(e.message)}</p>`;
  }
});

// Get AI recommendations
document.getElementById('get-recs-btn').addEventListener('click', async () => {
  const recsEl = document.getElementById('recommendations');
  recsEl.textContent = '취향을 분석하는 중입니다…';
  recsEl.className = 'loading';
  try {
    const data = await apiFetch('/recommendations');
    recsEl.className = '';
    recsEl.innerHTML =
      `<strong>선호 장르:</strong> ${escapeHtml(data.top_genres.join(', '))}\n\n` +
      escapeHtml(data.recommendations);
  } catch (e) {
    recsEl.className = 'error';
    recsEl.textContent = '오류: ' + e.message;
  }
});

loadBooks();
