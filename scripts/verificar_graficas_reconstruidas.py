"""Comprueba vistas, CSV, fotogramas y exportaciones de las reconstrucciones.

Uso: python scripts/verificar_graficas_reconstruidas.py CARPETA INFORME.json
     [--export-dir CARPETA_VACIA] [--browser RUTA_CHROME]
Requiere Playwright y un navegador instalado; no envía solicitudes externas.
"""
import argparse
import base64
import csv
import hashlib
import json
import math
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright


def equivalent(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isclose(a, b, rel_tol=1e-14, abs_tol=1e-14)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    return a == b


def subset(expected, actual):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and subset(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(expected) == len(actual) and all(subset(a, b) for a, b in zip(expected, actual))
    return equivalent(expected, actual)


def verify(root, report, export=None, executable=None, resume=False):
    root = root.resolve()
    catalog = json.loads((root/'catalogo.json').read_text(encoding='utf-8'))
    entries = catalog['entries']
    assert len(entries) == 40 and len({r['identity'] for r in entries}) == 40
    if export:
        export.mkdir(parents=True, exist_ok=True)
        if not resume:
            assert not any(export.iterdir()), 'La carpeta de exportación debe estar vacía.'
        else:
            expected = {r['slug']+'.'+ext for r in entries for ext in ['svg','png']}
            assert all(p.name in expected and p.is_file() for p in export.iterdir())

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(root)))
    Thread(target=server.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{server.server_port}'
    external = []
    records = json.loads(report.read_text(encoding='utf-8'))['results'] if resume and report.exists() else []
    seen = {r['slug']:r for r in records}
    try:
        with sync_playwright() as runtime:
            candidate = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
            kwargs = {'headless': True}
            if executable:
                kwargs['executable_path'] = executable
            elif candidate.exists():
                kwargs['executable_path'] = str(candidate)
            browser = runtime.chromium.launch(**kwargs)
            context = browser.new_context(viewport={'width': 1440, 'height': 1080}, service_workers='block')
            def route(request):
                if request.request.url.startswith(origin+'/'):
                    request.continue_()
                else:
                    external.append(request.request.url)
                    request.abort()
            context.route('**/*', route)
            page = context.new_page()
            page.goto(origin+'/index.html', wait_until='load')
            assert page.locator('tbody tr').count() == 40
            page.locator('#buscar').fill('China')
            assert 0 < page.locator('tbody tr:visible').count() < 40
            page.close()
            for item in entries:
                slug = item['slug']
                spec_path = root/'datos'/f'{slug}.json'
                assert hashlib.sha256(spec_path.read_bytes()).hexdigest() == item['spec_sha256']
                spec = json.loads(spec_path.read_text(encoding='utf-8'))
                if slug in seen:
                    assert seen[slug]['spec_sha256'] == item['spec_sha256']
                    assert all((root/'imagenes'/f'{slug}.{ext}').is_file() for ext in ['svg','png'])
                    continue
                expected_points = sum(len(t.get('x', [])) for t in spec['data'])
                with (root/'datos'/f'{slug}.csv').open(encoding='utf-8', newline='') as file:
                    csv_rows = list(csv.DictReader(file))
                assert len(csv_rows) == expected_points
                for row in csv_rows:
                    trace, index = spec['data'][int(row['traza'])], int(row['observacion'])
                    assert equivalent(json.loads(row['x']), trace['x'][index])
                    assert equivalent(json.loads(row['y']), trace['y'][index])
                page = context.new_page()
                errors, missing = [], []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('response', lambda response: missing.append(response.url) if response.status >= 400 else None)
                page.goto(origin+'/graficas/'+slug+'.html', wait_until='load')
                page.wait_for_function('window.graficaLista === true')
                observed = page.locator('#grafica').evaluate('(p)=>p.data.map(t=>({x:Array.from(t.x||[]),y:Array.from(t.y||[])}))')
                assert len(observed) == len(spec['data'])
                for a, b in zip(observed, spec['data']):
                    assert equivalent(a['x'], b.get('x', [])) and equivalent(a['y'], b.get('y', [])), slug
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+2'), slug
                if export:
                    for ext in ['svg', 'png']:
                        url = page.evaluate('(f)=>window.exportarGrafica(f)', ext)
                        prefix, raw = url.split(',', 1)
                        if ';base64' in prefix:
                            data = base64.b64decode(raw)
                        else:
                            from urllib.parse import unquote
                            data = unquote(raw).encode('utf-8')
                        assert len(data) > 1000, (slug, ext)
                        (export/f'{slug}.{ext}').write_bytes(data)
                for link in page.locator('a[download]').evaluate_all('(aa)=>aa.map(a=>a.getAttribute("href"))'):
                    assert (root/'graficas'/link).resolve().is_file(), (slug, 'missing download', link)
                frames = spec.get('frames') or []
                if frames:
                    assert page.locator('#grafica').evaluate('(p)=>p._transitionData._frames.length') == len(frames)
                    page.locator('#reproducir').click()
                    page.wait_for_function('window.reproduciendo === true')
                    page.locator('#pausar').click()
                    page.wait_for_function('window.reproduciendo === false')
                    last = frames[-1]
                    name = str(last.get('name', len(frames)-1))
                    page.select_option('#fotograma', value=name)
                    page.locator('#mostrar').click()
                    page.wait_for_function('(n)=>window.ultimoFotograma===n', arg=name)
                    changed = page.locator('#grafica').evaluate('(p)=>p.data.map(t=>({x:Array.from(t.x||[]),y:Array.from(t.y||[])}))')
                    patches = last.get('data', [])
                    for index, patch in zip(last.get('traces', range(len(patches))), patches):
                        for axis in ['x', 'y']:
                            if axis in patch:
                                assert equivalent(changed[index][axis], patch[axis]), (slug, axis)
                    if last.get('layout'):
                        changed_layout = page.locator('#grafica').evaluate('(p)=>p.layout')
                        assert subset(last['layout'], changed_layout), (slug, 'last frame layout')
                page.close()
                embed = context.new_page()
                embed.set_viewport_size({'width': 960, 'height': 440})
                embed.goto(origin+'/graficas/'+slug+'.html?embed=1', wait_until='load')
                embed.wait_for_function('window.graficaLista === true')
                assert embed.locator('body').get_attribute('class') == 'embed'
                assert embed.locator('.full-only:visible').count() == 0
                assert embed.evaluate('document.documentElement.scrollWidth <= innerWidth+2'), slug
                awaitables = embed.locator('#grafica').evaluate('(p)=>({w:p.clientWidth,h:p.clientHeight})')
                assert awaitables['w'] >= 950 and 280 <= awaitables['h'] <= 440, slug
                embed.set_viewport_size({'width': 720, 'height': 500})
                embed.wait_for_function('document.documentElement.scrollWidth <= innerWidth+2')
                embed.close()
                assert not errors and not missing, (slug, errors, missing)
                records.append({'identity': item['identity'], 'slug': slug, 'spec_sha256': item['spec_sha256'], 'traces': len(spec['data']), 'points_initial': expected_points, 'xy_matches_spec': True, 'CSV_matches_spec': True, 'downloads_present': True, 'frames': len(frames), 'last_frame_checked': bool(frames), 'play_pause_checked': bool(frames), 'embedded_view_checked': True, 'narrow_720_checked': True, 'javascript_errors': errors, 'missing_assets': missing})
                report.parent.mkdir(parents=True, exist_ok=True)
                report.write_text(json.dumps({'count': len(records), 'results': records, 'external_requests_attempted': external, 'browser': browser.version, 'exports': bool(export)}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
                print('VERIFIED', item['identity'], len(spec['data']), len(frames), flush=True)
            # Abrir directamente desde disco comprueba el uso previsto sin servidor.
            offline = browser.new_context()
            file_external = []
            def file_route(request):
                if request.request.url.startswith('file:'):
                    request.continue_()
                else:
                    file_external.append(request.request.url)
                    request.abort()
            offline.route('**/*', file_route)
            page = offline.new_page()
            page.goto((root/'graficas'/f'{entries[0]["slug"]}.html').as_uri(), wait_until='load')
            page.wait_for_function('window.graficaLista === true')
            assert not file_external
            offline.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    assert len(records) == 40 and not external
    assert len(list((root/'imagenes').glob('*.svg'))) == 40
    assert len(list((root/'imagenes').glob('*.png'))) == 40
    result = json.loads(report.read_text(encoding='utf-8'))
    result['file_protocol_checked'] = True
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'graficas': 40, 'external_requests_attempted': 0, 'file_protocol_checked': True}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('carpeta', type=Path)
    parser.add_argument('informe', type=Path)
    parser.add_argument('--export-dir', type=Path)
    parser.add_argument('--browser')
    parser.add_argument('--resume', action='store_true', help='Continuar sólo casos no comprobados, verificando las huellas de los casos anteriores.')
    args = parser.parse_args()
    verify(args.carpeta, args.informe, args.export_dir, args.browser, args.resume)
