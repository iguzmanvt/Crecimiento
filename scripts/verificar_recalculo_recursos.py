#!/usr/bin/env python3
"""Regenera los recursos esenciales desde sus insumos locales y coteja la salida.

No descarga datos ni sobrescribe el paquete. Las imágenes exportadas se revisan
por separado; aquí se comparan CSV, JSON, catálogo y vistas HTML publicadas.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def verify(root):
    source = root / "recursos_esenciales"
    catalog = json.loads((source / "catalogo.json").read_text(encoding="utf-8"))
    selected = {"catalogo.json", "index.html", "README.md", "recursos.css"}
    selected.update(p.relative_to(source).as_posix() for p in (source / "datos").iterdir() if p.suffix in (".csv", ".json"))
    selected.update(p.relative_to(source).as_posix() for p in (source / "graficas").glob("*.html"))
    results = []
    with tempfile.TemporaryDirectory(prefix="crecimiento_esenciales_") as temporary:
        output = Path(temporary)
        subprocess.run([sys.executable, str(root / "scripts/generar_recursos_esenciales.py"), "--output", str(output)], check=True)
        target = output / "recursos_esenciales"
        generated = {"catalogo.json", "index.html", "README.md", "recursos.css"}
        generated.update(p.relative_to(target).as_posix() for p in (target / "datos").iterdir() if p.suffix in (".csv", ".json"))
        generated.update(p.relative_to(target).as_posix() for p in (target / "graficas").glob("*.html"))
        assert selected == generated, "El conjunto de salidas regeneradas difiere"
        for relative in sorted(selected):
            before, after = source / relative, target / relative
            assert before.read_bytes() == after.read_bytes(), "La regeneración difiere: " + relative
            results.append({"path": relative, "bytes_identical": True, "sha256": hashlib.sha256(before.read_bytes()).hexdigest()})
    return {"status": "passed", "views": len(catalog["entries"]), "files_compared": len(results), "network_used": False, "environment": sys.version, "scope": "Regeneración de datos y vistas esenciales desde insumos archivados; no autentica objetos remotos históricos ni vuelve a exportar PNG/SVG.", "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.root.resolve())
    except (AssertionError, ValueError, OSError, subprocess.CalledProcessError) as error:
        report = {"status": "failed", "errors": [str(error)]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
