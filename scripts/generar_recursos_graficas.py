"""Regenera las vistas desde datos archivados, sin consultar servicios externos."""
import argparse,csv,hashlib,html,json,shutil
from pathlib import Path

CSS='''body{font:16px/1.5 system-ui,sans-serif;color:#172d46;background:#f5f7fa;margin:0}main{max-width:1180px;margin:auto;padding:28px}a{color:#075bb5}h1{line-height:1.2}.notice{background:#e8eef6;border-left:4px solid #31628f;padding:14px 18px}.warning{background:#fff2d4;border-left:4px solid #a65b00;padding:14px 18px}.plot{height:620px;background:white;margin-top:20px;border:1px solid #dce3eb}table{border-collapse:collapse;width:100%;background:white}th,td{padding:12px;text-align:left;border-bottom:1px solid #dce3eb;vertical-align:top}nav{margin:18px 0}button,input{font:inherit;padding:8px;margin:4px 8px 4px 0}details{margin:14px 0}code{overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}.scroll{overflow-x:auto}@media(max-width:700px){main{padding:15px}.plot{height:500px}th,td{padding:8px}}'''
def dump(value):return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))
def write(path,text):path.write_text(text,encoding='utf-8',newline='\n')
def text_title(layout):
    title=layout.get('title','Sin título');return title.get('text','Sin título') if isinstance(title,dict) else str(title)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def make_csv(path,data):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['traza','nombre','observacion','x_presente','y_presente','x','y'])
        for index,t in enumerate(data):
            xs=t.get('x',[]);ys=t.get('y',[])
            for i in range(max(len(xs),len(ys))):
                w.writerow([index,t.get('name',''),i,i<len(xs),i<len(ys),dump(xs[i]) if i<len(xs) else '',dump(ys[i]) if i<len(ys) else ''])
