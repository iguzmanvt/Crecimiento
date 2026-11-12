#!/usr/bin/env python3
"""Regenera los materiales canónicos preservando el archivo histórico.

python scripts/construir_entrega.py --output /tmp/crecimiento-render
python scripts/construir_entrega.py --skip-render  # postprocesa HTML ya renderizados

Requiere R/rmarkdown y los paquetes de los Rmd al renderizar. Los datos y motores
de visualización ya deben estar archivados en la copia completa del repositorio.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit, urlunsplit


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def repair_paths(text, destination, repo):
    # The Rmd use paths from their original folder. The canonical HTML is deeper.
    for folder in ("graficas_reconstruidas", "introduccion_local", "recursos_esenciales"):
        relative = os.path.relpath(repo / folder, destination.parent).replace("\\", "/") + "/"
        text = re.sub(r'(?:\.\./)+' + folder + '/', lambda _: relative, text)
    return text


def consult(repo, pandoc):
    """Convert published Markdown as-is; do not re-import historical originals."""
    records = []
    root = repo / "material_consulta"
    template = root / "consulta.template"
    for source in sorted(root.rglob("*.md")):
        target = source.with_name("index.html" if source.name == "README.md" else source.stem + ".html")
        title = next((s[2:].strip() for s in source.read_text(encoding="utf-8").splitlines() if s.startswith("# ")), source.stem)
        css = os.path.relpath(root / "consulta.css", source.parent).replace("\\", "/")
        subprocess.run([pandoc, str(source), "-f", "markdown", "-t", "html5", "--standalone", "--mathml", "--wrap=none", "--template", str(template), "--metadata", "title=" + title, "--css", css, "-o", str(target)], check=True)
        text = target.read_text(encoding="utf-8")
        def relink(m):
            value = html.unescape(m[1])
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path:
                return m[0]
            resolved = (target.parent / unquote(parts.path)).resolve()
            if root.resolve() not in resolved.parents:
                return m[0]
            new_path = re.sub(r'(^|/)README\.md$', r'\1index.html', parts.path)
            new_path = re.sub(r'\.md$', '.html', new_path)
            value = urlunsplit(('', '', new_path, parts.query, parts.fragment))
            return 'href="' + html.escape(value, quote=True) + '"'
        text = re.sub(r'href="([^\"]+)"', relink, text)
        target.write_text(text, encoding="utf-8", newline="\n")
        records.append({"markdown": source.relative_to(repo).as_posix(), "html": target.relative_to(repo).as_posix(), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rscript", default=shutil.which("Rscript"))
    parser.add_argument("--pandoc", default=shutil.which("pandoc"))
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument("--module", action="append")
    parser.add_argument("--consultation", action="store_true", help="Regenerar las páginas de consulta desde su Markdown publicado")
    args = parser.parse_args()
    repo = args.root.resolve()
    evidence = repo / "verificacion/estable_20261112"
    evidence.mkdir(parents=True, exist_ok=True)
    catalog_path = repo / "materiales_actualizados/catalogo.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    selected = [r for r in catalog["materials"] if not args.module or r["module"] in args.module]
    if args.module and set(args.module) - {r["module"] for r in selected}:
        raise ValueError("Módulo desconocido")
    if not args.skip_render:
        if not args.rscript:
            raise ValueError("Especifica --rscript o agrega Rscript al PATH")
        output = (args.output or Path(tempfile.mkdtemp(prefix="crecimiento-render-"))).resolve()
        env = os.environ.copy()
        if args.pandoc:
            env["RSTUDIO_PANDOC"] = str(Path(args.pandoc).resolve().parent)
        subprocess.run([args.rscript, str(repo / "scripts/renderizar_entrega.R"), str(output)] + (args.module or []), env=env, check=True)
        rendered = json.loads((output / "renderizado.json").read_text(encoding="utf-8"))
        if len(rendered["results"]) != len(selected) or any(r["status"] != "passed" for r in rendered["results"]):
            raise ValueError("Renderizado incompleto")
        for row in selected:
            source = output / row["html"]
            destination = repo / row["html"]
            # Replace only this generated canonical material folder.
            for old in destination.parent.iterdir():
                if old.is_file():
                    old.unlink()
                elif old.is_dir():
                    shutil.rmtree(old)
            shutil.copytree(source.parent, destination.parent, dirs_exist_ok=True, ignore=shutil.ignore_patterns("intermedios"))
        render_report = evidence / "renderizado.json"
        if args.module and render_report.exists():
            previous = json.loads(render_report.read_text(encoding="utf-8"))
            updated = {r["html"]: r for r in rendered["results"]}
            rendered["results"] = [updated.pop(r["html"], r) for r in previous["results"]] + list(updated.values())
        render_report.write_text(json.dumps(rendered, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    formulas = load(repo / "scripts/localizar_formulas.py", "formulas")
    formulas.vendor_manifest(repo / "vendor/mathjax")
    rows = []
    for row in selected:
        target = repo / row["html"]
        source_hash = hashlib.sha256((repo / row["source"]).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        if args.skip_render and row.get("source_sha256") != source_hash:
            raise ValueError("La fuente cambió: --skip-render no acredita su regeneración. Renderiza el módulo: " + row["module"])
        text = repair_paths(target.read_text(encoding="utf-8"), target, repo)
        target.write_text(text, encoding="utf-8", newline="\n")
        checked = formulas.localize(target, repo / "vendor/mathjax")
        row["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        row["source_sha256"] = source_hash
        row["source_hash_line_endings"] = "LF"
        rows.append({"html": row["html"], "tex_expressions": checked["tex_expressions"], "source_tex_unchanged": checked["source_tex_unchanged"], "sha256": row["sha256"]})
    # Consultation MathML is browser-native and uses no remote formula engine.
    if args.consultation:
        if not args.pandoc:
            raise ValueError("--consultation requiere --pandoc o Pandoc en PATH")
        entries = consult(repo, args.pandoc)
        (evidence / "consulta_generada.json").write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    consultation_path = repo / "material_consulta/catalogo.json"
    consultation = json.loads(consultation_path.read_text(encoding="utf-8"))
    for assignment in consultation["assignments"]:
        assignment["public_markdown_sha256"] = hashlib.sha256((repo / "material_consulta" / assignment["file"]).read_bytes()).hexdigest()
        assignment["public_html_sha256"] = hashlib.sha256((repo / "material_consulta" / assignment["html"]).read_bytes()).hexdigest()
    consultation_path.write_text(json.dumps(consultation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    portal = load(repo / "scripts/generar_portal.py", "portal")
    portal.generate(repo)
    processed_this_run = len(rows)
    formula_report = evidence / "formulas_locales.json"
    if args.module and formula_report.exists():
        previous = json.loads(formula_report.read_text(encoding="utf-8"))
        updated = {r["html"]: r for r in rows}
        rows = [updated.pop(r["html"], r) for r in previous["results"]] + list(updated.values())
    report = {"materials_processed": processed_this_run, "materials_in_report": len(rows), "mathjax_version": formulas.VERSION, "tex_expressions": sum(x["tex_expressions"] for x in rows), "results": rows}
    formula_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))


if __name__ == "__main__":
    main()
