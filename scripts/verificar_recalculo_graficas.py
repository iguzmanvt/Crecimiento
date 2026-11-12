"""Recalcula las 40 especificaciones sin red y coteja fuentes, datos y fotogramas.

Uso: python scripts/verificar_recalculo_graficas.py GRAFICAS INFORME.json
Python 3.10+, biblioteca estándar. Las salidas intermedias son temporales.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compare(a, b, maximum):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        maximum[0] = max(maximum[0], abs(a-b))
        return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(compare(a[k], b[k], maximum) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(compare(x, y, maximum) for x, y in zip(a, b))
    return a == b

def verify(root, report):
    root = root.resolve()
    catalog = json.loads((root/'catalogo.json').read_text(encoding='utf-8'))
    entries = catalog['entries']
    assert len(entries) == len({x['identity'] for x in entries}) == 40
    checked_inputs = {}
    for entry in entries:
        assert sha(root/entry['spec_path']) == entry['spec_sha256'], entry['identity']
        for path, expected in entry['local_inputs'].items():
            assert sha(root/path) == expected, (entry['identity'], path)
            checked_inputs[path] = expected
    groups = [('solow_accounting', []), ('ideas_taxes', ['--output']), ('energy_slowdown', ['--output'])]
    records = []
    with tempfile.TemporaryDirectory(prefix='recalculo_crecimiento_') as temporary:
        for group, flags in groups:
            folder = Path(temporary)/group
            command = [sys.executable, str(root/'fuentes'/group/'generar.py'), *flags, str(folder)]
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            selected = [e for e in entries if e['method_folder'] == 'fuentes/'+group]
            for entry in selected:
                actual = folder/(entry['slug']+'.json')
                expected = root/entry['spec_path']
                a = json.loads(expected.read_text(encoding='utf-8'))
                b = json.loads(actual.read_text(encoding='utf-8'))
                maximum = [0.0]
                assert compare(a, b, maximum), entry['identity']
                canonical = lambda p: p.read_bytes().replace(b'\r\n', b'\n')
                records.append({'identity': entry['identity'], 'group': group,
                    'spec_sha256': entry['spec_sha256'],
                    'equivalent_within_tolerance': True,
                    'byte_equal_after_LF_normalization': canonical(expected) == canonical(actual),
                    'maximum_numeric_difference': maximum[0]})
            print('RECALCULATED', group, len(selected), flush=True)
    assert len(records) == 40
    data = {'count': 40, 'environment': sys.version, 'platform': sys.platform,
        'relative_tolerance': 1e-12, 'absolute_tolerance': 1e-12,
        'inputs_checked': len(checked_inputs), 'network_used': False,
        'results': records, 'scope': 'Reproducción del cálculo y sus fotogramas; no validación independiente de todas las fuentes upstream.'}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'count': 40, 'byte_equal_after_LF_normalization': sum(x['byte_equal_after_LF_normalization'] for x in records),
        'maximum_numeric_difference': max(x['maximum_numeric_difference'] for x in records)}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('graficas', type=Path)
    parser.add_argument('informe', type=Path)
    args = parser.parse_args()
    verify(args.graficas, args.informe)
