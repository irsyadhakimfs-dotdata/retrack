# Desain Data Warehouse


## Slide 1

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Data 
Warehousing
Desain Data Warehouse



## Slide 2

brone.ub.ac.id
Outline 
Conceptual Design01
Logical Desain02
Physical Design03
Studi Kasus04



## Slide 3

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 4

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Conceptual
Design



## Slide 5

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Conceptual Design
• Desain konseptual dalam Data Warehouse (DW) adalah tahap
awal yang mendefinisikan struktur multidimensional untuk
merepresentasikan proses dan arsitektur DW secara abstrak, 
mencakup fakta, dimensi, serta hierarki kategorisasi guna
mendokumentasikan kebutuhan pengguna, meskipun belum
ada standar universal yang disepakati.



## Slide 6

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 7

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Pendekatan Pemodelan Multidimensional
• Berbasis Entitas (E/R): Stabil, fleksibel, dan telah lama 
digunakan.
• Berorientasi Objek: Representasi lebih dinamis, mendukung
UML sebagai standar.
• Model Ad Hoc: Notasi lebih efektif, ekspresi multidimensional 
lebih baik



## Slide 8

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Pendekatan Pemodelan Multidimensional
Berbasis Entitas (E/R): Menggunakan konsep entitas, atribut, dan relasi, sudah lama dipakai dalam
mendesain basis data yang stabil, fleksibel dan dapat diandalkan.
• Contoh : Data penjualan produk di toko ritel. Model E/R dapat terdiri dari beberapa entitas seperti Produk, 
Waktu, Toko, dan Penjualan. Relasi antar entitas menggambarkan hubungan seperti produk yang dijual pada
waktu tertentu di toko tertentu.
• Entitas:
Produk (ID_Produk, Nama_Produk, Kategori, Harga)
Toko (ID_Toko, Nama_Toko, Lokasi)
Waktu (ID_Waktu, Tanggal, Bulan, Tahun)
Penjualan (ID_Penjualan, ID_Produk, ID_Toko, ID_Waktu, Jumlah, Total_Penjualan)
• Relasi:
Penjualan menghubungkan Produk, Toko, dan Waktu dengan informasi penjualan (Jumlah, Total_Penjualan).
• Diagram E/R:
Penjualan (ID_Penjualan) akan menghubungkan entitas Produk, Toko, dan Waktu.
Relasi one-to-many dapat diterapkan antara Penjualan dan Produk, Toko, serta Waktu.



## Slide 9

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Pendekatan Pemodelan Multidimensional
Berorientasi Objek: Representasi lebih dinamis, mendukung UML 
(Unified Modeling Language) sebagai standar.
• Contoh :
Dalam model berorientasi objek, kita akan mendefinisikan kelas-kelas yang 
merepresentasikan entitas dan hubungan antar entitas. Misalnya, kita dapat
memiliki kelas seperti Produk, Toko, Waktu, dan Penjualan, dan setiap objek
dalam kelas tersebut akan memiliki atribut dan metode terkait.
• Kelas
Produk: Atribut: ID_Produk, Nama_Produk, Kategori, Harga
Toko: Atribut: ID_Toko, Nama_Toko, Lokasi.
Waktu: Atribut: ID_Waktu, Tanggal, Bulan, Tahun.
Penjualan: Atribut: ID_Penjualan, Produk, Toko, Waktu, Jumlah, Total_Penjualan.
• Diagram UML:
Model ini akan menggunakan diagram kelas untuk mendeskripsikan relasi antar
objek. Relasi antar objek bisa digambarkan sebagai asosiasi antara kelas-kelas, 
dan setiap kelas dapat memiliki operasi yang mengakses data atau melakukan
perhitungan.



## Slide 10

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Pendekatan Pemodelan Multidimensional
Model Ad Hoc: nalisis multidimensi secara langsung, menyajikan dalam bentuk dimensi fakta dan hirarki, efektif untuk
analisis atau pengambilan keputusan
Contoh :
Tanpa perlu merancang ulang database, dengan menggunakan model ad hoc sudah dapat menghasilkan laporan yang 
diinginkan secara cepat menggunakan alat OLAP seperti BI atau kueri SQL yang memungkinkan pengguna untuk menggali
data dengan cara yang lebih interaktif dan langsung. Dalam hal ini, data penjualan bisa dilihat dari berbagai perspektif seperti
penjualan per produk, penjualan per toko, atau penjualan per waktu.
• Dimensi:
Dimensi Produk: ID_Produk, Nama_Produk, Kategori
Dimensi Toko: ID_Toko, Nama_Toko, Lokasi
Dimensi Waktu: ID_Waktu, Tanggal, Bulan, Tahun
Fakta Penjualan: Jumlah, Total_Penjualan
• Struktur Cube (OLAP Cube):
Data penjualan bisa dianalisis dalam bentuk cube multidimensional, di mana dimensi produk, toko, dan waktu menjadi sumbu
untuk menganalisis fakta penjualan.
Pengguna bisa melakukan drill-down untuk melihat detail lebih lanjut, misalnya penjualan per bulan atau penjualan per produk
dalam satu toko.
Pengguna juga bisa melakukan drill-up untuk mendapatkan gambaran lebih luas, misalnya total penjualan per tahun.



