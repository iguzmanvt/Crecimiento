"""Verifica las 17 vistas Chart Studio sin red ni cambios en informes históricos.

Uso: python introduccion_local/chartstudio/verificar.py [--report RUTA.json]
El resumen se escribe en stdout. Sólo --report crea un informe solicitado.
Los hashes de insumos y archivos publicados son estrictos. El recálculo admite
1e-12 absoluto/relativo para flotantes, con estructura, tipos y textos exactos.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import html
import json
import math
import platform
import re
import struct
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ABSOLUTE_TOLERANCE = 1e-12
RELATIVE_TOLERANCE = 1e-12
EXPECTED_IDS = {150,152,66,154,160,170,174,202,207,156,172,176,205,209,158,168,118}
DERIVED_HASH_FIELDS = ('spec_sha256', 'csv_sha256')
SPEC_BLOCK = re.compile(r'(<script\b[^>]*\bid="spec"[^>]*>)(.*?)(</script\s*>)', re.S)
METADATA_BLOCK = re.compile(r'(<pre>)(.*?)(</pre>)', re.S)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


class Comparison:
    def __init__(self, absolute=ABSOLUTE_TOLERANCE, relative=RELATIVE_TOLERANCE):
        self.absolute = absolute
        self.relative = relative
        self.maximum = 0.0
        self.numeric_values = 0

    def compare(self, left, right, location):
        if type(left) is not type(right):
            raise ValueError(location + ': cambió el tipo de dato')
        if isinstance(left, bool) or left is None:
            if left != right:
                raise ValueError(location + ': cambió el valor lógico/nulo')
        elif isinstance(left, int):
            self.numeric_values += 1
            self.maximum = max(self.maximum, abs(left-right))
            if left != right:
                raise ValueError(location + ': cambió un entero')
        elif isinstance(left, float):
            if not math.isfinite(left) or not math.isfinite(right):
                raise ValueError(location + ': valor no finito')
            self.numeric_values += 1
            self.maximum = max(self.maximum, abs(left-right))
            if not math.isclose(left, right, rel_tol=self.relative, abs_tol=self.absolute):
                raise ValueError(location + ': diferencia numérica fuera de tolerancia')
        elif isinstance(left, dict):
            if list(left) != list(right):
                raise ValueError(location + ': cambiaron claves u orden del objeto')
            for key in left:
                self.compare(left[key], right[key], location + '.' + key)
        elif isinstance(left, list):
            if len(left) != len(right):
                raise ValueError(location + ': cambió la longitud de la lista')
            for i, (a, b) in enumerate(zip(left, right)):
                self.compare(a, b, location + '[' + str(i) + ']')
        elif left != right:
            raise ValueError(location + ': cambió texto u otro valor no numérico')


def exact(left, right, location):
    Comparison(absolute=0.0, relative=0.0).compare(left, right, location)


def canonical_entry(entry):
    # Each side's digests have already been checked against its own files.
    # Only those content-derived digests differ when floats differ by one ULP.
    # Input hashes, metadata strings, keys and all other fields stay untouched.
    result = dict(entry)
    for field in DERIVED_HASH_FIELDS:
        result[field] = '<verified-content-digest>'
    return result


def check_catalog(folder, published=False):
    catalog = read_json(folder/'catalogo.json')
    entries = catalog['entries']
    if len(entries) != 17 or {int(e['identity'].split(':')[1]) for e in entries} != EXPECTED_IDS:
        raise ValueError('Se requieren las 17 identidades exactas')
    if len({e['slug'] for e in entries}) != 17:
        raise ValueError('Slugs repetidos')
    for entry in entries:
        spec = folder/entry['spec_path']
        csv_path = folder/'datos'/(entry['slug']+'.csv')
        if sha(spec) != entry['spec_sha256'] or sha(csv_path) != entry['csv_sha256']:
            raise ValueError('Hash de archivo incoherente: '+entry['identity'])
        data = read_json(spec)
        if not data['data']:
            raise ValueError('Especificación vacía: '+entry['identity'])
        for trace in data['data']:
            if len(trace['x']) != len(trace['y']):
                raise ValueError('Longitudes x/y incompatibles: '+entry['identity'])
            if not all(value is None or type(value) in (int,float) and math.isfinite(value) for value in trace['y']):
                raise ValueError('Valores y no finitos: '+entry['identity'])
        if published:
            for relative, expected in entry['local_inputs'].items():
                if sha(folder/entry.get('input_base','fuentes')/relative) != expected:
                    raise ValueError('Hash de insumo diferente: '+relative)
            for suffix in ('svg','png'):
                path = folder/'imagenes'/(entry['slug']+'.'+suffix)
                if not path.is_file() or path.stat().st_size <= 1000:
                    raise ValueError('Falta exportación: '+str(path))
            png = folder/'imagenes'/(entry['slug']+'.png')
            if struct.unpack('>II',png.read_bytes()[16:24]) != (1200,700):
                raise ValueError('Dimensión PNG distinta: '+entry['identity'])
    return catalog


def canonical_catalog(catalog):
    result = dict(catalog)
    result['entries'] = [canonical_entry(entry) for entry in catalog['entries']]
    return result


def compare_csv(left, right, comparison, location):
    with left.open(encoding='utf-8-sig',newline='') as stream:
        a = list(csv.reader(stream))
    with right.open(encoding='utf-8-sig',newline='') as stream:
        b = list(csv.reader(stream))
    if not a or not b or a[0] != b[0] or len(a) != len(b):
        raise ValueError(location+': cambió estructura CSV')
    headers = a[0]
    for row_index, (row_a,row_b) in enumerate(zip(a[1:],b[1:]),start=2):
        if len(row_a) != len(headers) or len(row_b) != len(headers):
            raise ValueError(location+': cambió longitud de fila CSV')
        for column, value_a, value_b in zip(headers,row_a,row_b):
            where = location+':'+str(row_index)+':'+column
            if column in ('x','y'):
                comparison.compare(json.loads(value_a),json.loads(value_b),where)
            elif column == 'datos_adicionales' and value_a and value_b:
                try:
                    data_a,data_b = json.loads(value_a),json.loads(value_b)
                except json.JSONDecodeError:
                    exact(value_a,value_b,where)
                else:
                    comparison.compare(data_a,data_b,where)
            elif column == 'years_schooling':
                comparison.compare(float(value_a),float(value_b),where)
            else:
                exact(value_a,value_b,where)


def html_parts(path, entry, folder):
    source = path.read_text(encoding='utf-8')
    specifications = list(SPEC_BLOCK.finditer(source))
    metadata = list(METADATA_BLOCK.finditer(source))
    if len(specifications) != 1 or len(metadata) != 1:
        raise ValueError(str(path)+': cambió estructura de HTML/JSON')
    spec = json.loads(specifications[0].group(2))
    details = json.loads(html.unescape(metadata[0].group(2)))
    exact(spec,read_json(folder/entry['spec_path']),str(path)+':JSON incrustado')
    exact(details,entry,str(path)+':metadatos incrustados')
    # Remove only the JSON bodies. Opening/closing tags and all remaining text
    # must match exactly, apart from the Git newline convention.
    rest = SPEC_BLOCK.sub(lambda match:match.group(1)+'<verified-specification>'+match.group(3),source)
    rest = METADATA_BLOCK.sub(lambda match:match.group(1)+'<verified-metadata>'+match.group(3),rest)
    return rest, spec, canonical_entry(details)


def independent_checks(folder):
    with (folder/'fuentes/pwt100_seleccion.csv').open(encoding='utf-8-sig') as stream:
        pwt = list(csv.DictReader(stream))
    usa = next(row for row in pwt if row['countrycode']=='USA' and row['year']=='2019')
    formulas = [
        (150,lambda row:math.log(float(row['rgdpna'])/float(row['pop']))),
        (202,lambda row:float(row['labsh'])),
        (207,lambda row:float(row['labsh'])*float(row['rgdpna'])/(float(row['labsh'])*float(row['rgdpna'])+.05*float(row['rnna']))),
        (156,lambda row:float(row['rnna'])/float(row['rgdpna']))]
    checks = []
    for ident,formula in formulas:
        spec = read_json(folder/'datos'/f'iguzmanvt-{ident}.json')
        trace = next(trace for trace in spec['data'] if trace['name']=='Estados Unidos')
        actual = trace['y'][trace['x'].index(2019)]
        wanted = formula(usa)
        comparison = Comparison()
        comparison.compare(actual,wanted,str(ident)+':USA:2019')
        checks.append({'id':ident,'year':2019,'USA':actual,'independent_check':True,'maximum_numeric_difference':comparison.maximum})
    with (folder/'fuentes/data/pwt1001_na_data.csv').open(encoding='utf-8-sig') as stream:
        accounts = list(csv.DictReader(stream))
    row = next(row for row in accounts if row['countrycode']=='USA' and row['year']=='2019')
    for ident,numerator in ((170,'v_c'),(174,'v_i')):
        spec = read_json(folder/'datos'/f'iguzmanvt-{ident}.json')
        trace = next(trace for trace in spec['data'] if trace['name']=='Estados Unidos')
        actual = trace['y'][trace['x'].index(2019)]
        comparison = Comparison()
        comparison.compare(actual,float(row[numerator])/float(row['v_gdp']),str(ident)+':USA:2019')
        checks.append({'id':ident,'year':2019,'USA':actual,'independent_check':True,'maximum_numeric_difference':comparison.maximum})
    if sum(read_json(folder/'datos/iguzmanvt-168.json')['data'][0]['y']) != 150:
        raise ValueError('La distribución de escolaridad no suma 150 países')
    return checks


def verify(root):
    folder = root/'introduccion_local/chartstudio'
    catalog = check_catalog(folder,published=True)
    checks = independent_checks(folder)
    expected = {'index.html','catalogo.json','README.md','datos/iguzmanvt-168_paises.csv',
                'assets/clase.css','assets/clase.js','assets/plotly.min.js'}
    for entry in catalog['entries']:
        for suffix in ('json','csv'):
            expected.add('datos/'+entry['slug']+'.'+suffix)
        expected.add('graficas/'+entry['slug']+'.html')
    if len(expected) != 58:
        raise ValueError('Cambió el conjunto de artefactos de generación')
    records = []
    with tempfile.TemporaryDirectory(prefix='crecimiento_chartstudio_') as temporary:
        recalculated = Path(temporary)/'recalculo'
        subprocess.run([sys.executable,str(root/'scripts/generar_introduccion_chartstudio.py'),
                        '--output',str(recalculated)],check=True,capture_output=True)
        other = check_catalog(recalculated)
        generated = {path.relative_to(recalculated).as_posix()
                     for name in ('datos','graficas','assets')
                     for path in (recalculated/name).iterdir()
                     if path.is_file() and path.name != '.gitattributes'}
        generated.update(name for name in ('index.html','catalogo.json','README.md') if (recalculated/name).is_file())
        if generated != expected:
            raise ValueError('El generador produjo un conjunto de archivos distinto')
        for relative in sorted(expected):
            left,right = folder/relative,recalculated/relative
            comparison = Comparison()
            derived_changed = 0
            if relative == 'catalogo.json':
                comparison.compare(canonical_catalog(catalog),canonical_catalog(other),relative)
                derived_changed = sum(a[field]!=b[field] for a,b in zip(catalog['entries'],other['entries']) for field in DERIVED_HASH_FIELDS)
            elif relative.endswith('.json'):
                comparison.compare(read_json(left),read_json(right),relative)
            elif relative.endswith('.csv'):
                compare_csv(left,right,comparison,relative)
            elif relative.startswith('graficas/') and relative.endswith('.html'):
                entry = next(entry for entry in catalog['entries'] if relative=='graficas/'+entry['slug']+'.html')
                other_entry = next(candidate for candidate in other['entries'] if candidate['slug']==entry['slug'])
                rest_a,spec_a,metadata_a = html_parts(left,entry,folder)
                rest_b,spec_b,metadata_b = html_parts(right,other_entry,recalculated)
                exact(rest_a,rest_b,relative+':texto HTML')
                comparison.compare(spec_a,spec_b,relative+':JSON incrustado')
                comparison.compare(metadata_a,metadata_b,relative+':metadatos')
                derived_changed = sum(entry[field]!=other_entry[field] for field in DERIVED_HASH_FIELDS)
            else:
                exact(left.read_text(encoding='utf-8'),right.read_text(encoding='utf-8'),relative)
            raw_a,raw_b = left.read_bytes(),right.read_bytes()
            records.append({'path':relative,'equivalent_within_tolerance':True,
                            'byte_identical':raw_a==raw_b,
                            'byte_equal_after_LF_normalization':raw_a.replace(b'\r\n',b'\n')==raw_b.replace(b'\r\n',b'\n'),
                            'maximum_numeric_difference':comparison.maximum,
                            'numeric_values_compared':comparison.numeric_values,
                            'derived_hash_fields_changed_and_verified':derived_changed})
    return {'validated_at_utc':datetime.now(timezone.utc).isoformat(),'count':17,
            'environment':sys.version,'platform':platform.platform(),
            'identity_set_exact':True,'data_finite':True,'input_hashes':True,
            'published_spec_and_csv_hashes':True,'exports_dimensions':[1200,700],
            'absolute_tolerance':ABSOLUTE_TOLERANCE,'relative_tolerance':RELATIVE_TOLERANCE,
            'files_compared':len(records),
            'recalculated_files_equivalent':len(records),
            'recalculated_files_identical':sum(row['byte_identical'] for row in records),
            'byte_equal_after_LF_normalization':sum(row['byte_equal_after_LF_normalization'] for row in records),
            'maximum_numeric_difference':max(row['maximum_numeric_difference'] for row in records),
            'independent_numeric_checks':checks,'schooling_countries':150,
            'browser_record':'verificacion_navegador.json','network_used':False,
            'ignored_repository_metadata':['assets/.gitattributes'],
            'results':records,'status':'PASS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,help='Escribir un informe nuevo en esta ruta; sin esta opción no modifica informes')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    result = verify(root)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    keys = ('status','count','files_compared','recalculated_files_equivalent','recalculated_files_identical',
            'byte_equal_after_LF_normalization','maximum_numeric_difference','absolute_tolerance','relative_tolerance')
    print(json.dumps({key:result[key] for key in keys},ensure_ascii=False))


if __name__ == '__main__':
    if hasattr(sys.stdout,'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        main()
    except (ValueError,OSError,KeyError,subprocess.CalledProcessError) as error:
        print('ERROR:',str(error),file=sys.stderr)
        raise SystemExit(1)
