"""Construye las vistas locales de las 40 reconstrucciones docentes.

Uso: python scripts/generar_graficas_reconstruidas.py FUENTE SALIDA_VACIA
Los cálculos se repiten con los generadores de FUENTE/fuentes/*/generar.py.
La construcción de las vistas no consulta servicios externos.
"""
import argparse
import csv
import hashlib
import html
import json
import shutil
from pathlib import Path

CSS = '''*{box-sizing:border-box}body{margin:0;background:white;color:#243746;font:16px/1.5 Arial,Helvetica,sans-serif}main{max-width:1240px;margin:auto;padding:24px}h1{font-size:30px;line-height:1.25;font-weight:500}a{color:#075da8}nav{margin-bottom:18px}.note{border-left:3px solid #2375ae;background:#f1f6fa;padding:10px 16px}.plot{height:650px;width:100%;min-width:0}details{margin:16px 0}summary{cursor:pointer;font-weight:600}pre{white-space:pre-wrap;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left;vertical-align:top}input,select,button{font:inherit;padding:6px;margin:4px 8px 4px 0}small{font-size:13px}.scroll{overflow-x:auto}.embed-only{display:none}body.embed main{padding:0;max-width:none}body.embed .full-only{display:none}body.embed .embed-only{display:block;margin:0;padding:0 10px;font-size:11px;color:#52616b;height:24px}body.embed .plot{height:calc(100vh - 24px);min-height:285px}body.embed .animation{height:30px;display:flex;align-items:center;justify-content:flex-end;gap:4px;font-size:12px;padding:0 8px}body.embed .animation+.plot{height:calc(100vh - 54px)}body.embed .animation select,body.embed .animation button{font-size:12px;padding:2px;margin:0 3px}@media(max-width:700px){main{padding:15px}h1{font-size:24px}.plot{height:580px}td,th{padding:8px}}'''
JS = '''const spec=JSON.parse(document.getElementById('spec').textContent);const plot=document.getElementById('grafica');const embed=new URLSearchParams(location.search).get('embed')==='1';if(embed)document.body.classList.add('embed');
const layout=JSON.parse(JSON.stringify(spec.layout));delete layout.width;delete layout.height;layout.autosize=true;layout.font=Object.assign({family:'Arial, Helvetica, sans-serif',size:15,color:'#243746'},layout.font||{});layout.paper_bgcolor='#ffffff';layout.plot_bgcolor='#ffffff';
layout.margin=Object.assign({l:85,r:35,t:75,b:95},layout.margin||{});for(const k of Object.keys(layout)){if(/^xaxis\\d*$|^yaxis\\d*$/.test(k)&&typeof layout[k]==='object'){layout[k].automargin=true;}}
delete layout.updatemenus;delete layout.sliders;const footerAnnotations=(layout.annotations||[]).filter(a=>a.yref==='paper'&&a.y<0);const bottomLegend=layout.legend&&layout.legend.y<0;let footerOffset=bottomLegend?110:65;for(const a of footerAnnotations){a.y=0;a.yshift=-footerOffset;a.yanchor='top';const lines=String(a.text||'').split(/<br\\s*\\/?\\s*>|\\n/).length;footerOffset+=lines*15+6;}layout.margin.b=Math.max(layout.margin.b||0,110,footerAnnotations.length?footerOffset+20:0);const plotHeight=Math.max(100,plot.clientHeight-layout.margin.t-layout.margin.b);if(layout.legend){if(layout.legend.y>1){layout.legend.y=1.01;layout.legend.yanchor='bottom';}else if(layout.legend.y<0){layout.legend.y=-70/plotHeight;layout.legend.yanchor='top';}}for(const a of layout.annotations||[]){if(a.xref==='paper'&&a.x===0&&!a.xanchor)a.xanchor='left';}
const config={responsive:true,displaylogo:false,showSendToCloud:false,modeBarButtonsToRemove:['sendDataToCloud','editInChartStudio'],toImageButtonOptions:{format:'svg',filename:document.body.dataset.slug,width:1200,height:700}};
window.graficaLista=false;window.exportarGrafica=async(format)=>Plotly.toImage(plot,{format:format,width:1200,height:700});
Plotly.newPlot(plot,spec.data,layout,config).then(async()=>{const frames=spec.frames||[];if(frames.length){await Plotly.addFrames(plot,frames);const selector=document.getElementById('fotograma');frames.forEach((f,i)=>{const option=document.createElement('option');option.value=String(f.name===undefined?i:f.name);option.textContent=String(f.name===undefined?i:f.name);selector.appendChild(option);});document.getElementById('mostrar').onclick=async()=>{const name=selector.value;await Plotly.animate(plot,[name],{frame:{duration:0,redraw:true},transition:{duration:0},mode:'immediate'});window.ultimoFotograma=name;};document.getElementById('reproducir').onclick=()=>{window.reproduciendo=true;Plotly.animate(plot,frames.map(f=>String(f.name)),{frame:{duration:80,redraw:true},transition:{duration:0},mode:'immediate'}).then(()=>window.reproduciendo=false).catch(()=>window.reproduciendo=false);};document.getElementById('pausar').onclick=()=>{window.reproduciendo=false;Plotly.animate(plot,[null],{frame:{duration:0,redraw:false},transition:{duration:0},mode:'immediate'});};}window.graficaLista=true;}).catch(error=>{window.errorGrafica=String(error);document.getElementById('estado').textContent='No se pudo dibujar: '+error.message;});
'''


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value or '')


