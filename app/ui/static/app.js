const grid = document.getElementById('grid');
const modal = document.getElementById('modal');
const searchInput = document.getElementById('searchInput');
const statusText = document.getElementById('statusText');
const pagination = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prevPageBtn');
const nextPageBtn = document.getElementById('nextPageBtn');
const pageIndicator = document.getElementById('pageIndicator');
const installBtn = document.getElementById('installBtn');
const installStatus = document.getElementById('installStatus');
const modalImage = document.getElementById('modalImage');
const carouselThumbs = document.getElementById('carouselThumbs');
const carouselPrevBtn = document.getElementById('carouselPrevBtn');
const carouselNextBtn = document.getElementById('carouselNextBtn');
let activeTheme = null;
let activePreviewIndex = 0;
let installInFlight = false;
let currentPage = 1;
let currentView = 'browse';
let currentQuery = '';

const PAGE_SIZE = 12;

const escapeHtml = (text = '') => text.replace(/<[^>]*>/g, '');
const unique = (values) => [...new Set(values.filter(Boolean))];

function getPreviewUrls(theme) {
  return unique([
    ...(theme.preview_urls || []),
    theme.preview,
    theme.previewpic1,
    theme.previewpic2,
    theme.previewpic3,
    theme.previewpic4,
  ]);
}

function setStatus(message) {
  statusText.textContent = message;
}

function renderSkeletons(count = 6) {
  grid.innerHTML = Array.from({ length: count }, () => `
    <article class="bg-slate-900 border border-slate-800 rounded-xl p-4 animate-pulse">
      <div class="w-full h-40 rounded-lg bg-slate-800 mb-3"></div>
      <div class="h-4 bg-slate-800 rounded w-3/4 mb-2"></div>
      <div class="h-3 bg-slate-800 rounded w-1/2 mb-2"></div>
      <div class="h-3 bg-slate-800 rounded w-2/3"></div>
    </article>
  `).join('');
}

function renderCards(themes) {
  grid.innerHTML = '';
  if (!themes.length) {
    grid.innerHTML = '<p class="text-slate-400">No themes found for this view.</p>';
    return;
  }

  themes.forEach((theme) => {
    const card = document.createElement('article');
    card.className = 'bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-fuchsia-500 cursor-pointer';
    const preview = getPreviewUrls(theme)[0] || '';
    card.innerHTML = `
      <img src="${preview}" alt="${theme.name}" class="w-full h-40 rounded-lg object-cover bg-slate-800 mb-3" />
      <h3 class="font-semibold">${theme.name}</h3>
      <p class="text-xs text-slate-400">by ${theme.author}</p>
      <p class="text-xs text-slate-300 mt-2 line-clamp-2">${escapeHtml(theme.summary || 'No summary available.')}</p>
      <p class="text-xs text-slate-500 mt-2">⭐ ${theme.score} · ⬇ ${theme.downloads}</p>
    `;

    card.addEventListener('click', () => openModal(theme.id));
    grid.appendChild(card);
  });
}

function renderPaginationControls(data) {
  const isPaginated = currentView === 'browse' || currentView === 'trending' || currentView === 'search';
  if (!isPaginated) {
    pagination.classList.add('hidden');
    return;
  }

  pagination.classList.remove('hidden');
  pagination.classList.add('flex');
  pageIndicator.textContent = `Page ${data.page}`;
  prevPageBtn.disabled = data.page <= 1;
  nextPageBtn.disabled = !data.has_more;
}

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

async function loadBrowse(sort = 'top') {
  currentView = sort === 'trending' ? 'trending' : 'browse';
  setStatus(`Loading ${sort} themes...`);
  renderSkeletons(PAGE_SIZE);
  const data = await fetchJSON(`/api/themes?sort=${sort}&page=${currentPage}&page_size=${PAGE_SIZE}`);
  renderCards(data.items);
  renderPaginationControls(data);
  setStatus(`Showing ${data.items.length} themes from ${sort}.`);
}

async function loadInstalled() {
  currentView = 'installed';
  pagination.classList.add('hidden');
  setStatus('Loading installed themes...');
  renderSkeletons(4);
  const installed = await fetchJSON('/api/installed');
  if (!installed.length) {
    grid.innerHTML = '<p class="text-slate-400">No installed themes yet.</p>';
    setStatus('No installed themes yet.');
    return;
  }
  grid.innerHTML = installed.map((item) => `
    <article class="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <h3 class="font-semibold">${item.name}</h3>
      <p class="text-xs text-slate-400">ID: ${item.id}</p>
      <p class="text-xs text-slate-500">Installed version: ${item.version}</p>
    </article>
  `).join('');
  setStatus(`Showing ${installed.length} installed themes.`);
}

