# Enterprise Data, Data Mart, Kualitas Data


## Slide 1

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Enterprise Data, Data Mart, 
Kualitas Data
Pertemuan 3:


## Slide 2

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik
Data Warehouse


## Slide 3

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Warehouse
Secara umum Karakteristik Data Warehouse yaitu:
• Subject-Oriented
• Integrated
• Nonvolatile
• Time-Variant


## Slide 4

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Warehouse
1. Subject Oriented 
Maksud beorientasi pada subject:
• data pada DW terorganisasi berdasarkan subjek
utama, seperti pelanggan, penjualan, atau produk;
• difokuskan untuk pemodelan dan analisis data
untuk pembuat keputusan, bukan untuk operasi
sehari-hari atau pemrosesan transaksi;
Contoh: Sebuah perusahaan retail mengembangkan data warehouse
dengan subjek utama "penjualan." Data ini mencakup:
• Riwayat transaksi (tanggal, waktu, jumlah, lokasi).
• Kategori produk yang terjual.
• Profil pelanggan (usia, lokasi, preferensi).


## Slide 5

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Warehouse
2. Integrated
Maksud terintegrasi:
• Dibangun dengan mengintegrasikan
berbagai sumber data yang heterogen
menjadi satu.
• Contoh:
 Bank mengintegrasikan data dari
rekening tabungan (saving
account), rekening giro (checking
account), dan pinjaman (loans
account) untuk menentukan skor
kredit nasabah.


## Slide 6

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Warehouse
3. Non-Volatile
Maksud Nonvolatile:
• Tempat penyimpanan fisik data pada DW terpisah dari data operasional, perubahan pada data
tidak terjadi di DW tapi di basis data operasional.
• Operasi pada DW hanya pemuatan awal dan akses (insert dan read), tidak ada operasi update,
delete, recovery, dan mekanisme kontrol konkuren.
Contoh: Bank menyimpan data transaksi
nasabah untuk analisis historis dan 
pelaporan keuangan. Data transaksi
seperti deposito, penarikan, 
pembayaran pinjaman, dan transfer 
tetap tersimpan di data warehouse.


## Slide 7

Universitas Brawijaya - Building Up Noble Future
U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r e
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Warehouse
4. Time-Variant
Maksud Time-Variant:
• Rentang waktu data lebih lama dari pada data di sistem operasional.
• Setiap struktur kunci pada DW memiliki elemen waktu, baik secara 
eksplisit maupun implisit. 
Contoh: Bank menyimpan data historis
saldo rekening nasabah untuk
menganalisis pola tabungan atau
penggunaan dana.
Data saldo harian, mingguan,
atau bulanan disimpan untuk
setiap nasabah.


## Slide 8

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Data Mart


## Slide 9

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Tipe Utama Data Warehouse
• Enterprise Data Warehouse (EDW): Data warehouse skala
besar untuk seluruh perusahaan.
• Data Mart (DM): Subset dari data warehouse, fokus pada 
subjek atau departemen tertentu.


## Slide 10

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
~Enterprise Data Warehouses (EDW)
• Enterprise Data Warehouse (EDW) adalah gudang data yang digunakan
di seluruh organisasi untuk menyediakan pandangan terpusat dari
semua data perusahaan. 
• EDW mengintegrasikan data dari berbagai sumber untuk mendukung
Business Intelligence (BI) dan pengambilan keputusan strategis.


## Slide 11

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
~Data Mart (DM)
• Data Mart adalah subset dari data warehouse yang lebih
kecil dan terfokus pada area tertentu dari bisnis atau
departemen tertentu, seperti pemasaran, keuangan, atau
operasional.
• Data mart sering digunakan untuk memberikan akses
yang lebih cepat dan lebih spesifik kepada pengguna
yang memerlukan data terfokus


## Slide 12

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Karakteristik Data Mart
• Fokus pada Area Bisnis Tertentu
• Ruang Lingkup Terbatas
• Dibangun Berdasarkan Kebutuhan Pengguna Akhir
• Dapat Dibangun Secara Mandiri atau Berasal dari
EDW 
• Mendukung Pengambilan Keputusan di Level 
Departemen


