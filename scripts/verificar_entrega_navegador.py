#!/usr/bin/env python3
"""Abre el curso con Chromium, bloquea internet y comprueba sus vistas locales.

Requiere Playwright 1.58.0 y Chromium, o --browser-executable con Chrome local.
No modifica los materiales. Los informes/screenhots sólo se escriben donde se
indique con --report/--screenshots. Comprueba disco y subruta HTTP /Crecimiento/.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.metadata
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading
from urllib.parse import quote, urlsplit

from playwright.sync_api import sync_playwright

from verificar_entrega import CATALOGS, catalog_entries


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        if self.path.startswith("/Crecimiento/"):
            self.path = self.path[len("/Crecimiento"):]
        else:
            self.send_error(404, "Only the /Crecimiento/ subpath is served")
            return
        super().do_GET()

    def do_HEAD(self):
        if self.path.startswith("/Crecimiento/"):
            self.path = self.path[len("/Crecimiento"):]
        else:
            self.send_error(404, "Only the /Crecimiento/ subpath is served")
            return
        super().do_HEAD()


IMAGES = """async () => {
 const imgs=[...document.images];
 await Promise.all(imgs.map(i=>i.complete?Promise.resolve():new Promise(r=>{i.addEventListener('load',r,{once:true});i.addEventListener('error',r,{once:true});})));
 return {count:imgs.length,broken:imgs.filter(i=>!i.complete||i.naturalWidth===0||i.naturalHeight===0).map(i=>i.getAttribute('src'))};
}"""
MATH = """async () => {
 if (window.MathJax && MathJax.startup) await MathJax.startup.promise;
 return {version:window.MathJax?.version||null,
   expressions:window.MathJax?.startup?[...MathJax.startup.document.math].length:0,
   svg:document.querySelectorAll('mjx-container[jax=SVG]').length,
   errors:document.querySelectorAll('[data-mjx-error],[data-mml-node=merror]').length,
   mathml:document.querySelectorAll('math').length};
}"""
SLIDES = """() => [...document.querySelectorAll('slides>slide')].map((s,i)=>({index:i,
  width:s.clientWidth,height:s.clientHeight,scrollHeight:s.scrollHeight,
  scrollWidth:s.scrollWidth,overflowY:getComputedStyle(s).overflowY,
  overflowX:getComputedStyle(s).overflowX}))"""
PLOT = """() => { const numeric=a=>Array.isArray(a)?a.reduce((n,x)=>n+numeric(x),0):ArrayBuffer.isView(a)?[...a].filter(x=>Number.isFinite(x)).length:typeof a==='number'&&Number.isFinite(a)?1:0;
 const present=x=>typeof x==='string'?x.trim().length>0:typeof x==='number'&&Number.isFinite(x);
 return [...document.querySelectorAll('.js-plotly-plot')].map(g=>({
 data:g.data?.length||0,layout:!!g._fullLayout,
 width:g.getBoundingClientRect().width,height:g.getBoundingClientRect().height,
 svg:g.querySelectorAll('.main-svg').length,
 numeric:(g._fullData||g.data)?.reduce((n,t)=>n+['x','y','z','values'].reduce((m,k)=>m+numeric(t[k]),0),0)||0,
 categorical_pairs:(g._fullData||g.data)?.reduce((n,t)=>n+(Array.isArray(t.x)&&Array.isArray(t.y)?t.x.filter((x,i)=>present(x)&&present(t.y[i])&&(typeof x==='string'||typeof t.y[i]==='string')).length:0),0)||0,
 categorical_marks:g.querySelectorAll('.scatterlayer .point,.barlayer .point').length,
 tables:(g._fullData||g.data)?.filter(t=>t.type==='table').map(t=>{const cs=t.cells?.values||[];const rows=Math.max(0,...cs.map(c=>c.length));return {columns:cs.length,rows,nonempty_rows:Array.from({length:rows},(_,i)=>cs.length&&cs.every(c=>present(c[i]))).filter(Boolean).length};})||[],
 rendered_table_cells:g.querySelectorAll('.cell-text').length
})); }"""

TABLE_FIT = """() => {
 const g=document.querySelector('.js-plotly-plot');
 const tables=(g?._fullData||[]).filter(t=>t.type==='table').map(t=>{
   const columns=t.cells?.values||[];
   const rows=Math.max(0,...columns.map(c=>c.length));
   const cellHeight=Array.isArray(t.cells.height)?Math.max(...t.cells.height):t.cells.height;
   const domain=t.domain?.y||[0,1];
   return {rows,columns:columns.length,required_px:t.header.height+rows*cellHeight,
     available_px:g._fullLayout._size.h*(domain[1]-domain[0])};
 });
 const cells=[...g.querySelectorAll('.cell-text')].map(x=>{const b=x.getBoundingClientRect();return {text:x.textContent,top:b.top,bottom:b.bottom,left:b.left,right:b.right};});
 return {width:innerWidth,height:innerHeight,tables,rendered_cells:cells.length,
   all_text_within_frame:cells.every(b=>b.top>=0&&b.bottom<=innerHeight+1&&b.left>=0&&b.right<=innerWidth+1),cells};
}"""


def table_fit(frame):
    """The Plotly table's clipping viewport must fit every declared row."""
    frame.wait_for_function("document.querySelector('.js-plotly-plot')?._fullLayout")
    metrics = frame.evaluate(TABLE_FIT)
    if not metrics["tables"] or not metrics["all_text_within_frame"] or any(t["required_px"] > t["available_px"] + 1 for t in metrics["tables"]):
        raise ValueError("Filas de tabla recortadas por el marco o su ventana SVG: " + json.dumps(metrics))
    return metrics