def generate(source,destination):
    source=source.resolve();destination=destination.resolve()
    if source==destination or source in destination.parents:raise ValueError('La salida debe estar fuera de la fuente.')
    destination.mkdir(parents=True,exist_ok=True)
    if any(destination.iterdir()):raise ValueError('La salida debe estar vacía.')
    catalog=json.loads((source/'catalogo.json').read_text(encoding='utf-8'))
    for directory in ['graficas','datos','assets','licencias']:(destination/directory).mkdir()
    for name in ['assets','licencias']:
        for p in (source/name).iterdir():shutil.copyfile(p,destination/name/p.name)
    write(destination/'assets/galeria.css',CSS+'\n')
    shutil.copyfile(source/'catalogo.json',destination/'catalogo.json')
    if (source/'matriz_identidades.json').exists():shutil.copyfile(source/'matriz_identidades.json',destination/'matriz_identidades.json')
    entries=[]
    for item in catalog['graficas']:
        slug=item['slug'];input_file=source/'datos'/f'{slug}.json'
        if sha(input_file)!=item['datos_sha256']:raise ValueError('Cambió el respaldo '+slug)
        raw=input_file.read_text(encoding='utf-8');spec=json.loads(raw)
        assert isinstance(spec['data'],list) and isinstance(spec['layout'],dict)
        title=text_title(spec['layout']);title_escaped=html.escape(title)
        shutil.copyfile(input_file,destination/'datos'/input_file.name)
        make_csv(destination/'datos'/f'{slug}.csv',spec['data'])
        frames=spec.get('frames') or []
        status='Objeto del curso recuperado; identificador Chart Studio sin determinar.' if item['tipo']=='objeto_local' else 'Material fuente archivado; correspondencia con los identificadores pendientes sin demostrar.'
        source_link=html.escape(item.get('url_fuente',''))
        attribution=html.escape(item['procedencia'])
        auxiliary_links=[]
        for aux in item.get('auxiliares',[]):
            shutil.copyfile(source/'datos'/aux,destination/'datos'/aux)
            auxiliary_links.append(f'<a href="../datos/{html.escape(aux)}" download>{html.escape(aux)}</a>')
        warning=''
        buttons=''
        if slug=='oecd-rd-logrd':
            warning='<p class="warning"><strong>Revisión de escala:</strong> el archivo conserva valores ya transformados a ln y además un eje logarítmico. La vista inicial reproduce esa configuración. El botón de eje lineal ofrece una adaptación explícita para leer los valores ln; los datos descargables permanecen intactos.</p>'
            buttons='<button id="eje-lineal" type="button">Leer ln con eje lineal</button><button id="eje-original" type="button">Restaurar eje archivado</button>'
        animation='<p>Animación archivada: '+str(len(frames))+' fotogramas. Use el control del gráfico o seleccione un fotograma.</p><label for="frame">Fotograma: </label><select id="frame"></select><button id="mostrar-frame" type="button">Mostrar fotograma</button>' if frames else ''
        data_json=raw.replace('</','<\\/')
        options=dump({'frames':len(frames),'slug':slug})
        script='''const spec=JSON.parse(document.getElementById('datos-grafica').textContent);const plot=document.getElementById('grafica');const opts=OPTIONS;const layout=JSON.parse(JSON.stringify(spec.layout));delete layout.width;delete layout.height;layout.autosize=true;
const config={responsive:true,displaylogo:false,showSendToCloud:false,modeBarButtonsToRemove:['sendDataToCloud','editInChartStudio']};
window.graficaLista=false;Plotly.newPlot(plot,spec.data,layout,config).then(async()=>{if(spec.frames&&spec.frames.length){await Plotly.addFrames(plot,spec.frames);const selector=document.getElementById('frame');spec.frames.forEach((f,i)=>{const option=document.createElement('option');option.value=String(f.name===undefined?i:f.name);option.textContent=f.name===undefined?'Fotograma '+i:String(f.name);selector.appendChild(option);});document.getElementById('mostrar-frame').onclick=async()=>{const f=spec.frames.find((f,i)=>String(f.name===undefined?i:f.name)===selector.value);await Plotly.animate(plot,[String(f.name)],{frame:{duration:0,redraw:true},transition:{duration:0},mode:'immediate'});window.ultimoFotograma=String(f.name);};}if(opts.slug==='oecd-rd-logrd'){document.getElementById('eje-lineal').onclick=()=>Plotly.relayout(plot,{'yaxis.type':'linear'});document.getElementById('eje-original').onclick=()=>Plotly.relayout(plot,{'yaxis.type':spec.layout.yaxis.type});}window.graficaLista=true;}).catch(e=>{document.getElementById('estado').textContent='Error al dibujar: '+e.message;window.errorGrafica=String(e);});'''.replace('OPTIONS',options)
        page=f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title_escaped}</title><link rel="stylesheet" href="../assets/galeria.css"><main><nav><a href="../index.html">← Índice de vistas locales</a></nav><h1>{title_escaped}</h1><p class="notice">{html.escape(status)} Se conservan los valores y las etiquetas del respaldo; su fecha de edición estadística debe comprobarse en la fuente.</p>{warning}<p>{attribution}</p><p>{('<a href="'+source_link+'">Fuente fijada en GitHub</a> · ') if source_link else ''}<a href="../datos/{slug}.json" download>JSON completo</a> · <a href="../datos/{slug}.csv" download>CSV de la vista inicial</a></p><p>El CSV conserva los arrays explícitos de la vista inicial; el JSON incluye todos los fotogramas. No se calculan ni completan valores ausentes.</p>{animation}{buttons}<div id="grafica" class="plot"></div><p id="estado">Vista local. Puede ampliar, consultar valores y ocultar series desde la leyenda.</p><details><summary>Procedencia y límites</summary><pre>{html.escape(json.dumps(item,ensure_ascii=False,indent=2))}</pre></details><script type="application/json" id="datos-grafica">{data_json}</script><script src="../assets/plotly.min.js"></script><script>{script}</script></main></html>\n'''
        if auxiliary_links:page=page.replace('<div id="grafica"', '<p>Archivo de origen: '+' · '.join(auxiliary_links)+'</p><div id="grafica"',1)
        write(destination/'graficas'/f'{slug}.html',page)
        entries.append({'slug':slug,'title':title,'tipo':item['tipo'],'traces':len(spec['data']),'frames':len(frames),'json_sha256':sha(input_file),'csv_sha256':sha(destination/'datos'/f'{slug}.csv')})
    rows='\n'.join(f'<tr><td><a href="graficas/{r["slug"]}.html">{html.escape(r["title"])}</a></td><td>{"Objeto local" if r["tipo"]=="objeto_local" else "Fuente StudyGuide"}</td><td>{r["traces"]}</td><td>{r["frames"]}</td><td>{"Revisar escala" if r["slug"]=="oecd-rd-logrd" else "Valores archivados"}</td></tr>' for r in entries)
    index=f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vistas locales de apoyo — Crecimiento</title><link rel="stylesheet" href="assets/galeria.css"><main><h1>Vistas locales de apoyo a las gráficas pendientes</h1><p class="notice">{len(entries)} vistas con datos archivados. Las 40 identidades Chart Studio siguen sin autenticarse: estos materiales ofrecen alternativas temáticas y un objeto del curso recuperado. No se asignan por semejanza ni se actualizan las cifras.</p><p>Conserve esta carpeta completa. Las vistas funcionan sin conexión; los enlaces de procedencia llevan a fuentes externas. Las etiquetas originales se mantienen para cotejo.</p><nav><a href="../PENDIENTES_GRAFICAS_Y_PWT.md">Informe y matriz de los 40 identificadores</a> · <a href="catalogo.json">Catálogo verificable</a></nav><label for="buscar">Buscar título:</label><input id="buscar" type="search" placeholder="China, productividad, energía…"><div class="scroll"><table><thead><tr><th>Vista</th><th>Origen</th><th>Series</th><th>Fotogramas</th><th>Estado</th></tr></thead><tbody>{rows}</tbody></table></div><script>document.getElementById('buscar').addEventListener('input',e=>{{const q=e.target.value.toLocaleLowerCase();document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!r.textContent.toLocaleLowerCase().includes(q));}});</script></main></html>\n'''
    index=index.replace('../PENDIENTES_GRAFICAS_Y_PWT.md','README.md')
    write(destination/'index.html',index)
    readme=f'''# Vistas locales de apoyo a Crecimiento
\nAbrir [index.html](index.html) desde una copia local de esta carpeta. Conservar `assets`, `datos`, `graficas` y `licencias` juntos. Las {len(entries)} vistas funcionan sin conexión; los enlaces de procedencia abren fuentes externas. GitHub muestra el código HTML: para interactuar hay que descargar o clonar el repositorio y abrir el archivo local.
\nSe incluyen 43 widgets archivados de StudyGuide y una reconstrucción del objeto `fig` del curso con 265 pares, nueve países y obsTime 1981–2019. No se ha autenticado ninguno de los 40 identificadores Chart Studio pendientes. La [matriz](matriz_identidades.json) ofrece alternativas temáticas y sus límites; no establece identidades por parecido.
\nSe conservan los datos, etiquetas y fotogramas. La adaptación ajusta el tamaño al navegador y usa Plotly.js 2.11.1 local. Las animaciones conservan 250, 30, 7 y 7 fotogramas. Los CSV contienen la vista inicial; los JSON conservan las animaciones completas. No se rellenan faltantes.
\n`oecd-rd-logrd` conserva valores en ln junto con un eje logarítmico. La vista advierte esa configuración y permite cambiar explícitamente a eje lineal para leer los valores ln; restaurar la escala no modifica las descargas originales.
\nProcedencia: Dietz Vollrath, StudyGuide, commit `3a8c79f20022ef7b985b392d73921839a4317883`, [licencia MIT original](licencias/LICENSE-StudyGuide). Plotly.js: [licencia MIT](licencias/LICENSE-Plotly.js). Los metadatos estadísticos son los disponibles en cada respaldo; el código actual del curso puede usar una edición diferente. No se actualizan cifras ni se replican todos los cálculos económicos.
\n[Informe de seguimiento](https://github.com/iguzmanvt/Crecimiento/blob/main/PENDIENTES_GRAFICAS_Y_PWT.md). [Catálogo y huellas](catalogo.json). Para regenerar en una salida vacía externa: `python scripts/generar_recursos_graficas.py recursos_graficas /ruta/externa/vacia`.
'''
    write(destination/'README.md',readme)
    write(destination/'.gitattributes','* text eol=lf\n')
    write(destination/'.gitignore','# Vistas reproducibles incluidas con sus datos y recursos.\n!index.html\n!graficas/\n!graficas/*.html\n')
    write(destination/'generacion.json',json.dumps({'graficas':entries,'count':len(entries),'plotly_sha256':sha(destination/'assets/plotly.min.js'),'network_used':False},ensure_ascii=False,indent=2)+'\n')
    return entries
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('fuente',type=Path);p.add_argument('salida',type=Path);a=p.parse_args()
    result=generate(a.fuente,a.salida);print(json.dumps({'vistas':len(result),'animadas':sum(bool(r['frames']) for r in result)}))
