/**
 * ReFinance — charts.js
 * Inisialisasi Chart.js untuk semua halaman.
 * Warna diambil dari CSS variable via getComputedStyle agar otomatis
 * menyesuaikan light/dark mode.
 */

// -------------------------------------------------------
// Helper: ambil CSS variable
// -------------------------------------------------------

/**
 * Ambil nilai CSS variable dari root element.
 * @param {string} varName - nama variable tanpa '--', misal 'accent'
 * @returns {string} nilai warna CSS
 */
function cssVar(varName) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue('--' + varName)
    .trim();
}

// -------------------------------------------------------
// Konfigurasi default Chart.js
// -------------------------------------------------------

/**
 * Buat konfigurasi default Chart.js yang menyesuaikan tema.
 * Dipanggil saat render agar mengambil warna terkini.
 */
function getChartDefaults() {
  return {
    color: cssVar('text-2'),
    borderColor: cssVar('border'),
    backgroundColor: cssVar('card'),
  };
}

/**
 * Pasang defaults Chart.js global.
 */
function applyChartDefaults() {
  if (typeof Chart === 'undefined') return;

  Chart.defaults.font.family = "'Plus Jakarta Sans', system-ui, sans-serif";
  Chart.defaults.font.size = 12;
  Chart.defaults.color = cssVar('text-2');
  Chart.defaults.plugins.legend.labels.color = cssVar('text');
  Chart.defaults.plugins.tooltip.backgroundColor = cssVar('text');
  Chart.defaults.plugins.tooltip.titleColor = cssVar('card');
  Chart.defaults.plugins.tooltip.bodyColor = cssVar('card');
  Chart.defaults.plugins.tooltip.borderWidth = 0;
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.scale.grid.color = cssVar('border');
  Chart.defaults.scale.ticks.color = cssVar('text-2');
}

// -------------------------------------------------------
// Dashboard — Grafik pengeluaran mingguan (Bar)
// -------------------------------------------------------

/**
 * Inisialisasi grafik bar pengeluaran mingguan di dashboard.
 * @param {string} canvasId - ID canvas element
 * @param {Array} labels - Label hari/minggu
 * @param {Array} data - Data pengeluaran
 */
function initWeeklyExpenseChart(canvasId, labels, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  applyChartDefaults();

  return new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels || ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
      datasets: [{
        label: 'Pengeluaran (Rp)',
        data: data || [150000, 320000, 80000, 450000, 210000, 560000, 90000],
        backgroundColor: cssVar('accent') + 'CC',
        borderColor: cssVar('accent'),
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => 'Rp ' + ctx.parsed.y.toLocaleString('id-ID'),
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
        },
        y: {
          grid: { color: cssVar('border') },
          border: { display: false },
          ticks: {
            callback: val => 'Rp ' + (val / 1000) + 'k',
          }
        }
      }
    }
  });
}

// -------------------------------------------------------
// Laporan — Grafik tren (Line)
// -------------------------------------------------------

/**
 * Inisialisasi grafik line tren pemasukan vs pengeluaran.
 * @param {string} canvasId
 * @param {Array} labels
 * @param {Array} incomeData
 * @param {Array} expenseData
 */
