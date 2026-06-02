/**
 * ReFinance — main.js
 * Toggle dark mode, sidebar hamburger, dan event listener umum
 */

// -------------------------------------------------------
// Dark Mode Toggle
// -------------------------------------------------------

/**
 * Terapkan tema berdasarkan nilai yang tersimpan atau preferensi sistem.
 * Data disimpan ke localStorage agar persisten.
 */
function applyTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  // Perbarui ikon tombol toggle (jika ada)
  updateThemeToggleIcon(theme);
}

/**
 * Perbarui ikon dan label tombol toggle dark mode.
 */
function updateThemeToggleIcon(theme) {
  const toggleBtns = document.querySelectorAll('.theme-toggle');
  toggleBtns.forEach(btn => {
    const icon = btn.querySelector('.material-symbols-outlined');
    const label = btn.querySelector('.toggle-label');
    if (icon) {
      icon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
    }
    if (label) {
      label.textContent = theme === 'dark' ? 'Terang' : 'Gelap';
    }
  });
}

/**
 * Toggle antara light dan dark mode, simpan ke localStorage.
 */
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem('refinance-theme', next);
  applyTheme(next);
}

// Sinkronkan ikon toggle dengan tema yang sudah diterapkan oleh inline script di <head>
(function syncToggleIcon() {
  const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  updateThemeToggleIcon(theme);
})();

// -------------------------------------------------------
// Sidebar Hamburger (Mobile)
// -------------------------------------------------------

/**
 * Buka/tutup sidebar di tampilan mobile.
 */
function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  if (!sidebar) return;

  const isOpen = sidebar.classList.contains('open');
  if (isOpen) {
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('open');
    document.body.style.overflow = '';
  } else {
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

/**
 * Tutup sidebar (dipakai saat klik overlay).
 */
function closeSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  if (sidebar) sidebar.classList.remove('open');
  if (overlay) overlay.classList.remove('open');
  document.body.style.overflow = '';
}

// -------------------------------------------------------
// Modal Helpers
// -------------------------------------------------------

/**
 * Buka modal berdasarkan ID.
 * @param {string} modalId - ID elemen modal-overlay
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

/**
 * Tutup modal berdasarkan ID.
 * @param {string} modalId - ID elemen modal-overlay
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
}

/**
 * Tutup semua modal yang terbuka.
 */
function closeAllModals() {
  document.querySelectorAll('.modal-overlay.open').forEach(modal => {
    modal.classList.remove('open');
  });
  document.body.style.overflow = '';
}

// -------------------------------------------------------
// Tabs Helper
// -------------------------------------------------------

/**
 * Aktifkan tab berdasarkan nama panel.
 * @param {string} panelName - Nilai data-panel pada tombol tab
 * @param {Element} context - Kontainer tabs (default: document)
 */
function activateTab(panelName, context) {
  const root = context || document;

  // Nonaktifkan semua tab dan panel
  root.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  root.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));

  // Aktifkan yang dipilih
  const activeBtn = root.querySelector(`.tab-btn[data-panel="${panelName}"]`);
  const activePanel = root.querySelector(`#panel-${panelName}`);
  if (activeBtn) activeBtn.classList.add('active');
  if (activePanel) activePanel.classList.add('active');
}

// -------------------------------------------------------
// Format Angka ke Rupiah
// -------------------------------------------------------

/**
 * Format angka ke string Rupiah.
 * @param {number} amount
 * @returns {string} misal "Rp 1.500.000"
 */
function formatRupiah(amount) {
  return 'Rp ' + Math.abs(amount).toLocaleString('id-ID');
}

// -------------------------------------------------------
// Event Listeners (dipasang setelah DOM siap)
// -------------------------------------------------------

document.addEventListener('DOMContentLoaded', function () {

  // --- Theme toggle ---
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', toggleTheme);
  });

  // --- Hamburger sidebar ---
  const hamburgerBtn = document.querySelector('.hamburger-btn');
  if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', toggleSidebar);
  }

  // --- Tutup sidebar saat klik overlay ---
  const sidebarOverlay = document.querySelector('.sidebar-overlay');
  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', closeSidebar);
  }

  // --- Tutup modal saat klik overlay ---
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function (e) {
      // Hanya tutup jika klik langsung di overlay (bukan di modal)
      if (e.target === overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  });

  // --- Tombol tutup modal (.modal-close) ---
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', function () {
      const overlay = btn.closest('.modal-overlay');
      if (overlay) {
        overlay.classList.remove('open');
        document.body.style.overflow = '';
      }
    });
  });

  // --- Tabs ---
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const panelName = btn.dataset.panel;
      const tabsContainer = btn.closest('.tabs-container') || document;
      activateTab(panelName, tabsContainer === document ? undefined : tabsContainer);
    });
  });

  // --- Tutup modal dengan tombol Escape ---
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAllModals();
      closeSidebar();
    }
  });

  // --- Highlight nav item aktif berdasarkan path ---
  highlightActiveNav();
});

/**
 * Highlight item sidebar nav yang sesuai dengan URL saat ini.
 */
function highlightActiveNav() {
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    const href = item.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      item.classList.add('active');
    } else if (href === '/dashboard' && (currentPath === '/' || currentPath === '/dashboard')) {
      item.classList.add('active');
    }
  });
}
