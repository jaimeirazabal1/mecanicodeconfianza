const API = '';
let currentUser = null;

function getToken() {
  const match = document.cookie.match(/(^| )token=([^;]+)/);
  return match ? match[2] : null;
}

async function api(path, opts = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...opts.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...opts, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error del servidor' }));
    throw new Error(err.detail || 'Error');
  }
  return res.json();
}

async function apiFormData(path, formData) {
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { method: 'POST', headers, body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Error' }));
    throw new Error(err.detail || 'Error');
  }
  return res.json();
}

function setCookie(name, value) {
  document.cookie = `${name}=${value};path=/;max-age=${30*24*60*60}`;
}

function toggleMenu() {
  document.querySelector('.nav-links').classList.toggle('open');
}

function showStars(rating) {
  const full = Math.floor(rating);
  const half = rating % 1 >= 0.5 ? 1 : 0;
  const empty = 5 - full - half;
  return '★'.repeat(full) + (half ? '½' : '') + '☆'.repeat(empty);
}

function escapeHtml(text) {
  const d = document.createElement('div');
  d.textContent = text;
  return d.innerHTML;
}

function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

// ---- AUTH ----
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('loginError');
    try {
      const data = await api('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email: document.getElementById('email').value, password: document.getElementById('password').value }),
      });
      setCookie('token', data.access_token);
      window.location.href = '/';
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
    }
  });
}

const registerForm = document.getElementById('registerForm');
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('registerError');
    try {
      const data = await api('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          name: document.getElementById('name').value,
          email: document.getElementById('email').value,
          phone: document.getElementById('phone').value,
          password: document.getElementById('password').value,
          role: document.getElementById('role').value,
        }),
      });
      setCookie('token', data.access_token);
      window.location.href = '/';
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
    }
  });
}

// ---- SEARCH ----
const searchForm = document.getElementById('searchForm');
function loadSearch() {
  const params = new URLSearchParams(window.location.search);
  const q = params.get('q') || '';
  const location = params.get('location') || '';
  if (q && document.getElementById('searchQuery')) document.getElementById('searchQuery').value = q;
  if (location && document.getElementById('searchLocation')) document.getElementById('searchLocation').value = location;
  doSearch();
}