## Slide 11

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Model Konseptual Multidimensional
• Multidimensional Entity Relationship (ME/R): Mengadaptasi E/R untuk OLAP.
• Dimensional Fact Model (DFM): Skema pohon dengan fakta sebagai akar, tetapi
tidak mendukung generalisasi/spesialisasi dan hubungan banyak ke banyak.
• Fact Schema: Menggunakan konsep entitas dan hubungan antar dimensi.



## Slide 12

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Identifikasi dalam Desain Konseptual DW
1. Identifikasi Fakta (Fact)
• Fakta adalah data utama dalam analisis bisnis.
• Ditentukan dari hubungan many-to-many dalam E/R.
• Berisi nilai numerik yang dapat diagregasikan (misal penjualan, pendapatan).
• Dapat ditemukan dari query bisnis atau entitas yang sering diperbarui.
2. Identifikasi Hirarki Dimensional
• Granularitas: Tingkat kedetailan data dalam DW.
• Hierarki Sederhana: Satu jalur agregasi linier (misal Hari → Bulan → Tahun).
• Hierarki Multi Dimensi: Memiliki lebih dari satu jalur agregasi.
• Mendukung navigasi drill-up dan drill-down untuk analisis data.



## Slide 13

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
3. Identifikasi Ukuran
Ukuran adalah atribut numerik dari fakta yang bisa dihitung.
Contoh ukuran: Sum, Count, Average, Min, Max.
4. Identifikasi Agregasi (Aggregation)
• Agregasi merangkum informasi dari berbagai sumber.
• Berfungsi untuk mempercepat query OLAP dan menyusun ringkasan data 
pada level tertinggi.
• Jika ada kendala agregasi, skema harus disusun secara eksplisit.
Identifikasi dalam Desain Konseptual DW
Tanggal Produk Kota Jumlah Harga
21-04-2026 Indomie Surabaya 2 3.000
21-04-2026 Aqua Surabaya 1 4.000
22-04-2026 Indomie Malang 3 3.000
Bulan Total Penjualan
April 2026 (2×3000 + 1×4000 + 3×3000) 
= 19.000



## Slide 14

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Logical Design



## Slide 15

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 16

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 17

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Logical Design
• Logical design adalah desain DW yang berbentuk konsep dan abstrak. 
Model yang bisa digunakan untuk menggambarkan logical design adalah
Entity Relationship Modeling (ERM) atau Entity Relationship Diagram 
(ERD).
• ERM adalah proses identifikasi entitas atribut dan relasi (kerangka saja), 
sedangkan ERD adalah representasi visual dari hasil pemodelan tersebut
bentuk diagram. 
• Terdapat 3 schema yang dapat digunakan untuk memodelkan fakta dan
dimensi pada data warehouse yaitu star schema, snowflake schema, dan
fact constellation schema. Perbedaan ketiganya ada pada normalisasi
tabel dimensi dan kompleksitas hubungan antara fakta dan dimensi.



## Slide 18

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
1. Star Schema
• Star schema adalah skema DW yang berbentuk seperti
bintang di mana terdapat 1 tabel fakta yang dihubungkan
dengan tabel-tabel dimensinya.
• Kelebihan dari star schema adalah kesederhanaan desain
dan konsistensinya karena hanya memiliki 1 level dimensi.
Satu level tabel dimensi berati tabel dimensi tidak dilakukan
normalisasi. Hal ini juga akan mempermudah saat melakukan
proses ETL. Kinerja dari pengambilan data untuk analisis
query akan lebih cepat jika menggunakan star schema
karena query join yang diperlukan antara tabel fakta dan
dimensi menjadi lebih sedikit jika dibandingkan snowflake
schema.
• Kelemahan
- terjadinya duplikasi data pada tabel fakta. Karena dalam star schema, data faktual disimpan berulang-ulang
untuk setiap entitas yang relevan.
- dalam beberapa kasus, terdapat redudansi data yaitu data yang terhubung ke tabel fakta diulang dalam
tabel dimensi yang berbeda.
- kurang fleksibel untuk analisis kompleks



