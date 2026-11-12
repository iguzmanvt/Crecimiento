#!/usr/bin/env python3
"""Localize MathJax in rendered course HTML without changing its mathematical source.

Default: the 33 entries in materiales_actualizados/catalogo.json.
Examples:
  python scripts/localizar_formulas.py /path/to/repo --report /tmp/math.json
  python scripts/localizar_formulas.py /path/to/repo --check
  python scripts/localizar_formulas.py /path/to/repo --html /render/Material.html

The fixed MathJax distribution lives in vendor/mathjax. Only the loader and
its configuration are replaced; source Rmd, formula strings, and figures remain.
Python standard library only. Does not download or execute a browser.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

VERSION = "3.2.2"
SCRIPT_PATH = "es5/tex-svg-full.js"
START = "<!-- CRECIMIENTO_MATHJAX_LOCAL_BEGIN -->"
END = "<!-- CRECIMIENTO_MATHJAX_LOCAL_END -->"
BLOCK = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
SCRIPTS = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script\s*>", re.I | re.S)
REMOTE = re.compile(r"(?:https?:)?//(?:mathjax\.rstudio\.com|(?:cdn\.)?mathjax\.org|cdn\.jsdelivr\.net/npm/mathjax)[^\s\"'<>]*", re.I)
MATH = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]|\$\$(.*?)\$\$", re.S)


class Visible(HTMLParser):
    """Collect body text while leaving authored TeX strings untouched."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "body":
            self.in_body = False
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if self.in_body and not self.skip:
            self.parts.append(data)


def visible(source: str) -> str:
    parser = Visible()
    parser.feed(source)
    return "\n".join(parser.parts)


def expressions(source: str) -> list[str]:
    return ["".join(groups) for groups in MATH.findall(visible(source))]


def vendor_manifest(vendor: Path) -> dict:
    manifest = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != VERSION:
        raise ValueError("Unsupported MathJax vendor version")
    for item in manifest["files"]:
        path = vendor / item["path"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("MathJax vendor hash differs: " + item["path"])
    return manifest


def injection(html_path: Path, vendor: Path) -> str:
    relative = os.path.relpath(vendor / SCRIPT_PATH, html_path.parent).replace("\\", "/")
    # SVG includes font geometry; menu is disabled to avoid optional network-loaded
    # accessibility/UI components. All TeX packages are already in the full bundle.
    configuration = {
        "tex": {
            "inlineMath": [["\\(", "\\)"]],
            "displayMath": [["\\[", "\\]"], ["$$", "$$"]],
            "processEscapes": True,
        },
        "svg": {"fontCache": "local"},
        "options": {"enableMenu": False},
    }
    return (
        START + "\n"
        '<script id="crecimiento-mathjax-config">\n'
        "window.MathJax = " + json.dumps(configuration, ensure_ascii=False) + ";\n"
        "</script>\n"
        '<script id="MathJax-script" defer src="' + relative + '"></script>\n'
        '<style id="crecimiento-mathjax-style">'
        'mjx-container[display="true"]{max-width:100%;overflow-x:auto;overflow-y:hidden}'
        "</style>\n" + END
    )


def localize(path: Path, vendor: Path, check: bool = False) -> dict:
    source = path.read_text(encoding="utf-8")
    before = expressions(source)
    loader = injection(path, vendor)
    old_block = BLOCK.findall(source)
    remote_scripts = []

    def remove_remote(match):
        attrs, body = match.group("attrs"), match.group("body")
        if REMOTE.search(attrs + body):
            remote_scripts.append(match.group(0))
            return ""
        if "MathJax.Hub.Config" in body:
            raise ValueError("MathJax v2 custom configuration needs manual review: " + str(path))
        return match.group(0)

    without_block = BLOCK.sub("", source)
    prepared = SCRIPTS.sub(remove_remote, without_block)
    if len(old_block) > 1:
        raise ValueError("Duplicate local MathJax block: " + str(path))
    if not old_block and not remote_scripts:
        raise ValueError("No known MathJax loader: " + str(path))
    if old_block:
        # Replacing in place makes a second invocation byte-identical.
        result = BLOCK.sub(lambda _: loader, source)
        result = SCRIPTS.sub(lambda m: "" if REMOTE.search(m.group("attrs") + m.group("body")) else m.group(0), result)
    else:
        # All reviewed R Markdown documents use one late dynamic loader.
        first = source.find(remote_scripts[0])
        result = source[:first] + loader + source[first + len(remote_scripts[0]):]
        for other in remote_scripts[1:]:
            result = result.replace(other, "")
    if REMOTE.search(result):
        raise ValueError("Remote MathJax URL remains: " + str(path))
    if re.sub(r'\s+', ' ', visible(source)).strip() != re.sub(r'\s+', ' ', visible(result)).strip() or before != expressions(result):
        raise ValueError("Authored body or formula changed: " + str(path))
    if check and source != result:
        raise ValueError("HTML does not yet use the fixed local MathJax loader: " + str(path))
    changed = source != result
    if changed and not check:
        path.write_text(result, encoding="utf-8", newline="\n")
    raw = path.read_bytes()
    return {
        "html": str(path),
        "tex_expressions": len(before),
        "changed": changed,
        "source_tex_unchanged": True,
        "visible_body_unchanged": True,
        "mathjax_version": VERSION,
        "mathjax_relative_script": os.path.relpath(vendor / SCRIPT_PATH, path.parent).replace("\\", "/"),
        "remote_mathjax_references": 0,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Repository/package root containing vendor/mathjax")
    parser.add_argument("--vendor-dir", type=Path)
    parser.add_argument("--html", type=Path, action="append", help="Explicit HTML path; repeat as needed")
    parser.add_argument("--catalog", type=Path, help="Optional catalog; default materiales_actualizados/catalogo.json")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate loader and hashes without rewriting HTML")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    vendor = (args.vendor_dir or root / "vendor/mathjax").resolve()
    manifest = vendor_manifest(vendor)
    if args.html:
        paths = [(p if p.is_absolute() else root / p).resolve() for p in args.html]
    else:
        catalog_path = args.catalog or root / "materiales_actualizados/catalogo.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        paths = [(root / item["html"]).resolve() for item in catalog["materials"]]
    if len(paths) != len(set(paths)):
        raise ValueError("Duplicate HTML inputs")
    rows = []
    for path in paths:
        row = localize(path, vendor, args.check)
        try:
            row["html"] = path.relative_to(root).as_posix()
        except ValueError:
            row["html"] = path.name
        rows.append(row)
    report = {
        "mathjax_package": manifest["package"],
        "mathjax_version": VERSION,
        "htmls": len(rows),
        "tex_expressions": sum(row["tex_expressions"] for row in rows),
        "mode": "check" if args.check else "apply",
        "remote_mathjax_references": 0,
        "results": rows,
        "scope": "Sólo carga y configuración de fórmulas; no sustituye otros recursos externos de las clases.",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError) as error:
        print("ERROR:", str(error), file=sys.stderr)
        raise SystemExit(1)
