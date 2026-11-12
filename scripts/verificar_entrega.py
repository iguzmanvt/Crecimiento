#!/usr/bin/env python3
"""Comprueba la entrega publicada sin consultar internet ni ejecutar R.

Comprueba los catálogos, las huellas registradas y los destinos HTML/CSS de
recursos y enlaces locales. Los originales históricos quedan fuera del
recorrido estricto; las fuentes editoriales siguen siendo enlaces opcionales.
Esta comprobación estructural no sustituye una lectura académica ni el navegador.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from urllib.parse import unquote, urlsplit


CATALOGS = (
    "graficas_reconstruidas/catalogo.json",
    "introduccion_local/chartstudio/catalogo.json",
    "introduccion_local/owid/catalogo.json",
    "recursos_esenciales/catalogo.json",
)
CSS_URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
CSS_IMPORT = re.compile(r"@import\s+['\"]([^'\"]+)['\"]", re.I)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(path):
    """Match the renderer's LF normalization across Windows/Git checkouts."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = set()
        self.slides = 0
        self.script_type = None
        self.script_body = []
        self.scripts = []
        self.style_body = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "slide":
            self.slides += 1
        if tag == "script":
            self.script_type = attrs.get("type", "text/javascript")
            self.script_body = []
        if tag == "style":
            self.style_body = []
        active = {"img": "src", "script": "src", "iframe": "src", "source": "src", "video": "src", "audio": "src", "object": "data"}
        if tag in active and attrs.get(active[tag]):
            self.references.append((attrs[active[tag]], True, tag))
        if tag == "video" and attrs.get("poster"):
            self.references.append((attrs["poster"], True, "poster"))
        if tag == "link" and attrs.get("href"):
            self.references.append((attrs["href"], True, "link"))
        if tag == "a" and attrs.get("href"):
            self.references.append((attrs["href"], False, "a"))
        if tag == "use" and (attrs.get("href") or attrs.get("xlink:href")):
            self.references.append((attrs.get("href") or attrs["xlink:href"], True, "use"))
        if attrs.get("style"):
            self.references.extend((x, True, "style") for x in CSS_URL.findall(attrs["style"]))
        if attrs.get("srcset"):
            for item in attrs["srcset"].split(","):
                if item.strip() and not item.strip().startswith("data:"):
                    self.references.append((item.strip().split()[0], True, "srcset"))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self.script_type is not None:
            self.script_body.append(data)
        if self.style_body is not None:
            self.style_body.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script_type is not None:
            if self.script_type not in ("application/json", "application/ld+json"):
                self.scripts.append("".join(self.script_body))
            self.script_type = None
        if tag == "style" and self.style_body is not None:
            css = "".join(self.style_body)
            self.references.extend((x, True, "style-url") for x in CSS_URL.findall(css) + CSS_IMPORT.findall(css))
            self.style_body = None


def local_target(root, source, ref):
    parts = urlsplit(ref.strip())
    if parts.scheme or parts.netloc or not ref.strip():
        return None, parts
    if parts.path.startswith("/"):
        raise ValueError("Ruta absoluta incompatible con disco/subruta web: " + ref)
    path = (root / unquote(parts.path).lstrip("/")) if parts.path.startswith("/") else source.parent / unquote(parts.path)
    if not parts.path:
        path = source
    path = path.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("Destino fuera del paquete: " + ref)
    if path.is_dir():
        path = path / "index.html"
    return path, parts


def catalog_entries(data):
    for key in ("entries", "figures", "charts", "records"):
        if isinstance(data.get(key), list):
            return data[key]
    raise ValueError("Catálogo sin lista de figuras")