## Slide 19

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Star Schema 1
Tabel Fakta : Revenue yang menyimpan data 
transaksi utama seperti Units_Sold dan Revenue, 
serta beberapa Dimension Table yang terhubung 
langsung ke Fact Table. 
Tabel Dimensi :
-Dealer, yang berisi informasi tentang lokasi dan 
kontak dealer
-Branch Dim, yang menyimpan data cabang;
-Date Dim, yang mencatat aspek waktu seperti tahun, 
bulan, dan kuartal
-Product, yang menyimpan detail produk termasuk 
nama, model, dan varian. 
Hubungan antara Fact Table dan Dimension Table
menggunakan kunci asing (Foreign Keys).



## Slide 20

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Star Schema 2
Tabel Fakta :
Tabel Dimensi :
Foreign Key :



## Slide 21

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
2. Snowflake Schema
• Snowflake schema adalah skema data warehouse yang
merepresentasikan dimensinya dengan konsep normalisasi.
Normalisasi hingga bentuk 3NF (Third Normal Form) atau lebih
tinggi, dilakukan untuk menghilangkan redudansi data.
• Kelebihan dari penggunaan snowflake schema adalah beberapa
aplikasi analitis bekerja lebih baik dengan snowflake schema
dibandingkan dengan star schema. Struktur tabel dimensi yang
ternormalisasi juga memudahkan dalam melakukan update dan
maintenance DW.
• Kelemahan
- Desain yang Lebih Kompleks dan pemeliharaan yang rumit
- Kinerja query lebih lembat karena join yang lebih banyak yg
disebabkan tabel dimensi terpisah menjadi beberapa tabel.
- Kebutuhan Penyimpanan yang lebih banyak
- Kurang Efisien dalam Penggunaan OLAP



## Slide 22

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
2. Snowflake Schema
Contoh:
• Sebuah tabel Customer yang awalnya memiliki atribut Region, City, dan Detail dapat 
dipecah menjadi tiga tabel berbeda:
• Customer Region (menyimpan informasi wilayah pelanggan),
• Customer City (menyimpan informasi kota pelanggan),
• Customer Detail (menyimpan informasi spesifik pelanggan).
• Dengan cara ini, setiap tabel hanya menyimpan informasi yang berkaitan langsung 
dengan entitasnya, menghindari duplikasi data antar entitas.



## Slide 23

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Snowflake Schema 1
Gambar tersebut terdapat 2 dimensi yang dinormalisasi yaitu dimensi item dan location. Tidak
semua tabel dimensi pada snowflake schema harus dinormalisasi. Pada praktiknya proses 
pembuatan snowflake schema bisa dimulai dari star schema terlebih dahulu.
Star Schema    Snowflake Schema



## Slide 24

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Snowflake Schema 2
Star Schema  Snowflake Schema



## Slide 25

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
3. Fact constellation schema
• Fact constellation schema atau galaxy schema adalah
skema DW yang terdiri dari 2 atau lebih tabel fakta yang 
saling terhubung (related fact tables) dan dikelilingi oleh 
dimensi-dimensi. 
• Keuntungan dari galaxy schema adalah kemampuannya
untuk memodelkan bisnis lebih akurat dan menyeluruh
dengan menggunakan beberapa tabel fakta. Pemilihan
skema harus disesuaikan dengan kebutuhan analisis
data dari perusahaan atau organisasi. 
• Kelemahan
- Kompleksitas desain yang tinggi dan kesulitan dalam pemeliharaan
- Kinerja query lebih lembat
- Kebutuhan penyimpanan yang lebih banyak
- Kurang efisien dalam Penggunaan OLAP
- Pengelolaan dimensi yang rumit, dimensi yang tumpang tindih karena tabel dimensi digunakan bersama
oleh beberapa tabel fakta



## Slide 26

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Fact constellation Schema 1



## Slide 27

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Contoh Fact constellation Schema 2
TPD : Teacher Professional Development
Penempatan kerja dan Pelatihan Mahasiswa



## Slide 28

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Physical Design



## Slide 29

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 30

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id



