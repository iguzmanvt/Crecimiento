"""Genera el portal del curso desde sus catálogos, sin red ni cambios en las clases."""
from pathlib import Path
from urllib.parse import quote
import html, json, hashlib, sys
import os

def esc(value):
    return html.escape(str(value), quote=True)

def task_label(task_id):
    return "Tarea 5, variante temática" if task_id == "T5_variante" else "Tarea " + task_id[1:]

def generate_intro_index(repo):
    folder = repo / "introduccion_local"
    catalogs = [folder / name / "catalogo.json" for name in ("chartstudio", "owid")]
    if not all(path.is_file() for path in catalogs):
        return
    sections = []
    counts = []
    for path, label, context in zip(catalogs,
        ("Hechos del crecimiento", "Comparaciones internacionales"),
        ("Reconstrucciones por correspondencia temática con los materiales conservados. No se acredita identidad numérica o visual con los objetos Chart Studio originales.",
         "Adaptaciones de datos abiertos descargados el 12 de noviembre de 2026. La comparación de contaminación utiliza exposición a PM2.5, con unidades distintas de una tasa de mortalidad.")):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data["entries"]
        counts.append(len(entries))
        items = []
        for entry in entries:
            destination = repo / entry["html"] if entry.get("html") else path.parent / "graficas" / (entry["slug"] + ".html")
            relative = os.path.relpath(destination, folder).replace("\\", "/")
            source = entry.get("source_urls", [None])[0]
            source_link = (' · <a href="' + esc(source) + '">Fuente</a>') if source else ""
            period = entry.get("period", [])
            years = "–".join(str(y) for y in period) if isinstance(period, list) else str(period)
            items.append('<li><a href="' + esc(quote(relative, safe="/")) + '">' + esc(entry["title"]) + '</a> <small>' + esc(years) + '</small>' + source_link + '</li>')
        section_index = os.path.relpath(path.parent / "index.html", folder).replace("\\", "/")
        sections.append('<section><h2>' + esc(label) + '</h2><p>' + esc(context) + '</p><p><a href="' + esc(section_index) + '">Método, datos y límites de cada figura</a></p><ol>' + "".join(items) + '</ol></section>')
    page = '<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figuras de Introducción · Crecimiento Económico</title><style>body{font:17px/1.6 system-ui,sans-serif;color:#203448;max-width:1000px;margin:35px auto;padding:0 22px}a{color:#065ca5}h1,h2{line-height:1.2}section{margin:40px 0}li{margin:10px 0}small{color:#475b70}nav{margin-bottom:28px}</style></head><body><nav><a href="../portal/index.html">Materiales del curso</a></nav><main><h1>Figuras de Introducción</h1><p>Las ' + str(sum(counts)) + ' vistas se abren desde una copia completa del curso. Cada figura conserva datos, unidades, fuentes y su método. Los enlaces a las fuentes permiten consultar la edición original.</p>' + "".join(sections) + '</main></body></html>\n'
    (folder / "index.html").write_text(page, encoding="utf-8", newline="\n")
    manifest = {"source_catalogs": {p.relative_to(repo).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in catalogs}, "views": sum(counts), "files": {"index.html": hashlib.sha256((folder / "index.html").read_bytes()).hexdigest()}, "generator": "scripts/generar_portal.py"}
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