function initTrendChart(canvasId, labels, incomeData, expenseData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  applyChartDefaults();

  // Titik adaptif: makin banyak data (3/6 bulan) → titik makin kecil/hilang agar bersih
  const banyak = (labels || []).length;
  const radius = banyak > 45 ? 0 : (banyak > 14 ? 2 : 4);
  const hoverRadius = radius > 0 ? radius + 2 : 4;

  return new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels || ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
      datasets: [
        {
          label: 'Pemasukan',
          data: incomeData || [4500000, 5200000, 4800000, 6100000, 5700000, 6500000],
          borderColor: cssVar('pos'),
          backgroundColor: cssVar('pos') + '22',
          borderWidth: 2.5,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: cssVar('pos'),
          pointRadius: radius,
          pointHoverRadius: hoverRadius,
        },
        {
          label: 'Pengeluaran',
          data: expenseData || [3200000, 3800000, 3500000, 4200000, 3900000, 4500000],
          borderColor: cssVar('neg'),
          backgroundColor: cssVar('neg') + '22',
          borderWidth: 2.5,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: cssVar('neg'),
          pointRadius: radius,
          pointHoverRadius: hoverRadius,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
        },
        tooltip: {
          callbacks: {
            label: ctx => ctx.dataset.label + ': Rp ' + ctx.parsed.y.toLocaleString('id-ID'),
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: { maxTicksLimit: 8, maxRotation: 0, autoSkip: true },
        },
        y: {
          grid: { color: cssVar('border') },
          border: { display: false },
          ticks: {
            callback: val => 'Rp ' + (val / 1000000).toFixed(1) + 'jt',
          }
        }
      }
    }
  });
}

// -------------------------------------------------------
// Laporan — Grafik Pie komposisi kategori
// -------------------------------------------------------

/**
 * Inisialisasi grafik pie komposisi pengeluaran per kategori.
 * @param {string} canvasId
 * @param {Array} labels - nama kategori
 * @param {Array} data - nominal
 */
function initCategoryPieChart(canvasId, labels, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  applyChartDefaults();

  // Palet warna kategori — selaras tema Indigo/Amber, tetap kontras & aman buta warna
  const colors = [
    '#6366F1', '#10B981', '#F59E0B', '#F43F5E',
    '#8B5CF6', '#06B6D4', '#EC4899', '#84CC16',
  ];

  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: labels || ['Makanan', 'Transport', 'Hiburan', 'Belanja', 'Kesehatan', 'Lainnya'],
      datasets: [{
        data: data || [1200000, 450000, 300000, 800000, 200000, 350000],
        backgroundColor: colors,
        borderColor: cssVar('card'),
        borderWidth: 3,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '60%',
      plugins: {
        legend: {
          display: true,
          position: 'right',
          labels: {
            padding: 16,
            font: { size: 12, weight: '600' },
          }
        },
        tooltip: {
          callbacks: {
            label: ctx => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = ((ctx.parsed / total) * 100).toFixed(1);
              return ctx.label + ': Rp ' + ctx.parsed.toLocaleString('id-ID') + ' (' + pct + '%)';
            }
          }
        }
      }
    }
  });
}

// -------------------------------------------------------
// Laporan — Grafik Bar perbandingan bulan
// -------------------------------------------------------

/**
 * Inisialisasi grafik bar perbandingan bulan (pemasukan vs pengeluaran).
 * @param {string} canvasId
 * @param {Array} labels
 * @param {Array} incomeData
 * @param {Array} expenseData
 */
function initComparisonBarChart(canvasId, labels, incomeData, expenseData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return;

  applyChartDefaults();

  return new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels || ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun'],
      datasets: [
        {
          label: 'Pemasukan',
          data: incomeData || [4500000, 5200000, 4800000, 6100000, 5700000, 6500000],
          backgroundColor: cssVar('pos') + 'CC',
          borderColor: cssVar('pos'),
          borderWidth: 1.5,
          borderRadius: 4,
        },
        {
          label: 'Pengeluaran',
          data: expenseData || [3200000, 3800000, 3500000, 4200000, 3900000, 4500000],
          backgroundColor: cssVar('neg') + 'CC',
          borderColor: cssVar('neg'),
          borderWidth: 1.5,
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          align: 'end',
        },
        tooltip: {
          callbacks: {
            label: ctx => ctx.dataset.label + ': Rp ' + ctx.parsed.y.toLocaleString('id-ID'),
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
        },
        y: {
          grid: { color: cssVar('border') },
          border: { display: false },
          ticks: {
            callback: val => 'Rp ' + (val / 1000000).toFixed(1) + 'jt',
          }
        }
      }
    }
  });
}