## Slide 31

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Physical Design
• Physical design mencakup proses mengubah entitas menjadi tabel, mendeskripsikan
atribut sebagai kolom, serta menentukan tipe data yang sesuai. Selain itu, physical 
design juga melibatkan penetapan integrity constraint seperti primary key, foreign key, 
atau not null pada setiap kolom.
• Untuk optimasi query, proses ini mencakup pembuatan indeks pada tabel, melakukan
partition table, dan membuat materialized views untuk menyimpan hasil query yang 
sering dipakai jika diperlukan.
• Physical design digambarkan menggunakan Physical Data Model (PDM), yang 
kemudian dikonversi menjadi Data Definition Language (DDL). Selain itu, proses ini
juga mencakup pengaturan buffer pools dan table space, serta implementasi strategi
partisi tabel guna meningkatkan efisiensi sistem.
Tabel Fakta : Penjualan
id_fakta (PK, integer)
id_produk (FK)
id_waktu (FK)
jumlah (integer)
total_penjualan (decimal)
CREATE TABLE Fakta_Penjualan (
id_fakta INT AUTO_INCREMENT PRIMARY KEY,
id_produk VARCHAR(10),
id_waktu DATE,
jumlah INT,
total_penjualan DECIMAL(15,2)
);



## Slide 32

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Primary Key pada Tabel Fakta dan Tabel Dimensi
1. Single Compound Primary Key
Pada metode ini, tabel fakta memiliki satu primary key yang dibentuk dari kombinasi primary key
dari tabel-tabel dimensi. Metode ini memiliki kekurangan, yaitu ukuran penyimpanan tabel fakta
menjadi lebih besar. Single Compound Primary Key bisa untuk semua database.
• Dalam desain data warehouse, terdapat tiga pilihan dalam menentukan primary key pada 
tabel fakta, yaitu:
nim kode_mk nilai
101 IF101 80
101 IF102 85
102 IF101 75
1 mahasiswa bisa ambil banyak mata kuliah
1 mata kuliah diambil banyak mahasiswa
keunikan data hanya bisa dijamin dengan kombinasi beberapa kolom



## Slide 33

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Primary Key pada Tabel Fakta dan Tabel Dimensi
2. Concatenated Primary Key
Pada metode ini, semua primary key dari tabel dimensi digabungkan menjadi composite primary
key dalam tabel fakta. Model ini sering digunakan karena dapat menghemat ukuran penyimpanan
dibandingkan metode sebelumnya. Selain itu, pembuatan query menjadi lebih mudah karena tabel
fakta langsung terhubung dengan tabel dimensi.
Semua concatenated primary key adalah compound primary key. Tapi tidak semua compound
primary key adalah concatenated primary key
id_produk nama_produk
P01 Laptop
P02 HP
id_waktu tanggal
W01 2026-01-01
W02 2026-01-02
id_toko nama_toko
T01 TokoA
T02 Toko B
id_produk id_waktu id_toko jumlah total_penjualan
P01 W01 T01 2 20.000.000
P01 W02 T01 1 10.000.000
P02 W01 T02 3 9.000.000



## Slide 34

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Primary Key pada Tabel Fakta dan Tabel Dimensi
3. Generated Primary Key
Dalam metode ini, primary key tabel fakta dibuat secara independen tanpa bergantung pada
primary key dari tabel dimensi. Contohnya, primary key dapat dibuat menggunakan auto
increment.
id_produk (PK) nama_produk
P01 Laptop
P02 HP
id_waktu (PK) tanggal
W01 2026-01-01
W02 2026-01-02
id_toko (PK) nama_toko
T01 Toko A
T02 Toko B
id_penj
ualan
(PK)
id_produk
(FK)
id_waktu 
(FK)
id_toko 
(FK) jumlah total_penjualan
1 P01 W01 T01 2 20.000.000
2 P02 W01 T02 3 9.000.000
3 P01 W02 T01 1 10.000.000



## Slide 35

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Jenis primary key apa yang digunakan?



## Slide 36

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Buffer Pool dan Table Space Untuk DW 
• Buffer pool adalah sebuah area utama pada memory yang telah dialokasikan oleh 
pengelola basis data dengan tujuan untuk penyimpanan sementara (caching) tabel dan 
indeks data saat dibaca dari disk. 
• Penggunaan buffer pool dapat meningkatkan kinerja karena dapat mengurangi proses 
input/output dan optimasi pembacaan query pada DBMS. Sebuah buffer pool dapat
digunakan untuk lebih dari satu table space. Namun 1 table space hanya dapat
menggunakan 1 buffer pool. 
Gambar di samping menunjukkan
format query untuk pengaturan ukuran
page size saat membuat buffer pool.



