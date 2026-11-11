"""Extrae referencias y configuraciones archivadas; no ejecuta HTML ni usa red."""
import csv
import hashlib
import html
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
from urllib.parse import unquote_to_bytes, urlparse

COMMIT = "44f93109beda966ec5ea4717135897bf57fd5e97"
BLOBS = {
    "Crecimiento Economico 1.Rmd": "0483b5a5243d24817c337b6054409b52dc7f25d5",
    "Crecimiento Economico Intro.Rmd": "b0d57ba06347760a19425a04409d8b149a26d519",
    "Crecimiento Economico 1 Nota.Rmd": "2314147eba9fd0d94ea412cc0b849b11bc83583d",
    "Crecimiento-Economico-1-Nota.html": "e2e7a4c6818480c79e37539fc792160737bb482c",
}
URL = re.compile(r'''(?:https?:)?//(?:plotly\.com/~iguzmanvt/|ourworldindata\.org/grapher/)[^"'<>\s)]+''')

class Embeds(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "iframe" and attrs.get("src", "").startswith("data:text/html"):
            self.items.append((self.getpos()[0], attrs["src"]))

def references(text):
    result = []
    for match in URL.finditer(text):
        url = html.unescape(match[0])
        headings = re.findall(r"^\s{0,4}##\s+(.+)$", text[:match.start()], re.M)
        result.append({"url": url, "line": text.count("\n", 0, match.start()) + 1,
                       "context": headings[-1] if headings else ""})
    return result

def identity(url):
    if "plotly.com/~iguzmanvt/" in url:
        return "plotly:" + re.search(r"/([0-9]+)\.", url)[1]
    return url.replace("http://", "https://")

def main():
    folder = Path(__file__).resolve().parent
    intro = folder.parent
    sources, texts = {}, {}
    for name, expected in BLOBS.items():
        raw = (intro / name).read_bytes().replace(b"\r\n", b"\n")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if blob != expected:
            raise ValueError("Fuente modificada; revisar procedencia antes de regenerar: " + name)
        sources[name] = {"git_blob": blob, "sha256_lf": hashlib.sha256(raw).hexdigest()}
        texts[name] = raw.decode("utf-8")
    parsed = {name: references(texts[name]) for name in BLOBS if name.endswith(".Rmd")}
    main_refs = parsed["Crecimiento Economico Intro.Rmd"]
    note_refs = parsed["Crecimiento Economico 1 Nota.Rmd"]
    owid_note = [r for r in note_refs if "ourworldindata.org/grapher/" in r["url"]]
    parser = Embeds()
    parser.feed(texts["Crecimiento-Economico-1-Nota.html"])
    if len(parser.items) != 13 or len(owid_note) != 13 or len(main_refs) != 32:
        raise ValueError("Cambió el número de referencias archivadas.")
    configurations = []
    for index, ((line, uri), reference) in enumerate(zip(parser.items, owid_note), 1):
        payload = unquote_to_bytes(uri.split(",", 1)[1])
        document = payload.decode("utf-8")
        marker = re.search(r"const jsonConfig\s*=\s*//EMBEDDED_JSON\s*", document)
        if not marker:
            raise ValueError("Falta la configuración identificable de OWID.")
        config, _ = json.JSONDecoder().raw_decode(document[marker.end():])
        if set(config.get("data", {})) - {"availableEntities"}:
            raise ValueError("Estructura de datos distinta; inspeccionar antes de clasificarla como metadatos.")
        canonical = re.search(r'<link rel="canonical" href="([^"]+)"', document)
        configurations.append({"archive_index": index, "html_line": line,
            "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "association": "Orden de los 13 iframes de la nota Rmd y los 13 respaldos HTML; no prueba igualdad de ediciones estadísticas.",
            "note_reference": reference, "canonical_url_archived": html.unescape(canonical[1]),
            "numerical_observations_recovered": False, "configuration": config})
    config_by_url = {c["note_reference"]["url"]: c for c in configurations}
    records = []
    for order, reference in enumerate(main_refs, 1):
        url = reference["url"]
        chart_studio = "plotly.com" in url
        config = config_by_url.get(url)
        record = {"order": order, "provider": "Chart Studio" if chart_studio else "Our World in Data",
            "resource_id": re.search(r"/([0-9]+)\.embed", url)[1] if chart_studio else urlparse(url).path.rsplit("/", 1)[-1],
            "context": reference["context"], "source_url": url,
            "consultation_url": "https:" + url if url.startswith("//") else url,
            "status": "pendiente_datos_originales" if chart_studio else "configuracion_sin_observaciones" if config else "sin_configuracion_archivada",
            "configuration_archive_index": config["archive_index"] if config else None,
            "numerical_observations_recovered": False,
            "occurrences": [{"source": name, **r} for name, refs in parsed.items() for r in refs if identity(r["url"]) == identity(url)]}
        records.append(record)
    assert len({r["resource_id"] for r in records if r["provider"] == "Chart Studio"}) == 17
    assert sum(r["configuration_archive_index"] is not None for r in records) == 13
    catalog = {"source_commit": COMMIT, "sources": sources,
        "scope": "32 referencias de las presentaciones y 13 configuraciones de OWID archivadas. Cero series numéricas recuperadas.",
        "records": records, "archived_owid_configurations": configurations,
        "historical_note_differences": ["La nota repite la referencia 172 donde las dos presentaciones usan 176.", "La nota contiene 158.embe; las dos presentaciones usan 158.embed.", "Las presentaciones añaden dos referencias OWID sin página incrustada en la nota histórica."],
        "remote_evidence": "verificacion_remota_20261111.json"}
    csv_text = io.StringIO(newline="")
    columns = ["order", "provider", "resource_id", "context", "source_url", "status", "configuration_archive_index", "numerical_observations_recovered"]
    writer = csv.DictWriter(csv_text, columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    md = ["# Referencias externas de Introducción", "", "Corte documental: 11 de noviembre de 2026. Las 32 referencias siguen pendientes de recuperación numérica. Se conservan configuraciones archivadas de 13 recursos OWID; no contienen sus observaciones.", "", "| Orden | Proveedor e identificador | Contexto docente | Estado del respaldo |", "| ---: | --- | --- | --- |"]
    for r in records:
        label = (r["provider"] + " · " + r["resource_id"]).replace("|", "\\|")
        context = r["context"].replace("|", "\\|")
        state = "Configuración archivada; sin observaciones" if r["configuration_archive_index"] else "Datos originales pendientes" if r["provider"] == "Chart Studio" else "Sin configuración archivada"
        md.append(f'| {r["order"]} | [{label}]({r["consultation_url"]}) | {context} | {state} |')
    md += ["", "Las URL son referencias de consulta. Un enlace conservado no acredita disponibilidad o vigencia. Véanse la [procedencia y los siguientes pasos](README.md), el [catálogo completo con configuraciones](catalogo.json) y la [tabla CSV](referencias.csv).", ""]
    outputs = {"catalogo.json": json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", "referencias.csv": csv_text.getvalue(), "catalogo.md": "\n".join(md)}
    for name, content in outputs.items():
        (folder / name).write_bytes(content.encode("utf-8"))
    print("PASS: 32 referencias, 13 configuraciones OWID, cero series numéricas recuperadas; sin red.")

if __name__ == "__main__":
    main()
