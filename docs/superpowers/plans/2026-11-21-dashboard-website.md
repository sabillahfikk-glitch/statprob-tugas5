# Dashboard Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mengubah situs statis statprob menjadi website Data Analytics & Visualization Dashboard yang interaktif dan tetap bisa dipublikasikan lewat GitHub Pages.

**Architecture:** Dashboard adalah satu halaman statis (`dashboard.html` + `dashboard.css` + `dashboard.js`) di folder `output/`. Data 347 baris ditanam sebagai `window.SLEEP_DATA` oleh cell notebook, Chart.js 4.x disimpan lokal di `output/vendor/`, sehingga tidak ada server maupun CDN. Alur deploy `gh-pages` yang sudah ada dipakai kembali; `index.html` tetap menjadi pintu masuk.

**Tech Stack:** Python/pandas (ekspor data), HTML, CSS, vanilla JavaScript, Chart.js 4.x (vendored), GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-11-21-dashboard-website-design.md`

## Global Constraints

- GitHub Pages hanya menyajikan file statis — tidak ada backend, database, atau login.
- Repo sudah public; Pages aktif dari branch `gh-pages` (path `/`).
- Warna: aksen `#2e5c8a`, latar `#f4f7fa`, teks `#1f2d3d`.
- Chart.js **harus** berupa file lokal di `output/vendor/chart.umd.min.js`; dilarang tautan CDN (`https://`) di HTML/CSS/JS.
- Data berasal dari `df` hasil analisis (347 baris bersih), bukan data baru; tidak ada dependency Python baru.
- SEMUA file dashboard berada di `project uas/output/` agar deploy tidak berubah.

## Review Focus

- Filter tanpa hasil (kombinasi fakultas/gender/kafein kosong) → KPI harus `0`/`—` dan grafik kosong, bukan error → Task 3: browser eval kombinasi mustahil, cek `#kpi-n` = `0` dan tidak ada dialog error.
- Data dibuka dari `file://` → harus jalan tanpa `fetch` (CORS) → Task 2: cek `dashboard.html` memuat `dashboard-data.js` via tag `<script>` dan `dashboard.js` tidak mengandung `fetch(`.
- Chart.js tidak bergantung CDN → tetap tampil offline → Task 2: cek tidak ada `https://` di ketiga file dashboard dan file vendor berukuran > 100 KB.
- KPI benar-benar berubah saat filter → bukan angka statis → Task 3: browser eval ubah `#filter-fakultas`, cek `#kpi-n` berubah dari `347`.
- Layout tidak overflow di layar kecil → Task 3: cek `dashboard.css` memuat `@media` dan screenshot mobile tidak terpotong.

---

### Task 1: Ekspor data dashboard dari notebook

**Files:**
- Modify: `project uas/.ipynb` (1 code cell baru di akhir)
- Create/Modify: `project uas/output/dashboard-data.js`
- Test: `checks/verify_dashboard.py`

**Interfaces:**
- Consumes: `df` (347 baris), `OUTPUT` dari notebook.
- Produces: `window.SLEEP_DATA` — array of objects dengan 8 kunci: `Fakultas`, `Jenis_Kelamin`, `Konsumsi_Kafein`, `Durasi_Tidur_Jam`, `Screen_Time_Jam`, `Jam_Belajar_Mingguan`, `Skor_Stres`, `IPK`.

- [ ] **Step 1: Tulis test yang gagal**

