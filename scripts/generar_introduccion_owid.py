"""Genera las 15 vistas OWID de Introducción desde insumos archivados, sin red.

python scripts/generar_introduccion_owid.py [--output CARPETA]
La salida alternativa conserva referencias relativas al repositorio de origen.
"""
import argparse
import csv
import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'introduccion_local/owid'
COLORS = ['#2375ae', '#c65358', '#2c8b78', '#8f6aab', '#e59838', '#678087', '#a66747']
REGIONS = ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania', 'Sin región']
SPANISH = dict(zip(REGIONS, ['África', 'Asia', 'Europa', 'América del Norte', 'América del Sur', 'Oceanía', 'Sin región']))
LABELS = {'China': 'China', 'India': 'India', 'Sub Saharan Africa (Maddison)': 'África subsahariana (Maddison)',
          'Sub-Saharan Africa (WB)': 'África subsahariana (Banco Mundial)', 'United States': 'Estados Unidos',
          'United Kingdom': 'Reino Unido', 'Brazil': 'Brasil', 'Australia': 'Australia', 'Nigeria': 'Nigeria', **SPANISH}


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, separators=(',', ':'))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(slug):
    with (SOURCE/'originales'/f'{slug}.csv').open(encoding='utf-8-sig', newline='') as f:
        out = list(csv.DictReader(f))
    keys = [(r['Entity'], r['Year']) for r in out]
    assert len(keys) == len(set(keys)), 'Clave duplicada: '+slug
    return out


def metadata(slug):
    return json.loads((SOURCE/'metadatos'/f'{slug}.metadata.json').read_text(encoding='utf-8'))


