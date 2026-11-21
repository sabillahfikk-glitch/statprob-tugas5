"""Verification for the Data Analytics & Visualization Dashboard.

Usage (from repo root): python checks/verify_dashboard.py <data|files|js|entry|all>
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "project uas" / "output"

KEYS = {
    "Fakultas", "Jenis_Kelamin", "Konsumsi_Kafein",
    "Durasi_Tidur_Jam", "Screen_Time_Jam", "Jam_Belajar_Mingguan",
    "Skor_Stres", "IPK",
}


def check_data():
    path = OUT / "dashboard-data.js"
    assert path.exists(), "dashboard-data.js belum ada"
    teks = path.read_text(encoding="utf-8")
    assert "window.SLEEP_DATA" in teks, "window.SLEEP_DATA tidak ditemukan"
    payload = teks.split("=", 1)[1].strip().rstrip(";\n").strip()
    data = json.loads(payload)
    assert len(data) == 347, f"jumlah record {len(data)} bukan 347"
    assert set(data[0].keys()) == KEYS, "kunci data tidak sesuai"
    mean_tidur = sum(r["Durasi_Tidur_Jam"] for r in data) / len(data)
    assert round(mean_tidur, 3) == 6.355, f"mean tidur {mean_tidur}"
    print("PASS data: 347 record, 8 kunci, mean tidur 6.355")


IDS = [
    "kpi-n", "kpi-tidur", "kpi-stres", "kpi-ipk",
    "filter-fakultas", "filter-gender", "filter-kafein", "filter-reset",
    "chart-fakultas", "chart-kafein", "chart-tidur-stres", "chart-ipk-fakultas",
    "ringkasan-body", "heatmap",
]


def check_files():
    for name in ["dashboard.html", "dashboard.css", "dashboard-data.js", "vendor/chart.umd.min.js"]:
        assert (OUT / name).exists(), f"{name} belum ada"
    vendor = OUT / "vendor" / "chart.umd.min.js"
    assert len(vendor.read_bytes()) > 100_000, "Chart.js lokal terlalu kecil / belum terunduh"
    html = (OUT / "dashboard.html").read_text(encoding="utf-8")
    for element_id in IDS:
        assert f'id="{element_id}"' in html, f'id "{element_id}" belum ada di HTML'
    assert "dashboard-data.js" in html, "data script belum dimuat"
    assert "vendor/chart.umd.min.js" in html, "Chart.js lokal belum dimuat"
    for name in ["dashboard.html", "dashboard.css", "dashboard-data.js"]:
        isi = (OUT / name).read_text(encoding="utf-8")
        assert "https://" not in isi, f"{name} masih memuat tautan CDN/eksternal"
        assert "fetch(" not in isi, f"{name} memakai fetch() (tidak jalan dari file://)"
    css = (OUT / "dashboard.css").read_text(encoding="utf-8")
    assert "@media" in css, "CSS tidak punya aturan responsif"
    print("PASS files: HTML/CSS/vendor lokal lengkap, tanpa CDN dan fetch")


def check_js():
    js = (OUT / "dashboard.js").read_text(encoding="utf-8")
    assert "window.SLEEP_DATA" in js, "JS tidak mengonsumsi window.SLEEP_DATA"
    assert "window.__dashboard" in js, "helper window.__dashboard belum ada"
    assert "filter-fakultas" in js, "JS tidak mengikat filter fakultas"
    assert "filter-reset" in js, "JS tidak mengikat tombol reset"
    print("PASS js: dashboard.js mengonsumsi data dan mengikat filter")


def check_entry():
    html = (OUT / "index.html").read_text(encoding="utf-8")
    assert "dashboard.html" in html, "tautan dashboard belum ada di index.html"
    assert "Laporan Teknis" in html, "tautan laporan teknis hilang"
    assert "Poster Infografis" in html, "tautan poster hilang"
    print("PASS entry: halaman masuk menautkan dashboard, laporan, dan poster")


def check_all():
    for name in ["data", "files", "js", "entry"]:
        CHECKS[name]()
    print("PASS all: seluruh verifikasi dashboard lolos")


CHECKS = {
    "data": check_data,
    "files": check_files,
    "js": check_js,
    "entry": check_entry,
    "all": check_all,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHECKS:
        print(f"Usage: python checks/verify_dashboard.py <{'|'.join(CHECKS)}>", file=sys.stderr)
        sys.exit(2)
    CHECKS[sys.argv[1]]()


if __name__ == "__main__":
    main()
