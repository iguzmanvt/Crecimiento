#!/usr/bin/env python3
"""Recalcula las vistas OWID desde CSV archivados, sin red ni exportar imágenes.

Compara todos los CSV y las especificaciones JSON. En números usa tolerancia
absoluta y relativa 1e-12 para bibliotecas matemáticas de sistemas diferentes.
El contraste registra además si los bytes coinciden exactamente.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile


def compare(left, right, maximum):
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) == type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        maximum[0] = max(maximum[0], abs(left - right))
        return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-12)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(compare(left[k], right[k], maximum) for k in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(compare(a, b, maximum) for a, b in zip(left, right))
    return left == right


def verify(root):
    source = root / "introduccion_local/owid"
    catalog = json.loads((source / "catalogo.json").read_text(encoding="utf-8"))
    spec = importlib.util.spec_from_file_location("owid_recalculation", root / "scripts/generar_introduccion_owid.py")
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    results = []
    with tempfile.TemporaryDirectory(prefix="crecimiento_owid_") as temporary:
        target = Path(temporary)
        generated = generator.build(target)
        assert {e["slug"] for e in generated} == {e["slug"] for e in catalog["entries"]}, "Vistas regeneradas difieren"
        for entry in catalog["entries"]:
            slug = entry["slug"]
            before = source / "datos" / (slug + ".json")
            after = target / "datos" / (slug + ".json")
            maximum = [0.0]
            assert compare(json.loads(before.read_text(encoding="utf-8")), json.loads(after.read_text(encoding="utf-8")), maximum), "Especificación regenerada difiere: " + slug
            original_csv = (source / "datos" / (slug + ".csv")).read_bytes()
            generated_csv = (target / "datos" / (slug + ".csv")).read_bytes()
            assert original_csv == generated_csv, "CSV regenerado difiere: " + slug
            results.append({"slug": slug, "spec_equivalent_within_tolerance": True, "spec_bytes_identical": before.read_bytes() == after.read_bytes(), "csv_bytes_identical": True, "maximum_numeric_difference": maximum[0], "spec_sha256": hashlib.sha256(before.read_bytes()).hexdigest()})
    return {"status": "passed", "figures": len(results), "network_used": False, "absolute_tolerance": 1e-12, "relative_tolerance": 1e-12, "environment": sys.version, "platform": sys.platform, "scope": "Recálculo de CSV y especificaciones de las vistas OWID desde los insumos archivados; exportaciones visuales y conclusiones académicas se comprueban por separado.", "results": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = verify(args.root.resolve())
    except (AssertionError, ValueError, OSError, KeyError) as error:
        report = {"status": "failed", "errors": [str(error)]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
