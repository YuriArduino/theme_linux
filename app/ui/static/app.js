const grid = document.getElementById('grid');
const modal = document.getElementById('modal');
const searchInput = document.getElementById('searchInput');
let activeTheme = null;

const escapeHtml = (text = '') => text.replace(/<[^>]*>/g, '');

function renderCards(themes) {
  grid.innerHTML = '';
  themes.forEach((theme) => {
    const card = document.createElement('article');
    card.className = 'bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-fuchsia-500 cursor-pointer';
    card.innerHTML = `
      <img src="${theme.preview_urls?.[0] || ''}" alt="${theme.name}" class="w-full h-40 rounded-lg object-cover bg-slate-800 mb-3" />
      <h3 class="font-semibold">${theme.name}</h3>
      <p class="text-xs text-slate-400">by ${theme.author}</p>
      <p class="text-xs text-slate-500 mt-2">⭐ ${theme.score} · ⬇ ${theme.downloads}</p>
    `;

    card.addEventListener('click', () => openModal(theme.id));
    grid.appendChild(card);
  });
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadBrowse(sort = 'top') {
  const themes = await fetchJSON(`/api/themes?sort=${sort}`);
  renderCards(themes);
}

async function loadInstalled() {
  const installed = await fetchJSON('/api/installed');
  grid.innerHTML = installed.map((item) => `
    <article class="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <h3 class="font-semibold">${item.name}</h3>
      <p class="text-xs text-slate-400">ID: ${item.id}</p>
      <p class="text-xs text-slate-500">Installed version: ${item.version}</p>
    </article>
  `).join('');
}

async function loadUpdates() {
  const updates = await fetchJSON('/api/updates');
  if (!updates.length) {
    grid.innerHTML = '<p class="text-slate-400">All installed themes are up-to-date.</p>';
    return;
  }

  grid.innerHTML = updates.map((item) => `
    <article class="bg-slate-900 border border-amber-500/50 rounded-xl p-4">
      <h3 class="font-semibold">${item.name}</h3>
      <p class="text-xs text-slate-400">Installed: ${item.installed_version}</p>
      <p class="text-xs text-amber-300">Latest: ${item.latest_version}</p>
      <button data-install-id="${item.id}" class="mt-3 px-3 py-1 text-xs rounded bg-emerald-600">Update</button>
    </article>
  `).join('');

  document.querySelectorAll('[data-install-id]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      await installTheme(btn.dataset.installId);
      await loadUpdates();
    });
  });
}

async function openModal(themeId) {
  activeTheme = await fetchJSON(`/api/themes/${themeId}`);
  document.getElementById('modalTitle').textContent = activeTheme.name;
  document.getElementById('modalImage').src = activeTheme.preview_urls?.[0] || '';
  document.getElementById('modalSummary').textContent = escapeHtml(activeTheme.summary || 'No summary available.');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

async function installTheme(themeId) {
  await fetchJSON(`/api/themes/${themeId}/install`, { method: 'POST' });
  alert('Theme installed successfully.');
}

async function removeTheme(themeId) {
  await fetchJSON(`/api/themes/${themeId}`, { method: 'DELETE' });
  alert('Theme removed successfully.');
}

document.getElementById('searchBtn').addEventListener('click', async () => {
  const query = searchInput.value.trim();
  if (query.length < 2) {
    return;
  }
  const themes = await fetchJSON(`/api/themes/search?query=${encodeURIComponent(query)}`);
  renderCards(themes);
});

document.getElementById('installBtn').addEventListener('click', async () => {
  if (!activeTheme) return;
  await installTheme(activeTheme.id);
});

document.getElementById('removeBtn').addEventListener('click', async () => {
  if (!activeTheme) return;
  await removeTheme(activeTheme.id);
});

document.getElementById('closeModal').addEventListener('click', () => {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
});

document.querySelectorAll('.nav-btn').forEach((button) => {
  button.addEventListener('click', async () => {
    document.querySelectorAll('.nav-btn').forEach((btn) => btn.classList.remove('bg-fuchsia-600'));
    button.classList.add('bg-fuchsia-600');
    const view = button.dataset.view;

    if (view === 'browse') await loadBrowse('top');
    if (view === 'trending') await loadBrowse('trending');
    if (view === 'installed') await loadInstalled();
    if (view === 'updates') await loadUpdates();
  });
});

loadBrowse();
