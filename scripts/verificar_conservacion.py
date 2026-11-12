from pathlib import Path
import hashlib,json,re,subprocess,sys
repo=Path(sys.argv[1]).resolve()
baseline='8baa89bc7297cebdabff7196296ed4fb2704986f'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
paths=git('ls-tree','-r','--name-only',baseline,'Clases_Crecimiento_Economico').decode().splitlines()
# Git quotes non-ASCII paths unless core.quotepath=false; use NUL records instead.
paths=git('ls-tree','-rz','--name-only',baseline,'Clases_Crecimiento_Economico').decode().split('\0')
protected=[];sources=[]
for name in filter(None,paths):
    path=repo/name
    if path.suffix.lower() not in {'.png','.jpg','.jpeg','.html','.xlsx','.rmd'}:continue
    before=git('show',baseline+':'+name)
    after=path.read_bytes()
    if path.suffix.lower()=='.rmd':
        a=before.decode('utf-8-sig').replace('\r\n','\n');b=after.decode('utf-8-sig').replace('\r\n','\n')
        chunks_a=re.findall(r'```\{r[^\n]*\n.*?```',a,re.S)
        chunks_b=re.findall(r'```\{r[^\n]*\n.*?```',b,re.S)
        assert chunks_a==chunks_b,name
        sources.append({'source':name,'baseline_sha256':hashlib.sha256(before.replace(b'\r\n',b'\n')).hexdigest(),'final_sha256':hashlib.sha256(after.replace(b'\r\n',b'\n')).hexdigest(),'source_hash_line_endings':'LF','R_chunks':len(chunks_a),'R_chunks_preserved':True,'narrative_changed':a!=b})
    else:
        normalized=path.suffix.lower()=='.html'
        stored=after.replace(b'\r\n',b'\n') if normalized else after
        expected=before.replace(b'\r\n',b'\n') if normalized else before
        assert expected==stored,name
        protected.append({'path':name,'bytes':len(stored),'sha256':hashlib.sha256(stored).hexdigest(),'text_line_endings_normalized_to_LF':normalized})
report={'baseline':baseline,'protected_files':len(protected),'protected_bytes':sum(x['bytes'] for x in protected),'protected_formats':['historical HTML','PNG','JPG/JPEG','XLSX'],'protected_content_unchanged':True,'historical_HTML_line_endings_normalized_for_comparison':'LF; Windows Git worktree may use CRLF','Rmd_sources':len(sources),'R_chunks_preserved':sum(x['R_chunks'] for x in sources),'changed_Rmd_narratives':sum(x['narrative_changed'] for x in sources),'sources':sources,'protected':protected}
out=repo/'verificacion/estable_20261112/conservacion.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('sources','protected')},ensure_ascii=False))