def inspect_material(page, row, expected_formulas):
    page.wait_for_function("window.MathJax && MathJax.startup && MathJax.startup.promise")
    maths = page.evaluate(MATH)
    if maths["errors"] or maths["svg"] != expected_formulas or maths["expressions"] != expected_formulas:
        raise ValueError("Fórmulas renderizadas difieren: " + row["html"] + " " + json.dumps(maths))
    if maths["version"] != "3.2.2":
        raise ValueError("Versión MathJax: " + row["html"])
    images = page.evaluate(IMAGES)
    if images["broken"]:
        raise ValueError("Imágenes fallidas: " + row["html"] + " " + str(images["broken"]))
    slides = page.evaluate(SLIDES)
    navigation = None
    if row["kind"] == "presentacion":
        page.wait_for_selector("slides>slide.current", state="attached")
        current = page.evaluate("[...document.querySelectorAll('slides>slide')].indexOf(document.querySelector('slides>slide.current'))")
        if len(slides) < 2:
            raise ValueError("Presentación sin secuencia: " + row["html"])
        page.keyboard.press("ArrowRight")
        page.wait_for_function("start=>[...document.querySelectorAll('slides>slide')].indexOf(document.querySelector('slides>slide.current'))===start+1", arg=current)
        page.keyboard.press("ArrowLeft")
        page.wait_for_function("start=>[...document.querySelectorAll('slides>slide')].indexOf(document.querySelector('slides>slide.current'))===start", arg=current)
        navigation = True
        clipped = [s for s in slides if s["scrollHeight"] > s["height"] + 2 and s["overflowY"] not in ("auto", "scroll", "visible")]
        if clipped:
            raise ValueError("Diapositivas con desbordamiento vertical inaccesible: " + row["html"] + " " + str(clipped))
    embedded_tables = []
    # Regression: the net-zero table has eight categorical rows. A 390px
    # frame clipped the last rows inside Plotly even though their SVG bounding
    # boxes existed. Validate its real table viewport as well as outer bounds.
    for iframe in page.locator("iframe[src*='metas_neto_cero.html']").all():
        slide_index = iframe.evaluate("el=>[...document.querySelectorAll('slides>slide')].indexOf(el.closest('slide'))")
        if slide_index >= 0:
            current = page.evaluate("[...document.querySelectorAll('slides>slide')].indexOf(document.querySelector('slides>slide.current'))")
            direction = 1 if slide_index > current else -1
            while current != slide_index:
                page.keyboard.press("ArrowRight" if direction > 0 else "ArrowLeft")
                current += direction
                page.wait_for_function("i=>[...document.querySelectorAll('slides>slide')].indexOf(document.querySelector('slides>slide.current'))===i", arg=current)
        iframe.scroll_into_view_if_needed()
        frame = iframe.element_handle().content_frame()
        frame.wait_for_function("document.documentElement.dataset.ready==='true'")
        embedded_tables.append({"src": iframe.get_attribute("src"), "frame_height": iframe.get_attribute("height"), "metrics": table_fit(frame)})
    frame_sources = page.locator("iframe[src]").evaluate_all("xs=>xs.map(x=>x.getAttribute('src'))")
    return {"images": images["count"], "math": maths, "slides": len(slides), "navigation": navigation, "scrollable_slides": sum(s["scrollHeight"] > s["height"] + 2 for s in slides), "iframe_sources": frame_sources, "embedded_tables": embedded_tables}


