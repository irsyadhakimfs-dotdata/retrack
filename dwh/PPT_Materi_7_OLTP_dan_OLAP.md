# OLTP dan OLAP


## Slide 1

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Data 
Warehousing
OLTP dan OLAP



## Slide 2

brone.ub.ac.id
Outline 
Perbedaan OLAP dan OLTP01
Operasi OLTP02
Operasi OLAP03
Studi Kasus04



## Slide 3

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Perbedaan
OLAP dan OLTP



## Slide 4

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
OLTP (Online Transaction Processing)
• OLTP adalah sistem yang menangani transaksi data
• Mendukung operasi bisnis harian seperti pemesanan, penjualan dan transaksi 
keuangan
• Mendukung operasi Create, Read, Update, Delete
• Akses data cepat dengan waktu respon rendah
• Struktur tabel yang ter-normalisasi
• Menggunakan OLTP jika memerlukan transaksi yang cepat dan real-time, data harus 
selalu diperbarui dengan cepat.
• Contoh penggunaan : sistem perbankan, e-commerce



## Slide 5

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Contoh OLTP
customer_id nama kota
C001 Andi Malang
C002 Budi Blitar
produk_id nama_produk harga
P001 Laptop 10jt
P002 Mouse 100rb
transaksi_id customer_id tanggal
T001 C001 2026-05-01
detail_id transaksi_id produk_id qty
D001 T001 P001 1
D002 T001 P002 2



## Slide 6

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
OLAP (Online Analytical Processing)
• OLAP adalah sistem yang dirancang untuk analisis data dalam jumlah besar
• Mendukung pengambilan keputusan strategis dengan menganalisis data historis
• Banyak digunakan untuk membaca data daripada mengubahnya
• Struktur tabel yang ter-denormalisasi seperti star schema
• Menggunakan OLAP jika akan menganalisis data untuk keputusan strategis seperti 
melihat tren atau pola
• Contoh penggunaan : laporan penjualan, analisis pasar



## Slide 7

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
tanggal customer produk qty total
2026-05-01 Andi Laptop 1 10jt
2026-05-01 Andi Mouse 2 200rb
Fact_Sales
| date_id | customer_id | product_id | qty | total |
Dim_Customer
| customer_id | nama | kota |
Dim_Product
| product_id | nama_produk | kategori |
Dim_Date
| date_id | tanggal | bulan | tahun |
Contoh OLAP
Tabel Fakta



## Slide 8

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Operasi OLTP



## Slide 9

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLTP
• Create adalah operasi untuk 
menambahkan data baru ke dalam 
database. Dalam konteks OLTP, operasi ini 
harus cepat, akurat, dan menjaga 
konsistensi data. 
• Read adalah operasi untuk membaca atau 
mengambil data dari database. Dalam 
OLTP, operasi ini digunakan untuk 
menampilkan informasi transaksi secara 
real-time dengan akses cepat dan efisien.



## Slide 10

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLTP
• Update adalah operasi untuk 
mengubah data yang sudah ada di 
dalam database. Dalam OLTP, 
operasi ini digunakan untuk 
memperbarui informasi transaksi 
secara cepat dan akurat. 
• Delete adalah operasi untuk 
menghapus data dari database. 
Dalam OLTP, operasi ini berguna 
untuk menghapus transaksi yang 
tidak valid atau sudah tidak 
diperlukan.



## Slide 11

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Operasi OLAP



## Slide 12

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
SQL OLAP di Data Warehouse
Data Warehouse menyimpan data dalam bentuk yang cocok untuk OLAP, seperti 
star schema atau snowflake schema. OLAP memproses data dari Data Warehouse 
untuk menemukan tren, pola dan wawasan bisnis. 
SQL adalah perintah yang digunakan untuk mengakses data pada basis data. SQL 
OLAP adalah singkatan dari Structures Query Language Online Analytical 
Processing. SQL OLAP adalah perintah yang digunakan untuk mengakses data 
berupa hasil pengelompokan atau agregasi pada data warehouse. 
Operasi OLAP terdiri dari Slice, Dice, Drill Down, Roll Up, Roll Up



## Slide 13

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
• Slice : Mengambil subset dari data berdasarkan satu dimensi. 
Contoh : menampilkan data penjualan hanya untuk tahun tertentu.
• Dice : Mengambil subset dari data dengan memilih dua atau lebih dimensi. 
Contoh : menampilkan data penjualan untuk produk tertentu dan tahun tertentu.



## Slide 14

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
• Drill Down: Memperdalam analisis dengan mengurangi level agregasi. 
Contoh : Dari total penjualan ke penjualan per produk.
• Roll Up : Mengelompokkan data untuk mendapatkan ringkasan. 
Contoh : mengelompokkan data penjualan per bulan menjadi per tahun.



## Slide 15

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
• Pivot (Rotate) : Mengubah perspektif data untuk menganalisis dari sudut yang 
berbeda. Mengubah tampilan data dengan cara meringkas, mengelompokkan, dan 
menyusun ulang data dalam bentuk tabel yang lebih mudah dibaca.
Contoh : mengubah kolom menjadi baris dan sebaliknya.