Buat `checks/verify_dashboard.py` dengan subcommand `data`:
- `assert (OUT / "dashboard-data.js").exists()`,
- baca teks, `assert "window.SLEEP_DATA" in teks`,
- ekstrak array JSON antara `= ` dan `;`, `json.loads`,
- `assert len(data) == 347`,
- `assert set(data[0].keys()) == {8 kunci di atas}`,
- `assert round(sum(r["Durasi_Tidur_Jam"] for r in data)/len(data), 3) == 6.355`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify_dashboard.py data`
Expected: FAIL — file belum ada.

- [ ] **Step 3: Tambah cell ekspor di notebook**

Cell Python:
- `kolom = ["Fakultas", "Jenis_Kelamin", "Konsumsi_Kafein", "Durasi_Tidur_Jam", "Screen_Time_Jam", "Jam_Belajar_Mingguan", "Skor_Stres", "IPK"]`
- `records = df[kolom].round(3).to_dict(orient="records")`
- tulis `OUTPUT / "dashboard-data.js"` dengan isi `"window.SLEEP_DATA = " + json.dumps(records, ensure_ascii=False) + ";\n"`, encoding utf-8.
- `import json` di dalam cell tersebut.

- [ ] **Step 4: Eksekusi notebook dan jalankan test**

Run (dari `project uas/`): `python -m jupyter nbconvert --to notebook --execute --inplace .ipynb`
Lalu dari root: `python checks/verify_dashboard.py data`
Expected: PASS — 347 record, 8 kunci, mean tidur 6.355.

- [ ] **Step 5: Commit**

```bash
git add checks/verify_dashboard.py 'project uas/.ipynb' 'project uas/output/dashboard-data.js'
git commit -m "feat: export dashboard data from notebook"
```

---

### Task 2: Kerangka halaman, CSS, dan Chart.js lokal

**Files:**
- Create: `project uas/output/dashboard.html`, `project uas/output/dashboard.css`, `project uas/output/vendor/chart.umd.min.js`
- Test: `checks/verify_dashboard.py` (subcommand `files`)

**Interfaces:**
- Consumes: `dashboard-data.js` dari Task 1.
- Produces: elemen dengan ID tetap — `#kpi-n`, `#kpi-tidur`, `#kpi-stres`, `#kpi-ipk`, `#filter-fakultas`, `#filter-gender`, `#filter-kafein`, `#filter-reset`, `#chart-fakultas`, `#chart-kafein`, `#chart-tidur-stres`, `#chart-ipk-fakultas`, `#ringkasan-body`, `#heatmap`.

- [ ] **Step 1: Tulis test yang gagal**

Tambah subcommand `files` di `checks/verify_dashboard.py`:
- untuk tiap file `dashboard.html`, `dashboard.css`, `dashboard.js`, `dashboard-data.js`, `vendor/chart.umd.min.js`: `assert path.exists()`,
- `assert len(vendor.read_bytes()) > 100_000`,
- `html = dashboard.html.read_text()`; untuk tiap ID di atas: `assert f'id="{id}"' in html`,
- `assert "dashboard-data.js" in html` dan `assert "vendor/chart.umd.min.js" in html`,
- untuk ketiga file dashboard: `assert "https://" not in isi` dan `assert "fetch(" not in isi`,
- `css = dashboard.css.read_text()`; `assert "@media" in css`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify_dashboard.py files`
Expected: FAIL — file belum ada.

- [ ] **Step 3: Buat file HTML/CSS dan unduh Chart.js**

- `dashboard.html`: header judul "Akademik & Tidur — Analytics Dashboard", sidebar berisi tiga `<select>` (`#filter-fakultas`, `#filter-gender`, `#filter-kafein`) yang diisi dinamis oleh JS + tombol `#filter-reset`; empat kartu KPI dengan `#kpi-*`; grid 5 panel (4 `<canvas>` + `<img id="heatmap" src="10_korelasi_heatmap.png">`); tabel dengan `<tbody id="ringkasan-body">`; footer tautan ke `14_laporan_teknis.html` dan `16_poster_infografis.html`. Muat script secara berurutan: `vendor/chart.umd.min.js`, `dashboard-data.js`, `dashboard.js`.
- `dashboard.css`: layout sidebar + grid responsif, palet warna dari Global Constraints, `@media (max-width: 900px)` yang menumpuk sidebar dan grid.
- Unduh Chart.js 4.x UMD build dari jsdelivr ke `output/vendor/chart.umd.min.js` (tulis biner).

- [ ] **Step 4: Jalankan test, pastikan lolos**

Run: `python checks/verify_dashboard.py files`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add 'project uas/output/dashboard.html' 'project uas/output/dashboard.css' 'project uas/output/vendor/chart.umd.min.js' checks/verify_dashboard.py
git commit -m "feat: add dashboard shell, styles and vendored Chart.js"
```

---

### Task 3: Logika interaktif dashboard

**Files:**
- Create: `project uas/output/dashboard.js`
- Test: browser (browser-control skill) + `checks/verify_dashboard.py` subcommand `js`

**Interfaces:**
- Consumes: `window.SLEEP_DATA` (Task 1), ID elemen (Task 2), `Chart` global dari Chart.js.
- Produces: KPI terhitung, 4 grafik Chart.js, tabel tersaring, helper `window.__dashboard` dengan `filtered()` mengembalikan array data aktif (dipakai test).

- [ ] **Step 1: Tulis test yang gagal**

Tambah subcommand `js` di `checks/verify_dashboard.py`:
- `js = (OUT / "dashboard.js").read_text()`,
- `assert "window.SLEEP_DATA" in js`,
- `assert "window.__dashboard" in js`,
- `assert "filter-fakultas" in js` dan `assert "filter-reset" in js`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify_dashboard.py js`
Expected: FAIL — `dashboard.js` belum ada.