## Slide 13

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Penggunaan Data Mart
Data Mart Penjualan:
• Berisi data transaksi penjualan, jumlah produk yang terjual, pendapatan per wilayah, 
analisis pelanggan, dan kinerja produk.
• Dapat digunakan oleh tim penjualan dan pemasaran untuk menganalisis tren
penjualan, mengidentifikasi produk terlaris, dan merencanakan kampanye
pemasaran.
Data Mart Sumber Daya Manusia (SDM):
• Menyimpan data terkait karyawan, seperti rekrutmen, gaji, kinerja karyawan, 
pelatihan, dan absensi.
• Dapat digunakan oleh tim HR untuk menganalisis turnover karyawan, mengelola
pelatihan, atau melakukan analisis kinerja.


## Slide 14

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id


## Slide 15

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Operational 
Data Store


## Slide 16

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id


## Slide 17

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Operational Data Store (ODS)
• Operational Data Store (ODS) menyimpan data operasional yang terkini dan sering
kali digunakan sebagai tempat penyimpanan sementara sebelum data dipindahkan
ke EDW. 
• Tidak cocok untuk analisis jangka panjang tetapi sangat berguna untuk pemantauan
waktu nyata.
• ODS menjadi jembatan antara sistem operasional (yang mengelola transaksi harian) 
dan Data Warehouse (yang mengelola analisis historis) / area staging


## Slide 18

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Karakteristik ODS
• ODS sering menggunakan Third Normal Form (3NF) atau struktur
yang mendekati bentuk normalisasi database relasional
• ODS mengumpulkan dan mengintegrasikan data dari berbagai sistem
operasional
• Data Real-Time atau Near Real-Time
• Tidak Berfokus pada Analisis


## Slide 19

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
ODS vs Data Warehouse
• Siklus Data: Data dari sistem operasional -> ODS -> diproses dan dibersihkan -> 
DWH. 
• Fokus Berbeda:
- ODS: Kecepatan akses data untuk operasi sehari-hari.
- DWH: Volume data besar untuk analisis jangka panjang.
• ETL Process: ODS menyiapkan data sebelum diekstrak, ditransformasi, dan dimuat 
(ETL) ke Data Warehouse.
• Peran ODS sebagai Buffer: Mencegah pembaruan data yang terlalu sering ke 
DWH, menjaga stabilitas DWH.
• Integrasi Data: ODS mengonsolidasikan data dari berbagai sumber, sehingga DWH 
dapat fokus pada analisis dan laporan yang lebih dalam.


## Slide 20

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Kualitas Data


## Slide 21

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Kualitas adalah konsep kunci dalam pembangunan Data Warehouse, di mana semua tahapan
dalam pembangunan Data Warehouse. Oleh karena itu, penting kiranya pemahaman mengenai
dimensi kualitas khususnya kualitas data di setiap fase Pembangunan Data Warehouse.
Beberapa survei menunjukkan presentase yang signifikan atas kegagalan Data Warehouse
memenuhi harapan bahkan gagal total. Tingkat kegagalan bervariasi, ada yang menyebutkan
antara 20% hingga 50% (Agosta, 2004; Conner, 2003; Watson et al, 2001). Kegagalan ini
disebabkan karena penyebab tunggal yaitu tidak adanya kualitas. Oleh karena itu dirasa perlu
untuk menentukan dimensi Data Quality apa saja yang sangat penting dalam Pembangunan
Data Warehouse.


## Slide 22

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Kualitas data mengukur seberapa
baik kumpulan data memenuhi
kriteria untuk akurasi,
kelengkapan, validitas, konsistensi,
keunikan, ketepatan waktu dalam
Data Warehouse


## Slide 23

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Faktor kunci dalam membangun Data Warehouse
adalah perbaikan proses informasi untuk
meningkatkan kinerja organisasi. Aspek ini berkaitan
dengan kapan dan bagaimana data diterapkan dalam
pengambilan Keputusan.
Dalam pengambilan Keputusan, informasi mengurangi
ketidakpastian, memungkinkan organisasi bereaksi
secara cepat terhadap peristiwa bisnis, dan
mendukung organisasi dalam membuat perubahan
strategi Perusahaan, rencana, dan indicator kinerja.


## Slide 24

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Empat sudut pandang yang mendasari kualitas
informasi menurut (Eppler, 2006) yaitu:
1. Relevansi/ relevance
2. Kondisi Baik/ soundness
3. Proses/ process
4. Infrastruktur/ infrastructure


