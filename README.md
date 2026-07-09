Laporan Proyek: Aplikasi Rara Laundry
Sistem Informasi Manajemen Layanan dan Pesanan Laundry

Pada proyek kali ini, saya mengembangkan sebuah perangkat lunak bernama Rara Laundry. Aplikasi ini dirancang sebagai solusi digital untuk membantu para pemilik usaha dan staf operasional laundry dalam mengadministrasikan data pesanan, mengatur tarif layanan, serta melakukan rekapitulasi transaksi harian.

Ringkasan Fitur Sistem
Dalam sistem ini, saya telah mengimplementasikan beberapa modul utama, yaitu:

Keamanan Akses (Otentikasi): Proses registrasi dan login pengguna diproteksi menggunakan mekanisme token JWT (JSON Web Tokens).

Pengelolaan Modul Layanan: Terdapat fasilitas CRUD (Tambah, Baca, Ubah, Hapus) untuk mengatur daftar harga layanan. Sistem ini sudah mendeskripsikan secara spesifik antara layanan laundry tipe kiloan dan satuan.

Administrasi Order: Berfungsi untuk menginput pesanan baru dengan fitur kalkulasi total biaya secara otomatis, pencetakan struk untuk antrean, dan pembaruan status ketika cucian sudah selesai.

Modul Pengiriman (Delivery): Fitur tambahan yang memfasilitasi layanan antar-jemput pakaian pelanggan, lengkap dengan fungsi cetak label pengiriman barang.

Perekaman Laporan dan Transaksi: Halaman khusus untuk meninjau riwayat pesanan yang telah tuntas. Selain itu, terdapat fitur untuk mengekspor "Laporan Sabtu" ke dalam format file .csv.

Sistem Presensi: Fitur absensi (check-in) harian bagi karyawan. Data ini tersinkronisasi langsung (real-time) dengan database, dan sistem membatasi karyawan agar hanya bisa melakukan satu kali absensi dalam sehari.

Spesifikasi Teknologi yang Digunakan
Untuk membangun perangkat lunak ini, saya membaginya ke dalam dua arsitektur utama:

Sisi Antarmuka (Frontend):

HTML5 sebagai kerangka dasar halaman.

Tailwind CSS (diakses via CDN) untuk mempermudah styling dan desain responsif.

Vanilla JavaScript terintegrasi dengan Fetch API untuk komunikasi data.

FontAwesome untuk kebutuhan ikon antarmuka.

CryptoJS untuk menangani kebutuhan signature pada API.

Sisi Server (Backend):

Bahasa Pemrograman Python 3.

Framework FastAPI yang dijalankan dengan Uvicorn untuk membangun web server yang cepat.

Supabase sebagai penyedia database (PostgreSQL Serverless).

HTTPX digunakan sebagai klien HTTP di sisi internal server.

Petunjuk Konfigurasi dan Instalasi
Berikut adalah langkah-langkah yang saya dokumentasikan untuk menjalankan aplikasi ini di lingkungan lokal (localhost):

Tahap 1: Inisialisasi Backend (FastAPI dan Supabase)

Buat akun dan sebuah project baru melalui situs Supabase.

Masuk ke menu SQL Editor pada dashboard Supabase, kemudian jalankan script yang ada di dalam file backend/supabase_init.sql. Langkah ini wajib dilakukan untuk membuat tabel attendance beserta struktur kolom lainnya.

Buka terminal atau command prompt, arahkan ke direktori backend/, lalu instal seluruh library yang dibutuhkan dengan perintah:
pip install fastapi uvicorn supabase httpx pydantic

Buka file konfigurasi main.py. Ganti value dari variabel SUPABASE_URL dan SUPABASE_KEY agar sesuai dengan kredensial API dari proyek Supabase yang baru saja dibuat.

Nyalakan server dengan mengeksekusi perintah berikut:
cd backend
uvicorn main:app --reload
(Server backend akan berjalan dan bisa diakses pada http://127.0.0.1:8000).

Tahap 2: Inisialisasi Frontend
Cari dan buka file frontend/index.html menggunakan code editor.

Pastikan variabel API_URL yang ada di dalam tag script sudah merujuk ke endpoint lokal, yaitu http://127.0.0.1:8000.

Jalankan file index.html tersebut melalui web browser (Chrome/Firefox). Sebagai alternatif, bisa juga memanfaatkan ekstensi Live Server di Visual Studio Code (biasanya berjalan di http://127.0.0.1:5500).

Catatan Evaluasi dan Implementasi

Kendala Koneksi (Free Tier): Apabila saat pengujian sistem gagal memuat data (Connection Error), silakan cek kembali dashboard Supabase. Untuk pengguna paket gratis (Free Tier), database biasanya akan beralih ke mode Paused atau tidur jika lama tidak ada aktivitas. Solusinya adalah dengan menekan tombol Restore pada proyek tersebut.

Keamanan Data: Untuk menjamin keamanan pengguna, seluruh password tidak disimpan dalam bentuk teks biasa (plaintext), melainkan telah melalui proses hashing otomatis oleh layanan autentikasi Supabase.