- [ ] **Step 3: Implementasi `dashboard.js`**

- `const RAW = window.SLEEP_DATA || [];`
- isi tiga `<select>` dari nilai unik data; pasang listener `change` pada filter dan `click` pada reset;
- `function filtered()` menyaring `RAW` berdasarkan ketiga select (nilai kosong = semua) dan mengembalikan array;
- `window.__dashboard = { filtered };`
- `renderKPI(rows)`: tulis `rows.length` ke `#kpi-n`, mean `Durasi_Tidur_Jam` (2 desimal) ke `#kpi-tidur`, mean `Skor_Stres` (1 desimal) ke `#kpi-stres`, mean `IPK` (2 desimal) ke `#kpi-ipk`; untuk `rows.length === 0` tampilkan `0`/`—`;
- `renderCharts(rows)`: hancurkan chart lama, lalu buat 4 chart — bar jumlah responden per Fakultas, doughnut Konsumsi_Kafein, scatter Durasi_Tidur_Jam vs Skor_Stres, bar rata-rata IPK & Skor_Stres/10 per Fakultas (dua sumbu);
- `renderTable(rows)`: isi `#ringkasan-body` dengan satu baris per fakultas (n, rata-rata tidur, stres, IPK);
- `init()` memanggil kelima render lalu dipanggil saat DOM siap.

- [ ] **Step 4: Jalankan test dan uji di browser**

Run: `python checks/verify_dashboard.py js`
Expected: PASS.

Lalu buka dengan browser-control (dari root repo):
```
python 'C:\Users\Boy\.config\opencode\skills\browser-control\scripts\browser.py' open 'file:///C:/Users/Boy/statprob/project%20uas/output/dashboard.html' --wait 1500
python 'C:\Users\Boy\.config\opencode\skills\browser-control\scripts\browser.py' text --max 2000
python 'C:\Users\Boy\.config\opencode\skills\browser-control\scripts\browser.py' eval 'document.getElementById("kpi-n").textContent'
```
Expected: teks mengandung "Dashboard", `#kpi-n` = `347`.

Uji filter:
```
python '...browser.py' eval 'var s=document.getElementById("filter-fakultas"); s.value="Sains & Teknik"; s.dispatchEvent(new Event("change")); document.getElementById("kpi-n").textContent'
```
Expected: angka berubah dari `347` menjadi `104`.

Uji kombinasi mustahil (Review Focus 1): set ketiga filter ke kombinasi yang tidak ada, `#kpi-n` harus `0` dan tidak ada error.

- [ ] **Step 5: Commit**

```bash
git add 'project uas/output/dashboard.js' checks/verify_dashboard.py
git commit -m "feat: add interactive dashboard filtering and charts"
```

---

### Task 4: Pintu masuk, deploy, dan verifikasi publik

**Files:**
- Modify: `project uas/output/index.html`
- Modify: checked-out `gh-pages` branch (di folder sementara)

**Interfaces:**
- Consumes: semua file dashboard dari Task 1–3.
- Produces: tautan dashboard di halaman masuk + versi terdeploy di GitHub Pages.

- [ ] **Step 1: Tulis test yang gagal**

Tambah subcommand `entry` di `checks/verify_dashboard.py`:
- `html = (OUT / "index.html").read_text()`,
- `assert "dashboard.html" in html`,
- `assert "Laporan Teknis" in html` dan `assert "Poster Infografis" in html`.

- [ ] **Step 2: Jalankan test, pastikan gagal**

Run: `python checks/verify_dashboard.py entry`
Expected: FAIL — tautan belum ada.

- [ ] **Step 3: Tambah tautan dashboard ke `index.html`**

Tambah kartu pertama `Dashboard` yang mengarah ke `dashboard.html`, dengan deskripsi "Analisis interaktif: filter fakultas, gender, dan kafein", tetap mempertahankan tiga kartu lama.

- [ ] **Step 4: Jalankan test, lalu deploy**

Run: `python checks/verify_dashboard.py entry`
Expected: PASS.

Salin seluruh isi `project uas/output/` ke working copy branch `gh-pages`, `git add -A`, commit, push `origin HEAD:gh-pages`.

- [ ] **Step 5: Verifikasi publik**

Buka `https://sabillahfikk-glitch.github.io/statprob-tugas5/dashboard.html` dengan webfetch/browser; pastikan judul, KPI `347`, dan grafik muncul. Gunakan `?v=2` bila CDN masih menyajikan cache lama.

- [ ] **Step 6: Commit**

```bash
git add 'project uas/output/index.html' checks/verify_dashboard.py
git commit -m "feat: link dashboard from landing page and deploy"
```
