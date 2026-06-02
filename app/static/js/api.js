/**
 * ReFinance — api.js
 * Helper fetch terpusat untuk semua endpoint /api
 * Menangani redirect ke /login jika response 401.
 */

/**
 * Fetch generik ke endpoint API.
 * @param {string} url - URL endpoint
 * @param {object} options - opsi fetch (method, headers, body)
 * @returns {Promise<object>} data dari response JSON
 * @throws {Error} jika request gagal atau server error
 */
async function apiFetch(url, options = {}) {
  // Set header default untuk JSON
  const defaultHeaders = { 'Content-Type': 'application/json' };
  options.headers = Object.assign(defaultHeaders, options.headers || {});

  let response;
  try {
    response = await fetch(url, options);
  } catch (networkErr) {
    // Error jaringan (offline, dll.)
    throw new Error('Tidak dapat terhubung ke server. Periksa koneksi internet.');
  }

  // Jika 401 — pengguna belum login, redirect ke halaman login
  if (response.status === 401) {
    window.location.href = '/login';
    throw new Error('Sesi habis. Silakan login kembali.');
  }

  let json;
  try {
    json = await response.json();
  } catch (parseErr) {
    throw new Error('Response server tidak valid.');
  }

  // Jika server mengembalikan ok: false, lempar error dengan pesan dari server
  if (!json.ok) {
    throw new Error(json.error || 'Terjadi kesalahan pada server.');
  }

  return json.data;
}

/**
 * GET request ke URL tertentu.
 * @param {string} url
 * @returns {Promise<any>}
 */
async function apiGet(url) {
  return apiFetch(url, { method: 'GET' });
}

/**
 * POST request dengan body JSON.
 * @param {string} url
 * @param {object} body
 * @returns {Promise<any>}
 */
async function apiPost(url, body) {
  return apiFetch(url, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUT request dengan body JSON.
 * @param {string} url
 * @param {object} body
 * @returns {Promise<any>}
 */
async function apiPut(url, body) {
  return apiFetch(url, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETE request ke URL tertentu.
 * @param {string} url
 * @returns {Promise<any>}
 */
async function apiDelete(url) {
  return apiFetch(url, { method: 'DELETE' });
}

/**
 * Tampilkan pesan error di dalam elemen container.
 * @param {Element} container - elemen DOM tempat pesan ditampilkan
 * @param {string} pesan - teks pesan error
 */
function tampilkanError(container, pesan) {
  if (!container) return;
  container.innerHTML = `
    <div class="alert alert-danger" style="display:flex; align-items:center; gap:0.5rem;">
      <span class="material-symbols-outlined">error</span>
      <span>${pesan}</span>
    </div>`;
}

/**
 * Tampilkan loading skeleton di dalam elemen container.
 * @param {Element} container
 * @param {string} tinggi - tinggi skeleton (default: 80px)
 */
function tampilkanLoading(container, tinggi = '80px') {
  if (!container) return;
  container.innerHTML = `<div class="skeleton" style="height:${tinggi}; border-radius:var(--radius-card); background: var(--border); animation: pulse 1.5s ease-in-out infinite;"></div>`;
}

/**
 * Tambahkan animasi pulse ke CSS jika belum ada.
 */
(function tambahAnimasiPulse() {
  if (document.getElementById('rf-pulse-style')) return;
  const style = document.createElement('style');
  style.id = 'rf-pulse-style';
  style.textContent = `
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }
  `;
  document.head.appendChild(style);
})();