## Slide 37

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Table Space Untuk DW 
• Table space adalah struktur penyimpanan yang berisi tabel, indeks, large 
object dan long data. Table space digunakan untuk mengelola data dalam
basis data ke penyimpanan logis (logical storage) yang berhubungan dengan
tempat data disimpan pada suatu system.
Gambar diatas menunjukkan hubungan
antara basis data, table space dan tabel. 
CREATE TABLESPACE <nama table space> 
PAGESIZE 32K 
MANAGED BY AUTOMATIC STORAGE 
BUFFERPOOL <nama buffer pool> 
Contoh pembuatan table space 
untuk penyimpanan logis tabel
fakta dengan ukuran page size 32 
KB. Ukuran page size buffer pool 
yang digunakan juga harus sama
32 KB.



## Slide 38

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Tabel Partisi 
• Tabel partisi membagi data-data yang disimpan pada tabel tersebut ke dalam beberapa objek
penyimpanan, yang disebut dengan data partisi. Data dipartisi berdasarkan nilai dari kolom
yang dipartisi pada tabel tersebut. Cara melakukan partisi tabel dengan menggunakan klausa
PARTITION BY saat melakukan query CREATE TABLE. Penyimpanan data-data yang dipartisi
Contoh pembuatan tabel partisi dengan
peletakan data partisi pada table space 
yang berbeda. Data-data pada tabel
detail pembayaran dibagi berdasarkan
kolom waktu_transaksi yaitu dibagi
menjadi 2 partisi. Partisi pertama untuk
data transaksi tahun 2015 dan partisi
kedua untuk data transaksi tahun 2016. 
CREATE TABLE DETAIL PEMBAYARAN ( 
WAKTU TRANSAKSI TIMESTAMP, NIM VARCHAR(15), 
ID PROGRAM STUDI SMALLINT, 
ID SELEKSI SMALLINT, 
ID JENIS PEMBAYARAN SMALLINT, JUMLAH PEMBAYARAN DOUBLE, PRIMARY KEY 
(WAKTU TRANSAKSI, NIM, 
ID PROGRAM STUDI, ID SELEKSI, 
ID JENIS PEMBAYARAN) 
) 
IN TBSREG1 
INDEX IN TBSIDX1 
LONG IN TBSLRG1 
PARTITION BY RANGE (waktu_transaksi) ( 
STARTING FROM '2015-01-01 00:00:00' ENDING 
AT '2015-12-31 23:59:59' 
IN TBSPARTREG1 
INDEX IN TBSPARTIDX1 
LONG IN TBSPARTLRG1, 
STARTING FROM '2016-01-01 00:00:00' ENDING 
AT '2016-12-31 23:59:59' 
IN TBSPARTREG2 
INDEX IN TBSPARTIDX2 
LONG IN TBSPARTLRG2 
);



## Slide 39

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Tabel Partisi 
Data-data pada tabel detail pembayaran
dibagi berdasarkan kolom
waktu_transaksi yaitu dibagi menjadi 2 
partisi. 
Partisi pertama untuk data transaksi
tahun 2015 dan partisi kedua untuk data 
transaksi tahun 2016. 
waktu_transa
ksi NIM id_program_s
tudi
jumlah_pemb
ayaran
2015-03-10 22001 1 2.000.000
2015-07-21 22002 1 2.500.000
2016-02-11 22003 2 3.000.000
2016-08-05 22001 1 2.000.000
waktu_transa
ksi NIM id_program_s
tudi
jumlah_pemb
ayaran
2015-03-10 22001 1 2.000.000
2015-07-21 22002 1 2.500.000
waktu_transa
ksi NIM id_program_s
tudi
jumlah_pemb
ayaran
2016-02-11 22003 2 3.000.000
2016-08-05 22001 1 2.000.000



## Slide 40

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Slowly Changing Dimensions 
• Slowly changing dimensions adalah perubahan data pada tabel dimensi dapat
terjadi pada rentang waktu yang relatif lama. Pemilihan strategi penanganan slowly 
changing dimension harus melibatkan pemilik bisnis juga. 
• Langkah pertama dalam menangani slowly changing dimensions adalah
mengidentifikasi dimensi yang berubah pada skema DW yang telah dibuat. 
Kemudian mengomunikasikan dengan pemilik bisnis terkait strategi yang akan
digunakan untuk menangani perubahan dimensi. Berikut ini adalah 3 tipe strategi 
yang dapat digunakan untuk menangani perubahan data dimensi:
1) Type 1
Baris baru menggantikan baris yang lama. Tidak ada jejak rekaman untuk data yang 
lama. Sebagai contoh, pada gambar di bawah menunjukkan bahwa tidak ada data 
historis yang mencatat bahwa David pernah tinggal di New York.