def inspect_graph(page):
    # A preserved historical image (for example FRED) is a valid published view.
    # All numerical reconstructions must initialize a nonempty Plotly object.
    if page.locator(".plot, #grafica, .js-plotly-plot").count():
        page.wait_for_function("[...document.querySelectorAll('.js-plotly-plot')].some(x=>x._fullLayout&&x.data?.length)")
    plots = page.evaluate(PLOT)
    def observations_drawn(plot):
        if plot["numeric"]:
            return True
        if plot["categorical_pairs"] and plot["categorical_marks"]:
            return True
        return bool(plot["rendered_table_cells"] and any(t["columns"] and t["nonempty_rows"] for t in plot["tables"]))
    if plots and any(not p["layout"] or not p["data"] or p["width"] < 50 or p["height"] < 50 or not observations_drawn(p) for p in plots):
        raise ValueError("Vista vacía o sin observaciones representadas: " + page.url + " " + str(plots))
    images = page.evaluate(IMAGES)
    if images["broken"] or (not plots and not images["count"]):
        raise ValueError("Vista sin figura: " + page.url + " " + str(images))
    selections = []
    for selector in page.locator("select").all():
        values = selector.locator("option").evaluate_all("xs=>xs.map(x=>x.value)")
        if len(values) > 1:
            selector.select_option(values[-1])
            # Some reconstructions separate selection from the Show action.
            show = page.locator("#mostrar")
            if show.count():
                show.click()
            page.wait_for_timeout(120)
            selector.select_option(values[0])
            if show.count():
                show.click()
            selections.append({"options": len(values), "first": values[0], "last": values[-1]})
    return {"plots": plots, "images": images["count"], "animation_selection": selections}


def inspect_portal(page, consultation):
    modules = consultation["modules"]
    tasks = consultation["assignments"]
    assert page.locator(".topic:visible").count() == len(modules)
    assert page.locator(".assignment:visible").count() == len(tasks)
    page.keyboard.press("Tab")
    assert page.evaluate("document.activeElement.className") == "skip-link"
    page.keyboard.press("Enter")
    assert page.evaluate("document.activeElement.id") == "contenido"
    search = page.locator("#course-search")
    search.fill("SOLÓW")
    assert page.locator("#tema-Solow").is_visible()
    search.fill("Tarea 2")
    expected = {m["module"] for m in modules if any(t["task_id"] == "T2" for t in m.get("assignment_refs", []))}
    found = set(page.locator(".topic:visible").evaluate_all("xs=>xs.map(x=>x.id.replace('tema-',''))"))
    assert expected == found, (expected, found)
    assert page.locator(".assignment:visible").evaluate_all("xs=>xs.map(x=>x.dataset.taskIds)") == ["T2"]
    search.fill("zxqsinresultados")
    assert page.locator(".topic:visible").count() == 0
    assert page.locator(".assignment:visible").count() == 0
    assert page.locator("#no-topics").is_visible() and page.locator("#no-tasks").is_visible()
    page.locator("#clear-search").click()
    assert page.locator(".topic:visible").count() == len(modules)
    assert page.evaluate("document.activeElement.id") == "course-search"
    page.locator("#tema-Solow summary").click()
    assert page.locator("#tema-Solow details").get_attribute("open") is not None
    dimensions = []
    for width in (1440, 900, 390):
        page.set_viewport_size({"width": width, "height": 1000})
        result = page.evaluate("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})")
        assert result["scrollWidth"] <= width + 1, result
        dimensions.append(result)
    return {"topics": len(modules), "assignments": len(tasks), "accent_search": True, "assignment_search": True, "empty_search": True, "keyboard_skip": True, "details": True, "widths": dimensions}


