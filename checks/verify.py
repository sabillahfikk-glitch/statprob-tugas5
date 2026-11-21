"""Verification checks for Task 5 deliverables.

Usage (from repo root): python checks/verify.py <notebook|charts|report|poster|legacy|all>
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB_PATH = ROOT / "project uas" / ".ipynb"
OUT = ROOT / "project uas" / "output"


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


CHECKS = {"notebook": check_notebook}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in CHECKS:
        print(f"Usage: python checks/verify.py <{'|'.join(CHECKS)}>", file=sys.stderr)
        sys.exit(2)
    CHECKS[sys.argv[1]]()


if __name__ == "__main__":
    main()