async function doSearch(page = 1) {
  const container = document.getElementById('results');
  if (!container) return;
  container.innerHTML = '<div class="loading">Buscando...</div>';

  const q = document.getElementById('searchQuery')?.value || '';
  const location = document.getElementById('searchLocation')?.value || '';
  const sort = document.getElementById('searchSort')?.value || 'rating';
  const available = document.getElementById('filterAvailable')?.checked || false;
  const activeSpecialty = document.querySelector('.filter-chip.active');
  const specialty = activeSpecialty?.dataset?.specialty || '';

  try {
    const params = new URLSearchParams({ q, location, sort, page: String(page), available: String(available), specialty });
    const data = await api(`/api/mechanics?${params}`);

    if (data.mechanics.length === 0) {
      container.innerHTML = '<div class="empty-state">No se encontraron mecánicos. Intenta con otros términos de búsqueda.</div>';
      return;
    }

    container.innerHTML = data.mechanics.map(m => `
      <a href="/mecanicos/${m.id}" class="mechanic-card">
        <div class="mechanic-card-body">
          <div class="mechanic-card-header">
            <div class="mechanic-avatar">${m.user_avatar ? `<img src="${m.user_avatar}" alt="">` : '🔧'}</div>
            <div class="mechanic-info">
              <h3>${escapeHtml(m.business_name || m.user_name || 'Mecánico')}</h3>
              <div class="mechanic-specialties">
                ${m.specialties.slice(0, 3).map(s => `<span class="spec-tag">${escapeHtml(s)}</span>`).join('')}
              </div>
            </div>
          </div>
          <div class="mechanic-stats">
            <span class="stars">${showStars(m.avg_rating)} ${m.avg_rating > 0 ? m.avg_rating : '—'}</span>
            <span>📝 ${m.review_count} reseñas</span>
            <span>📅 ${m.years_experience} años</span>
          </div>
          ${m.location ? `<div class="mechanic-location">📍 ${escapeHtml(m.location)}</div>` : ''}
          ${m.description ? `<div class="mechanic-description">${escapeHtml(m.description.substring(0, 120))}${m.description.length > 120 ? '...' : ''}</div>` : ''}
          <div class="${m.available ? 'mechanic-available' : 'mechanic-unavailable'}">${m.available ? '✅ Disponible' : '❌ No disponible'}</div>
        </div>
      </a>
    `).join('');

    const totalPages = Math.ceil(data.total / 20);
    const pagination = document.getElementById('pagination');
    if (totalPages > 1) {
      pagination.innerHTML = Array.from({ length: Math.min(totalPages, 10) }, (_, i) =>
        `<button class="page-btn ${i + 1 === page ? 'active' : ''}" onclick="doSearch(${i + 1})">${i + 1}</button>`
      ).join('');
    } else {
      pagination.innerHTML = '';
    }
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

if (searchForm) {
  searchForm.addEventListener('submit', (e) => { e.preventDefault(); doSearch(); });
  document.addEventListener('DOMContentLoaded', () => {
    loadSearch();
    loadSpecialties();
  });
}

async function loadSpecialties() {
  const container = document.getElementById('specialtyFilters');
  if (!container) return;
  try {
    const specs = await api('/api/specialties');
    specs.forEach(s => {
      const btn = document.createElement('button');
      btn.className = 'filter-chip';
      btn.dataset.specialty = s.name;
      btn.textContent = s.name;
      btn.onclick = () => { btn.classList.toggle('active'); doSearch(); };
      container.appendChild(btn);
    });
  } catch (e) {}
}

if (document.getElementById('filterAvailable')) {
  document.getElementById('filterAvailable').addEventListener('change', () => doSearch());
}
if (document.getElementById('searchSort')) {
  document.getElementById('searchSort').addEventListener('change', () => doSearch());
}

// ---- MECHANIC DETAIL ----
async function loadMechanicDetail() {
  const container = document.getElementById('mechanicDetail');
  if (!container) return;
  const mechanicId = container.closest('.mechanic-detail-page')?.dataset?.mechanicId || window.location.pathname.split('/').pop();

  try {
    const m = await api(`/api/mechanics/${mechanicId}`);
    const token = getToken();
    let canReview = !!token;

    container.innerHTML = `
      <div class="mechanic-detail-header">
        <div class="mechanic-detail-avatar">${m.user_avatar ? `<img src="${m.user_avatar}" alt="">` : '🔧'}</div>
        <div class="mechanic-detail-info">
          <h1>${escapeHtml(m.business_name || m.user_name || 'Mecánico')} ${m.verified ? '<span class="verified-badge">✅ Verificado</span>' : ''}</h1>
          ${m.location ? `<p>📍 ${escapeHtml(m.location)}</p>` : ''}
          <div class="mechanic-detail-stats">
            <div class="stat-item"><span class="stat-value stars">${m.avg_rating > 0 ? m.avg_rating : '—'}</span><span class="stat-label">${showStars(m.avg_rating)}</span></div>
            <div class="stat-item"><span class="stat-value">${m.review_count}</span><span class="stat-label">Reseñas</span></div>
            <div class="stat-item"><span class="stat-value">${m.years_experience}</span><span class="stat-label">Años exp.</span></div>
            <div class="stat-item"><span class="stat-value">${m.available ? '✅' : '❌'}</span><span class="stat-label">${m.available ? 'Disponible' : 'No disponible'}</span></div>
          </div>
          ${m.description ? `<p class="mechanic-detail-desc">${escapeHtml(m.description)}</p>` : ''}
          <div class="mechanic-specialties">${m.specialties.map(s => `<span class="spec-tag">${escapeHtml(s)}</span>`).join(' ')}</div>
          <div class="mechanic-contact">
            ${token ? `<a href="/mensajes/${m.user_id}" class="btn btn-primary">💬 Contactar</a>` : `<a href="/login" class="btn btn-primary">💬 Inicia sesión para contactar</a>`}
            ${m.phone_visible && m.user_phone ? `<a href="tel:${m.user_phone}" class="btn btn-outline">📞 ${escapeHtml(m.user_phone)}</a>` : ''}
          </div>
        </div>
      </div>
      <div class="reviews-section">
        <h3>Reseñas ${m.review_count > 0 ? `(${m.review_count})` : ''}</h3>
        ${canReview ? `
          <form id="reviewForm" class="auth-form" style="margin-bottom:1.5rem;padding:1rem;background:var(--surface-alt);border-radius:var(--radius-sm)">
            <div class="form-group">
              <label>Tu calificación</label>
              <div class="star-input">
                ${[1,2,3,4,5].map(i => `<span class="star-option" data-value="${i}" onclick="setRating(${i})">☆</span>`).join('')}
                <span id="selectedRating" style="margin-left:.5rem;font-weight:600">0</span>
              </div>
            </div>
            <div class="form-group">
              <label>Comentario</label>
              <textarea id="reviewComment" class="form-input" rows="3" placeholder="Cuenta tu experiencia..."></textarea>
            </div>
            <div id="reviewError" class="form-error hidden"></div>
            <button type="submit" class="btn btn-primary">Enviar reseña</button>
          </form>
        ` : ''}
        <div id="reviewsList">${m.review_count > 0 ? '' : '<p class="empty-state">Sin reseñas aún. ¡Sé el primero!</p>'}</div>
      </div>
      ${m.photos.length > 0 ? `
        <div class="reviews-section">
          <h3>Trabajos del mecánico</h3>
          <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem">
            ${m.photos.map(p => `<img src="${p}" style="width:100%;border-radius:var(--radius-sm);object-fit:cover;aspect-ratio:1">`).join('')}
          </div>
        </div>
      ` : ''}
    `;

    const reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
      reviewForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const ratingEl = document.getElementById('selectedRating');
        const rating = parseFloat(ratingEl.textContent);
        const comment = document.getElementById('reviewComment').value;
        const errEl = document.getElementById('reviewError');
        if (rating < 1) { errEl.textContent = 'Selecciona una calificación'; errEl.classList.remove('hidden'); return; }
        try {
          await api(`/api/mechanics/${mechanicId}/reviews`, {
            method: 'POST',
            body: JSON.stringify({ rating, comment }),
          });
          window.location.reload();
        } catch (e) {
          errEl.textContent = e.message;
          errEl.classList.remove('hidden');
        }
      });
    }

    loadReviews(mechanicId);
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

let currentRating = 0;
function setRating(val) {
  currentRating = val;
  document.getElementById('selectedRating').textContent = val;
  document.querySelectorAll('.star-option').forEach((el, i) => {
    el.textContent = i < val ? '★' : '☆';
    el.style.color = i < val ? '#f59e0b' : '#94a3b8';
  });
}

async function loadReviews(mechanicId) {
  const container = document.getElementById('reviewsList');
  if (!container) return;
  try {
    const reviews = await api(`/api/mechanics/${mechanicId}/reviews`);
    if (reviews.length === 0) {
      container.innerHTML = '<p class="empty-state">Sin reseñas aún. ¡Sé el primero!</p>';
      return;
    }
    container.innerHTML = reviews.map(r => `
      <div class="review-card">
        <div class="review-header">
          <div class="review-avatar">${r.client_avatar ? `<img src="${r.client_avatar}" style="width:40px;height:40px;border-radius:50%;object-fit:cover">` : '👤'}</div>
          <div>
            <div class="review-author">${escapeHtml(r.client_name || 'Anónimo')}</div>
            <div class="review-rating">${showStars(r.rating)}</div>
          </div>
          <div class="review-date">${formatDate(r.created_at)}</div>
        </div>
        ${r.comment ? `<p class="review-comment">${escapeHtml(r.comment)}</p>` : ''}
      </div>
    `).join('');
  } catch (e) {}
}

// ---- PROFILE ----
async function loadProfile() {
  const container = document.getElementById('profileView');
  if (!container) return;
  try {
    const m = await api('/api/me/my-profile');
    container.innerHTML = `
      <div style="display:flex;gap:2rem;flex-wrap:wrap">
        <div class="mechanic-detail-avatar">${m.user_avatar ? `<img src="${m.user_avatar}" alt="">` : '🔧'}</div>
        <div style="flex:1">
          <h2>${escapeHtml(m.business_name || m.user_name || 'Mi Perfil')}</h2>
          <p>${escapeHtml(m.description || 'Sin descripción')}</p>
          <div class="mechanic-stats">
            <span>⭐ ${m.avg_rating || '—'}</span>
            <span>📝 ${m.review_count} reseñas</span>
            <span>📅 ${m.years_experience} años</span>
            <span>📍 ${escapeHtml(m.location || 'Sin ubicación')}</span>
          </div>
        </div>
        <button class="btn btn-outline" onclick="showEditProfile()">✏️ Editar perfil</button>
      </div>
    `;

    loadMyReviews();
    loadMyTutorials();
    loadMyPhotos();
  } catch (e) {
    if (e.message.includes('No tienes perfil')) {
      container.innerHTML = `
        <div class="empty-state">
          <p>Aún no tienes perfil de mecánico. ¡Crea uno para empezar!</p>
          <button class="btn btn-primary" onclick="showEditProfile()">Crear perfil</button>
        </div>
      `;
    } else {
      container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
    }
  }
}

function showEditProfile() {
  window.location.href = '/perfil?edit=1';
}

function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`.tab-btn[onclick*="${tab}"]`).classList.add('active');
  document.getElementById(`${tab}Tab`).classList.add('active');
}