def seed_paths(root, require_new=True):
    materials = json.loads((root / "materiales_actualizados/catalogo.json").read_text(encoding="utf-8"))
    consultation = json.loads((root / "material_consulta/catalogo.json").read_text(encoding="utf-8"))
    paths = {root / "index.html", root / "portal/index.html", root / "materiales_actualizados/index.html", root / "introduccion_local/index.html"}
    paths.update(root / x["html"] for x in materials["materials"])
    paths.update((root / "material_consulta").rglob("*.html"))
    catalog_info = []
    for relative in CATALOGS:
        path = root / relative
        if not path.is_file():
            if require_new:
                raise ValueError("Falta catálogo requerido: " + relative)
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = catalog_entries(data)
        if not entries:
            raise ValueError("Catálogo sin figuras: " + relative)
        slugs = [entry["slug"] for entry in entries]
        if len(slugs) != len(set(slugs)):
            raise ValueError("Slugs duplicados: " + relative)
        htmls = {path.parent / "index.html"}
        for entry in entries:
            published_html = root / entry["html"] if entry.get("html") else path.parent / "graficas" / (entry["slug"] + ".html")
            if not published_html.is_file():
                raise ValueError("Vista de catálogo inexistente: " + str(published_html))
            htmls.add(published_html)
            for field in ("csv", "json", "png", "svg", "image_png", "image_svg"):
                if entry.get(field) and not (root / entry[field]).is_file():
                    raise ValueError("Destino de catálogo inexistente: " + entry[field])
            specpath = path.parent / entry.get("spec_path", "datos/" + entry["slug"] + ".json")
            if entry.get("spec_sha256"):
                if not specpath.is_file() or digest(specpath) != entry["spec_sha256"]:
                    raise ValueError("Huella JSON de figura: " + entry["slug"])
            if entry.get("csv_sha256"):
                csvpath = path.parent / "datos" / (entry["slug"] + ".csv")
                if not csvpath.is_file() or digest(csvpath) != entry["csv_sha256"]:
                    raise ValueError("Huella CSV de figura: " + entry["slug"])
            if entry.get("data_sha256"):
                csvpath = path.parent / "datos" / (entry["slug"] + ".csv")
                if not csvpath.is_file() or digest(csvpath) != entry["data_sha256"]:
                    raise ValueError("Huella de datos: " + entry["slug"])
            for local, expected in entry.get("local_inputs", {}).items():
                source = path.parent / entry.get("input_base", entry.get("local_inputs_base", "")) / local
                if not source.is_file() or digest(source) != expected:
                    raise ValueError("Huella de insumo: " + str(source))
        # Archived source HTML can retain remote loaders. Only the published
        # views named by the catalog enter the strict current-delivery scope.
        if not all(p.is_file() for p in htmls):
            raise ValueError("Catálogo sin vistas HTML: " + relative)
        paths.update(htmls)
        catalog_info.append({"catalog": relative, "entries": len(entries), "html_views": len(htmls), "sha256": digest(path)})
    return sorted(paths), materials, consultation, catalog_info