// -------------------------------------------------------
// Market — Grafik line kurs USD/IDR 6 bulan
// -------------------------------------------------------

/**
 * Inisialisasi grafik line kurs USD/IDR.
 * @param {string} canvasId - ID elemen canvas
 * @param {Array} labels - tanggal string "YYYY-MM-DD"
 * @param {Array} data - nilai kurs float
 * @returns {Chart|null}
 */
function initUsdIdrLineChart(canvasId, labels, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return null;

  applyChartDefaults();

  const chart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Kurs USD/IDR',
        data: data,
        borderColor: cssVar('accent'),
        backgroundColor: cssVar('accent') + '22',
        borderWidth: 2.5,
        tension: 0.3,
        fill: true,
        pointRadius: 2,
        pointHoverRadius: 5,
        pointBackgroundColor: cssVar('accent'),
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => 'Rp ' + ctx.parsed.y.toLocaleString('id-ID'),
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: {
            maxTicksLimit: 8,
            maxRotation: 0,
          }
        },
        y: {
          grid: { color: cssVar('border') },
          border: { display: false },
          ticks: {
            callback: val => 'Rp ' + (val / 1000).toFixed(0) + 'k',
          }
        }
      }
    }
  });

  // Daftarkan agar terupdate saat tema berubah
  if (!window._rfCharts) window._rfCharts = [];
  window._rfCharts.push(chart);
  return chart;
}

// -------------------------------------------------------
// Market / Emas — Grafik line harga emas per gram
// -------------------------------------------------------

/**
 * Inisialisasi grafik line harga emas (Rupiah per gram).
 * @param {string} canvasId - ID elemen canvas
 * @param {Array} labels - tanggal string "YYYY-MM-DD"
 * @param {Array} data - harga emas per gram (Rupiah)
 * @returns {Chart|null}
 */
function initGoldLineChart(canvasId, labels, data) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof Chart === 'undefined') return null;

  applyChartDefaults();

  // Warna emas (amber) konsisten dengan ikon emas di seluruh aplikasi
  const emas = '#D97706';

  const chart = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Harga Emas (Rp/gram)',
        data: data,
        borderColor: emas,
        backgroundColor: emas + '22',
        borderWidth: 2.5,
        tension: 0.3,
        fill: true,
        pointRadius: 2,
        pointHoverRadius: 5,
        pointBackgroundColor: emas,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => 'Rp ' + ctx.parsed.y.toLocaleString('id-ID') + ' /gram',
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          border: { display: false },
          ticks: { maxTicksLimit: 8, maxRotation: 0 }
        },
        y: {
          grid: { color: cssVar('border') },
          border: { display: false },
          ticks: {
            callback: val => 'Rp ' + (val / 1000).toFixed(0) + 'k',
          }
        }
      }
    }
  });

  // Daftarkan agar terupdate saat tema berubah
  if (!window._rfCharts) window._rfCharts = [];
  window._rfCharts.push(chart);
  return chart;
}

// -------------------------------------------------------
// Inisialisasi ulang chart saat tema berubah
// -------------------------------------------------------

/**
 * Destroy dan reinit semua chart yang terdaftar saat tema berubah.
 * Simpan referensi chart di window._rfCharts = []
 */
function reinitChartsOnThemeChange() {
  // Pantau perubahan atribut data-theme di <html>
  const observer = new MutationObserver(function () {
    applyChartDefaults();
    // Paksa update warna pada chart yang aktif
    if (window._rfCharts) {
      window._rfCharts.forEach(chart => {
        if (chart && typeof chart.update === 'function') {
          chart.update();
        }
      });
    }
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme'],
  });
}

// Mulai memantau tema saat DOM siap
document.addEventListener('DOMContentLoaded', function () {
  if (typeof Chart !== 'undefined') {
    applyChartDefaults();
    reinitChartsOnThemeChange();
  }
});
