# Tugas 5 — Data Visualizer & Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Melengkapi Tugas 5 dengan 4 grafik pendukung, laporan teknis HTML, dan poster infografis PNG yang seluruhnya dihasilkan dari notebook `project uas/.ipynb`.

**Architecture:** Semua perubahan terjadi di dalam satu notebook. Cell baru ditambahkan setelah cell 30 (visualisasi utama): 4 cell grafik pendukung, 1 cell laporan HTML, 1 cell poster. Cell laporan membaca file PNG dari `output/` dan menyisipkannya sebagai base64 agar HTML mandiri. Tidak ada file sumber Python baru selain skrip verifikasi di `checks/`.

**Tech Stack:** Python 3, pandas, numpy, matplotlib, seaborn, pillow; `jupyter nbconvert` untuk eksekusi notebook; HTML/CSS inline untuk laporan.

**Spec:** `docs/superpowers/specs/2026-11-21-tugas5-visualisasi-laporan-poster-design.md`

## Global Constraints

- Tidak menambah dependency di luar `project uas/requirements.txt`.
- Jalankan semua perintah dari direktori `project uas/` agar path relatif `output/` benar.
- Penomoran output baru: `10_` sampai `16_`; **jangan** menimpa/mengubah `01_`–`09_`.
- Gaya visual: `sns.set_theme(style="whitegrid")`, palet biru/hijau, `dpi=200`.
- Angka hasil analisis (n=347, mean tidur 6.355, mean stres 58.292, mean IPK 3.250) tidak diubah.
- Perbaikan editor hanya pada label legend cell 28; tidak mengubah data atau perhitungan.

## Review Focus

- Label legend cell 28 masih salah (`title="Konsumsi_Kafein"` padahal garis Mean/Median) → `checks/verify.py notebook`.
- File output lama `01_`–`09_` ikut tertimpa saat eksekusi ulang → `checks/verify.py legacy` (git diff hanya boleh menambah file baru).
- HTML laporan bergantung pada folder `output/` (gambar tidak tampil saat dibuka sendiri) → `checks/verify.py report` menolak `src` selain `data:image/png;base64`.
- Angka di laporan/poster tidak cocok dengan hasil analisis → `checks/verify.py report` dan `poster` mencari string nilai kunci.
- Poster tidak potrait / terlalu kecil untuk dicetak → `checks/verify.py poster` mengecek rasio dan dimensi minimum.

---

### Task 1: Fondasi notebook — perbaikan legend & penanda bagian baru

**Files:**
- Modify: `project uas/.ipynb` (cell 28, dan tambah 1 markdown cell setelah cell 30)
- Create: `checks/verify.py` (subcommand `notebook`)

**Interfaces:**
- Consumes: notebook yang sudah ada (32 cell).
- Produces: notebook dengan label legend benar dan header `## 1.8 Grafik Pendukung Analisis`; `checks/verify.py` dengan pola CLI `python checks/verify.py <nama>`.

- [ ] **Step 1: Tulis test yang gagal**

Buat `checks/verify.py` dengan subcommand `notebook` yang:
- memuat `project uas/.ipynb` via `json.load`,
- menggabungkan `source` tiap cell menjadi string,
- `assert 'title="Statistik"' in src_cell28`,
- `assert 'title="Konsumsi_Kafein"' not in src_cell28`,
- `assert any('1.8 Grafik Pendukung Analisis' in s for s in semua_cell_markdown)`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify.py notebook` (dari root repo)
Expected: FAIL denganAssertionError pada label legend / header belum ada.

- [ ] **Step 3: Perbaiki cell 28 dan tambah header**

Di `project uas/.ipynb`:
- cell 28: ganti `ax.legend(title="Konsumsi_Kafein", loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.15))` → `ax.legend(title="Statistik", loc="upper center", ncol=2, bbox_to_anchor=(0.5, -0.15))`.
- sisipkan cell markdown baru **setelah** cell 30 dengan source `## 1.8 Grafik Pendukung Analisis\n`.

- [ ] **Step 4: Jalankan test, pastikan lolos**