## Slide 25

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id


## Slide 26

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Informasi yang relevan adalah informasi yang memadai bagi yang
membutuhkannya. Hal ini menunjukkan ruang lingkup informasi yang
komprehensif, dengan ketepatan dan Tingkat perincian yang mencukupi serta
kejelasan argumentasi sehingga mudah diterapkan.
Informasi yang baik adalah informasi yang memiliki karakteristik intrinsic
tertentu yang menjadikannya berkualitas tinggi terlepas dari komunitas yang
berhubungan dengan informasi tersebut.


## Slide 27

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Kualitas Data di Fase-Fase 
Pembangunan Data 
Warehouse


## Slide 28

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Dalam proses Pembangunan Data Warehouse,
data diproses melalui beberapa fase, di mana
setiap fase menghasilkan perubahan data untuk
memenuhi kebutuhan pengguna melalui informasi
dalam bentuk laporan. Semua fase selaing
mempengaruhi, karena output dari satu fase
menjadi input untuk fase berikutnya. Memahami
dimensi Data Quality secara menyeluruh adalah
Langkah awal dalam meningkatkan kualitas Data
Warehouse


## Slide 29

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Fase Analisis Kebutuhan
Data Quality sering diartikan sebagai kesesuaian penggunaan fitness for use. Penilaian Data
Quality mempertimbangkan sejauh mana data memenuhi kebutuhan pengguna. Beberapa
dimensi seperti konsistensi dan ketepatan waktu dapat dinilai secara objektif externally driven.
Namun, untuk pendekatan berbasis pengguna user-driven, dimensi tertentu, seperti
keringkasan, lebih subjektif dan bergantung pada persepsi pengguna.
Perspektif Goal-Driven
Dari perspektif pembuat keputusan, tidak semua informasi tersedia dalam format yang
mendukung pengambilan keputusan. Karena itu, dimensi seperti akurasi, konsistensi, ketepatan
waktu, keterlacakan, interaktivitas, kemudahan perawatan, dan kecepatan menjadi penting
dalam pendekatan berbasis tujuan.


## Slide 30

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Pendekatan Data-Driven
Jika data tidak cukup mendukung analisis, seperti data yang berasal dari sistem
ERP yang kompleks, dimensi seperti akurasi, konsistensi, kebenaran, kekinian,
dan aksesibilitas menjadi fokus utama untuk menjamin kualitas analisis.
Pendekatan Process-Driven
Dalam pendekatan berbasis proses, pengambil keputusan perlu memahami
keseluruhan proses bisnis dan data terkait untuk analisis menyeluruh. Dimensi
utama yang diperhatikan adalah akurasi, konsistensi, ketepatan waktu,
keterlacakan, dan kecepatan.


## Slide 31

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id
Model Konseptual dan Data Warehouse
Model konseptual organisasi menentukan kualitas DW berdasarkan faktor-faktor seperti
akurasi, konsistensi, kebenaran, kekinian, keterlacakan, aksesibilitas, dan kecepatan. Desain
logis DW, melalui skema bintang dan OLAP, memastikan akses efisien dan penyimpanan data
yang mendukung dimensi kualitas ini. Skema bintang membantu memodelkan data, sedangkan
OLAP memungkinkan analisis multidimensional, dengan fokus pada dimensi keringkasan,
keamanan, dan kenyamanan.
Perspektif Goal-Driven
Secara fisik, arsitektur DW mencakup jaringan penyimpanan, transformasi, dan komunikasi
data. Dimensi utama seperti akurasi, konsistensi, kekinian, ketepatan waktu, dan pemeliharaan
menjadi prioritas karena volume data yang terus berubah.


## Slide 32

Universitas Brawijaya - Building Up Noble Future
Universitas Brawijaya - Building Up Noble Future
brone.ub.ac.id
brone.ub.ac.id


## Slide 33

Tim Dosen
1
 Dr. Adji Achmad Rinaldo
Fernandes, S.Si., M.Sc. 2 Meilina Retno Hapsari, 
S.Si., M.Stat


## Slide 34

brone.ub.ac.id
brone.ub.ac.id
Thank You
Data Warehouse
