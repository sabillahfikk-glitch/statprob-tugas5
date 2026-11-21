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


CHECKS = {"data": check_data}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHECKS:
        print(f"Usage: python checks/verify_dashboard.py <{'|'.join(CHECKS)}>", file=sys.stderr)
        sys.exit(2)
    CHECKS[sys.argv[1]]()


if __name__ == "__main__":
    main()