## Slide 41

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Slowly Changing Dimensions 
2) Type 2
Baris baru ditambahkan pada tabel dimensi (membuat record baru) sehingga data 
lama tidak terhapus. Gambar di bawah ini menunjukkan contoh perubahan tempat
tinggal dari David yang tetap dicatat pada dimensi pelanggan. 
3) Type 3
Tabel dimodifikasi untuk mencerminkan perubahan. Data baru dimasukkan ke baris 
yang sama (tidak membuat record baru). Gambar berikut menunjukkan contoh
perubahan dicatat pada kolom current state dan tanggal perubahan data dicatat pada 
kolom effective date.



## Slide 42

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus



## Slide 43

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
Perusahaan ABC memiliki 3 kantor cabang berbeda. Data pegawai baru
selalu disimpan pada kantor cabang yang berbeda DBMS yaitu MySQL, DB2
dan Microsoft SQL Server. Saat ini pimpinan perusahaan ABC ingin
mengetahui perkembangan jumlah pegawai yang diterima di perusahaan
tersebut dari tahun ke tahun berdasarkan demografi jenis kelamin dan
departemen di mana pegawai tersebut ditempatkan. Solusi dari kebutuhan
pimpinan perusahaan ABC ini adalah dengan membuat data warehouse yang
dapat menyimpan jumlah pegawai baru secara keseluruhan dan detail jumlah
pegawai baru berdasarkan dimensi tahun masuk, demografi dan departemen.
Berikut ini adalah tahapan desain data warehouse yang meliputi analisis
kebutuhan dengan information package, membuat logical design dengan
model star schema dan membuat physical design dengan diagram dan DDL.



## Slide 44

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
Information Package DW Pegawai
Berdasarkan analisis kebutuhan data warehouse yang telah dijabarkan oleh pemilik
bisnis maka dibuatlah information package seperti pada Tabel 5. Information Package 
DW Pegawai. Tabel di bawah menjelaskan bahwa terdapat 3 dimensi yaitu tahun, 
demografi jenis kelamin dan departemen. Setiap dimensi dapat dijabarkan menurut
hierarki atau kategori. Fakta berisi pengukuran dari DW yaitu jumlah pegawai baru.



## Slide 45

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
Logical Design dengan Star Schema 
Berdasarkan information package pada table di slide sebelumnya, maka dibuatlah
desain star schema untuk DW pegawai baru seperti pada Gambar di bawah. Star 
schema dipilih karena semua dimensi hanya memiliki 1 hierarki sehingga tidak perlu
dilakukan normalisasi menjadi snowflake schema. Pada entitas pegawai baru
ditunjukkan pengukuran atau measurement yaitu jumlah pegawai baru. Desain star 
schema dapat dibuat seperti pada Gambar untuk menunjukkan hubungan antara
dimensi dan fakta saja ataupun menggunakan konsep Entity Relationship Diagram 
(ERD) yang dilengkapi dengan penjelasan atribut dan relasi.



## Slide 46

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
Physical Design Dw Pegawai
Setelah menentukan logical design maka tahapan selanjutnya adalah membuat
physical design. Phyisical Design menjelaskan secara lengkap kolom dan tipe data 
yang ada pada tabel fakta dan dimensi. Primary key yang digunakan pada tabel fakta
termasuk concatenated primary key di mana semua primary key pada tabel dimensi
digabungkan menjadi composite primary key pada tabel fakta. Setiap primary key pada 
tabel fact_employees sekaligus berperan sebagai foreign key di tabel fact_employees
yang diambil dari ketiga tabel dimensi. Physical Data Diagram DW Pegawai Baru 
sebagai berikut.



## Slide 47

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
DDL Buffer Pool dan Table Space
--PEMBUATAN BUFFERPOOL
CREATE BUFFERPOOL BFRDWEMP16K PAGESIZE 16K;
--TABLESPACE REGULER
CREATE REGULER TABLESPACEREG_HOT1
PAGESIZE 16K
MANAGED BY AUTOMATIC STORAGE
USING STOGROUP SG_HOT1
AUTORESIZE YES
BUFFERPOOL BFRDWEMP16K;
--TABLESPACE INDEX
CREATE LARGE TABLESPACEIDX_HOT1
PAGESIZE 16K
MANAGED BY AUTOMATIC STORAGE
USING STOGROUP SG_HOT1
AUTORESIZE YES
BUFFERPOOL BFRDWEMP16K;
--TABLESPACE LONG
CREATE LARGE TABLESPACELOB HOT1
PAGESIZE 16K
MANAGED BY AUTOMATIC STORAGE
USING STOGROUP SG_HOT1
AUTORESIZE YES
BUFFERPOOL BFRDWEMP16K;



