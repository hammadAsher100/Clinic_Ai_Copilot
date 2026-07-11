/**
 * Clinical AI Co-Pilot — API Client Module
 *
 * Handles all fetch() calls to the FastAPI backend, JWT token management,
 * and error handling with user-friendly messages.
 */

const API_BASE = '';  // Same origin

// ── Token Management ──────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem('auth_token');
}

function setToken(token) {
  localStorage.setItem('auth_token', token);
}

function clearToken() {
  localStorage.removeItem('auth_token');
}

function isAuthenticated() {
  return !!getToken();
}

function authHeaders() {
  const token = getToken();
  const headers = { 'Accept': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// ── Auth ──────────────────────────────────────────────────────────────

async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Login failed');
  }
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Not authenticated');
  return res.json();
}

function logout() {
  clearToken();
  window.location.href = '/static/frontend/index.html';
}

// ── Cases ─────────────────────────────────────────────────────────────

async function createCase(patientName, patientAge, patientSex) {
  const res = await fetch(`${API_BASE}/api/v1/cases`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient_name: patientName || 'Anonymous',
      patient_age: patientAge ? parseInt(patientAge) : null,
      patient_sex: patientSex || null,
    }),
  });
  if (!res.ok) throw new Error('Failed to create case');
  return res.json();
}

async function listCases() {
  const res = await fetch(`${API_BASE}/api/v1/cases`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to list cases');
  return res.json();
}

// ── Predictions ───────────────────────────────────────────────────────

async function predictImage(file, caseId, patientName) {
  const formData = new FormData();
  formData.append('file', file);
  if (caseId) formData.append('case_id', caseId);
  if (patientName) formData.append('patient_name', patientName);

  const res = await fetch(`${API_BASE}/api/v1/predict/image`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${getToken()}` },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Image prediction failed');
  }
  return res.json();
}

async function predictTabular(features) {
  const res = await fetch(`${API_BASE}/api/v1/predict/tabular`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(features),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Tabular prediction failed');
  }
  return res.json();
}

async function predictText(symptoms, caseId) {
  const res = await fetch(`${API_BASE}/api/v1/predict/text`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ symptoms, case_id: caseId || null }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Text prediction failed');
  }
  return res.json();
}

// ── LLM Co-Pilot ─────────────────────────────────────────────────────

async function summarizeCase(caseId) {
  const res = await fetch(`${API_BASE}/api/v1/copilot/summarize`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Summarization failed');
  }
  return res.json();
}

// ── HITL ──────────────────────────────────────────────────────────────

async function getCaseReview(caseId) {
  const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/review`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to load case review');
  return res.json();
}

async function submitDecision(caseId, modality, action, editedValue) {
  const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/decision`, {
    method: 'POST',
    headers: { ...authHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify({
      modality,
      action,
      edited_value: editedValue || null,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Decision submission failed');
  }
  return res.json();
}

// ── Reports ───────────────────────────────────────────────────────────

async function generateReport(caseId) {
  const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/generate-report`, {
    method: 'POST',
    headers: authHeaders(),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Report generation failed');
  }
  return res.json();
}

function getReportDownloadUrl(caseId) {
  return `${API_BASE}/api/v1/cases/${caseId}/report/download`;
}

async function getReportStatus(caseId) {
  const res = await fetch(`${API_BASE}/api/v1/cases/${caseId}/report/status`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error('Failed to check report status');
  return res.json();
}

// ── Toast Notifications ───────────────────────────────────────────────

function showToast(message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => toast.remove(), 4000);
}

// ── Loading Overlay ───────────────────────────────────────────────────

function showLoading(message = 'Processing...') {
  let overlay = document.querySelector('.loading-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
      <div class="loading-spinner"></div>
      <div class="loading-text">${message}</div>
    `;
    document.body.appendChild(overlay);
  } else {
    overlay.querySelector('.loading-text').textContent = message;
  }
  requestAnimationFrame(() => overlay.classList.add('active'));
}

function hideLoading() {
  const overlay = document.querySelector('.loading-overlay');
  if (overlay) overlay.classList.remove('active');
}
