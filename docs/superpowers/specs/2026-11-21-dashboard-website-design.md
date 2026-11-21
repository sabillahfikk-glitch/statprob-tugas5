# Desain: Website Data Analytics & Visualization Dashboard

**Repo:** `sabillahfikk-glitch/statprob-tugas5` · **Tanggal:** 2026-11-21

## Intent & why

Situs saat ini hanya halaman indeks statis berisi tautan laporan teknis dan poster. Pemilik ingin proyek ini tampil sebagai **website Data Analytics & Visualization Dashboard**: satu halaman yang merangkum data dan visualisasi secara interaktif, tetap bisa diakses publik lewat GitHub Pages.

## Goals

1. Dashboard satu halaman dengan KPI cards, grafik, filter, dan tabel ringkasan.
2. Filter Fakultas / Jenis Kelamin / Konsumsi Kafein mengubah grafik dan KPI secara langsung.
3. Tetap bisa dibuka dari `file://` maupun GitHub Pages (tanpa server, tanpa CDN).
4. Terhubung ke laporan teknis dan poster yang sudah ada.
5. Data berasal dari `df` hasil analisis notebook (347 responden bersih), bukan data baru.

## Non-goals / anti-goals

- Backend, database, login, atau penyimpanan data di server.
- Mengubah angka/metode analisis di notebook.
- Mengganti laporan teknis dan poster yang sudah ada.
- Dependensi Python baru.

## Constraints

- GitHub Pages hanya menyajikan file statis: HTML, CSS, JS, JSON/JS data, gambar.
- Repo sudah public dan Pages aktif dari branch `gh-pages` (folder `/`).
- Warna mengikuti laporan teknis: biru `#2e5c8a`, latar `#f4f7fa`, teks `#1f2d3d`.
- Library Chart.js harus di-**bundling lokal** di repo (tanpa tautan CDN) agar dashboard tetap tampil saat offline.

## Approaches

| Pendekatan | Kelebihan | Kekurangan | Keputusan |
|---|---|---|---|
| A. Chart.js di-bundling lokal | Grafik benar-benar interaktif mengikuti filter; tetap jalan offline; file ringan (~200 KB JS) | Perlu menanam data 347 baris dan menulis konfigurasi grafik | **Dipilih** |
| B. Dashboard statis (pakai 13 PNG) | Paling cepat, tanpa library | Filter hanya mengubah tabel/angka, grafik diam | Ditolak |
| C. Plotly dari notebook | Interaktif penuh, diekspor dari Python | File jauh lebih besar, alur update lebih rumit | Ditolak |

Alasan memilih A: pengguna meminta "website dashboard" tanpa contoh visual tertentu, jadi hasilnya harus terasa sebagai dashboard sungguhan, bukan sekadar kumpulan gambar.

## Keputusan desain (pilihan saya)

- **Lokasi file:** `project uas/output/` agar alur deploy `gh-pages` yang sudah ada tidak berubah. File baru: `dashboard.html`, `dashboard.css`, `dashboard.js`, `dashboard-data.js`, dan `vendor/chart.umd.min.js`. `index.html` tetap menjadi halaman masuk dan diberi tautan ke dashboard.
- **Data:** cell baru di `.ipynb` menulis `output/dashboard-data.js` berisi `window.SLEEP_DATA = [...]` (347 baris dari `df`). Memakai script JS, bukan `fetch`, agar tetap jalan saat dibuka langsung dari disk.
- **Layout:** header judul + KPI cards; sidebar filter; grid grafik (bar distribusi fakultas, doughnut kafein, scatter tidur–stres, bar rata-rata IPK & stres per fakultas); heatmap korelasi memakai PNG `10_` yang sudah ada; tabel ringkasan yang ikut tersaring; footer tautan laporan & poster. Responsif untuk layar kecil.
- **Interaksi:** perubahan filter menghitung ulang KPI, menggambar ulang grafik Chart.js, dan menyaring tabel. Tombol "Reset" mengembalikan semua filter.
- **Deploy:** salin isi `output/` ke branch `gh-pages` seperti alur saat ini, lalu verifikasi URL publik.

## Yang masih jadi keputusan builder

Tidak ada. Pilihan warna, jenis grafik, dan struktur file sudah ditetapkan di atas sebagai keputusan saya.

## Gate

Desain ini harus disetujui sebelum kode dibuat. Setelah disetujui, langkah berikutnya adalah `writing-plans`.
