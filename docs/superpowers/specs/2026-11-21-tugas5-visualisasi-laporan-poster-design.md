# Desain: Tugas 5 — Data Visualizer & Editor

**Repo:** `iddaann/statprob` · **Lokasi kerja:** `project uas/` · **Tanggal:** 2026-11-21

## Intent & why

Tugas 5 bertujuan mengubah hasil analisis statistik Kelompok 23 (Tema C: Akademik & Tidur) menjadi tampilan yang mudah dipahami. Notebook sudah berisi analisis lengkap dan 3 grafik utama (histogram, boxplot, grouped bar chart). Yang belum ada adalah **grafik pendukung analisis**, **tampilan laporan teknis**, dan **poster infografis**. Pekerjaan ini melengkapi ketiganya tanpa mengubah angka-angka hasil analisis.

## Goals

1. Menambahkan 4 grafik pendukung ke notebook yang menjelaskan hubungan antarvariabel (korelasi, tidur–stres, screen time–IPK, IPK menurut kategori).
2. Menghasilkan **laporan teknis** berupa satu file HTML mandiri yang merangkai seluruh analisis + grafik menjadi narasi yang rapi dan siap dicetak ke PDF.
3. Menghasilkan **poster infografis** berupa gambar PNG potrait berisi KPI utama, mini-grafik, dan temuan kunci.
4. Semua dihasilkan dari cell notebook yang sama, tersimpan di `project uas/output/`, dan bisa dijalankan ulang (reproducible).

## Non-goals / anti-goals

- Mengubah dataset, metode statistik, atau angka hasil analisis yang sudah ada.
- Membangun aplikasi web / dashboard interaktif — tidak diminta dan menambah dependency.
- Mengganti 3 grafik utama yang sudah ada (histogram, boxplot, grouped bar).

## Constraints

- Stack sudah tersedia di `requirements.txt`: pandas, numpy, matplotlib, seaborn, scipy, statsmodels, pillow. **Tidak menambah dependency baru.**
- Cell baru harus tetap bisa dijalankan dari direktori `project uas/` (path relatif `output/`).
- Penomoran file output lanjutan: `10_` sampai `16_`, tidak menimpa file `01_`–`09_`.
- Gaya visual mengikuti notebook: `sns.set_theme(style="whitegrid")`, palet biru/hijau, `dpi=200`.

## Approaches

| Pendekatan | Kelebihan | Kekurangan | Keputusan |
|---|---|---|---|
| **A. Integrasi di notebook** — tambah cell grafik + cell pembuat laporan & poster di `.ipynb` | Satu sumber, reproducible, sesuai alur tugas kelompok | Notebook jadi lebih panjang | **Dipilih pengguna** |
| B. File terpisah — notebook murni analisis, script + laporan + poster terpisah | Mudah diedit per bagian | Perlu menjalankan beberapa file, hasil bisa beda versi | Ditolak |
| C. Laporan & poster saja — grafik pendukung minimal | Paling cepat | Tidak memenuhi tanggung jawab "grafik pendukung analisis lainnya" | Ditolak |

## Keputusan desain (cara dibuat — pilihan saya, bukan kesepakatan terpisah)

- **Grafik pendukung (4 cell baru, sebelum laporan):**
  - `10_korelasi_heatmap.png` — heatmap korelasi Pearson 5 variabel numerik.
  - `11_scatter_tidur_stres.png` — scatter + garis regresi `Durasi_Tidur_Jam` vs `Skor_Stres`.
  - `12_scatter_screentime_ipk.png` — scatter `Screen_Time_Jam` vs `IPK`, warna per fakultas.
  - `13_rataan_ipk_stres_fakultas.png` — grouped bar rata-rata IPK & stres per fakultas (dua sumbu, direktif visual tambahan).
- **Laporan teknis:** `14_laporan_teknis.html` — HTML tunggal, CSS inline, berisi ringkasan eksekutif, tabel statistika deskriptif, tabel kualitas data (missing/outlier), dan semua grafik (1–13) dalam layout grid. Grafik disisipkan sebagai base64 agar file bisa dibuka tanpa folder `output/`. Bisa dicetak ke PDF lewat browser.
- **Poster infografis:** `15_poster_infografis.png` — Matplotlib `GridSpec`, ukuran potrait ~A3 (rasio 1:1.414) @200 dpi. Berisi judul, 4 KPI (n=347, rata-rata tidur 6.36 jam, stres 58.3, IPK 3.25), 3 mini-grafik, dan 3 temuan kunci. Opsi tambahan `16_poster_infografis.html` untuk versi yang mudah diedit/dicetak bila dibutuhkan.
- **Perbaikan editor (minor):** label legend di cell 28 (`ax.legend(title="Konsumsi_Kafein")`) salah karena sebenarnya menandai garis Mean/Median. Akan diganti menjadi `title="Statistik"`. Tidak mengubah data.
- **Struktur cell:** grafik pendukung ditambahkan setelah cell 30; cell laporan & poster di akhir. Tidak menyisipkan/menimpa cell lama kecuali label legend tersebut.

## Yang masih jadi keputusan builder

Tidak ada. Format (HTML untuk laporan, PNG untuk poster), palet warna, dan ukuran poster sudah ditetapkan di atas sebagai pilihan saya dan bisa dikoreksi saat review desain.

## SKILL.md gates

Desain ini harus disetujui sebelum implementasi. Setelah disetujui, langkah berikutnya adalah `writing-plans`.
