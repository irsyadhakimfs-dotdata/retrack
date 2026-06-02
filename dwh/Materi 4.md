# Pengembangan Data Warehouse

## Metodologi Data Warehouse

### Pendekatan Pengembangan Data Warehouse

Dua pendekatan utama dalam membangun Data Warehouse:

- Bill Inmon: *The Father of Data Warehousing*
- Ralph Kimball: *The Father of Data Mart Design*

---

## Pendekatan Inmon

### Definisi
Membuat Data Warehouse sebagai repositori pusat sebelum membangun Data Marts.

### Arsitektur
- Data Warehouse (DWH) terpusat dibangun terlebih dahulu.
- Data Marts dibangun berdasarkan kebutuhan bisnis setelah Data Warehouse tersedia.

### Struktur Data
- Menggunakan Third Normal Form (3NF).
- Data terstruktur dan terorganisir untuk menghindari redundansi.

### Arsitektur Inmon (Lanjutan)
- Setelah Enterprise Data Warehouse (EDW) terbentuk, Data Marts dapat dibangun berdasarkan kebutuhan analisis spesifik.
- Data Marts mengambil data dari EDW dan tidak selalu menerapkan Star Schema.
- Bentuk Data Mart dapat berbeda sesuai kebutuhan organisasi, namun tetap menjaga integrasi dan konsistensi data dari EDW.

### Keunggulan Inmon
- Data konsisten dan terintegrasi.
- Skalabilitas tinggi.
- Menyediakan pandangan menyeluruh terhadap data organisasi.

### Kekurangan Inmon
- Waktu implementasi lebih lama.
- Membutuhkan biaya investasi awal yang besar.

---

## Pendekatan Kimball

### Keunggulan Kimball
- Waktu implementasi lebih cepat.
- Biaya lebih rendah.
- Fokus langsung pada kebutuhan bisnis.

### Kekurangan Kimball
- Konsistensi data dapat berkurang jika Data Mart tidak terintegrasi dengan baik.
- Pemeliharaan menjadi lebih rumit saat jumlah Data Mart bertambah.

---

# Data Flow Architecture

## 1. Single DDS

Arsitektur paling sederhana.

### Komponen
- Stage Area untuk data mentah.
- DDS (Dimensional Data Store) untuk data yang telah diproses.

### Proses
1. Data masuk ke Stage Area.
2. Data ditransformasi ke format dimensional.
3. Data disimpan di DDS.

### Keunggulan
- Implementasi cepat.
- Maintenance lebih mudah.
- Cocok untuk proyek kecil hingga menengah.

---

## 2. NDS + DDS

Arsitektur dengan normalisasi data.

### Komponen
- Stage Area untuk data mentah.
- NDS (Normalized Data Store) untuk data ternormalisasi.
- DDS (Dimensional Data Store) untuk data dimensional.

### Proses
1. Data masuk ke Stage Area.
2. Data dinormalisasi di NDS.
3. Data ditransformasi ke format dimensional di DDS.

### Keunggulan
- Data lebih terstruktur.
- Mengurangi redundansi.
- Memudahkan pelacakan perubahan data.

---

## 3. ODS + DDS

Arsitektur untuk data operasional dan historikal.

### Komponen
- Stage Area untuk data mentah.
- ODS (Operational Data Store) untuk data operasional real-time.
- DDS (Dimensional Data Store) untuk data historikal.

### Proses
1. Data operasional masuk ke ODS.
2. Data historikal masuk ke DDS.
3. Sistem dapat menghasilkan laporan real-time dan analisis historikal.

### Keunggulan
- Mendukung analisis real-time.
- Memisahkan data operasional dan historikal.
- Fleksibel untuk berbagai jenis analisis.

---

## 4. Federated Data Warehouse

Arsitektur untuk integrasi banyak Data Warehouse.

### Komponen
- Multiple Data Warehouse atau Data Mart.
- Layer federasi.
- Aturan bisnis untuk integrasi.

### Proses
1. Data dari berbagai sumber diintegrasikan.
2. Standardisasi dilakukan menggunakan aturan bisnis.
3. Sistem menyediakan tampilan data yang terpadu.

### Keunggulan
- Sangat fleksibel.
- Dapat mengintegrasikan sistem legacy.
- Mendukung otonomi masing-masing Data Warehouse.

---

# Software Pembangunan Data Warehouse

## 1. Amazon Redshift

Platform Data Warehouse berbasis cloud dari Amazon yang dirancang untuk analisis data skala besar.

---

## 2. Panoply

Platform Data Warehouse berbasis cloud yang mengotomatisasi proses integrasi dan pengelolaan data.

---

## 3. BigQuery

Platform Data Warehouse serverless dari Google yang mendukung analisis data dalam skala besar menggunakan SQL.

---

# Ringkasan

Terdapat dua pendekatan utama dalam pembangunan Data Warehouse:

| Inmon | Kimball |
|---------|---------|
| Data Warehouse dibangun terlebih dahulu | Data Mart dibangun terlebih dahulu |
| Menggunakan 3NF | Menggunakan Star Schema |
| Integrasi tinggi | Implementasi cepat |
| Biaya lebih besar | Biaya lebih rendah |
| Cocok untuk perusahaan besar | Cocok untuk kebutuhan bisnis yang spesifik |

Selain itu terdapat beberapa arsitektur Data Flow yang umum digunakan:

- Single DDS
- NDS + DDS
- ODS + DDS
- Federated Data Warehouse

Beberapa software populer untuk pembangunan Data Warehouse:

- Amazon Redshift
- Panoply
- Google BigQuery