def verify(root):
    root = root.resolve()
    errors = []
    def ensure(condition, message):
        if not condition:
            errors.append(message)
    seeds, materials, consultation, catalog_info = seed_paths(root)
    ensure(materials["count"] == len(materials["materials"]), "Conteo del catálogo de materiales")
    module_names = [x["module"] for x in consultation["modules"]]
    ensure(len(module_names) == len(set(module_names)), "Temas duplicados")
    for module in module_names:
        found = [x["kind"] for x in materials["materials"] if x["module"] == module]
        ensure(found.count("notas") == 1 and found.count("presentacion") == 1, "Notas/presentación: " + module)
    ensure({x["module"] for x in materials["materials"]} == set(module_names), "Temas difieren entre catálogos")
    for item in materials["materials"]:
        path = root / item["html"]
        ensure(path.is_file(), "Falta material: " + item["html"])
        ensure((root / item["source"]).is_file(), "Falta fuente: " + item["source"])
        ensure(bool(item.get("source_sha256")), "Falta huella de la fuente: " + item["source"])
        if (root / item["source"]).is_file() and item.get("source_sha256"):
            ensure(source_digest(root / item["source"]) == item["source_sha256"], "La fuente cambió sin regenerar: " + item["source"])
        if path.is_file():
            ensure(digest(path) == item["sha256"], "Huella de material: " + item["html"])
    for task in consultation["assignments"]:
        for key, hashkey in (("file", "public_markdown_sha256"), ("html", "public_html_sha256")):
            path = root / "material_consulta" / task[key]
            ensure(path.is_file(), "Falta tarea: " + task[key])
            if path.is_file():
                ensure(digest(path) == task[hashkey], "Huella de tarea: " + task[key])
    manifest_path = root / "portal/manifest.json"
    portal_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name, expected in portal_manifest["source_catalogs"].items():
        ensure(digest(root / name) == expected, "Catálogo de entrada del portal cambió: " + name)
    for name, expected in portal_manifest["files"].items():
        ensure(digest(root / "portal" / name) == expected, "Huella del portal: " + name)
    ensure(portal_manifest["topics"] == len(module_names), "Conteo de temas del portal")
    ensure(portal_manifest["assignments"] == len(consultation["assignments"]), "Conteo de tareas del portal")
    ensure(all((root / p).is_file() for p in portal_manifest["local_targets"]), "Destinos del portal")
    for relative in CATALOGS[1:]:
        collection = str(Path(relative).parent / "index.html").replace("\\", "/")
        ensure(collection in portal_manifest["local_targets"], "El portal no enlaza " + collection)
    portal_matches = True
    with tempfile.TemporaryDirectory(prefix="crecimiento_portal_") as temporary:
        temp = Path(temporary)
        for directory in ("material_consulta", "materiales_actualizados", "portal"):
            (temp / directory).mkdir()
        for name in ("material_consulta/catalogo.json", "materiales_actualizados/catalogo.json", "portal/portal.css", "portal/portal.js"):
            shutil.copyfile(root / name, temp / name)
        for name in portal_manifest["local_targets"]:
            target = temp / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.touch()
        for name in CATALOGS[1:3]:
            target = temp / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / name, target)
        spec = importlib.util.spec_from_file_location("course_portal", root / "scripts/generar_portal.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.generate(temp)
        for name in ("portal/index.html", "portal/manifest.json", "index.html", "introduccion_local/index.html", "introduccion_local/manifest.json"):
            identical = (temp / name).read_bytes() == (root / name).read_bytes()
            portal_matches = portal_matches and identical
            ensure(identical, "Generación del portal difiere: " + name)
    documents = {}
    queue = deque(seeds)
    seen = set()
    links_checked = resources_checked = 0
    external_links = set()
    external_active = []
    def parse(path):
        if path not in documents:
            doc = Document()
            doc.feed(path.read_text(encoding="utf-8-sig"))
            documents[path] = doc
        return documents[path]
    while queue:
        path = queue.popleft().resolve()
        if path in seen:
            continue
        seen.add(path)
        ensure(path.is_file(), "Falta archivo recorrido: " + path.relative_to(root).as_posix())
        if not path.is_file():
            continue
        if path.suffix.lower() == ".html":
            doc = parse(path)
            refs = doc.references
            # A dynamic remote MathJax loader is an active dependency even
            # though it does not have a static script[src] attribute.
            if any(re.search(r"(?:mathjax\.rstudio|cdn\.jsdelivr\.net/npm/mathjax|cdn\.mathjax)", s, re.I) for s in doc.scripts):
                external_active.append({"source": path.relative_to(root).as_posix(), "kind": "dynamic_mathjax"})
        elif path.suffix.lower() == ".css":
            css = path.read_text(encoding="utf-8-sig")
            refs = [(x, True, "css-url") for x in CSS_URL.findall(css) + CSS_IMPORT.findall(css)]
        else:
            continue
        for reference, active, kind in refs:
            if reference.startswith(("data:", "blob:", "javascript:", "mailto:", "tel:")):
                continue
            if active:
                resources_checked += 1
            else:
                links_checked += 1
            try:
                target, parts = local_target(root, path, reference)
            except ValueError as error:
                errors.append(str(error) + " en " + path.relative_to(root).as_posix())
                continue
            if target is None:
                if active and parts.scheme in ("http", "https", ""):
                    external_active.append({"source": path.relative_to(root).as_posix(), "kind": kind, "url": reference})
                elif not active:
                    external_links.add(reference)
                continue
            if not target.is_file():
                errors.append("Destino inexistente: " + path.relative_to(root).as_posix() + " → " + reference)
                continue
            if parts.fragment and target.suffix.lower() == ".html":
                target_doc = parse(target)
                fragment = unquote(parts.fragment)
                numeric_slide = fragment.isdigit() and 1 <= int(fragment) <= target_doc.slides
                ensure(fragment in target_doc.ids or numeric_slide, "Ancla inexistente: " + path.relative_to(root).as_posix() + " → " + reference)
            if active and target.suffix.lower() in (".html", ".css"):
                queue.append(target)
    ensure(not external_active, "Hay dependencias externas activas")
    math_path = root / "scripts/localizar_formulas.py"
    spec = importlib.util.spec_from_file_location("course_math", math_path)
    math_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(math_module)
    math_module.vendor_manifest(root / "vendor/mathjax")
    formulas = []
    for row in materials["materials"]:
        record = math_module.localize(root / row["html"], root / "vendor/mathjax", check=True)
        formulas.append({"html": row["html"], "tex_expressions": record["tex_expressions"]})
    return {"status": "passed" if not errors else "failed", "scope": "Catálogos, huellas y grafo local HTML/CSS de la entrega actualizada; originales históricos y disponibilidad editorial fuera del alcance.", "materials": len(materials["materials"]), "topics": len(module_names), "assignments": len(consultation["assignments"]), "seed_htmls": len(seeds), "html_and_css_scanned": len(seen), "local_link_references": links_checked, "active_resource_references": resources_checked, "optional_external_links": len(external_links), "external_active": external_active, "catalogs": catalog_info, "portal_generation_identical": portal_matches, "tex_expressions": sum(x["tex_expressions"] for x in formulas), "math_by_material": formulas, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.root)
    except (OSError, ValueError, KeyError, AssertionError) as error:
        report = {"status": "failed", "errors": [str(error)]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key not in ("math_by_material", "catalogs")}, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