async function loadMyReviews() {
  const container = document.getElementById('myReviews');
  if (!container) return;
  try {
    const m = await api('/api/me/my-profile');
    if (!m.review_count) { container.innerHTML = '<p class="empty-state">Aún no tienes reseñas</p>'; return; }
    const reviews = await api(`/api/mechanics/${m.id}/reviews`);
    container.innerHTML = reviews.map(r => `
      <div class="review-card">
        <div class="review-header">
          <div class="review-avatar">👤</div>
          <div>
            <div class="review-author">${escapeHtml(r.client_name || 'Anónimo')}</div>
            <div class="review-rating">${showStars(r.rating)}</div>
          </div>
          <div class="review-date">${formatDate(r.created_at)}</div>
        </div>
        ${r.comment ? `<p class="review-comment">${escapeHtml(r.comment)}</p>` : ''}
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<p class="empty-state">Error al cargar reseñas</p>`;
  }
}

async function loadMyTutorials() {
  const container = document.getElementById('myTutorials');
  if (!container) return;
  try {
    const m = await api('/api/me/my-profile');
    const tutorials = await api(`/api/tutorials?mechanic_id=${m.id}`);
    if (tutorials.length === 0) { container.innerHTML += '<p class="empty-state">No has creado tutoriales aún</p>'; return; }
    container.innerHTML = tutorials.map(t => `
      <div style="padding:1rem;border-bottom:1px solid var(--border)">
        <h4>${escapeHtml(t.title)}</h4>
        <div class="tutorial-meta"><span>📂 ${t.category || 'General'}</span><span>📊 ${t.difficulty || '—'}</span></div>
        <button class="btn btn-sm btn-danger" onclick="deleteTutorial(${t.id})">Eliminar</button>
      </div>
    `).join('');
  } catch (e) {}
}

async function deleteTutorial(id) {
  if (!confirm('¿Eliminar tutorial?')) return;
  try {
    await api(`/api/tutorials/${id}`, { method: 'DELETE' });
    loadMyTutorials();
  } catch (e) {
    alert(e.message);
  }
}

function showCreateTutorial() {
  document.getElementById('tutorialModal').classList.add('open');
}

function closeModal() {
  document.getElementById('tutorialModal')?.classList.remove('open');
}

const tutorialForm = document.getElementById('tutorialForm');
if (tutorialForm) {
  tutorialForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      await api('/api/tutorials', {
        method: 'POST',
        body: JSON.stringify({
          title: document.getElementById('tutTitle').value,
          description: document.getElementById('tutDesc').value,
          content: document.getElementById('tutContent').value,
          video_url: document.getElementById('tutVideo').value,
          category: document.getElementById('tutCategory').value,
          difficulty: document.getElementById('tutDifficulty').value,
        }),
      });
      closeModal();
      tutorialForm.reset();
      loadMyTutorials();
    } catch (e) {
      alert(e.message);
    }
  });
}