## Slide 48

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 1 : Desain DW Pegawai
DDL Membuat Tabel Fakta dan Dimensi
--TABLE DIM_WAKTU 
CREATE TABLE DIM_WAKTU(
ID WAKTU SMALLINT NOT NULL PRIMARY KEY , T
AHUN YEAR 
) 
IN REG HOT1 
INDEX IN IDX HOT1
LONG IN LOB_HOT1; 
--TABLE DIM_DEMOGRAFI 
CREATE TABLE DIM_DEMOGRAFI(
ID_DEMOGRAFI SMALLINT NOT NULL PRIMARY KEY , 
JENIS_KELAMIN VARCHAR(25) 
) 
IN REG_HOT1 
INDEX IN IDX_HOT1
LONG IN LOB_HOT1; 
--TABLE DIM_DEPARTEMEN 
CREATE TABLE DIM_DEPARTEMEN( I
D_DEPARTEMEN SMALLINT NOT NULL PRIMARY KEY , 
NAMA_DEPARTEMEN VARCHAR(45) 
) 
--
IN REG_HOT1 
INDEX IN IDX_HOT1 
LONG IN LOB_HOT1; 
--TABLE FACT_EMPLOYEES 
CREATE TABLE FACT_EMPLOYEES ( 
ID_DEMOGRAFI SMALLINT NOT NULL, 
FOREIGN KEY(ID_DEMOGRAFI) REFERENCES 
DIM_DEMOGRAFI (ID_DEMOGRAFI), 
ID_WAKTU SMALLINT NOT NULL, 
FOREIGN KEY(ID_WAKTU) REFERENCES DIM_WAKTU 
(ID_WAKTU), ID_DEPARTEMEN SMALLINT NOT NULL, 
FOREIGN KEY(ID_DEPARTEMEN) REFERENCES 
DIM_DEPARTEMEN (ID_DEPARTEMEN), 
TOTAL_PEGAWAI BIGINT 
) 
IN REG_HOT1 
INDEX IN IDX_HOT1 
LONG IN LOB_HOT1;



## Slide 49

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
Toko X ingin membuat Data Warehouse untuk mempermudah menyimpan data 
hasil penjualan dan melakukan analisis terkait data penjualan. Rancangan Data 
Warehouse terdiri dari 1 tabel fakta yaitu penjualan dan 4  tabel dimensi.
• Tabel Dimensi : DimProduct, DimCustomer, DimDate, DimStore
• Tabel Fakta : FactSales



## Slide 50

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
Konseptual Design
Tabel DimProduct
ProductID
ProductName
Category
Brand
Price
TabelDimCustomer
CustomerID
CustomerName
Gender 
Email  
City
Tabel DimDate
DateID
Date 
Day 
Month 
Year
Tabel DimStore
StoreID
StoreName
StoreLocation
Tabel FactSales
SaleID
DateID
ProductID
CustomerID
StoreID
QuantitySold
TotalAmount



## Slide 51

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
Logical Design dengan Star Schema 
Berdasarkan information package pada table di slide sebelumnya, maka dibuatlah
desain star schema untuk DW penjualan seperti pada Gambar di bawah. Pada entitas
penjualan ditunjukkan pengukuran atau measurement yaitu QuantitySold dan Total 
Amount. Desain star schema dapat dibuat seperti pada Gambar untuk menunjukkan
hubungan antara dimensi dan fakta saja ataupun menggunakan konsep ERD yang 
dilengkapi dengan penjelasan atribut dan relasi. 
DimStore
DimDate
DimProduct
DimCustomer
FactSales



## Slide 52

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
Physical Design
Setelah menentukan logical design maka tahapan selanjutnya adalah membuat physical design. 
PDD menjelaskan secara lengkap kolom dan tipe data yang ada pada tabel fakta dan dimensi. 
Primary key yang digunakan pada tabel fakta termasuk generated primary key di mana semua
primary key pada tabel dimensi digabungkan menjadi composite primary key pada tabel fakta. 
Setiap primary key pada tabel Fact_Sales sekaligus berperan sebagai foreign key di tabel
Fact_Sales yang diambil dari keempat tabel dimensi.



