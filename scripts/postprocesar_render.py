"""Copia recursos compartidos y adapta las rutas de renders externos del curso.

Uso desde R: python scripts/postprocesar_render.py REPO SALIDA --prepare
             python scripts/postprocesar_render.py REPO SALIDA --html ARCHIVO
Conserva los archivos históricos. No descarga recursos ni modifica fuentes Rmd.
"""
from pathlib import Path
import argparse, html, json, os, re, shutil, subprocess, sys
from urllib.parse import urlsplit, unquote

FOLDERS=('introduccion_local','recursos_esenciales','graficas_reconstruidas','recursos_graficas','vendor/mathjax')
SHARED_NAMES=('introduccion_local','recursos_esenciales','graficas_reconstruidas','recursos_graficas','vendor/mathjax')
ATTRIBUTE=re.compile(r'''(?P<before>\b(?:src|href)\s*=\s*)(?P<quote>["'])(?P<url>.*?)(?P=quote)''',re.I|re.S)


def outside(path,repo):
    path=path.resolve();repo=repo.resolve()
    if path==repo or repo in path.parents:raise ValueError('La salida debe estar fuera del repositorio.')
    return path


def prepare(repo,out):
    out.mkdir(parents=True,exist_ok=True)
    for name in FOLDERS:
        source=repo/name;destination=out/name
        if not source.is_dir():raise ValueError('Falta el recurso compartido: '+name)
        if destination.exists():raise ValueError('La carpeta de recurso ya existe: '+str(destination))
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree(source,destination)
    return {'shared_folders':list(FOLDERS),'copied':True}


def postprocess(repo,out,path):
    path=path.resolve()
    if out not in path.parents or not path.is_file():raise ValueError('El HTML debe pertenecer a la carpeta externa de salida.')
    text=path.read_text(encoding='utf-8');changes=[]
    def replace(match):
        url=html.unescape(match['url']);split=urlsplit(url)
        if split.scheme or split.netloc or not split.path:return match.group(0)
        decoded=unquote(split.path).replace('\\','/')
        normalized=re.sub(r'^(?:\./|\.\./)+','',decoded)
        shared=next((name for name in SHARED_NAMES if normalized==name or normalized.startswith(name+'/')),None)
        if shared is None:return match.group(0)
        target=out/normalized
        if not target.exists():raise ValueError('Recurso local ausente en salida: '+normalized)
        adjusted=os.path.relpath(target,path.parent).replace('\\','/')
        if split.query:adjusted+='?'+split.query
        if split.fragment:adjusted+='#'+split.fragment
        if adjusted!=url:changes.append({'before':url,'after':adjusted})
        return match['before']+match['quote']+html.escape(adjusted,quote=True)+match['quote']
    rewritten=ATTRIBUTE.sub(replace,text)
    path.write_text(rewritten,encoding='utf-8',newline='\n')
    command=[sys.executable,str(repo/'scripts/localizar_formulas.py'),str(repo),'--vendor-dir',str(out/'vendor/mathjax'),'--html',str(path),'--report',str(path.parent/'formulas_locales.json')]
    subprocess.run(command,check=True)
    return {'html':path.relative_to(out).as_posix(),'shared_paths_changed':len(changes),'mathjax_local':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('repo',type=Path);parser.add_argument('out',type=Path);parser.add_argument('--prepare',action='store_true');parser.add_argument('--html',type=Path,action='append',default=[]);args=parser.parse_args()
    repo=args.repo.resolve();out=outside(args.out,repo)
    if not args.prepare and not args.html:parser.error('Indicar --prepare o --html.')
    if args.prepare:print(json.dumps(prepare(repo,out),ensure_ascii=False))
    for path in args.html:print(json.dumps(postprocess(repo,out,path),ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:print('ERROR:',str(error),file=sys.stderr);raise SystemExit(1)