async function uploadPhoto(event) {
  const file = event.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('file', file);
  try {
    await apiFormData('/api/mechanics/profile/photo', fd);
    loadMyPhotos();
  } catch (e) {
    alert(e.message);
  }
}

async function loadMyPhotos() {
  const container = document.getElementById('myPhotos');
  if (!container) return;
  try {
    const m = await api('/api/me/my-profile');
    if (!m.photos.length) { container.innerHTML += '<p class="empty-state">Sube fotos de tus trabajos</p>'; return; }
    container.innerHTML = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:1rem;margin-top:1rem">' +
      m.photos.map(p => `<img src="${p}" style="width:100%;border-radius:var(--radius-sm);object-fit:cover;aspect-ratio:1">`).join('') +
      '</div>';
  } catch (e) {}
}

// ---- TUTORIALS ----
async function loadTutorials() {
  const container = document.getElementById('tutorialsList');
  if (!container) return;
  const category = document.getElementById('tutCategoryFilter')?.value || '';
  container.innerHTML = '<div class="loading">Cargando...</div>';
  try {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    const tutorials = await api(`/api/tutorials?${params}`);
    if (tutorials.length === 0) {
      container.innerHTML = '<div class="empty-state">No hay tutoriales aún</div>';
      return;
    }
    container.innerHTML = tutorials.map(t => `
      <a href="/tutoriales/${t.id}" class="tutorial-card">
        <div class="tutorial-card-body">
          <h3>${escapeHtml(t.title)}</h3>
          <div class="tutorial-meta">
            <span>📂 ${t.category || 'General'}</span>
            <span>📊 ${t.difficulty || '—'}</span>
            <span>👨‍🔧 ${escapeHtml(t.mechanic_name || 'Mecánico')}</span>
          </div>
          <p class="tutorial-desc">${escapeHtml(t.description || '').substring(0, 150)}</p>
        </div>
      </a>
    `).join('');
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

async function loadTutorialDetail() {
  const container = document.getElementById('tutorialDetail');
  if (!container) return;
  const id = window.location.pathname.split('/').pop();
  try {
    const t = await api(`/api/tutorials/${id}`);
    container.innerHTML = `
      <div class="tutorial-detail-card">
        <h1>${escapeHtml(t.title)}</h1>
        <div class="tutorial-meta">
          <span>📂 ${t.category || 'General'}</span>
          <span>📊 ${t.difficulty || '—'}</span>
          <span>👨‍🔧 ${escapeHtml(t.mechanic_name || 'Mecánico')}</span>
          <span>📅 ${formatDate(t.created_at)}</span>
        </div>
        ${t.video_url ? `
          <iframe class="tutorial-video" src="${t.video_url.replace('watch?v=', 'embed/')}" frameborder="0" allowfullscreen></iframe>
        ` : ''}
        ${t.description ? `<p style="color:var(--text-secondary);margin-bottom:1rem">${escapeHtml(t.description)}</p>` : ''}
        <div class="tutorial-content">${t.content || ''}</div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

// ---- MESSAGES ----
async function loadConversations() {
  const container = document.getElementById('conversationsList');
  if (!container) return;
  try {
    const convos = await api('/api/messages');
    if (convos.length === 0) {
      container.innerHTML = '<div class="empty-state">No tienes conversaciones. Contacta a un mecánico desde su perfil.</div>';
      return;
    }
    container.innerHTML = convos.map(c => `
      <a href="/mensajes/${c.other_user_id}" class="conversation-item ${c.unread > 0 ? 'unread' : ''}">
        <div class="conversation-avatar">👤</div>
        <div class="conversation-info">
          <div class="conversation-name">${escapeHtml(c.last_message.sender_name || 'Usuario')} ${c.unread > 0 ? `<span style="color:var(--primary);font-weight:600">(${c.unread} nuevos)</span>` : ''}</div>
          <div class="conversation-preview">${escapeHtml(c.last_message.content.substring(0, 80))}</div>
        </div>
        <div class="conversation-time">${formatDate(c.last_message.created_at)}</div>
      </a>
    `).join('');
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

async function loadConversation() {
  const container = document.getElementById('messagesContainer');
  if (!container) return;
  const otherId = window.location.pathname.split('/').pop();
  try {
    const msgs = await api(`/api/messages/${otherId}`);
    if (msgs.length === 0) {
      container.innerHTML = '<div class="empty-state">No hay mensajes aún. Envía el primero.</div>';
    } else {
      container.innerHTML = msgs.map(m => `
        <div class="message ${m.sender_id == otherId ? 'message-received' : 'message-sent'}">
          <div class="message-content">${escapeHtml(m.content)}</div>
          <div class="message-time">${formatDate(m.created_at)}</div>
        </div>
      `).join('');
      container.scrollTop = container.scrollHeight;
    }

    const otherUser = await api(`/api/mechanics?q=${otherId}`);
    const nameEl = document.getElementById('conversationWith');
    if (nameEl) nameEl.textContent = `Conversación`;

    const form = document.getElementById('messageForm');
    if (form) {
      form.onsubmit = async (e) => {
        e.preventDefault();
        const input = document.getElementById('messageInput');
        const content = input.value.trim();
        if (!content) return;
        input.value = '';
        try {
          await api('/api/messages', {
            method: 'POST',
            body: JSON.stringify({ receiver_id: parseInt(otherId), content }),
          });
          loadConversation();
        } catch (e) {
          alert(e.message);
        }
      };
    }
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

// ---- SERVICES & BOOKINGS ----
async function loadMechanicServices(mechanicId) {
  const container = document.getElementById('servicesList');
  if (!container) return;
  try {
    const services = await api(`/api/mechanics/${mechanicId}/services`);
    if (services.length === 0) {
      container.innerHTML = '<p class="empty-state">Este mecánico aún no ha publicado servicios</p>';
      return;
    }
    container.innerHTML = services.map(s => `
      <div class="service-card" style="padding:1rem;border:1px solid var(--border);border-radius:var(--radius-sm);margin-bottom:.75rem">
        <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:.5rem">
          <div>
            <h4 style="margin-bottom:.25rem">${escapeHtml(s.title)}</h4>
            <div style="font-size:.85rem;color:var(--text-secondary);margin-bottom:.25rem">
              <span>📂 ${s.category || 'General'}</span>
              ${s.duration ? `<span style="margin-left:1rem">⏱ ${escapeHtml(s.duration)}</span>` : ''}
            </div>
            ${s.description ? `<p style="font-size:.85rem;color:var(--text-secondary)">${escapeHtml(s.description)}</p>` : ''}
          </div>
          <div style="text-align:right">
            <div style="font-size:1.3rem;font-weight:700;color:var(--primary)">$${s.price.toFixed(2)}</div>
            ${document.cookie.includes('token') ? `<button class="btn btn-sm btn-primary" onclick="showHireModal(${s.id}, '${escapeHtml(s.title)}', ${s.price})">Contratar</button>` : `<a href="/login" class="btn btn-sm btn-outline">Inicia sesión</a>`}
          </div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    container.innerHTML = `<p class="empty-state">Error: ${e.message}</p>`;
  }
}

function showHireModal(serviceId, title, price) {
  const existing = document.getElementById('hireModal');
  if (existing) existing.remove();
  const modal = document.createElement('div');
  modal.id = 'hireModal';
  modal.className = 'modal open';
  modal.innerHTML = `
    <div class="modal-content">
      <span class="modal-close" onclick="this.closest('.modal').remove()">&times;</span>
      <h2>Contratar Servicio</h2>
      <p style="margin-bottom:1rem"><strong>${escapeHtml(title)}</strong> — $${price.toFixed(2)}</p>
      <form id="hireForm" class="auth-form">
        <div class="form-group">
          <label>Descripción de lo que necesitas</label>
          <textarea id="hireDesc" class="form-input" rows="3" placeholder="Describe el problema de tu vehículo..."></textarea>
        </div>
        <div class="form-group">
          <label>Fecha sugerida</label>
          <input type="date" id="hireDate" class="form-input">
        </div>
        <div id="hireError" class="form-error hidden"></div>
        <button type="submit" class="btn btn-primary btn-block">Solicitar Servicio</button>
      </form>
    </div>
  `;
  document.body.appendChild(modal);
  document.getElementById('hireForm').onsubmit = async (e) => {
    e.preventDefault();
    const errEl = document.getElementById('hireError');
    try {
      await api('/api/bookings', {
        method: 'POST',
        body: JSON.stringify({
          service_id: serviceId,
          description: document.getElementById('hireDesc').value,
          scheduled_date: document.getElementById('hireDate').value,
        }),
      });
      modal.remove();
      alert('¡Solicitud enviada! El mecánico te contactará pronto.');
    } catch (e) {
      errEl.textContent = e.message;
      errEl.classList.remove('hidden');
    }
  };
}

async function loadBookings() {
  const container = document.getElementById('bookingsList');
  if (!container) return;
  try {
    const bookings = await api('/api/bookings');
    if (bookings.length === 0) {
      container.innerHTML = '<div class="empty-state">No tienes contrataciones aún. Busca un mecánico y contrata un servicio.</div>';
      return;
    }
    container.innerHTML = bookings.map(b => `
      <div class="booking-card" data-status="${b.status}" style="background:var(--surface);border-radius:var(--radius);box-shadow:var(--shadow);padding:1.5rem;margin-bottom:1rem">
        <div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:.5rem">
          <div>
            <h3>${escapeHtml(b.service_title || 'Servicio')}</h3>
            <p style="font-size:.9rem;color:var(--text-secondary);margin:.25rem 0">
              ${b.mechanic_name ? `👨‍🔧 ${escapeHtml(b.mechanic_name)}` : ''}
              ${b.client_name ? `👤 ${escapeHtml(b.client_name)}` : ''}
            </p>
            ${b.description ? `<p style="font-size:.85rem;color:var(--text-secondary)">${escapeHtml(b.description)}</p>` : ''}
            ${b.scheduled_date ? `<p style="font-size:.85rem;color:var(--text-secondary)">📅 ${b.scheduled_date}</p>` : ''}
          </div>
          <div style="text-align:right">
            <div style="font-size:1.2rem;font-weight:700;color:var(--primary)">$${(b.price || 0).toFixed(2)}</div>
            <div class="status-badge status-${b.status}" style="margin-top:.5rem;padding:.25rem .75rem;border-radius:12px;font-size:.8rem;font-weight:600">${statusLabel(b.status)}</div>
          </div>
        </div>
        ${b.status === 'pending' ? `
          <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border);display:flex;gap:.5rem;flex-wrap:wrap">
            ${userRole === 'mechanic' ? `
              <button class="btn btn-sm btn-primary" onclick="updateBooking(${b.id}, 'accepted')">✅ Aceptar</button>
              <button class="btn btn-sm btn-danger" onclick="updateBooking(${b.id}, 'cancelled')">❌ Rechazar</button>
            ` : `
              <button class="btn btn-sm btn-danger" onclick="updateBooking(${b.id}, 'cancelled')">Cancelar solicitud</button>
            `}
          </div>
        ` : ''}
        ${b.status === 'accepted' && userRole === 'mechanic' ? `
          <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border)">
            <button class="btn btn-sm btn-primary" onclick="updateBooking(${b.id}, 'in_progress')">🔧 Iniciar trabajo</button>
          </div>
        ` : ''}
        ${b.status === 'in_progress' ? `
          <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid var(--border)">
            <button class="btn btn-sm btn-success" style="background:var(--success);color:#fff;border:none;padding:.4rem .8rem;border-radius:var(--radius-sm);font-weight:600;cursor:pointer" onclick="updateBooking(${b.id}, 'completed')">✅ Completar</button>
          </div>
        ` : ''}
      </div>
    `).join('');
    window.allBookings = bookings;
  } catch (e) {
    container.innerHTML = `<div class="empty-state">Error: ${e.message}</div>`;
  }
}