async function loadUpdates() {
  currentView = 'updates';
  pagination.classList.add('hidden');
  setStatus('Checking for updates...');
  renderSkeletons(4);
  const updates = await fetchJSON('/api/updates');
  if (!updates.length) {
    grid.innerHTML = '<p class="text-slate-400">All installed themes are up-to-date.</p>';
    setStatus('All installed themes are up-to-date.');
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
  setStatus(`Found ${updates.length} themes with updates.`);
}

function updateCarousel() {
  if (!activeTheme) return;

  const previews = getPreviewUrls(activeTheme);
  modalImage.src = previews[activePreviewIndex] || '';
  modalImage.alt = activeTheme.name || 'Theme preview';

  if (previews.length <= 1) {
    carouselPrevBtn.classList.add('hidden');
    carouselNextBtn.classList.add('hidden');
    carouselThumbs.classList.add('hidden');
    carouselThumbs.innerHTML = '';
    return;
  }

  carouselPrevBtn.classList.remove('hidden');
  carouselNextBtn.classList.remove('hidden');
  carouselThumbs.classList.remove('hidden');
  carouselThumbs.classList.add('flex');
  carouselThumbs.innerHTML = previews.map((preview, index) => `
    <button
      data-preview-index="${index}"
      class="shrink-0 rounded-lg border ${index === activePreviewIndex ? 'border-fuchsia-500' : 'border-slate-700'} overflow-hidden"
    >
      <img src="${preview}" alt="${activeTheme.name} preview ${index + 1}" class="h-16 w-24 object-cover bg-slate-800" />
    </button>
  `).join('');

  carouselThumbs.querySelectorAll('[data-preview-index]').forEach((button) => {
    button.addEventListener('click', () => {
      activePreviewIndex = Number(button.dataset.previewIndex || 0);
      updateCarousel();
    });
  });
}

function syncInstallState(message = '') {
  installBtn.disabled = installInFlight;
  installBtn.textContent = installInFlight ? 'Installing...' : 'Install';
  installStatus.textContent = message;
}

async function openModal(themeId) {
  activeTheme = await fetchJSON(`/api/themes/${themeId}`);
  document.getElementById('modalTitle').textContent = activeTheme.name;
  document.getElementById('modalSummary').textContent = escapeHtml(activeTheme.summary || 'No summary available.');
  activePreviewIndex = 0;
  syncInstallState('');
  updateCarousel();
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

async function installTheme(themeId) {
  installInFlight = true;
  syncInstallState('Downloading and installing theme...');
  try {
    await fetchJSON(`/api/themes/${themeId}/install`, { method: 'POST' });
    syncInstallState('Theme installed successfully.');
  } finally {
    installInFlight = false;
    syncInstallState(installStatus.textContent);
  }
}

async function removeTheme(themeId) {
  await fetchJSON(`/api/themes/${themeId}`, { method: 'DELETE' });
  installStatus.textContent = 'Theme removed successfully.';
}

document.getElementById('searchBtn').addEventListener('click', async () => {
  const query = searchInput.value.trim();
  if (query.length < 2) {
    return;
  }
  currentView = 'search';
  currentQuery = query;
  currentPage = 1;
  setStatus(`Searching for "${query}"...`);
  renderSkeletons(PAGE_SIZE);
  const data = await fetchJSON(`/api/themes/search?query=${encodeURIComponent(query)}&page=${currentPage}&page_size=${PAGE_SIZE}`);
  renderCards(data.items);
  renderPaginationControls(data);
  setStatus(`Found ${data.items.length} themes for "${query}".`);
});

installBtn.addEventListener('click', async () => {
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

carouselPrevBtn.addEventListener('click', () => {
  if (!activeTheme) return;
  const previews = getPreviewUrls(activeTheme);
  activePreviewIndex = (activePreviewIndex - 1 + previews.length) % previews.length;
  updateCarousel();
});

carouselNextBtn.addEventListener('click', () => {
  if (!activeTheme) return;
  const previews = getPreviewUrls(activeTheme);
  activePreviewIndex = (activePreviewIndex + 1) % previews.length;
  updateCarousel();
});

prevPageBtn.addEventListener('click', async () => {
  if (currentPage <= 1) return;
  currentPage -= 1;
  await loadCurrentView();
});

nextPageBtn.addEventListener('click', async () => {
  currentPage += 1;
  await loadCurrentView();
});

async function loadCurrentView() {
  if (currentView === 'browse') {
    await loadBrowse('top');
    return;
  }
  if (currentView === 'trending') {
    await loadBrowse('trending');
    return;
  }
  if (currentView === 'search') {
    setStatus(`Searching for "${currentQuery}"...`);
    renderSkeletons(PAGE_SIZE);
    const data = await fetchJSON(`/api/themes/search?query=${encodeURIComponent(currentQuery)}&page=${currentPage}&page_size=${PAGE_SIZE}`);
    renderCards(data.items);
    renderPaginationControls(data);
    setStatus(`Found ${data.items.length} themes for "${currentQuery}".`);
    return;
  }
  if (currentView === 'installed') {
    await loadInstalled();
    return;
  }
  await loadUpdates();
}

document.querySelectorAll('.nav-btn').forEach((button) => {
  button.addEventListener('click', async () => {
    document.querySelectorAll('.nav-btn').forEach((btn) => btn.classList.remove('bg-fuchsia-600'));
    button.classList.add('bg-fuchsia-600');
    const view = button.dataset.view;
    currentPage = 1;

    if (view === 'browse') await loadBrowse('top');
    if (view === 'trending') await loadBrowse('trending');
    if (view === 'installed') await loadInstalled();
    if (view === 'updates') await loadUpdates();
  });
});

loadCurrentView();