Run: `python checks/verify.py notebook`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add project\ uas/.ipynb checks/verify.py
git commit -m "fix: correct legend label and add supporting-viz section header"
```

---

### Task 2: Empat grafik pendukung analisis

**Files:**
- Modify: `project uas/.ipynb` (4 code cell baru setelah header Task 1)

**Interfaces:**
- Consumes: `df` (347 baris, sudah bersih), `kolom_numerik` dari cell 14.
- Produces: `project uas/output/10_korelasi_heatmap.png`, `11_scatter_tidur_stres.png`, `12_scatter_screentime_ipk.png`, `13_rataan_ipk_stres_fakultas.png`.

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan subcommand `charts` di `checks/verify.py` yang untuk ke-4 nama file di atas:
- `assert path.exists()`,
- buka dengan `PIL.Image.open`, `assert img.format == "PNG"`, `assert img.width >= 800 and img.height >= 500`,
- `assert nama_file in source_notebook` (cell penyimpanannya ada).

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify.py charts`
Expected: FAIL karena file belum ada.

- [ ] **Step 3: Tambah 4 code cell ke notebook**

Isi tiap cell:
- `10_`: `sns.heatmap(df[kolom_numerik].corr(), annot=True, cmap="Blues", fmt=".2f", cbar_kws={"label": "Pearson r"})`, judul "Matriks Korelasi Variabel Numerik", `plt.savefig(OUTPUT / "10_korelasi_heatmap.png", dpi=200, bbox_inches="tight")`.
- `11_`: `sns.regplot(data=df, x="Durasi_Tidur_Jam", y="Skor_Stres", scatter_kws={"alpha":.6}, line_kws={"color":"#c0392b"})`, judul "Hubungan Durasi Tidur dengan Skor Stres", `savefig(..., "11_scatter_tidur_stres.png")`.
- `12_`: `sns.scatterplot(data=df, x="Screen_Time_Jam", y="IPK", hue="Fakultas", palette="Set2", alpha=.8)`, judul "Screen Time vs IPK per Fakultas", `savefig(..., "12_scatter_screentime_ipk.png")`.
- `13_`: bar grouped dua metrik (mean IPK & mean stres/10) per fakultas pada dua sumbu dengan `ax2 = ax.twinx()`, label sumbu jelas, `savefig(..., "13_rataan_ipk_stres_fakultas.png")`.
Semua cell diakhiri `plt.tight_layout()` sebelum `savefig` dan `plt.show()` setelahnya.

- [ ] **Step 4: Eksekusi notebook dan jalankan test**

Run (dari `project uas/`): `jupyter nbconvert --to notebook --execute --inplace .ipynb`
Lalu dari root: `python checks/verify.py charts`
Expected: PASS; 4 file PNG valid muncul di `output/`.

- [ ] **Step 5: Commit**

```bash
git add project\ uas/.ipynb project\ uas/output/10_*.png project\ uas/output/11_*.png project\ uas/output/12_*.png project\ uas/output/13_*.png checks/verify.py
git commit -m "feat: add four supporting analysis charts"
```

---

### Task 3: Laporan teknis HTML mandiri

**Files:**
- Modify: `project uas/.ipynb` (1 code cell baru setelah grafik pendukung)

**Interfaces:**
- Consumes: `df`, `deskriptif`, `tabel_outlier`, `ringkas`, dan file PNG `01_`–`13_` di `output/`.
- Produces: `project uas/output/14_laporan_teknis.html`.

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan subcommand `report` di `checks/verify.py`:
- `assert file.exists()`,
- baca sebagai UTF-8,
- `assert "<!DOCTYPE html>" in html`,
- untuk tiap heading: "Ringkasan Eksekutif", "Statistika Deskriptif", "Kualitas Data", "Visualisasi" → `assert heading in html`,
- `assert html.count("data:image/png;base64,") >= 9`,
- `assert 'src="output/' not in html` dan `assert 'src="http' not in html`,
- `assert all(x in html for x in ["347", "6.355", "58.292", "3.250"])`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify.py report`
Expected: FAIL karena file belum ada.

- [ ] **Step 3: Tambah cell pembangun laporan**

Cell Python harus:
- membuat string HTML dengan CSS inline (font sistem, grid 2 kolom, kartu metrik, tabel bergaris, print media query),
- helper `b64(path)` membaca PNG dan mengembalikan `data:image/png;base64,<...>` via `base64.b64encode`,
- menyisipkan 4 metrik kunci (347 responden; 6.355 jam tidur; 58.292 skor stres; 3.250 IPK),
- menyisipkan tabel `deskriptif`, `tabel_outlier`, dan `ringkas` sebagai HTML tabel (pandas `.to_html()`),
- menyisipkan gambar `07_`–`13_` sebagai `<img src="data:...">`,
- menulis hasil dengan `encoding="utf-8"` ke `OUTPUT / "14_laporan_teknis.html"`, lalu `print` path.

- [ ] **Step 4: Eksekusi notebook dan jalankan test**

Run (dari `project uas/`): `jupyter nbconvert --to notebook --execute --inplace .ipynb`
Lalu dari root: `python checks/verify.py report`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add project\ uas/.ipynb project\ uas/output/14_laporan_teknis.html checks/verify.py
git commit -m "feat: generate standalone technical report HTML"
```