function statusLabel(status) {
  const labels = { pending: 'Pendiente', accepted: 'Aceptado', in_progress: 'En Progreso', completed: 'Completado', cancelled: 'Cancelado' };
  return labels[status] || status;
}

async function updateBooking(id, status) {
  try {
    await api(`/api/bookings/${id}/status`, { method: 'PUT', body: JSON.stringify({ status }) });
    loadBookings();
  } catch (e) {
    alert(e.message);
  }
}

function filterBookings(status) {
  document.querySelectorAll('.bookings-filters .btn').forEach(b => b.classList.remove('active-filter'));
  document.querySelector(`.bookings-filters .btn[data-filter="${status}"]`).classList.add('active-filter');
  document.querySelectorAll('.booking-card').forEach(c => {
    c.style.display = (status === 'all' || c.dataset.status === status) ? '' : 'none';
  });
}

// ---- PROFILE SERVICES ----
async function loadProfileServices() {
  const container = document.getElementById('myServices');
  if (!container) return;
  try {
    const m = await api('/api/me/my-profile');
    const services = await api(`/api/mechanics/${m.id}/services`);
    if (services.length === 0) {
      container.innerHTML = '<p class="empty-state">No has publicado servicios aún</p>';
      return;
    }
    container.innerHTML = services.map(s => `
      <div style="padding:1rem;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem">
        <div>
          <h4>${escapeHtml(s.title)}</h4>
          <div style="font-size:.85rem;color:var(--text-secondary)">💰 $${s.price.toFixed(2)} ${s.category ? `| 📂 ${s.category}` : ''} ${s.duration ? `| ⏱ ${s.duration}` : ''}</div>
        </div>
        <button class="btn btn-sm btn-danger" onclick="deleteService(${s.id})">Eliminar</button>
      </div>
    `).join('');
  } catch (e) {}
}