def run(args):
    root = args.root.resolve()
    import importlib.util
    spec = importlib.util.spec_from_file_location("course_math", root / "scripts/localizar_formulas.py")
    math_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(math_module)
    materials = json.loads((root / "materiales_actualizados/catalogo.json").read_text(encoding="utf-8"))["materials"]
    consultation = json.loads((root / "material_consulta/catalogo.json").read_text(encoding="utf-8"))
    graphs = []
    for relative in CATALOGS:
        catalog_path = root / relative
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        for entry in catalog_entries(data):
            path = root / entry["html"] if entry.get("html") else catalog_path.parent / "graficas" / (entry["slug"] + ".html")
            graphs.append(path)
    consultation_htmls = sorted((root / "material_consulta").rglob("*.html"))
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = "http://127.0.0.1:" + str(server.server_port) + "/Crecimiento/"
    results, failures = [], []
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
    executable = args.browser_executable
    if not executable and os.name == "nt":
        candidate = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if candidate.is_file():
            executable = str(candidate)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, **({"executable_path": executable} if executable else {}))
            browser_version = browser.version
            for mode in ("file", "subpath"):
                context = browser.new_context(viewport={"width": 1440, "height": 1080}, service_workers="block", accept_downloads=True)
                def local_only(route):
                    parts = urlsplit(route.request.url)
                    if parts.scheme in ("file", "data", "blob", "about") or (parts.scheme == "http" and parts.hostname == "127.0.0.1"):
                        route.continue_()
                    else:
                        route.abort()
                context.route("**/*", local_only)
                def inspect(path, category, detail=None):
                    relative = path.relative_to(root).as_posix()
                    url = path.as_uri() if mode == "file" else base + quote(relative, safe="/")
                    page = context.new_page()
                    errors, failed_requests, remote_requests = [], [], []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("requestfailed", lambda request: failed_requests.append(request.url))
                    page.on("response", lambda response: failed_requests.append(str(response.status) + " " + response.url) if response.status >= 400 else None)
                    page.on("request", lambda request: remote_requests.append(request.url) if urlsplit(request.url).scheme in ("http", "https") and urlsplit(request.url).hostname != "127.0.0.1" else None)
                    try:
                        page.goto(url, wait_until="load", timeout=60000)
                        if category == "material":
                            count = len(math_module.expressions(path.read_text(encoding="utf-8")))
                            measured = inspect_material(page, detail, count)
                        elif category == "graph":
                            measured = inspect_graph(page)
                        elif category == "portal":
                            measured = inspect_portal(page, consultation)
                        else:
                            measured = {"images": page.evaluate(IMAGES), "math": page.evaluate(MATH)}
                        if errors or failed_requests or remote_requests:
                            raise ValueError(json.dumps({"javascript": errors, "failed_requests": failed_requests, "remote_requests": remote_requests}))
                        results.append({"path": relative, "mode": mode, "category": category, "status": "passed", "metrics": measured, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
                        if args.screenshots and ((category == "portal") or (category == "graph" and len([r for r in results if r["category"] == "graph" and r["mode"] == mode]) == 1)):
                            page.screenshot(path=str(args.screenshots / (mode + "_" + category + ".png")), full_page=False)
                        print(mode, category, relative, "OK", flush=True)
                    except Exception as error:
                        failures.append({"path": relative, "mode": mode, "category": category, "error": str(error), "javascript": errors, "failed_requests": failed_requests, "remote_requests": remote_requests})
                        print(mode, category, relative, "FAILED", str(error)[:700], flush=True)
                    finally:
                        page.close()
                inspect(root / "portal/index.html", "portal")
                for row in materials:
                    inspect(root / row["html"], "material", row)
                for path in graphs:
                    inspect(path, "graph")
                # Native MathML consultation pages use the same files in both
                # modes; check every page once over the hosted subpath.
                if mode == "subpath":
                    for path in consultation_htmls:
                        inspect(path, "consultation")
                context.close()
            context = browser.new_context(java_script_enabled=False)
            page = context.new_page()
            page.goto((root / "portal/index.html").as_uri(), wait_until="load")
            assert page.locator(".topic:visible").count() == len(consultation["modules"])
            assert page.locator(".assignment:visible").count() == len(consultation["assignments"])
            assert page.locator("#search-control").is_hidden()
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    return {"status": "failed" if failures else "passed", "browser": browser_version, "playwright": importlib.metadata.version("playwright"), "modes": ["file", "HTTP /Crecimiento/"], "materials": len(materials), "graphs": len(graphs), "consultation_pages": len(consultation_htmls), "checks_passed": len(results), "portal_without_javascript": True, "scope": "Vistas actuales con red externa bloqueada: MathJax/SVG, imágenes, objetos Plotly, controles de selección disponibles, navegación de presentaciones y portal. No valida conclusiones docentes, fuentes externas opcionales ni identidad histórica.", "results": results, "failures": failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--browser-executable")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    try:
        report = run(args)
    except Exception as error:
        report = {"status": "failed", "failures": [{"error": str(error)}]}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("results", "failures")}, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