def num(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def layout(title, x, y, log=False):
    return {'title': {'text': title, 'font': {'size': 21}}, 'xaxis': {'title': {'text': x}, 'type': 'log' if log else 'linear', 'gridcolor': '#e7ecf0', 'zeroline': False},
            'yaxis': {'title': {'text': y}, 'gridcolor': '#e7ecf0', 'rangemode': 'tozero', 'zeroline': False},
            'legend': {'orientation': 'h', 'y': -0.18, 'x': 0}, 'margin': {'l': 90, 'r': 35, 't': 90, 'b': 135},
            'paper_bgcolor': '#fff', 'plot_bgcolor': '#fff', 'font': {'family': 'Arial, Helvetica, sans-serif', 'size': 15, 'color': '#243746'},
            'hovermode': 'closest'}


def scatter(slug, title, xlabel, ylabel, *, ycol=None, log=True, alternative=False):
    data = rows(slug)
    cols = list(data[0])
    xc = next(c for c in cols if c.startswith('GDP per capita') and 'Annotation' not in c)
    yc = ycol or cols[3]
    used = []
    if alternative:
        pm = {(r['Entity'], r['Year']): num(r[list(r)[3]]) for r in rows('average-exposure-pm25-pollution')}
        for r in data:
            r = dict(r)
            r[yc] = pm.get((r['Entity'], r['Year']))
            used.append(r)
        data = used
    valid = []
    for r in data:
        xv, yv = num(r.get(xc)), num(r.get(yc))
        if len(r['Code']) == 3 and xv is not None and xv > 0 and yv is not None and int(r['Year']) >= 1950:
            valid.append({'entity': r['Entity'], 'code': r['Code'], 'year': int(r['Year']), 'x': xv, 'y': yv,
                          'region': r.get('World region according to OWID') or 'Sin región', 'status': 'estimación publicada', 'annotation': '; '.join(str(r[c]) for c in r if 'Annotation' in c and r[c])})
    by_year = {}
    for r in valid:
        by_year.setdefault(r['year'], []).append(r)
    assert by_year
    # Corte explícito para evitar que los pocos países más recientes sustituyan toda la muestra.
    years = sorted(y for y, rr in by_year.items() if len(rr) >= 50)
    assert years, 'Sin corte con 50 países: '+slug
    default = max(years)

    def traces(year):
        out = []
        for i, region in enumerate(REGIONS):
            rr = sorted([r for r in by_year[year] if r['region'] == region], key=lambda r: r['entity'])
            out.append({'type': 'scatter', 'mode': 'markers', 'name': SPANISH[region], 'x': [r['x'] for r in rr],
                        'y': [r['y'] for r in rr], 'text': [r['entity'] for r in rr], 'customdata': [[r['year'], r['code'], r['annotation']] for r in rr],
                        'marker': {'color': COLORS[i], 'size': 9, 'opacity': 0.78, 'line': {'color': '#fff', 'width': 0.5}},
                        'hovertemplate': '%{text}<br>Año: %{customdata[0]}<br>PIB por habitante: %{x:,.1f}<br>Indicador: %{y:,.3f}<br>%{customdata[2]}<extra></extra>'})
        return out

    spec = {'data': traces(default), 'layout': layout(f'{title} · {default}', xlabel, ylabel, log),
            'frames': [{'name': str(y), 'data': traces(y), 'layout': {'title': {'text': f'{title} · {y}'}}} for y in years]}
    return spec, valid, {'default_year': default, 'country_counts_by_year': {str(y): len(by_year[y]) for y in sorted(by_year)},
                         'period': [min(years), max(years)], 'display_years': years,
                         'method': 'Países con código de tres letras y valores de ambas variables en el mismo año. Se conserva únicamente PIB positivo. No se interpolan ni arrastran valores. Cada punto tiene igual tamaño. Selector: años desde 1950 con al menos 50 países; corte inicial: el más reciente que cumple esa regla. CSV conserva también los demás pares válidos.'}


def lines(slug, title, ylabel, entities, column=None, start=None, end=None, log=False):
    data = rows(slug)
    col = column or list(data[0])[3]
    series, valid = [], []
    for i, entity in enumerate(entities):
        rr = sorted([r for r in data if r['Entity'] == entity and num(r.get(col)) is not None and (start is None or int(r['Year']) >= start) and (end is None or int(r['Year']) <= end)], key=lambda r: int(r['Year']))
        assert rr, 'Entidad sin observaciones: '+entity
        yearvals = [(int(r['Year']), num(r[col])) for r in rr]
        # Insertar huecos explícitos impide unir años ausentes como si fueran continuos.
        lookup = dict(yearvals)
        years = list(range(min(lookup), max(lookup)+1))
        series.append({'type': 'scatter', 'mode': 'lines+markers', 'marker': {'size': 3}, 'name': LABELS.get(entity, entity), 'x': years,
                       'y': [lookup.get(y) for y in years], 'connectgaps': False, 'line': {'color': COLORS[i], 'width': 2.5},
                       'hovertemplate': '%{x}: %{y:,.3f}<extra>%{fullData.name}</extra>'})
        valid += [{'entity': entity, 'year': y, 'x': y, 'y': v, 'status': 'dato publicado'} for y, v in yearvals]
    lay = layout(title, 'Año', ylabel)
    if log:
        lay['yaxis']['type'] = 'log'
        lay['yaxis'].pop('rangemode', None)
    return {'data': series, 'layout': lay}, valid, {'period': [min(r['year'] for r in valid), max(r['year'] for r in valid)],
               'entities': entities, 'method': 'Selección de entidades y periodo del enlace del curso o su configuración archivada. No se interpolan ausencias: los años faltantes aparecen como huecos. Niveles publicados; sin medias propias entre países.'}


def employment(slug):
    data = sorted([r for r in rows(slug) if r['Code'] == 'USA'], key=lambda r: int(r['Year']))
    cc = ['People employed in agriculture', 'People employed in manufacturing', 'People employed in services']
    names = ['Agricultura', 'Manufactura / industria (fuente)', 'Servicios']
    use = [r for r in data if all(num(r[c]) is not None for c in cc)]
    assert use
    traces, valid = [], []
    for i, (c, name) in enumerate(zip(cc, names)):
        vals = [100 * num(r[c]) / sum(num(r[v]) for v in cc) for r in use]
        traces.append({'type': 'scatter', 'mode': 'lines', 'stackgroup': 'empleo', 'name': name,
                       'x': [int(r['Year']) for r in use], 'y': vals, 'line': {'color': COLORS[i], 'width': 1},
                       'hovertemplate': '%{x}: %{y:.2f}%<extra>%{fullData.name}</extra>'})
        valid += [{'entity': 'United States', 'series': name, 'year': int(r['Year']), 'x': int(r['Year']), 'y': v,
                   'numerator_people': num(r[c]), 'denominator_people': sum(num(r[k]) for k in cc), 'status': 'cálculo propio sobre datos publicados'} for r, v in zip(use, vals)]
    for j in range(len(use)):
        assert math.isclose(sum(t['y'][j] for t in traces), 100, abs_tol=1e-9)
    lay = layout('Empleo por sector · Estados Unidos', 'Año', 'Participación en el empleo de los tres sectores (%)')
    lay['yaxis']['range'] = [0, 100]
    return {'data': traces, 'layout': lay}, valid, {'period': [int(use[0]['Year']), int(use[-1]['Year'])],
        'method': '100 × empleo del sector / suma de empleo en los tres sectores, para cada año disponible. No se incorpora empleo ausente. Los valores absolutos y el denominador quedan en el CSV.',
        'extra_limits': 'El nombre histórico de la variable es industria y el metadato vigente dice manufactura. Se conserva la terminología de la fuente sin asumir cobertura sectorial idéntica a otra clasificación.'}


def population(slug, ages=False):
    raw = rows(slug)
    entities = ['World'] if ages else REGIONS[:-1]
    traces, valid = [], []
    if ages:
        pairs = [('Children (Under-15s)', 'Children (under-15s) (Projected)', 'Menores de 15 años'),
                 ('Working-age adults (15-64 years)', 'Working-age adults (15-64 years) (Projected)', '15 a 64 años'),
                 ('Older people (65+ years)', 'Older people (65+ years) (Projected)', '65 años o más')]
    else:
        pairs = [('Population', 'Population', SPANISH[e]) for e in entities]
    for i, (est, proj, label) in enumerate(pairs):
        entity = 'World' if ages else entities[i]
        rr = sorted([r for r in raw if r['Entity'] == entity and 1950 <= int(r['Year']) <= 2100], key=lambda r: int(r['Year']))
        assert len(rr) == 151
        years = [int(r['Year']) for r in rr]
        vals = []
        for r in rr:
            y = int(r['Year'])
            v = num(r[est if y <= 2023 else proj])
            assert v is not None
            vals.append(v/1e9)
            valid.append({'entity': entity, 'series': label, 'year': y, 'x': y, 'y': v/1e9, 'people': v,
                          'status': 'estimación publicada' if y <= 2023 else 'proyección media UN WPP 2024'})
        traces.append({'type': 'scatter', 'mode': 'lines', 'stackgroup': 'poblacion', 'name': label, 'x': years,
                       'y': vals, 'line': {'color': COLORS[i], 'width': 1}, 'hovertemplate': '%{x}: %{y:.3f} mil millones<extra>%{fullData.name}</extra>'})
    title = 'Población mundial por grupos de edad' if ages else 'Población mundial por región'
    lay = layout(title, 'Año', 'Miles de millones de personas')
    lay['shapes'] = [{'type': 'rect', 'xref': 'x', 'yref': 'paper', 'x0': 2023.5, 'x1': 2100, 'y0': 0, 'y1': 1, 'line': {'width': 0}, 'fillcolor': 'rgba(70,70,70,0.10)', 'layer': 'above'},
                     {'type': 'line', 'xref': 'x', 'yref': 'paper', 'x0': 2023.5, 'x1': 2023.5, 'y0': 0, 'y1': 1, 'line': {'color': '#536571', 'dash': 'dot', 'width': 1.5}}]
    lay['annotations'] = [{'xref': 'paper', 'yref': 'paper', 'x': 1, 'y': 1.03, 'text': 'Sombreado: proyección media desde 2024', 'showarrow': False, 'xanchor': 'right', 'font': {'size': 12}}]
    return {'data': traces, 'layout': lay}, valid, {'period': [1950, 2100], 'projection_start': 2024,
        'method': 'Niveles divididos entre 1.000.000.000. Estimaciones hasta 2023 y escenario medio de UN WPP 2024 desde 2024. Área sombreada identifica proyecciones; no se presentan como observaciones.',
        'extra_limits': 'El grupo de 15 a 64 años es población en edad laboral, no población ocupada ni económicamente activa.' if ages else 'Las seis regiones son las entidades de la configuración archivada de OWID. América del Norte incluye su delimitación OWID, no sólo Canadá y Estados Unidos.'}


CONFIG = [
('life-expectancy-years-vs-real-gdp-per-capita-2011us','owid-01-vida','Esperanza de vida y PIB por habitante','PIB por habitante (dólares internacionales de 2011)','Esperanza de vida al nacer (años)'),
('child-mortality-gdp-per-capita','owid-02-mortalidad-infantil','Mortalidad de menores de 5 años y PIB por habitante','PIB por habitante (dólares internacionales de 2011)','Muertes antes de 5 años por cada 100 nacidos vivos (%)'),
('children-per-woman-by-gdp-per-capita','owid-03-fecundidad','Fecundidad y PIB por habitante','PIB por habitante (dólares internacionales de 2021)','Nacimientos por mujer'),
('urbanization-vs-gdp','owid-04-urbanizacion','Urbanización y PIB por habitante','PIB por habitante (dólares internacionales de 2021)','Población urbana (%)'),
('outdoor-pollution-rate-vs-gdp','owid-05-exposicion-pm25','Exposición a PM2.5 y PIB por habitante','PIB por habitante (dólares internacionales de 2011)','Exposición media anual a PM2.5 (µg/m³)'),
('co-emissions-per-capita-vs-gdp-per-capita-international-','owid-06-co2','Emisiones de CO₂ y PIB por habitante','PIB por habitante (dólares internacionales de 2011)','CO₂ por habitante (toneladas)'),
('the-share-of-people-living-in-extreme-poverty-vs-gdp-per-capita','owid-07-pobreza-pib','Pobreza extrema y PIB por habitante','PIB por habitante (dólares internacionales de 2021)','Población con menos de US$3 al día (PPA 2021, %)'),
('gdp-per-capita-maddison-2020','owid-08-pib-regiones','PIB por habitante · China, India y África subsahariana','','Dólares internacionales de 2011 · escala logarítmica'),
('share-of-population-in-extreme-poverty','owid-09-pobreza-regiones','Pobreza extrema · China, India y África subsahariana','','Población con menos de US$3 al día (PPA 2021, %)'),
('global-hunger-index-vs-gdp-per-capita','owid-10-hambre','Índice Global del Hambre y PIB por habitante','PIB por habitante (dólares internacionales de 2021)','Índice Global del Hambre (puntos; edición 2021)'),
('share-of-adults-defined-as-obese','owid-11-obesidad','Obesidad en adultos de 18 años o más','','Adultos con IMC ≥30 kg/m² (%)'),
('gdppercapita-vs-annual-hours-worked','owid-12-horas','Horas anuales trabajadas y PIB por habitante','PIB por habitante (dólares internacionales de 2021)','Horas anuales por persona ocupada'),
('employment-by-economic-sector','owid-13-empleo-sectores','Empleo por sector · Estados Unidos','','Participación (%)'),
('historical-and-projected-population-by-region','owid-14-poblacion-regiones','Población mundial por región','','Miles de millones de personas'),
('dependency-age-groups-to-2100','owid-15-poblacion-edades','Población mundial por grupos de edad','','Miles de millones de personas')]


VISIBLE_SOURCES = [
    'Riley; HMD; ONU WPP 2024 y Maddison 2023',
    'Gapminder; UN IGME 2025 y Maddison 2023',
    'ONU WPP 2024 y Penn World Table 11.0 (2025)',
    'ONU DESA y Banco Mundial WDI 2026',
    'Banco Mundial WDI 2026 (PM2.5) y Maddison 2023 (PIB)',
    'Global Carbon Budget 2026 y Maddison 2023',
    'Banco Mundial PIP 2026 y WDI 2026',
    'Maddison Project Database 2023',
    'Banco Mundial Poverty and Inequality Platform 2026',
    'Global Hunger Index 2021 y Banco Mundial WDI 2026',
    'OMS Global Health Observatory 2026 · Adaptación CC BY-NC-SA 4.0',
    'Penn World Table 11.0 (2025)',
    'Herrendorf et al. (2017) · Cálculos propios',
    'ONU World Population Prospects 2024',
    'ONU World Population Prospects 2024',
]


def build(out):
    specmod = importlib.util.spec_from_file_location('reconstruccion_base', ROOT/'scripts/generar_graficas_reconstruidas.py')
    helper = importlib.util.module_from_spec(specmod)
    specmod.loader.exec_module(helper)
    out = out.resolve()
    for d in ['graficas', 'datos', 'imagenes', 'assets']:
        (out/d).mkdir(parents=True, exist_ok=True)
    write(out/'assets/clase.css', helper.CSS+'\n')
    write(out/'assets/clase.js', helper.JS+'\n')
    original_catalog = json.loads((ROOT/'Clases_Crecimiento_Economico/Introduction/referencias_externas/catalogo.json').read_text(encoding='utf-8'))
    mappings = original_catalog['records']
    lic = json.loads((SOURCE/'metadatos/licencias_indicadores.json').read_text(encoding='utf-8'))
    catalog = []
    for n, (resource, slug, title, xlabel, ylabel) in enumerate(CONFIG, 1):
        if n in [1, 2, 3, 4, 6, 7, 10, 12]:
            spec, points, info = scatter(resource, title, xlabel, ylabel, log=n != 12)
        elif n == 5:
            # Se cruza PM2.5 con el PIB Maddison del mismo país-año, sin recuperar observaciones restringidas.
            spec, points, info = scatter('life-expectancy-years-vs-real-gdp-per-capita-2011us', title, xlabel, ylabel,
                                         ycol='Life expectancy at birth', alternative=True)
        elif n == 8:
            spec, points, info = lines(resource, title, ylabel, ['China', 'India', 'Sub Saharan Africa (Maddison)'], start=1979, end=2018, log=True)
        elif n == 9:
            spec, points, info = lines(resource, title, ylabel, ['China', 'India', 'Sub-Saharan Africa (WB)'], end=2023)
        elif n == 11:
            spec, points, info = lines(resource, title, ylabel, ['United States', 'United Kingdom', 'Brazil', 'India', 'Australia', 'Nigeria'])
        elif n == 13:
            spec, points, info = employment(resource)
        else:
            spec, points, info = population(resource, ages=n == 15)
        if n == 1:
            spec['layout']['annotations']=[{'xref':'paper','yref':'paper','x':0,'y':1.03,'xanchor':'left','showarrow':False,'font':{'size':12,'color':'#8d4c36'},'text':'Dato atípico del origen: R. Centroafricana 2022 (18,8 años). Ver alcance.'}]
        if n == 5:
            meta_slugs = ['average-exposure-pm25-pollution', 'life-expectancy-years-vs-real-gdp-per-capita-2011us']
            ids = [1293799, 900793]
        else:
            meta_slugs = [resource]
            ids = [v.get('owidVariableId') for v in metadata(resource)['columns'].values() if v.get('owidVariableId')]
        sources = []
        for ms in meta_slugs:
            m = metadata(ms)
            for c in m['columns'].values():
                if n == 5 and c.get('owidVariableId') not in ids:
                    continue
                if c.get('owidVariableId'):
                    sources.append({k: c.get(k) for k in ['owidVariableId', 'titleLong', 'unit', 'lastUpdated', 'citationLong']})
        limits = ['Edición descargada el 12 de noviembre de 2026. No reproduce las cifras ni el diseño del enlace del semestre de 2023.',
                  'Asociación descriptiva: la figura no identifica un efecto causal. La disponibilidad varía por país y año.']
        if n == 1:
            limits.append('La fuente publica un dato atípico para República Centroafricana en 2022: 18,8177 años. El contraste con WDI/DataBank y FRED confirma 18,8 años en esas publicaciones, pero los metadatos consultados no explican el extremo. Se conserva sin corregirlo ni atribuirle una causa. Véase metadatos/control_calidad_vida.json.')
        if n == 5:
            limits.append('Sustitución de variable: muestra concentración/exposición a partículas PM2.5, no muertes atribuidas a contaminación. La serie de mortalidad restringida no se descarga ni redistribuye.')
        if n in [7, 9]:
            limits.append('La línea de pobreza vigente es US$3 diarios a PPA de 2021. No es comparable de forma directa con los umbrales y bases PPA de versiones anteriores del curso. Las tasas regionales incorporan extrapolaciones del productor; la vista de China, India y África subsahariana se trunca en 2023 para excluir años posteriores.')
        if n in [8, 9]:
            limits.append('La delimitación regional de África subsahariana procede respectivamente de Maddison y del Banco Mundial; los dos agregados no presuponen idéntica composición.')
        if n == 10:
            limits.append('Las anotaciones del CSV identifican países representados mediante puntos medios de categorías de severidad. Esos valores no son mediciones puntuales exactas. El índice publicado en 2021 combina componentes y ventanas de referencia. El año del índice no significa que todos sus insumos se midieran en ese año; se cruza con PIB del mismo año etiquetado.')
        if n == 11:
            limits.append('Estimación cruda, ambos sexos, adultos de 18 años o más. Reutilización de la adaptación bajo CC BY-NC-SA 4.0, según términos de la OMS archivados.')
        if info.get('extra_limits'):
            limits.append(info['extra_limits'])
        original = next(r for r in mappings if r.get('provider') == 'Our World in Data' and r.get('resource_id') == resource)
        rec = {'original_url': original['source_url'], 'source_occurrences': original['occurrences'], 'course_context': original.get('context'), 'order': n, 'provider': 'Our World in Data', 'resource_id': resource, 'slug': slug, 'title': title,
               'html': f'introduccion_local/owid/graficas/{slug}.html', 'image_png': f'introduccion_local/owid/imagenes/{slug}.png',
               'status': 'sustitución de variable' if n == 5 else 'adaptación a edición nueva', 'source_urls': ['https://ourworldindata.org/grapher/'+s for s in meta_slugs],
               'source_metadata': sources, 'source_vintage': [{'variable_id': x['owidVariableId'], 'updated': x['lastUpdated']} for x in sources],
               'units': {'x': xlabel or 'Año', 'y': ylabel}, 'limitations': limits,
               'licenses': [x for x in lic if x['id'] in ids and not x.get('nonRedistributable')], **info}
        if n == 1:
            rec['quality_note']='Dato atípico CAF 2022 conservado y marcado; no se infiere causa.'
            rec['quality_sources']=['https://databank.worldbank.org/reports.aspx?country=CAF&series=SP.DYN.LE00.IN&source=2','https://fred.stlouisfed.org/series/SPDYNLE00INCAF']
        if n == 5:
            pm = json.loads((SOURCE/'metadatos/pollution_alternative_full.metadata.json').read_text(encoding='utf-8'))
            rec['licenses'].append({'id': 1293799, 'nonRedistributable': pm['nonRedistributable'], 'licenses': [o.get('license') for o in pm['origins']]})
        if n == 15:
            grouped = {}
            for p in points: grouped.setdefault(p['year'], {})[p['series']] = p['people']
            ratios = [{'year': y, 'children_0_14': d['Menores de 15 años'], 'working_age_15_64': d['15 a 64 años'], 'older_65_plus': d['65 años o más'], 'dependents_per_100_working_age': 100*(d['Menores de 15 años']+d['65 años o más'])/d['15 a 64 años'], 'status': 'estimación publicada' if y <= 2023 else 'proyección media UN WPP 2024'} for y,d in sorted(grouped.items())]
            with (out/'datos/dependencia_demografica.csv').open('w',encoding='utf-8',newline='') as f:
                wr=csv.DictWriter(f,fieldnames=list(ratios[0]),lineterminator='\n');wr.writeheader();wr.writerows(ratios)
            rec['supplementary_csv']='introduccion_local/owid/datos/dependencia_demografica.csv'
            rec['dependency_formula']='100 × (población 0–14 + población 65+) / población 15–64. Razón demográfica, no dependencia económica observada.'
        visible_source = 'Fuente: '+VISIBLE_SOURCES[n-1]+' vía Our World in Data.<br>Edición de descarga: 12 de noviembre de 2026.'
        spec['layout'].setdefault('annotations', []).append({'xref':'paper','yref':'paper','x':0,'y':-0.28,'xanchor':'left','yanchor':'top','showarrow':False,'align':'left','font':{'size':14,'color':'#52616b'},'text':visible_source})
        rec['visible_source'] = visible_source
        write(out/'datos'/f'{slug}.json', dump(spec)+'\n')
        with (out/'datos'/f'{slug}.csv').open('w', encoding='utf-8', newline='') as f:
            fields = sorted(set().union(*(r.keys() for r in points)))
            wr = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
            wr.writeheader()
            wr.writerows(points)
        rec['spec_sha256'] = sha(out/'datos'/f'{slug}.json')
        rec['data_sha256'] = sha(out/'datos'/f'{slug}.csv')
        rec['observations'] = len(points)
        rel = lambda p: os.path.relpath(p, out/'graficas').replace('\\', '/')
        metadata_links = ' · '.join(f'<a href="{html.escape(rel(SOURCE/"metadatos"/(s+".metadata.json")))}">Metadatos {i+1}</a>' for i, s in enumerate(meta_slugs))
        source_links = ' · '.join(f'<a href="{html.escape(u)}">Fuente {i+1}</a>' for i, u in enumerate(rec['source_urls']))
        license_text = ' · '.join(sorted(set(l['name'] for item in rec['licenses'] for l in item.get('licenses', []) if l and l.get('name'))))
        if any(not any(l for l in item.get('licenses', [])) for item in rec['licenses']):
            license_text += (' · ' if license_text else '')+'Algunas series no indican licencia específica en los metadatos; consultar origen'
        rec['license_summary'] = license_text
        period = f'{rec["period"][0]}–{rec["period"][1]}'
        animation = '<div class="animation"><button type="button" id="reproducir">Reproducir</button><button type="button" id="pausar">Pausar</button><label for="fotograma">Año: </label><select id="fotograma"></select><button type="button" id="mostrar">Mostrar</button></div>' if spec.get('frames') else ''
        # Seleccionar el año inicial en el control sin ejecutar una animación.
        select_js = f'<script>const defaultYear="{info.get("default_year", "")}";const tick=setInterval(()=>{{if(window.graficaLista){{const s=document.getElementById("fotograma");if(s)s.value=defaultYear;clearInterval(tick);}}}},50);</script>'
        embedded = dump(spec).replace('</', '<\\/')
        page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="../assets/clase.css"></head><body data-slug="{slug}"><main><div class="full-only"><nav><a href="../index.html">Gráficas de Introducción</a></nav><h1>{html.escape(title)}</h1><p class="note">{html.escape(rec['status'].capitalize())}. Datos descargados el 12 de noviembre de 2026.</p><p><strong>Periodo:</strong> {period}. <strong>Unidades:</strong> {html.escape(ylabel)}.</p></div>{animation}<div id="grafica" class="plot" role="img" aria-label="{html.escape(title)}"></div><p class="embed-only">Edición 2026 · datos y fuentes en la vista completa.</p><div class="full-only"><p id="estado">Consulte los valores al señalar los puntos o series.</p><p><a href="../datos/{slug}.csv" download>Datos CSV</a> · <a href="../datos/{slug}.json" download>Especificación JSON</a> · <a href="../imagenes/{slug}.png" download>PNG</a> · <a href="../imagenes/{slug}.svg" download>SVG</a></p><p><strong>Método:</strong> {html.escape(info['method'])}</p><p><strong>Alcance:</strong> {html.escape(' '.join(limits))}</p><p>{source_links} · {metadata_links}</p><p><strong>Condiciones de reutilización:</strong> {html.escape(license_text)}. Ver metadatos y condiciones por serie.</p><details><summary>Procedencia, edición y unidades</summary><pre>{html.escape(json.dumps(rec, ensure_ascii=False, indent=2))}</pre></details></div><script type="application/json" id="spec">{embedded}</script><script src="{rel(ROOT/'recursos_graficas/assets/plotly.min.js')}"></script><script src="../assets/clase.js"></script>{select_js}</main></body></html>\n'''
        write(out/'graficas'/f'{slug}.html', page)
        catalog.append(rec)
    write(out/'.gitignore', '!index.html\n!graficas/\n!graficas/*.html\n!imagenes/\n!imagenes/*.png\n')
    write(out/'.gitattributes', '* text eol=lf\n*.png binary\n')
    write(out/'catalogo.json', json.dumps({'date_downloaded': '2026-11-12', 'network_used_by_generator': False, 'entries': catalog}, ensure_ascii=False, indent=2)+'\n')
    matrix = ['# Correspondencia de los 15 destinos OWID', '', 'Edición descargada el 12 de noviembre de 2026. El catálogo JSON conserva cada ocurrencia en R Markdown y el enlace original con sus filtros.', '', '| Destino original | Vista local | Unidad vertical | Corte inicial / periodo | Alcance |', '| --- | --- | --- | --- | --- |']
    for r in catalog:
        period = str(r.get('default_year') or (str(r['period'][0])+'–'+str(r['period'][1])))
        matrix.append('| ['+r['resource_id']+']('+r['original_url']+') | ['+r['title']+'](graficas/'+r['slug']+'.html) | '+r['units']['y']+' | '+period+' | '+r['status']+' |')
    write(out/'CORRESPONDENCIA.md', '\n'.join(matrix)+'\n')
    header = '<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gráficas OWID de Introducción</title><link rel="stylesheet" href="assets/clase.css"><main><h1>Gráficas de Introducción · OWID</h1><p>15 vistas locales con datos archivados el 12 de noviembre de 2026. Cada vista conserva fuentes, unidades, edición, CSV y especificación. PM2.5 sustituye la mortalidad por contaminación con otra variable expresamente identificada.</p><table><thead><tr><th>Tema</th><th>Periodo</th><th>Alcance</th></tr></thead><tbody>'
    body = ''.join(f'<tr><td><a href="graficas/{r["slug"]}.html">{html.escape(r["title"])}</a></td><td>{r["period"][0]}–{r["period"][1]}</td><td>{html.escape(r["status"])}</td></tr>' for r in catalog)
    write(out/'index.html', header+body+'</tbody></table><p><a href="README.md">Método y reproducción</a> · <a href="catalogo.json">Catálogo</a></p></main></html>\n')
    write(out/'README.md', '''# Gráficas OWID de Introducción

Abrir `index.html` desde una copia completa del repositorio. Las vistas y los datos funcionan sin conexión. Los enlaces a la procedencia se consultan por internet. Las 15 vistas son adaptaciones de los destinos de las tres fuentes R Markdown de Introducción. La edición descargada el 12 de noviembre de 2026 sustituye las cifras históricas enlazadas; no certifica igualdad con ellas.

Repetir el cálculo desde la raíz: `python scripts/generar_introduccion_owid.py`. El script sólo lee CSV y metadatos archivados en esta carpeta y usa la biblioteca estándar de Python. `--output` genera una copia alternativa. Con `--export`, el mismo comando exporta PNG y SVG de la vista inicial con Plotly.js local y Playwright Chromium instalado. La generación de datos sólo requiere la biblioteca estándar de Python; la exportación requiere Playwright y su navegador.

Las dispersiones emparejan país y año, excluyen PIB no positivo y filas sin ambas variables. El tamaño del punto es uniforme. El selector incluye años desde 1950 con al menos 50 países; el corte inicial es el último que cumple esa regla y el CSV conserva todos los pares válidos. La elección prioriza una muestra amplia y evita mezclar fechas. Las líneas no interpolan años faltantes. La composición del empleo divide cada sector entre la suma de los tres sectores disponibles. Las poblaciones se expresan en miles de millones y separan estimaciones hasta 2023 del escenario medio UN WPP 2024 a partir de 2024.

PM2.5 muestra exposición media anual en µg/m³ y PIB Maddison del mismo país-año. Sustituye una gráfica de mortalidad por contaminación cuyos metadatos impiden redistribuir observaciones. La serie restringida no forma parte de los datos locales. La fecundidad no se denomina crecimiento poblacional. La mortalidad infantil se define como probabilidad de morir antes de cinco años, no mortalidad de menores de un año. La población de 15 a 64 años no equivale al empleo.

La pobreza usa la definición vigente de US$3 diarios a PPA de 2021. La serie Maddison descargada bajo un nombre que incluye `2020` contiene en sus metadatos la edición Maddison Project Database 2023, en dólares internacionales de 2011. El catálogo conserva esa diferencia. Los agregados de África subsahariana de Maddison y del Banco Mundial tienen sus propias delimitaciones. Las dispersiones con PWT o Banco Mundial usan dólares internacionales de 2021 según su metadato. No se combinan esas bases como si fueran iguales.

## Fuentes y reutilización

Los CSV originales y los metadatos completos se conservan en `originales/` y `metadatos/`; `catalogo.json` identifica fuente, versión, unidad, fecha, licencia y transformación por figura. Se atribuye cada serie al productor y a Our World in Data como procesador. Las condiciones son específicas de cada origen, y no se sustituye su licencia por una licencia general del repositorio. La adaptación de obesidad de la OMS se ofrece para uso no comercial bajo CC BY-NC-SA 4.0, con atribución a World Health Organization – Global Health Observatory (2026) y OWID. La serie PM2.5 obtenida del Banco Mundial figura como CC BY 4.0 en los metadatos. UN WPP usa CC BY 3.0 IGO. Los demás detalles y enlaces de condiciones constan en el catálogo.

El archivo de esperanza de vida contiene un dato atípico para República Centroafricana en 2022 (18,8177 años), confirmado también en WDI/DataBank y FRED (18,8). Se mantiene con advertencia visible: el contraste acredita lo publicado, no explica ni valida sustantivamente ese valor. El registro de contraste está en `metadatos/control_calidad_vida.json`.

El gráfico de hambre mantiene la edición 2021: los componentes del índice pueden referirse a ventanas de años diferentes. Las asociaciones descriptivas no identifican efectos causales. Las imágenes exportadas representan el corte inicial, y el JSON conserva los años del selector.
''')
    return catalog


def export_images(out, catalog):
    from playwright.sync_api import sync_playwright
    import base64
    from urllib.parse import unquote_to_bytes
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        ctx=browser.new_context(viewport={'width':1400,'height':1000})
        external=[]
        def route(r):
            if r.request.url.startswith(('http:','https:')): external.append(r.request.url);r.abort()
            else: r.continue_()
        ctx.route('**/*',route)
        page=ctx.new_page()
        for row in catalog:
            page.goto((out/'graficas'/(row['slug']+'.html')).resolve().as_uri(),wait_until='load')
            page.wait_for_function('window.graficaLista===true',timeout=60000)
            for ext in ('png','svg'):
                data=page.evaluate('async ext=>await window.exportarGrafica(ext)',ext)
                payload=data.split(',',1)[1]
                raw=base64.b64decode(payload) if ';base64,' in data else unquote_to_bytes(payload)
                (out/'imagenes'/(row['slug']+'.'+ext)).write_bytes(raw)
        browser.close()
        assert not external, external


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=SOURCE)
    parser.add_argument('--export', action='store_true', help='Exportar PNG/SVG con Playwright Chromium instalado, sin red.')
    args = parser.parse_args()
    result = build(args.output)
    if args.export: export_images(args.output.resolve(), result)
    print(json.dumps({'figures': len(result), 'network_used': False, 'entries': [{'slug': r['slug'], 'year': r.get('default_year'), 'period': r['period'], 'observations': r['observations']} for r in result]}, ensure_ascii=False), flush=True)
