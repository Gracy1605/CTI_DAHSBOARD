const API_BASE = 'http://localhost:5000';
const authStorage = { access: 'cti_access_token', refresh: 'cti_refresh_token' };
const state = { page: 1, per_page: 10, pages: 1, search: '', severity: '', sort_by: 'first_seen', order: 'asc', stats: null };

const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');

const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

const totalThreatsEl = document.getElementById('total-threats');
const highThreatsEl = document.getElementById('high-threats');
const mediumThreatsEl = document.getElementById('medium-threats');
const lowThreatsEl = document.getElementById('low-threats');

const searchInput = document.getElementById('search-input');
const severityFilter = document.getElementById('severity-filter');
const sortBy = document.getElementById('sort-by');
const orderBy = document.getElementById('order-by');
const searchBtn = document.getElementById('search-btn');

const threatTableBody = document.querySelector('#threat-table tbody');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const paginationInfo = document.getElementById('pagination-info');
const generalError = document.getElementById('general-error');
const loginError = document.getElementById('login-error');

let severityChart = null;

function storeTokens(tokens) {
  try {
    localStorage.setItem(authStorage.access, tokens.access_token);
    localStorage.setItem(authStorage.refresh, tokens.refresh_token);
  } catch (e) {
    // Fallback to sessionStorage if localStorage fails (e.g., file:// protocol)
    sessionStorage.setItem(authStorage.access, tokens.access_token);
    sessionStorage.setItem(authStorage.refresh, tokens.refresh_token);
  }
}

function getAccessToken() {
  try {
    return localStorage.getItem(authStorage.access) || sessionStorage.getItem(authStorage.access);
  } catch {
    return sessionStorage.getItem(authStorage.access);
  }
}

function getRefreshToken() {
  try {
    return localStorage.getItem(authStorage.refresh) || sessionStorage.getItem(authStorage.refresh);
  } catch {
    return sessionStorage.getItem(authStorage.refresh);
  }
}

function clearTokens() {
  try {
    localStorage.removeItem(authStorage.access);
    localStorage.removeItem(authStorage.refresh);
  } catch {}
  try {
    sessionStorage.removeItem(authStorage.access);
    sessionStorage.removeItem(authStorage.refresh);
  } catch {}
}

function showLogin() { loginScreen.classList.add('active'); dashboardScreen.classList.remove('active'); }
function showDashboard() { loginScreen.classList.remove('active'); dashboardScreen.classList.add('active'); }

async function refreshToken() {
  const refresh = getRefreshToken();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refresh}`,
      },
    });
    if (!res.ok) throw new Error('Refresh failed');
    const data = await res.json();
    if (data.access_token) localStorage.setItem(authStorage.access, data.access_token);
    return !!data.access_token;
  } catch { clearTokens(); return false; }
}

async function requestWithAuth(url, options = {}) {
  const token = getAccessToken();
  options.headers = options.headers || {};
  if (token) options.headers['Authorization'] = `Bearer ${token}`;
  let response = await fetch(url, options);
  if (response.status === 401 && getRefreshToken()) {
    if (await refreshToken()) {
      options.headers['Authorization'] = `Bearer ${getAccessToken()}`;
      response = await fetch(url, options);
    }
  }
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

async function performLogin() {
  loginError.textContent = '';
  const username = usernameInput.value.trim();
  const password = passwordInput.value.trim();
  if (!username || !password) { loginError.textContent = 'Enter username & password'; return; }

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) { const err = await res.json(); throw new Error(err.message || 'Login failed'); }
    const data = await res.json();
    storeTokens(data);
    showDashboard();
    await initializeDashboard();
  } catch (err) { loginError.textContent = err.message; }
}

async function fetchStats() {
  const stats = await requestWithAuth(`${API_BASE}/stats`);
  state.stats = stats;
  totalThreatsEl.textContent = stats.total_threats || '0';
  highThreatsEl.textContent = stats.high || '0';
  mediumThreatsEl.textContent = stats.medium || '0';
  lowThreatsEl.textContent = stats.low || '0';
  renderChart(stats);
}

async function fetchThreats() {
  generalError.textContent = '';
  const params = new URLSearchParams();
  if (state.severity) params.append('severity', state.severity);
  if (state.search) params.append('search', state.search);
  if (state.sort_by) params.append('sort_by', state.sort_by);
  if (state.order) params.append('order', state.order);
  params.append('page', state.page);
  params.append('per_page', state.per_page);

  try {
    const data = await requestWithAuth(`${API_BASE}/threats?${params.toString()}`);
    renderTable(data.data || []);
    state.pages = data.pages || 1;
    paginationInfo.textContent = `Page ${data.page || state.page} of ${state.pages}`;
    prevPageBtn.disabled = state.page <= 1;
    nextPageBtn.disabled = state.page >= state.pages;
  } catch (err) { generalError.textContent = 'Failed to load threat data. ' + err.message; threatTableBody.innerHTML = ''; }
}

function renderTable(threats) {
  threatTableBody.innerHTML = '';
  if (!threats.length) {
    const tr = document.createElement('tr');
    tr.innerHTML = '<td colspan="8" style="text-align:center; color:#99b3d4;">No threats found</td>';
    threatTableBody.appendChild(tr);
    return;
  }
  threats.forEach(t => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${t.id}</td>
      <td>${t.ioc_value}</td>
      <td>${t.ioc_type}</td>
      <td>${t.severity}</td>
      <td>${t.category}</td>
      <td>${t.source}</td>
      <td>${t.first_seen}</td>
      <td>${t.last_seen}</td>
    `;
    threatTableBody.appendChild(row);
  });
}