async function deleteService(id) {
  if (!confirm('¿Eliminar servicio?')) return;
  try {
    await api(`/api/services/${id}`, { method: 'DELETE' });
    loadProfileServices();
  } catch (e) {
    alert(e.message);
  }
}

function showCreateService() {
  const existing = document.getElementById('serviceModal');
  if (existing) existing.remove();
  const modal = document.createElement('div');
  modal.id = 'serviceModal';
  modal.className = 'modal open';
  modal.innerHTML = `
    <div class="modal-content">
      <span class="modal-close" onclick="this.closest('.modal').remove()">&times;</span>
      <h2>Crear Servicio</h2>
      <form id="serviceForm" class="auth-form">
        <div class="form-group"><label>Título</label><input type="text" id="svcTitle" class="form-input" required></div>
        <div class="form-group"><label>Descripción</label><textarea id="svcDesc" class="form-input" rows="3"></textarea></div>
        <div class="form-group"><label>Precio ($)</label><input type="number" id="svcPrice" class="form-input" step="0.01" min="0" required></div>
        <div class="form-group"><label>Categoría</label>
          <select id="svcCategory" class="form-input">
            <option value="">Seleccionar...</option>
            <option value="Motor">Motor</option>
            <option value="Frenos">Frenos</option>
            <option value="Suspensión">Suspensión</option>
            <option value="Transmisión">Transmisión</option>
            <option value="Eléctrico">Eléctrico</option>
            <option value="Aire Acondicionado">Aire Acondicionado</option>
            <option value="Mantenimiento">Mantenimiento</option>
            <option value="Diagnóstico">Diagnóstico</option>
            <option value="Otro">Otro</option>
          </select>
        </div>
        <div class="form-group"><label>Duración estimada</label>
          <select id="svcDuration" class="form-input">
            <option value="">Seleccionar...</option>
            <option value="1 hora">1 hora</option>
            <option value="2 horas">2 horas</option>
            <option value="4 horas">4 horas</option>
            <option value="1 día">1 día</option>
            <option value="2-3 días">2-3 días</option>
            <option value="1 semana">1 semana</option>
          </select>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Publicar Servicio</button>
      </form>
    </div>
  `;
  document.body.appendChild(modal);
  document.getElementById('serviceForm').onsubmit = async (e) => {
    e.preventDefault();
    try {
      await api('/api/services', {
        method: 'POST',
        body: JSON.stringify({
          title: document.getElementById('svcTitle').value,
          description: document.getElementById('svcDesc').value,
          price: parseFloat(document.getElementById('svcPrice').value),
          category: document.getElementById('svcCategory').value,
          duration: document.getElementById('svcDuration').value,
        }),
      });
      modal.remove();
      loadProfileServices();
    } catch (e) {
      alert(e.message);
    }
  };
}

// ---- INIT ----
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  const userEl = document.querySelector('.nav-user-name');
  window.userRole = userEl ? (document.querySelector('a[href="/perfil"]') ? 'mechanic' : 'client') : null;

  if (path === '/buscar' || path.startsWith('/buscar')) loadSearch();
  if (path.startsWith('/mecanicos/') && path !== '/mecanicos/') {
    loadMechanicDetail();
    const id = path.split('/').pop();
    setTimeout(() => loadMechanicServices(id), 500);
  }
  if (path === '/perfil') { loadProfile(); setTimeout(() => loadProfileServices(), 500); }
  if (path === '/tutoriales') loadTutorials();
  if (path.startsWith('/tutoriales/') && path !== '/tutoriales/') loadTutorialDetail();
  if (path === '/mensajes') loadConversations();
  if (path.startsWith('/mensajes/') && path !== '/mensajes/') loadConversation();
  if (path === '/contrataciones') loadBookings();
});
