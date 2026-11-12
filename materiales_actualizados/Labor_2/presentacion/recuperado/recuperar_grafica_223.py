"""Recupera la serie archivada y genera una vista SVG/HTML sin red ni dependencias.

Ejecutar con Python 3 desde cualquier directorio. No ejecuta el HTML archivado.
"""
import csv
import hashlib
import html
import io
import json
import math
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote_to_bytes

SOURCE_NAME = "Crecimiento-Economico---Mercado-Laboral-2-Nota.html"
# Huella del archivo histórico, con saltos LF como en Git.
SOURCE_SHA256 = "774bba6dd74789ec022b3cb3e888d29074e18910360b8bc10f4c1628c3367638"
SOURCE_COMMIT = "d8216e86cbf822a798ec72ac6433a26c20c8cfca"
SOURCE_BLOB = "d35266c14a35b05f3a76a9d7e9a317fa910c0cdb"
DATA_SHA256 = "aebfe2a0cbd4f85e21a7a44ef714954999b379a199df6ba3ff5936fec4fc8cfc"
LAYOUT_SHA256 = "854bf49545a13a9ff3579b4194cbcf21b7ac872c10d24b0b7ae946abaecca23f"


class ArchiveParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.embeds = []
        self.scripts = {}
        self.script_id = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("img", "iframe") and attrs.get("src", "").startswith("data:text/html"):
            self.embeds.append(attrs["src"])
        if tag == "script":
            self.script_id = attrs.get("id")
            if self.script_id:
                self.scripts[self.script_id] = ""

    def handle_data(self, data):
        if self.script_id:
            self.scripts[self.script_id] += data

    def handle_endtag(self, tag):
        if tag == "script":
            self.script_id = None


def digest(value):
    return hashlib.sha256(value).hexdigest()


def extract(source):
    # Git puede convertir LF a CRLF al hacer checkout en Windows.
    raw = source.read_bytes().replace(b"\r\n", b"\n")
    if digest(raw) != SOURCE_SHA256:
        raise ValueError("La fuente difiere del archivo histórico verificado.")
    document = ArchiveParser()
    document.feed(raw.decode("utf-8"))
    candidates = []
    for uri in document.embeds:
        prefix, encoded = uri.split(",", 1)
        if ";base64" in prefix:
            raise ValueError("Formato de respaldo inesperado.")
        embed = ArchiveParser()
        embed.feed(unquote_to_bytes(encoded).decode("utf-8"))
        if embed.scripts.get("plot-fid", "").strip() == "iguzmanvt:223":
            candidates.append(embed.scripts)
    if len(candidates) != 1:
        raise ValueError("Debe existir un único respaldo de iguzmanvt:223.")
    scripts = candidates[0]
    for key, expected in [("plot-data", DATA_SHA256), ("plot-layout", LAYOUT_SHA256)]:
        if digest(scripts[key].encode("utf-8")) != expected:
            raise ValueError("El contenido de " + key + " cambió.")
    data, layout = json.loads(scripts["plot-data"]), json.loads(scripts["plot-layout"])
    if len(data) != 1 or data[0]["x"] != list(range(1950, 2008)):
        raise ValueError("La cobertura histórica no coincide.")
    if len(data[0]["y"]) != 58 or not all(math.isfinite(y) for y in data[0]["y"]):
        raise ValueError("Serie incompleta o no finita.")
    if layout["yaxis"]["range"] != [0, 0.02]:
        raise ValueError("El intervalo vertical cambió.")
    return {
        "provenance": {
            "repository": "iguzmanvt/Crecimiento", "commit": SOURCE_COMMIT,
            "path": "Clases_Crecimiento_Economico/Labor_2/" + SOURCE_NAME,
            "git_blob": SOURCE_BLOB, "source_sha256_lf": SOURCE_SHA256,
            "plot_data_sha256": DATA_SHA256, "plot_layout_sha256": LAYOUT_SHA256,
            "plot_fid": "iguzmanvt:223",
            "coverage": "1950-2007", "observations": 58,
            "status": "Recuperación del respaldo docente histórico, sin actualización estadística.",
            "unverified_metadata": ["proveedor y edición estadística", "definición de población", "fórmula de la tasa a 10 años", "anualización", "dirección temporal del intervalo"],
        },
        "data": data, "layout": layout, "frames": json.loads(scripts["plot-frames"]),
    }