function renderChart(stats) {
  if (!stats) return;
  const ctx = document.getElementById('severity-chart').getContext('2d');

  // Destroy existing chart if it exists
  if (severityChart) {
    severityChart.destroy();
    severityChart = null;
  }

  const total = (stats.high || 0) + (stats.medium || 0) + (stats.low || 0);
  if (total === 0) return; // Don't render empty chart

  severityChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['High', 'Medium', 'Low'],
      datasets: [{
        data: [stats.high || 0, stats.medium || 0, stats.low || 0],
        backgroundColor: ['#ff4d4f', '#ffb86c', '#3affc9'],
        borderColor: ['#ff7a7f', '#ffd09a', '#8cffde'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: {
        padding: 10
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#dcefff',
            padding: 15,
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || '';
              const value = context.parsed || 0;
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
              return `${label}: ${value} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

// ===================== NEW AUTO-FETCH =====================
async function fetchLiveThreats() {
  try {
    await requestWithAuth(`${API_BASE}/fetch-live`, { method: 'POST' });
  } catch (err) {
    console.error('Live fetch failed (non-blocking):', err);
  }
}

async function initializeDashboard() {
  try {
    // 1️⃣ fetch live threats automatically
    await fetchLiveThreats();
    // 2️⃣ then fetch stats & table
    await fetchStats();
    await fetchThreats();
  } catch (err) { generalError.textContent = 'Unable to initialize dashboard. ' + err.message; }
}

function bindEvents() {
  loginBtn.addEventListener('click', performLogin);
  logoutBtn.addEventListener('click', () => { clearTokens(); showLogin(); });

  searchBtn.addEventListener('click', () => { state.search = searchInput.value.trim(); state.page = 1; fetchThreats(); });
  searchInput.addEventListener('keydown', e => { if(e.key==='Enter') searchBtn.click(); });
  severityFilter.addEventListener('change', () => { state.severity = severityFilter.value; state.page=1; fetchThreats(); });
  sortBy.addEventListener('change', () => { state.sort_by = sortBy.value; state.page=1; fetchThreats(); });
  orderBy.addEventListener('change', () => { state.order = orderBy.value; state.page=1; fetchThreats(); });

  prevPageBtn.addEventListener('click', () => { if(state.page>1){ state.page--; fetchThreats(); }});
  nextPageBtn.addEventListener('click', () => { if(state.page<state.pages){ state.page++; fetchThreats(); }});
}

async function init() {
  bindEvents();
  if (getAccessToken()) { showDashboard(); await initializeDashboard(); }
  else showLogin();
}

init();