def period_text(value):
    if isinstance(value, list) and len(value) == 2:
        return str(value[0])+'–'+str(value[1])
    if isinstance(value, dict):
        if value.get('label'):
            return str(value['label'])
        start = value.get('start', value.get('first_year'))
        end = value.get('end', value.get('last_year'))
        if start is not None and end is not None:
            frequency = {'annual': 'anual', 'yearly': 'anual'}.get(value.get('frequency'), value.get('frequency', ''))
            return str(start)+'–'+str(end)+(('; '+frequency) if frequency else '')
    return normalize(value)


def module_text(value):
    names = {'Accounting':'Contabilidad del crecimiento', 'Solow':'Solow', 'Ideas':'Ideas e I+D', 'Energy':'Energía', 'Slowdown':'Desaceleración', 'Taxes':'Política fiscal'}
    if isinstance(value, list):
        return ' / '.join(names.get(v, v) for v in value)
    return names.get(value, normalize(value))


def kind_text(value):
    lower = str(value).lower()
    if 'simul' in lower or 'model' in lower:
        return 'Modelo o simulación'
    if 'adapt' in lower or 'archiv' in lower:
        return 'Adaptación de datos conservados'
    return 'Cálculo con datos publicados'


def csv_export(path, spec):
    with path.open('w', encoding='utf-8', newline='') as file:
        out = csv.writer(file, lineterminator='\n')
        out.writerow(['traza', 'serie', 'observacion', 'x', 'y', 'texto', 'datos_adicionales'])
        for ti, trace in enumerate(spec['data']):
            xs, ys = trace.get('x', []), trace.get('y', [])
            if len(xs) != len(ys):
                raise ValueError('Arrays x/y incompatibles: '+str(ti))
            texts = trace.get('text', [])
            extra = trace.get('customdata', [])
            for i, (x, y) in enumerate(zip(xs, ys)):
                text = texts[i] if isinstance(texts, list) and i < len(texts) else texts if isinstance(texts, str) else ''
                custom = extra[i] if isinstance(extra, list) and i < len(extra) else ''
                out.writerow([ti, trace.get('name', ''), i, dump(x), dump(y), normalize(text), normalize(custom)])