def svg_view(payload):
    trace, layout = payload["data"][0], payload["layout"]
    x, y = trace["x"], trace["y"]
    x0, x1 = layout["xaxis"]["range"]
    y0, y1 = layout["yaxis"]["range"]
    px = lambda v: 90 + (v - x0) / (x1 - x0) * 825
    py = lambda v: 370 - (v - y0) / (y1 - y0) * 310
    esc = html.escape
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 440" role="img" aria-labelledby="title desc">',
        '<title id="title">' + esc(layout["title"]["text"]) + '</title>',
        '<desc id="desc">United States of America. 58 observaciones de 1950 a 2007. Valores decimales originales recuperados. Rango vertical de 0 a 0.02.</desc>',
        '<rect width="960" height="440" fill="white"/>',
        '<g font-family="Arial, sans-serif" fill="#243447">',
        '<text x="90" y="29" font-size="23">' + esc(layout["title"]["text"]) + '</text>',
    ]
    for tick in (0, 0.005, 0.01, 0.015, 0.02):
        p = py(tick)
        parts.append(f'<line x1="90" x2="915" y1="{p:.6f}" y2="{p:.6f}" stroke="#e0e5eb"/>')
        parts.append(f'<text x="74" y="{p + 5:.6f}" font-size="14" text-anchor="end">{tick:g}</text>')
    for tick in range(1950, 2020, 10):
        p = px(tick)
        parts.append(f'<text x="{p:.6f}" y="395" font-size="14" text-anchor="middle">{tick:g}</text>')
    parts += [
        '<text x="500" y="426" text-anchor="middle" font-size="16">' + esc(layout["xaxis"]["title"]["text"]) + '</text>',
        '<text x="24" y="220" text-anchor="middle" font-size="16" transform="rotate(-90 24 220)">' + esc(layout["yaxis"]["title"]["text"]) + '</text>',
    ]
    coords = " ".join(f"{px(a):.6f},{py(b):.6f}" for a, b in zip(x, y))
    parts.append(f'<polyline id="serie-usa" points="{coords}" stroke="#c092a8" stroke-width="2" fill="none"/>')
    for year, value in zip(x, y):
        parts.append(f'<circle class="observation" cx="{px(year):.6f}" cy="{py(value):.6f}" r="3" fill="#c092a8" data-year="{year}" data-value="{value}"><title>{year} · {value}</title></circle>')
    return "\n".join(parts + ["</g>", "</svg>"]) + "\n"


def main():
    folder = Path(__file__).resolve().parent
    payload = extract(folder.parent / SOURCE_NAME)
    csv_text = io.StringIO(newline="")
    writer = csv.writer(csv_text, lineterminator="\n")
    writer.writerow(["year", "population_growth_original"])
    writer.writerows(zip(payload["data"][0]["x"], payload["data"][0]["y"]))
    svg = svg_view(payload)
    rows = "\n".join(f"<tr><td>{year}</td><td>{value}</td></tr>" for year, value in zip(payload["data"][0]["x"], payload["data"][0]["y"]))
    document = '''<!doctype html>
<html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mercado Laboral 2 · Gráfica 223 recuperada</title>
<style>body{font:17px/1.6 system-ui,sans-serif;color:#243447;max-width:1080px;margin:40px auto;padding:0 24px}h1{font-size:26px}svg{width:100%;height:auto}a{color:#145b8c}table{border-collapse:collapse;margin:16px 0}td,th{padding:5px 20px;border-bottom:1px solid #dce2e8;text-align:right}summary{cursor:pointer}p{max-width:85ch}.meta{color:#485b6b;font-size:15px}</style>
<h1>Mercado Laboral 2 · Gráfica 223 recuperada</h1>
<p>Vista local del respaldo docente de <strong>iguzmanvt:223</strong>. Conserva los 58 valores de 1950–2007, las etiquetas, la serie de Estados Unidos y los intervalos originales de ambos ejes. El dibujo SVG se reconstruyó para abrirlo sin conexión.</p>
''' + svg + '''<p class="meta">El respaldo no documenta el proveedor o edición de la serie ni la fórmula, anualización o dirección temporal de la «tasa de crecimiento a 10 años». Se conservan los valores decimales archivados, sin convertirlos a porcentajes ni redondearlos.</p>
<p><a href="grafica_223.csv">Datos CSV</a> · <a href="grafica_223.json">Datos y diseño originales JSON</a> · <a href="grafica_223.svg">Gráfica SVG</a> · <a href="README.md">Procedencia y reproducción</a></p>
<details><summary>Consultar las 58 observaciones</summary><table><thead><tr><th scope="col">Año</th><th scope="col">Tasa de crecimiento a 10 años · valor original</th></tr></thead><tbody>''' + rows + '''</tbody></table></details>
</html>
'''
    outputs = {"grafica_223.json": json.dumps(payload, ensure_ascii=False, indent=2) + "\n", "grafica_223.csv": csv_text.getvalue(), "grafica_223.svg": svg, "grafica_223.html": document}
    for name, content in outputs.items():
        (folder / name).write_bytes(content.encode("utf-8"))
    print("PASS: respaldo 223, 58 pares exactos, JSON/CSV/SVG/HTML regenerados sin red.")


if __name__ == "__main__":
    main()