---

### Task 4: Poster infografis

**Files:**
- Modify: `project uas/.ipynb` (1 code cell baru di akhir)

**Interfaces:**
- Consumes: `df`, `deskriptif`, file PNG `10_`, `11_`, `12_`.
- Produces: `project uas/output/15_poster_infografis.png`, `project uas/output/16_poster_infografis.html`.

- [ ] **Step 1: Tulis test yang gagal**

Tambahkan subcommand `poster` di `checks/verify.py`:
- `assert Path("project uas/output/15_poster_infografis.png").exists()`,
- `Image.open(...)`, `assert img.format == "PNG"`, `assert img.height > img.width`, `assert img.width >= 1000 and img.height >= 1400`,
- `assert Path("project uas/output/16_poster_infografis.html").exists()`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify.py poster`
Expected: FAIL karena file belum ada.

- [ ] **Step 3: Tambah cell pembangun poster**

Cell Python harus:
- membuat figure Matplotlib dengan `figsize=(12, 17)` (rasio ~A3 potrait) dan `dpi=200`,
- `GridSpec(4, 2, height_ratios=[1.1, 2, 2, 1.2])` untuk: header judul, 4 kartu KPI, 3 mini-grafik (gambar PNG dibaca via `plt.imread` dan ditampilkan dengan `imshow`, axis dimatikan), dan footer 3 temuan kunci,
- warna latar lembut, judul "AKADEMIK & TIDUR", subjudul "Kelompok 23 · Tema C · n = 347 mahasiswa",
- KPI: 6.36 jam tidur, 58.3 skor stres, 3.25 IPK, 46.4% kafein tinggi,
- temuan kunci: korelasi negatif tidur–stres, screen time vs IPK, perbedaan stres antar fakultas,
- `fig.savefig(OUTPUT / "15_poster_infografis.png", dpi=200, bbox_inches="tight", facecolor=bg)`,
- menulis `16_poster_infografis.html` berisi wrapper HTML yang menampilkan PNG poster dengan CSS center + print styles (versi mudah dicetak/diedit).

- [ ] **Step 4: Eksekusi notebook dan jalankan test**

Run (dari `project uas/`): `jupyter nbconvert --to notebook --execute --inplace .ipynb`
Lalu dari root: `python checks/verify.py poster`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add project\ uas/.ipynb project\ uas/output/15_poster_infografis.png project\ uas/output/16_poster_infografis.html checks/verify.py
git commit -m "feat: generate infographic poster PNG and printable HTML"
```

---

### Task 5: Verifikasi akhir

**Files:**
- Modify: `checks/verify.py` (subcommand `all`, `legacy`)

**Interfaces:**
- Consumes: semua output dari Task 1–4.
- Produces: status PASS/FAIL akhir.

- [ ] **Step 1: Tambah subcommand `all` dan `legacy`**

`all` menjalankan berurutan `notebook`, `legacy`, `charts`, `report`, `poster`.
`legacy` menjalankan `git diff --name-only` dan `assert` tidak ada file `output/0[1-9]_*` yang berubah (hanya file baru yang boleh muncul).

- [ ] **Step 2: Jalankan verifikasi penuh**

Run: `python checks/verify.py all`
Expected: PASS untuk kelima subcommand. Jika gagal, perbaiki task yang bersangkutan lalu ulangi.

- [ ] **Step 3: Commit terakhir**

```bash
git add checks/verify.py
git commit -m "test: add final verification commands for task 5"
```
