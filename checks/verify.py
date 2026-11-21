"""Verification checks for Task 5 deliverables.

Usage (from repo root): python checks/verify.py <notebook|charts|report|poster|legacy|repro|all>
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
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


def check_poster():
    img_path = OUT / "15_poster_infografis.png"
    assert img_path.exists(), "poster PNG belum ada"
    with Image.open(img_path) as img:
        assert img.format == "PNG", "poster bukan PNG"
        assert img.height > img.width, "poster harus potrait"
        assert img.width >= 1000 and img.height >= 1400, "poster terlalu kecil"
    assert (OUT / "16_poster_infografis.html").exists(), "poster HTML belum ada"
    print("PASS poster: poster infografis PNG dan HTML valid")


def check_legacy():
    base = subprocess.run(
        ["git", "merge-base", "main", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    changed = subprocess.run(
        ["git", "diff", "--name-only", base, "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    dirty = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    bad = [p for p in changed + dirty if re.search(r"output/0[1-9]_", p)]
    assert not bad, "file output lama ikut berubah: " + ", ".join(bad)
    print("PASS legacy: file output 01_-09_ tidak diubah (committed maupun working tree)")


def check_repro():
    """Run the real regplot cell twice in fresh processes; output bytes must match."""
    nb, _ = notebook_source()
    cell = next(c for c in nb["cells"] if c.get("id") == "tugas5-regresi-tidur-stres")
    src = "".join(cell["source"])
    prelude = (
        "import sys\n"
        "import pandas as pd\n"
        "import matplotlib\n"
        'matplotlib.use("Agg")\n'
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from pathlib import Path\n"
        'df = pd.read_csv(sys.argv[1]).dropna(subset=["IPK"])\n'
        "OUTPUT = Path(sys.argv[2])\n"
        "OUTPUT.mkdir(parents=True, exist_ok=True)\n"
    )
    csv = ROOT / "project uas" / "Kelompok_23_Tema_C_Akademik_Tidur.csv"
    hashes = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for i in range(2):
            script = tmp / f"run{i}.py"
            script.write_text(prelude + src, encoding="utf-8")
            outdir = tmp / f"out{i}"
            subprocess.run(
                [sys.executable, str(script), str(csv), str(outdir)], check=True,
                capture_output=True,
            )
            png = outdir / "11_scatter_tidur_stres.png"
            hashes.append(hashlib.sha256(png.read_bytes()).hexdigest())
    assert hashes[0] == hashes[1], "grafik regplot berbeda antar dua eksekusi (tidak reproducible)"
    print("PASS repro: regplot deterministik antar dua eksekusi")


def check_all():
    for name in ["notebook", "legacy", "charts", "report", "poster", "repro"]:
        CHECKS[name]()
    print("PASS all: seluruh verifikasi Task 5 lolos")


CHECKS = {
    "notebook": check_notebook,
    "legacy": check_legacy,
    "charts": check_charts,
    "report": check_report,
    "poster": check_poster,
    "repro": check_repro,
    "all": check_all,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHECKS:
        print(f"Usage: python checks/verify.py <{'|'.join(CHECKS)}>", file=sys.stderr)
        sys.exit(2)
    CHECKS[sys.argv[1]]()


if __name__ == "__main__":
    main()
