"""Verification checks for Task 5 deliverables.

Usage (from repo root): python checks/verify.py <notebook|charts|report|poster|legacy|all>
"""

import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "project uas" / ".ipynb"
OUT = ROOT / "project uas" / "output"

CHART_FILES = [
    "10_korelasi_heatmap.png",
    "11_scatter_tidur_stres.png",
    "12_scatter_screentime_ipk.png",
    "13_rataan_ipk_stres_fakultas.png",
]


def notebook_source():
    with NB_PATH.open(encoding="utf-8") as f:
        nb = json.load(f)
    return nb, ["".join(c.get("source", [])) for c in nb["cells"]]


def check_notebook():
    nb, sources = notebook_source()
    cell28 = sources[28]
    assert 'title="Statistik"' in cell28, "cell 28 legend title harus 'Statistik'"
    assert 'title="Konsumsi_Kafein"' not in cell28, "label legend lama masih ada di cell 28"
    markdown = ["".join(c.get("source", [])) for c in nb["cells"] if c["cell_type"] == "markdown"]
    assert any("1.8 Grafik Pendukung Analisis" in s for s in markdown), "header bagian 1.8 belum ada"
    print("PASS notebook: legend diperbaiki dan header 1.8 ada")


def check_charts():
    _, sources = notebook_source()
    all_source = "\n".join(sources)
    for name in CHART_FILES:
        path = OUT / name
        assert path.exists(), f"{name} belum ada"
        with Image.open(path) as img:
            assert img.format == "PNG", f"{name} bukan PNG"
            assert img.width >= 800 and img.height >= 500, f"{name} terlalu kecil"
        assert name in all_source, f"cell penyimpan {name} belum ada di notebook"
    print("PASS charts: 4 grafik pendukung valid")


def check_report():
    path = OUT / "14_laporan_teknis.html"
    assert path.exists(), "laporan teknis belum ada"
    html = path.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html, "bukan dokumen HTML"
    for heading in ["Ringkasan Eksekutif", "Statistika Deskriptif", "Kualitas Data", "Visualisasi"]:
        assert heading in html, f"bagian '{heading}' belum ada"
    assert html.count("data:image/png;base64,") >= 9, "gambar tidak disisipkan sebagai base64"
    assert 'src="output/' not in html, "laporan masih bergantung pada folder output/"
    assert 'src="http' not in html, "laporan bergantung pada gambar eksternal"
    for value in ["347", "6.355", "58.292", "3.250"]:
        assert value in html, f"nilai kunci {value} tidak ada di laporan"
    print("PASS report: laporan teknis HTML mandiri valid")


CHECKS = {"notebook": check_notebook, "charts": check_charts, "report": check_report}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHECKS:
        print(f"Usage: python checks/verify.py <{'|'.join(CHECKS)}>", file=sys.stderr)
        sys.exit(2)
    CHECKS[sys.argv[1]]()


if __name__ == "__main__":
    main()