def generate(repo):
    generate_intro_index(repo)
    target = repo / "portal"
    target.mkdir(exist_ok=True)
    consultation_path = repo / "material_consulta/catalogo.json"
    materials_path = repo / "materiales_actualizados/catalogo.json"
    data = json.loads(consultation_path.read_text(encoding="utf-8"))
    materials = json.loads(materials_path.read_text(encoding="utf-8"))
    modules, assignments = data["modules"], data["assignments"]
    assert len(modules) == 16 and len(assignments) == 8
    by_module = {}
    for item in materials["materials"]:
        by_module.setdefault(item["module"], {})[item["kind"]] = item
    by_assignment = {x["id"]: x for x in assignments}
    targets = set()
    def link(path, text, classes=""):
        assert (repo / path.split("#")[0]).exists(), path
        targets.add(path)
        url = quote("../" + path, safe="/#?=&:")
        return '<a' + (' class="' + classes + '"' if classes else '') + ' href="' + esc(url) + '">' + esc(text) + "</a>"
    toc, sections = [], []
    for position, module in enumerate(modules, 1):
        slug, title = module["module"], module["title"]
        selected = by_module[slug]
        actions = [link(selected["presentacion"]["html"], "Abrir presentación", "action-primary"), link(selected["notas"]["html"], "Notas"), link("material_consulta/" + slug + ".html", "Lecturas y recursos")]
        readings = "<ul>" + "".join("<li>" + esc(t) + "</li>" for t in module["assigned_readings"]) + "</ul>"
        refs, related = module.get("assignment_refs", []), []
        for ref in refs:
            task = by_assignment[ref["task_id"]]
            related.append("<li>" + link("material_consulta/" + task["html"], task_label(ref["task_id"])) + ": " + esc(ref["sections"]) + ' <span class="relation">(' + esc(ref["relation"]) + ")</span></li>")
        exercise = '<div class="related"><h4>Ejercicios relacionados</h4><ul>' + "".join(related) + "</ul></div>" if related else '<p class="related-note">Consulta los enunciados disponibles en el <a href="#tareas">banco de tareas</a>.</p>'
        search = " ".join([title, slug] + module["assigned_readings"] + [x["sections"] + " " + task_label(x["task_id"]) for x in refs])
        task_ids = " ".join(x["task_id"] for x in refs)
        toc.append('<li data-topic-link="' + esc(slug) + '"><a href="#tema-' + esc(slug) + '"><span>' + str(position).zfill(2) + "</span> " + esc(title) + "</a></li>")
        sections.append('<article class="topic searchable" id="tema-' + esc(slug) + '" data-kind="tema" data-task-ids="' + esc(task_ids) + '" data-search="' + esc(search) + '"><div class="topic-heading"><span class="number" aria-hidden="true">' + str(position).zfill(2) + '</span><div><h3>' + esc(title) + '</h3><p class="locator">' + esc(module["program_locator"]) + '</p></div></div><div class="actions">' + "".join(actions) + '</div><details><summary>Lecturas del programa y ejercicios</summary><div class="details-content"><h4>Lecturas</h4>' + readings + exercise + "</div></details></article>")
    tasks = []
    for task in assignments:
        section_text = " · ".join(task["sections"])
        search = " ".join([task_label(task["id"]), task["title"], section_text])
        tasks.append('<li class="assignment searchable" data-kind="tarea" data-task-ids="' + esc(task["id"]) + '" data-search="' + esc(search) + '"><div><h3>' + link("material_consulta/" + task["html"], task_label(task["id"])) + '</h3><p>' + esc(task["title"]) + '</p><p class="assignment-sections">' + esc(section_text) + "</p></div></li>")
    resources = [
        link(data["program"]["repo_path"], "Programa del curso (PDF)"),
        link("material_consulta/index.html", "Índice de lecturas y recursos"),
        link("material_consulta/tareas/index.html", "Índice de tareas"),
        link("materiales_actualizados/Accounting/ejemplo/Material.html", "Ejemplo calculado de Estados Unidos"),
        link("graficas_reconstruidas/index.html", "Gráficas y datos"),
    ]
    for path, label in [
        ("introduccion_local/index.html", "Figuras de Introducción: índice completo"),
        ("introduccion_local/chartstudio/index.html", "Introducción: hechos del crecimiento"),
        ("introduccion_local/owid/index.html", "Introducción: comparaciones internacionales"),
        ("recursos_esenciales/index.html", "Energía, medio ambiente y trabajo: recursos locales"),
    ]:
        if (repo / path).is_file():
            resources.append(link(path, label))
    page = '<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Notas, presentaciones, lecturas y ejercicios del curso Crecimiento Económico."><title>Crecimiento Económico · Materiales del curso</title><link rel="stylesheet" href="portal.css"><script src="portal.js" defer></script></head><body>\n'
    page += '<a class="skip-link" href="#contenido">Saltar al contenido</a><header class="site-header"><a class="brand" href="#inicio">Crecimiento Económico</a><nav aria-label="Navegación principal"><a href="#temas">Temas</a><a href="#tareas">Tareas</a><a href="#recursos">Recursos</a></nav></header>'
    page += '<main id="contenido" tabindex="-1"><section class="intro" id="inicio"><p class="eyebrow">ECO-18300 · ITAM · Primavera 2023</p><h1>Materiales para estudiar<br class="wide-break"> crecimiento económico</h1><p class="intro-text">Accede a las presentaciones y notas del curso. Cada tema reúne sus lecturas del programa y los ejercicios relacionados.</p><div class="search" hidden id="search-control"><label for="course-search">Buscar tema, lectura o ejercicio</label><div class="search-row"><input type="search" id="course-search" placeholder="Por ejemplo: Solow, innovación o Tarea 2" autocomplete="off" aria-describedby="search-status"><button type="button" id="clear-search" hidden>Limpiar búsqueda</button></div><p id="search-status" role="status" aria-live="polite">16 temas y 8 enunciados disponibles.</p></div></section>'
    page += '<section class="course-layout" id="temas"><aside class="topic-navigation" aria-labelledby="topic-nav-title"><h2 id="topic-nav-title">Elegir tema</h2><ol>' + "".join(toc) + '</ol></aside><div class="topic-list"><div class="section-heading"><h2>Temas del curso</h2><p>Presentación, notas y consulta en cada tema.</p></div><p class="empty-state" id="no-topics" hidden>No hay temas que coincidan con la búsqueda.</p>' + "".join(sections) + "</div></section>"
    page += '<section class="assignments-section" id="tareas"><div class="section-heading"><h2>Tareas y ejercicios</h2><p>Siete enunciados del archivo del curso y una variante temática. Son materiales de consulta y no fijan una fecha de entrega vigente.</p></div><p class="empty-state" id="no-tasks" hidden>No hay tareas que coincidan con la búsqueda.</p><ul class="assignments">' + "".join(tasks) + "</ul></section>"
    page += '<section class="resources-section" id="recursos"><h2>Programa y recursos</h2><ul>' + "".join("<li>" + item + "</li>" for item in resources) + '</ul><p>Las lecturas conservan la edición indicada en el programa. Algunos textos completos requieren acceso a la fuente editorial o institucional.</p></section></main>'
    page += '<footer><p>Curso de Crecimiento Económico · Archivo docente de Primavera 2023</p><p><a href="https://github.com/iguzmanvt/Crecimiento">Código y fuentes en GitHub</a> <span aria-hidden="true">·</span> <a href="#inicio">Volver al inicio</a></p></footer></body></html>\n'
    (target / "index.html").write_text(page, encoding="utf-8", newline="\n")
    names = ["index.html", "portal.css", "portal.js"]
    manifest = {"topics": len(modules), "assignments": len(assignments), "source_catalogs": {p.relative_to(repo).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in (consultation_path, materials_path)}, "local_targets": sorted(targets), "files": {name: hashlib.sha256((target / name).read_bytes()).hexdigest() for name in names}, "generator": "scripts/generar_portal.py", "network_dependencies": []}
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (repo / "index.html").write_text('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url=portal/index.html"><title>Crecimiento Económico</title></head><body><p><a href="portal/index.html">Abrir los materiales de Crecimiento Económico</a></p></body></html>\n', encoding="utf-8", newline="\n")
    return manifest

if __name__ == "__main__":
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    result = generate(root)
    print(json.dumps({"topics": result["topics"], "assignments": result["assignments"], "local_targets": len(result["local_targets"]), "output": "portal/index.html"}))
