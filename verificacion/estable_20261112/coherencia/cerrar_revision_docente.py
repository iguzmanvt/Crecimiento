from pathlib import Path
import argparse, json,subprocess,re,hashlib,difflib,shutil
ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);args=ap.parse_args();root=Path(args.repo)
out=root/'verificacion/estable_20261112/coherencia'
a=json.loads((out/'parches.json').read_text(encoding='utf-8'))['files'];b=json.loads((out/'parches_adicionales.json').read_text(encoding='utf-8'))
paths=sorted({x['path'] for x in a+b});manifest=[]
for rel in paths:
 p=root/rel;s=p.read_text(encoding='utf-8-sig');base=subprocess.check_output(['git','show',f'8baa89bc7297cebdabff7196296ed4fb2704986f:{rel}'],cwd=root).decode('utf-8-sig')
 olds=base.splitlines(keepends=True);news=s.splitlines(keepends=True);codes=difflib.SequenceMatcher(a=olds,b=news).get_opcodes();indexes=set()
 for tag,i,j,k,l in codes:
  if tag in ('insert','replace'):indexes.update(range(k,l))
 inside=False
 for i,line in enumerate(news):
  if line.startswith('```'):inside=not inside
  if i in indexes and not inside:news[i]=line.rstrip()+'\n'
 final=''.join(news)
 assert re.findall(r'```\{r.*?```',s,re.S)==re.findall(r'```\{r.*?```',final,re.S)
 p.write_text(final,encoding='utf-8',newline='\n')
 manifest.append({'path':rel,'baseline_sha256':hashlib.sha256(base.encode()).hexdigest(),'final_sha256':hashlib.sha256(final.encode()).hexdigest(),'R_chunks_preserved_from_baseline':re.findall(r'```\{r.*?```',base,re.S)==re.findall(r'```\{r.*?```',final,re.S)})
assert all(x['R_chunks_preserved_from_baseline'] for x in manifest)
(out/'fuentes_finales.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ('aplicar_revision_docente.py','completar_revision_docente.py','cerrar_revision_docente.py'):
 p=Path(__file__).parent/name
 if p.exists():shutil.copy2(p,out/name)
# Prueba de dirección del efecto mecánico del peso laboral sobre el residuo.
j=json.loads((out/'formulas.json').read_text(encoding='utf-8'))
for gk,gl in ((.04,.01),(.01,.04)):
 residual=lambda sl:.03-(1-sl)*gk-sl*gl
 actual=(residual(.61)-residual(.6))/.01;expected=gk-gl
 assert abs(actual-expected)<1e-12
 j['checks'].append({'check':f'Derivada residuo sL, gK={gk},gL={gl}','passed':True,'actual':actual,'expected':expected})
(out/'formulas.json').write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources':len(paths),'modules':sorted({p.split('/')[1] for p in paths}),'R_chunks_preserved':True,'numerical_checks':len(j['checks'])},ensure_ascii=True))