## Slide 53

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
CREATE TABLE DimProduct (
ProductID NCHAR(10) PRIMARY KEY,
ProductName NVARCHAR(100) NOT NULL,
Category NVARCHAR(50),
Brand NVARCHAR(50),
Price NCHAR(20)
);
CREATE TABLE DimCustomer (
CustomerID NCHAR(10) PRIMARY KEY,
CustomerName NVARCHAR(100) NOT NULL,
Gender NVARCHAR(10),
Email NVARCHAR(100) UNIQUE,
City NVARCHAR(50)
);
CREATE TABLE DimDate (
DateID NCHAR(8) PRIMARY KEY,
Date DATE,
Day INT CHECK (Day BETWEEN 1 AND 31),
Month INT CHECK (Month BETWEEN 1 AND 12),
Year INT CHECK (Year BETWEEN 1900 AND 2100)
);
CREATE TABLE DimStore (
StoreID NCHAR(5) PRIMARY KEY,
StoreName NVARCHAR(100) NOT NULL,
StoreLocation NVARCHAR(100)
);
CREATE TABLE FactSales (
SaleID NCHAR(10) PRIMARY KEY,
DateID NCHAR(8),
ProductID NCHAR(10),
CustomerID NCHAR(10),
StoreID NCHAR(5),
QuantitySold INT,
TotalAmount DECIMAL(10,2),
FOREIGN KEY (DateID) REFERENCES DimDate(DateID),
FOREIGN KEY (ProductID) REFERENCES DimProduct(ProductID),
FOREIGN KEY (CustomerID) REFERENCES DimCustomer(CustomerID),
FOREIGN KEY (StoreID) REFERENCES DimStore(StoreID)
);
Membuat Tabel Dimensi dan Fakta dengan SQL Server



## Slide 54

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus 2: Desain DW Penjualan
Menampilkan Data dengan Star Scheme dengan SQL Server
SELECT
sf.SaleID,
dc.CustomerName,
dp.ProductName,
dp.Category,
ds.StoreName,
ds.StoreLocation,
dd.Date,
sf.QuantitySold,
sf.TotalAmount
FROM FactSales sf
JOIN DimCustomer dc ON sf.CustomerID = dc.CustomerID
JOIN DimProduct dp ON sf.ProductID = dp.ProductID
JOIN DimStore ds ON sf.StoreID = ds.StoreID
JOIN DimDate dd ON sf.DateID = dd.DateID;



## Slide 55

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Kegiatan Mandiri



## Slide 56

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Kegiatan Mandiri
Dinas Kesehatan ingin merancang sebuah data warehouse yang menyimpan data terkait rumah sakit atau
layanan kesehatan. Pada skema ini, tabel fakta berisi data terkait kunjungan pasien, dan tabel dimensi
mengorganisasi atribut terkait data tersebut seperti informasi pasien, dokter, rumah sakit, dan waktu.
• Tabel Fakta : Fact_Visits menyimpan informasi visit_id, patient_id, doctor_id, hospital_id, date_id, 
diagnosis_id, treatment_id, total_cost
• Tabel Dimensi :
1. Dim_Patient menyimpan informasi patient_id, patient_name, gender, birth_date, address_id
2. Dim_Doctor menyimpan informasi doctor_id, doctor_name, specialization_id
3. Dim_Hospital menyimpan informasi hospital_id, hospital_name, hospital_location
4. Dim_Date menyimpan informasi date_id, date, month_id, year_id
5. Dim_Diagnosis menyimpan informasi diagnosis_id, diagnosis_name
6. Dim_Treatment menyimpan informasi treatment_id, treatment_name
7. Dim_Adress menyimpan informasi address_id, street_address, city, state, zip_code
8. Dim_Specialization menyimpan informasi specialization_id, specialization_name



## Slide 57

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Kegiatan Mandiri
1. Dari informasi tersebut, desain logikal apa yang digunakan? Jelaskan
alasannya.
2. Identifikasi ukuran yang ada di Data Warehouse tersebut.
3. Tentukan tipe data masing-masing atribut dan primary key pada masing-masing
tabel dimensi.
4. Tentukan jenis primary key pada tabel fakta
5. Buatlah diagram desain logikal sesuai jawaban No 1 Saudara yang dilengkapi
dengan penjelasan atribut dan relasinya.



## Slide 58

Tim Dosen
1 Dr. Adji Achmad Rinaldo
Fernandes, S.Si., M.Sc. 2 Meilina Retno Hapsari, 
S.Si., M.Stat



## Slide 59

brone.ub.ac.id
Thank You
Insert the Sub Title of Your Presentation