def generate(source, destination):
    source, destination = source.resolve(), destination.resolve()
    if source == destination or source in destination.parents:
        raise ValueError('La salida debe estar fuera de la fuente.')
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('La salida debe estar vacía.')
    manifest = json.loads((source/'catalogo.json').read_text(encoding='utf-8'))
    entries = manifest['entries']
    if len(entries) != 40 or len({row['identity'] for row in entries}) != 40:
        raise ValueError('Se requieren 40 identidades distintas.')
    for name in ['datos', 'graficas', 'imagenes', 'assets']:
        (destination/name).mkdir()
    for folder in ['fuentes', 'licencias']:
        shutil.copytree(source/folder, destination/folder)
    shutil.copyfile(source/'assets/plotly.min.js', destination/'assets/plotly.min.js')
    write(destination/'assets/clase.css', CSS+'\n')
    write(destination/'assets/clase.js', JS+'\n')
    shutil.copyfile(source/'catalogo.json', destination/'catalogo.json')
    records = []
    for item in entries:
        slug = item['slug']
        if not slug.replace('-', '').isalnum():
            raise ValueError('Slug no válido.')
        data = source/'datos'/f'{slug}.json'
        if sha(data) != item['spec_sha256']:
            raise ValueError('Cambió la especificación: '+slug)
        raw = data.read_text(encoding='utf-8')
        spec = json.loads(raw)
        assert spec['data'] and isinstance(spec['layout'], dict)
        shutil.copyfile(data, destination/'datos'/data.name)
        csv_export(destination/'datos'/f'{slug}.csv', spec)
        for ext in ['svg', 'png']:
            image = source/'imagenes'/f'{slug}.{ext}'
            if image.exists():
                shutil.copyfile(image, destination/'imagenes'/image.name)
        title = html.escape(item['title'])
        description = html.escape(normalize(item.get('description')))
        formula = html.escape(normalize(item.get('formula')))
        limits = html.escape('; '.join(str(v) for v in item['limitations']) if isinstance(item.get('limitations'), list) else normalize(item.get('limitations')))
        sources = ' · '.join('<a href="'+html.escape(url, quote=True)+'">Fuente '+str(i+1)+'</a>' for i, url in enumerate(item.get('source_urls', [])))
        frames = spec.get('frames') or []
        animation = '<div class="animation"><button type="button" id="reproducir">Reproducir</button><button type="button" id="pausar">Pausar</button><label for="fotograma">Fotograma: </label><select id="fotograma"></select><button type="button" id="mostrar">Mostrar</button></div>' if frames else ''
        embedded = raw.replace('</', '<\\/')
        page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><link rel="stylesheet" href="../assets/clase.css"></head><body data-slug="{slug}"><main><div class="full-only"><nav><a href="../index.html">← Gráficas de Crecimiento</a></nav><h1>{title}</h1><p class="note">Reconstrucción docente. {description}</p><p><strong>Periodo:</strong> {html.escape(period_text(item.get('period')))}. <strong>Unidades:</strong> {html.escape(normalize(item.get('units')))}.</p><p><strong>Edición:</strong> {html.escape(normalize(item.get('source_vintage')))}.</p></div>{animation}<div id="grafica" class="plot" role="img" aria-label="{title}"></div><p class="embed-only">Reconstrucción docente · datos y fuentes en la vista completa.</p><div class="full-only"><p id="estado">Puede consultar valores, ampliar el gráfico y ocultar series desde la leyenda.</p><p><a href="../datos/{slug}.csv" download>Datos CSV</a> · <a href="../datos/{slug}.json" download>Datos y animación JSON</a> · <a href="../imagenes/{slug}.svg" download>Imagen SVG</a> · <a href="../imagenes/{slug}.png" download>Imagen PNG</a></p><p><strong>Método:</strong> {formula}</p><p><strong>Alcance:</strong> {limits}</p><p>{sources}</p><details><summary>Procedencia, edición y reproducción</summary><pre>{html.escape(json.dumps(item, ensure_ascii=False, indent=2))}</pre></details></div><script type="application/json" id="spec">{embedded}</script><script src="../assets/plotly.min.js"></script><script src="../assets/clase.js"></script></main></body></html>\n'''
        write(destination/'graficas'/f'{slug}.html', page)
        records.append({'identity': item['identity'], 'slug': slug, 'traces': len(spec['data']), 'frames': len(frames), 'points_initial': sum(len(t.get('x', [])) for t in spec['data']), 'spec_sha256': sha(data), 'csv_sha256': sha(destination/'datos'/f'{slug}.csv')})
    rows = '\n'.join(f'<tr><td>{html.escape(module_text(r.get("module")))}</td><td><a href="graficas/{r["slug"]}.html">{html.escape(r["title"])}</a></td><td>{html.escape(period_text(r.get("period")))}</td><td>{html.escape(kind_text(r.get("kind")))}</td></tr>' for r in entries)
    index = f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gráficas reconstruidas de Crecimiento</title><link rel="stylesheet" href="assets/clase.css"><main><h1>Gráficas de Crecimiento Económico</h1><p class="note">40 reconstrucciones para los seis módulos afectados por el cierre de Chart Studio. Se emplean datos publicados, archivos conservados y modelos explícitos. Las reconstrucciones siguen los temas y el estilo de la clase; no se atribuye identidad visual o numérica con los archivos desaparecidos.</p><p>Las gráficas funcionan sin conexión. Abra cada vista para consultar datos, fuentes, fórmulas y límites. Las simulaciones están identificadas como modelos y las proyecciones, cuando existen, separadas de las observaciones.</p><p><a href="README.md">Guía y reproducción</a> · <a href="catalogo.json">Catálogo de fuentes</a></p><label for="buscar">Buscar:</label><input type="search" id="buscar" placeholder="Solow, China, energía…"><div class="scroll"><table><thead><tr><th>Módulo</th><th>Gráfica</th><th>Periodo</th><th>Elaboración</th></tr></thead><tbody>{rows}</tbody></table></div><script>document.getElementById('buscar').addEventListener('input',e=>{{const q=e.target.value.toLocaleLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase().includes(q));}});</script></main></html>\n'''
    write(destination/'index.html', index)
    write(destination/'README.md', '''# Gráficas reconstruidas de Crecimiento

40 gráficas locales integradas en las fuentes Rmd de seis módulos. Abrir `index.html` conservando esta carpeta completa. GitHub muestra el código HTML: descargar o clonar para interactuar. Las vistas, las animaciones y las descargas funcionan sin conexión; los enlaces de procedencia abren fuentes externas.

Cada gráfica incluye CSV, especificación JSON completa, SVG, PNG y método de elaboración. El CSV describe la vista inicial; el JSON conserva todos los fotogramas. Las imágenes representan la vista inicial. El historial conserva las referencias originales de Chart Studio; los identificadores aquí organizan las sustituciones y no autentican los objetos desaparecidos.

Las fórmulas y los insumos archivados están en `fuentes/`. Ejecutar cada `generar.py` con una salida vacía para repetir el cálculo del grupo. El catálogo fija las huellas de las especificaciones integradas. Para reconstruir las vistas desde esta carpeta, ejecutar desde la raíz del repositorio:

```sh
python scripts/generar_graficas_reconstruidas.py graficas_reconstruidas /ruta/externa/vacia
```

Para repetir los cálculos sin red, con Python 3.10 o posterior y sólo su biblioteca estándar:

```sh
python graficas_reconstruidas/fuentes/solow_accounting/generar.py /salida/vacia/solow
python graficas_reconstruidas/fuentes/ideas_taxes/generar.py --output /salida/vacia/ideas
python graficas_reconstruidas/fuentes/energy_slowdown/generar.py --output /salida/vacia/energia
```

Los manifiestos de cada grupo describen los resultados del recálculo; `catalogo.json` contiene las rutas de las especificaciones integradas. Las tablas derivadas de energía y demografía, incluidos los numeradores y denominadores de dependencia, se conservan en `fuentes/energy_slowdown/derivados/`.

Las imágenes se exportan con el control de descarga de cada gráfico; `scripts/verificar_graficas_reconstruidas.py` permite regenerarlas en el navegador y comprobar datos, fotogramas y recursos locales. La construcción de HTML y CSV no requiere red. El navegador debe tener acceso a Plotly.js local, incluido con su licencia MIT.

Para notas y presentaciones, usar `scripts/renderizar_modulos.R` con el módulo deseado. El renderizador lleva las gráficas a la salida manteniendo los enlaces relativos. Los HTML históricos se conservan como antecedentes; las fuentes Rmd y los materiales actualizados usan las reconstrucciones.

No se interpolan valores ausentes ni se presentan asociaciones como causalidad. Las variaciones de especificación, muestra y unidades constan en el catálogo y las vistas individuales.
''')
    write(destination/'.gitignore', '!index.html\n!graficas/\n!graficas/*.html\n!imagenes/\n!imagenes/*.png\n')
    write(destination/'.gitattributes', '* text eol=lf\n*.png binary\n')
    write(destination/'generacion.json', json.dumps({'count': 40, 'entries': records, 'plotly_sha256': sha(destination/'assets/plotly.min.js'), 'network_used': False}, ensure_ascii=False, indent=2)+'\n')
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fuente', type=Path)
    parser.add_argument('salida', type=Path)
    args = parser.parse_args()
    result = generate(args.fuente, args.salida)
    print(json.dumps({'graficas': len(result), 'animadas': sum(bool(r['frames']) for r in result)}))