## Slide 16

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Studi Kasus



## Slide 17

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Contoh
Dataset berikut merupakan dataset transaksi penjualan di sebuah supermarket. Dataset tersebut disimpan 
dalam sebuah database bernama “data” di MySQL dan diberi nama “data_supermarket”. Dataset tersebut 
mencakup berbagai informasi mengenai pembelian pelanggan dan terdiri dari 14 variabel, yaitu:
Invoice_ID
Branch
Customer_Type
Gender
Product_Line
Unit_Price
Quantity
Tax5%
Total
Date
Time
Payment
Rating
Akses dataset : Akses Dataset data_supermarket



## Slide 18

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLTP
Create : menambahkan data baru ke dalam 
database. 
Read : Menampilkan data dengan nilai 
Invoice_ID  = “123-19-1176”



## Slide 19

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLTP
Update : Mengubah nilai pada kolom Payment menjadi "Debit Card" untuk baris 
dengan Invoice_ID = "740-22-2500
Delete: Menghapus baris yang memiliki nilai Invoice_ID = “669-54-1719”



## Slide 20

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
Slice : Mengambil subset dari data berdasarkan satu dimensi. 
Contoh : Menampilkan data transaksi hanya dari cabang (Branch) "A".



## Slide 21

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
Dice : Mengambil subset dari data dengan memilih dua atau lebih dimensi. 
Contoh : Menampilkan data penjualan hanya untuk cabang A, kota Yangon, dan produk 
Electronic Accessories.



## Slide 22

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
Drill Down: Memperdalam analisis dengan mengurangi level agregasi. 
Contoh : Menghitung total pendapatan per kota, lalu memperdalam analisis dengan  
menghitung total pendapatan per cabang dalam satu kota tertentu (Kota “Mandalay”).



## Slide 23

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
Roll Up : Mengelompokkan data untuk mendapatkan ringkasan. 
Contoh : Menghitung total pendapatan per cabang (level detail), kemudian menggabungkan
untuk mendapatkan total pendapatan per kota.



## Slide 24

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Operasi OLAP
Pivot (Rotate) : Mengubah perspektif data untuk menganalisis dari sudut yang berbeda. 
Mengubah tampilan data dengan cara meringkas, mengelompokkan, dan menyusun ulang 
data dalam bentuk tabel yang lebih mudah dibaca.
Contoh : Melihat total pendapatan berdasarkan Branch dan Payment dalam bentuk pivot.
Branch Payment total_revenue
A Cash 1000
A Ewallet 1500
A Credit Card 2000
B Cash 1200
B Ewallet 1300
B Credit Card 1700
Branch Cash Ewallet Credit 
Card
A 1000 1500 2000
B 1200 1300 1700



## Slide 25

U n i v e r s i t a s  B r a w i j a y a - B u i l d i n g  U p  N o b l e  F u t u r ebrone.ub.ac.id
Kegiatan Mandiri



## Slide 26

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Contoh
Sebuah perusahaan retail ingin membangun Data Warehouse untuk menganalisis penjualan produk
mereka. Data warehouse ini akan membantu mereka mendapatkan wawasan yang lebih mendalam tentang
penjualan produk, perilaku pelanggan, tren penjualan dan kinerja toko. Tujuan utamanya adalah untuk
meningkatkan strategi penjualan, optimalisasi stok dan memprediksi permintaan pasar. Skema yang digunakan
adalah Star Schema, yang terdiri dari satu tabel fakta dan beberapa tabel dimensi.
 Tabel Fakta : fakta_penjualan
 Tabel Dimensi : dim_produk
 Tabel Dimensi : dim_toko
 Tabel Dimensi : dim_pelanggan
 Tabel Dimensi : dim_waktu



## Slide 27

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id



## Slide 28

Universitas Brawijaya - Building Up Noble Futurebrone.ub.ac.id
Pertanyaan :
1. Berapa total penjualan Elektronik di Toko Utama pada kuartal pertama 2024?
2. Berapa total penjualan untuk kategori Fashion di tahun 2024?
3. Berapa total penjualan per kuartal di tahun 2024?
4. Dari total penjualan tahun 2024 kemudian ingin mengetahui berapa total penjualan per bulan.
5. Ingin mengetahui total penjualan berdasarkan nama toko sebagai baris dan kategori produk 
sebagai kolom.
Identifikasi :
a. Operasi apa yang digunakan pada masing-masing pertanyaan.
b. Jawab pertanyaan masing-masing tanpa menggunakan Software. Jelaskan dengan tabelnya 
juga.



## Slide 29

Tim Dosen
1 Dr. Adji Achmad Rinaldo
Fernandes, S.Si., M.Sc. 2 Meilina Retno Hapsari, 
S.Si., M.Stat



## Slide 30

brone.ub.ac.id
Thank You
Data Warehouse

