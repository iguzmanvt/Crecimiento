"""Reconstruye 17 destinos Chart Studio de Introducción con insumos archivados.

Uso: python scripts/generar_introduccion_chartstudio.py [--output RUTA]
Sin red. La exportación PNG/SVG se hace con --export (requiere Playwright/Chromium).
Se preservan las fuentes y no se atribuye identidad con los originales desaparecidos.
"""
from pathlib import Path
import argparse, csv, hashlib, html, importlib.util, json, math, shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'introduccion_local/chartstudio/fuentes'
GROUP1=['AUS','CAN','GBR','MEX','USA']
GROUP2=['CHN','DEU','JPN','KOR','NGA','USA']
NAMES={'AUS':'Australia','CAN':'Canadá','GBR':'Reino Unido','MEX':'México','USA':'Estados Unidos','CHN':'China','DEU':'Alemania','JPN':'Japón','KOR':'Corea del Sur','NGA':'Nigeria','IND':'India'}
COLORS=['#2171b5','#e6550d','#238b45','#756bb1','#cb181d','#636363']
COMMON_LIMIT='Sustitución docente por correspondencia temática. No se autentica la identidad numérica o visual del objeto Chart Studio desaparecido.'
PWT_URL='https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100?lang=en'
PWT_NA='https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt1001?lang=en'
STUDY='https://github.com/dvollrath/StudyGuide/tree/3a8c79f20022ef7b985b392d73921839a4317883'


def dump(v,pretty=False):return json.dumps(v,ensure_ascii=False,allow_nan=False,indent=2 if pretty else None,separators=None if pretty else (',',':'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(v,encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def val(r,k):
 try:
  x=float(r[k]);return x if math.isfinite(x) else None
 except (ValueError,TypeError,KeyError):return None


def trace(name,x,y,i=0,mode='lines',text=None):
 t={'name':name,'type':'scatter','mode':mode,'x':x,'y':y,'line':{'color':COLORS[i%len(COLORS)],'width':2.2},'marker':{'color':COLORS[i%len(COLORS)],'size':5},'connectgaps':False}
 if text is not None:t['text']=text
 return t


def layout(title,ytitle,xtitle='Año',percent=False,source='PWT 10.0; cálculos propios'):
 out={'title':{'text':title,'x':0.025,'xanchor':'left','font':{'size':22}},'paper_bgcolor':'white','plot_bgcolor':'white','font':{'family':'Arial, sans-serif','size':15,'color':'#243746'},'margin':{'l':95,'r':30,'t':85,'b':145},'xaxis':{'title':{'text':xtitle},'showline':True,'linecolor':'#bac7d1','gridcolor':'#e5ebf0','zeroline':False,'automargin':True},'yaxis':{'title':{'text':ytitle},'showline':True,'linecolor':'#bac7d1','gridcolor':'#e5ebf0','zerolinecolor':'#b6c3cc','automargin':True},'legend':{'orientation':'h','x':0,'y':-0.19,'font':{'size':12}},'hovermode':'x unified','annotations':[{'text':'Fuente: '+source,'xref':'paper','yref':'paper','x':0,'y':-0.28,'xanchor':'left','showarrow':False,'font':{'size':11,'color':'#52616b'}}]}
 if percent:out['yaxis']['tickformat']='.0%'
 return out


def build_specs():
 pwt=rows(SOURCE/'pwt100_seleccion.csv');na=rows(SOURCE/'data/pwt1001_na_data.csv');school=rows(SOURCE/'data/pwt1001_labor_detail.csv');mad=rows(SOURCE/'maddison2010_regiones.csv')
 known=json.loads((SOURCE/'insumos.json').read_text(encoding='utf-8'))
 for path,h in known['inputs_sha256'].items():assert sha(SOURCE/path)==h,path
 schooling=json.loads((SOURCE/'manifest_escolaridad.json').read_text(encoding='utf-8'))
 for entry in schooling['files']:assert sha(SOURCE/entry['path'])==entry['sha256'],entry['path']
 entries=[];specs={};details={}
 def add(ident,title,spec,units,period,formula,inputs,kind='Cálculo con datos publicados',limits=(),urls=(PWT_URL,),vintage='PWT 10.0, revisión de junio de 2021; datos 1950–2019; selección del Excel oficial conservado.'):
  slug='iguzmanvt-'+str(ident);specs[slug]=spec
  entries.append({'identity':'iguzmanvt:'+str(ident),'slug':slug,'original_url':'https://plotly.com/~iguzmanvt/'+str(ident)+'.embed','title':title,'module':'Introduction','units':units,'period':period,'formula':formula,'kind':kind,'source_urls':list(urls),'source_vintage':vintage,'captured_on':'2026-11-12','historical_identity_authenticated':False,'limitations':[COMMON_LIMIT,*limits],'input_base':'fuentes','input_paths':inputs,'local_inputs':{path:sha(SOURCE/path) for path in inputs},'generator':'scripts/generar_introduccion_chartstudio.py','spec_path':'datos/'+slug+'.json'})
 def lines(group,records,value,minyear=1950):
  out=[]
  for i,country in enumerate(group):
   selected=sorted([r for r in records if r.get('countrycode')==country and int(r['year'])>=minyear],key=lambda r:int(r['year']))
   x=[];y=[]
   for row in selected:
    z=value(row)
    if z is not None:x.append(int(row['year']));y.append(z)
   assert x,country
   out.append(trace(NAMES[country],x,y,i))
  return out
 def logpc(r):
  y,p=val(r,'rgdpna'),val(r,'pop')
  return math.log(y/p) if y and p and y>0 and p>0 else None
 def ky(r):
  k,y=val(r,'rnna'),val(r,'rgdpna')
  return k/y if k is not None and y and y>0 else None
 def phi(r):
  l,y,k=val(r,'labsh'),val(r,'rgdpna'),val(r,'rnna')
  return l*y/(l*y+.05*k) if None not in (l,y,k) and l*y+.05*k>0 else None
 def ratio(r,a,b):
  x,y=val(r,a),val(r,b)
  return x/y if x is not None and y and y>0 else None
 groups_note='Grupo 1: Australia, Canadá, Reino Unido, México y Estados Unidos. Grupo 2: China, Alemania, Japón, Corea del Sur, Nigeria y Estados Unidos. Son muestras docentes del código conservado, no clasificaciones de desarrollo.'
 for ident,g,title in [(150,GROUP1,'PIB per cápita: trayectorias del grupo 1'),(152,GROUP2,'PIB per cápita: trayectorias del grupo 2')]:
  spec={'data':lines(g,pwt,logpc),'layout':layout(title,'Ln del PIB per cápita (US$ de 2017)'),'frames':[]}
  add(ident,title,spec,'Logaritmo natural de US$ de 2017 a precios nacionales constantes',[1950,2019],'ln(rgdpna/pop). Las dos variables están en millones, que se cancelan; cálculo sin redondeo previo.',['pwt100_seleccion.csv'],limits=(groups_note,'Una línea aproximadamente recta en logaritmos sugiere crecimiento proporcional relativamente estable, sin excluir ciclos ni cambios de tendencia.'))
 by={}
 for r in mad:by.setdefault(r['region'],[]).append(r)
 title='PIB por habitante de regiones históricas, 1820–2008';data=[]
 for i,(region,rr) in enumerate(by.items()):
  rr=sorted([r for r in rr if val(r,'gdppc') and val(r,'gdppc')>0],key=lambda r:int(r['year']))
  data.append(trace(rr[0]['label'],[int(r['year']) for r in rr],[math.log(float(r['gdppc'])) for r in rr],i,'lines+markers'))
 add(66,title,{'data':data,'layout':layout(title,'Ln del PIB por habitante (dólares GK de 1990)',source='Maddison, edición 2010; cálculos propios'),'frames':[]},'Logaritmo natural de dólares internacionales Geary-Khamis de 1990',[1820,2008],'ln(gdppc) de agregados regionales archivados de la hoja PerCapita GDP; no se interpolan ausencias.',['maddison2010_regiones.csv','data/md2010_horizontal.xlsx'],urls=('https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/md2010_horizontal.xlsx',),vintage='Maddison Database 2010, consulta 12 de noviembre de 2026.',limits=('Los agregados y fronteras son los de la edición 2010. Esta escala de precios no se combina con PWT 2017.','Los huecos temporales se conservan como observaciones disponibles; los segmentos son guía visual.'))
 title='Ingreso inicial y crecimiento posterior: muestra de países';data=[]
 for i,c in enumerate(GROUP2):
  rr={int(r['year']):r for r in pwt if r['countrycode']==c};x=[];y=[];text=[]
  for yr in sorted(rr):
   if yr-10 in rr and logpc(rr[yr]) is not None and logpc(rr[yr-10]) is not None:
    x.append(logpc(rr[yr-10]));y.append((logpc(rr[yr])-logpc(rr[yr-10]))/10);text.append(str(yr-10)+'–'+str(yr))
  data.append(trace(NAMES[c],x,y,i,'markers',text))
 ll=layout(title,'Variación anual media de ln(PIB pc), 10 años','Ln del PIB per cápita al inicio',True);ll['hovermode']='closest'
 add(154,title,{'data':data,'layout':ll,'frames':[]},'Eje x: ln(US$ de 2017 por persona); eje y: variación logarítmica anual',[1950,2019],'x=ln(PIBpc[t−10]); y=(ln(PIBpc[t])−ln(PIBpc[t−10]))/10. Ventanas móviles por país y calendario exacto.',['pwt100_seleccion.csv'],limits=(groups_note,'Correlación descriptiva en una muestra seleccionada. No prueba convergencia mundial incondicional ni efecto causal.'))
 for ident,g,a,title in [(170,GROUP1,'v_c','Consumo privado como proporción del PIB: grupo 1'),(172,GROUP2,'v_c','Consumo privado como proporción del PIB: grupo 2'),(174,GROUP1,'v_i','Formación bruta de capital como proporción del PIB: grupo 1'),(176,GROUP2,'v_i','Formación bruta de capital como proporción del PIB: grupo 2')]:
  data=lines(g,na,lambda r:ratio(r,a,'v_gdp'));ys=[y for t in data for y in t['x']]
  add(ident,title,{'data':data,'layout':layout(title,('Consumo privado / PIB' if a=='v_c' else 'Formación bruta de capital / PIB'),percent=True,source='Cuentas nacionales PWT 10.01; cálculos propios'),'frames':[]},'Proporción a precios nacionales corrientes',[min(ys),max(ys)],a+'/v_gdp, sin redondeo previo, con numerador y denominador en la misma moneda y precios corrientes.',['data/pwt1001_na_data.csv'],urls=(PWT_NA,STUDY),vintage='Archivo de cuentas nacionales PWT 10.01 conservado por StudyGuide en commit 3a8c79f (2024); captura 12 de noviembre de 2026.',limits=(groups_note,'v_i incluye la formación bruta de capital total, incluidas existencias. No se identifica con formación bruta de capital fijo.','Las series nacionales no se fuerzan a los intervalos narrativos de los originales. Las observaciones ausentes se omiten.'))
 for ident,g,fun,title,unit,formula,lim in [(202,GROUP1,lambda r:val(r,'labsh'),'Participación laboral en el PIB: grupo 1','Proporción del PIB a precios nacionales corrientes','labsh, sin transformación.','Los tramos constantes pueden provenir de extrapolación o supuestos de PWT, no de observaciones anuales idénticas.'),(205,GROUP2,lambda r:val(r,'labsh'),'Participación laboral en el PIB: grupo 2','Proporción del PIB a precios nacionales corrientes','labsh, sin transformación.','Los tramos constantes pueden provenir de extrapolación o supuestos de PWT, no de observaciones anuales idénticas.'),(207,GROUP1,phi,'Participación laboral en costos: aproximación del grupo 1','Proporción calculada con rendimiento supuesto de 5%','phi_L=(labsh×rgdpna)/(labsh×rgdpna+0.05×rnna).','Aproximación del código docente: supone rendimiento del capital de 5% en todo país y año y combina labsh corriente con magnitudes a precios nacionales constantes. No es una participación de costos observada ni identifica beneficios.'),(209,GROUP2,phi,'Participación laboral en costos: aproximación del grupo 2','Proporción calculada con rendimiento supuesto de 5%','phi_L=(labsh×rgdpna)/(labsh×rgdpna+0.05×rnna).','Aproximación del código docente: supone rendimiento del capital de 5% en todo país y año y combina labsh corriente con magnitudes a precios nacionales constantes. No es una participación de costos observada ni identifica beneficios.'),(156,GROUP1,ky,'Relación capital/producto: grupo 1','Stock de capital / PIB anual (años de producto)','rnna/rgdpna; ambas magnitudes a precios nacionales constantes de 2017.','Cociente de stock y flujo, no tasa de inversión. Se omiten 1950–1959 para reducir la influencia de la inicialización del capital.'),(158,GROUP2,ky,'Relación capital/producto: grupo 2','Stock de capital / PIB anual (años de producto)','rnna/rgdpna; ambas magnitudes a precios nacionales constantes de 2017.','Cociente de stock y flujo, no tasa de inversión. Se omiten 1950–1959 para reducir la influencia de la inicialización del capital.')]:
  data=lines(g,pwt,fun,1960 if ident in (156,158) else 1950)
  percent=ident not in (156,158)
  add(ident,title,{'data':data,'layout':layout(title,'Capital / PIB anual' if not percent else ('W / (W + 0.05 K)' if ident in (207,209) else 'Compensación laboral / PIB'),percent=percent),'frames':[]},unit,[1960 if ident in (156,158) else 1950,2019],formula,['pwt100_seleccion.csv'],kind='Aproximación con supuesto' if ident in (207,209) else 'Cálculo con datos publicados',limits=(groups_note,lim))
 # A distribution across country means, not a distribution of individuals.
 selected=sorted([{'countrycode':r['countrycode'],'year':2010,'years_schooling':val(r,'yr_sch'),'source':r.get('source','')} for r in school if r['year']=='2010' and val(r,'yr_sch') is not None],key=lambda r:r['countrycode'])
 assert len(selected)==150 and len({r['countrycode'] for r in selected})==150
 boundaries=list(range(0,17,2));counts=[];labels=[]
 for a,b in zip(boundaries,boundaries[1:]):
  counts.append(sum(a<=r['years_schooling']<b for r in selected));labels.append(str(a)+' a <'+str(b))
 assert sum(counts)==len(selected)
 title='Distribución entre países del promedio de escolaridad, 2010'
 data=[{'type':'bar','name':'Países','x':labels,'y':counts,'marker':{'color':'#2171b5'},'hovertemplate':'Promedio: %{x} años<br>%{y} países<extra></extra>'}]
 spec={'data':data,'layout':layout(title,'Número de países','Años medios de escolaridad',source='PWT 10.01, detalle laboral; cálculo propio (150 países)'),'frames':[]}
 add(168,title,spec,'Países por intervalo de 2 años de escolaridad media',[2010,2010],'Se agrupan los 150 promedios nacionales yr_sch disponibles en 2010 en intervalos [0,2), [2,4), …, [14,16). Cada país recibe el mismo peso.',['data/pwt1001_labor_detail.csv','manifest_escolaridad.json'],urls=(PWT_NA,'https://www.rug.nl/ggdc/docs/pwt100-user-guide-to-data-files.pdf',STUDY),vintage='PWT 10.01, detalle laboral archivado en StudyGuide commit 3a8c79f; consulta 12 de noviembre de 2026.',limits=('La distribución compara promedios de países: no es una distribución de escolaridad entre personas ni usa ponderaciones de población.','yr_sch mide años medios de escolaridad, no el índice hc. PWT combina series de Barro-Lee y Cohen-Soto-Leker; se conserva el indicador de fuente por país.'))
 details['iguzmanvt-168_paises.csv']=selected
 # Preserve the two reconstructions already recalculated in the first delivery.
 origins=json.loads((SOURCE/'reconstrucciones_locales/catalogo_origen.json').read_text(encoding='utf-8'))['entries']
 for ident in (118,160):
  slug='iguzmanvt-'+str(ident);origin=next(e for e in origins if e['slug']==slug);spec=json.loads((SOURCE/'reconstrucciones_locales'/f'{slug}.json').read_text(encoding='utf-8'))
  title=origin['title'];add(ident,title,spec,origin['units'],origin['period'],origin.get('formula',''),['reconstrucciones_locales/'+slug+'.json','reconstrucciones_locales/catalogo_origen.json'],kind='Reutilización de reconstrucción verificada',limits=tuple(origin['limitations']),urls=tuple(origin['source_urls']),vintage=origin['source_vintage'])
  entries[-1]['reused_from']='graficas_reconstruidas/datos/'+slug+'.json';entries[-1]['origin_input_hashes']=origin.get('local_inputs',{})
  if ident==160:entries[-1]['limitations'].append('La relación representada es inversión y nivel del PIB per cápita. No es una regresión causal sobre la tasa de crecimiento.')
  if ident==118:entries[-1]['limitations'].append('El cambio de investigadores emplea un rezago de diez observaciones dividido entre diez, que puede abarcar más de diez años cuando hay huecos. El eje lo indica.')
 assert len(entries)==17 and len({r['identity'] for r in entries})==17
 return entries,specs,details


def generate(output):
 output=output.resolve();output.mkdir(parents=True,exist_ok=True)
 module_spec=importlib.util.spec_from_file_location('growth_style',ROOT/'scripts/generar_graficas_reconstruidas.py');module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
 for name in ('datos','graficas','imagenes','assets'):(output/name).mkdir(exist_ok=True)
 write(output/'assets/clase.css',module.CSS+'\n');write(output/'assets/clase.js',module.JS+'\n')
 shutil.copyfile(ROOT/'graficas_reconstruidas/assets/plotly.min.js',output/'assets/plotly.min.js')
 entries,specs,details=build_specs()
 for entry in entries:
  slug=entry['slug'];spec=specs[slug];raw=dump(spec)
  write(output/'datos'/f'{slug}.json',raw+'\n');module.csv_export(output/'datos'/f'{slug}.csv',spec);entry['spec_sha256']=sha(output/'datos'/f'{slug}.json');entry['csv_sha256']=sha(output/'datos'/f'{slug}.csv')
  entry['traces']=len(spec['data']);entry['frames']=len(spec.get('frames',[]));entry['points_initial']=sum(len(t['x']) for t in spec['data'])
  sources=' · '.join('<a href="'+html.escape(u,quote=True)+'">Fuente '+str(i+1)+'</a>' for i,u in enumerate(entry['source_urls']))
  frames=spec.get('frames',[])
  animation='<div class="animation"><button type="button" id="reproducir">Reproducir</button><button type="button" id="pausar">Pausar</button><label for="fotograma">Fotograma: </label><select id="fotograma"></select><button type="button" id="mostrar">Mostrar</button></div>' if frames else ''
  escaped=raw.replace('</','<\\/')
  page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(entry['title'])}</title><link rel="stylesheet" href="../assets/clase.css"></head><body data-slug="{slug}"><main><div class="full-only"><nav><a href="../index.html">Gráficas de Introducción</a></nav><h1>{html.escape(entry['title'])}</h1><p class="note">Reconstrucción docente. {html.escape(COMMON_LIMIT)}</p><p><strong>Periodo:</strong> {html.escape(str(entry['period']))}. <strong>Unidades:</strong> {html.escape(entry['units'])}.</p><p><strong>Edición:</strong> {html.escape(entry['source_vintage'])}.</p></div>{animation}<div id="grafica" class="plot" role="img" aria-label="{html.escape(entry['title'],quote=True)}"></div><p class="embed-only">Introducción · datos, fuentes y método en la vista completa.</p><div class="full-only"><p id="estado">Consulte valores, amplíe la figura y seleccione series desde la leyenda.</p><p><a href="../datos/{slug}.csv" download>Datos CSV</a> · <a href="../datos/{slug}.json" download>Datos y fotogramas JSON</a> · <a href="../imagenes/{slug}.svg" download>Imagen SVG</a> · <a href="../imagenes/{slug}.png" download>Imagen PNG</a></p><p><strong>Método:</strong> {html.escape(entry['formula'])}</p><p><strong>Alcance:</strong> {html.escape(' '.join(entry['limitations']))}</p><p>{sources}</p><details><summary>Procedencia y reproducción</summary><pre>{html.escape(dump(entry,True))}</pre></details></div><script id="spec" type="application/json">{escaped}</script><script src="../assets/plotly.min.js"></script><script src="../assets/clase.js"></script></main></body></html>\n'''
  write(output/'graficas'/f'{slug}.html',page)
 for name,records in details.items():
  with (output/'datos'/name).open('w',encoding='utf-8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(records[0]),lineterminator='\n');w.writeheader();w.writerows(records)
 catalog={'schema_version':1,'date':'2026-11-12','originals_authenticated':0,'functional_reconstructions':17,'entries':entries}
 write(output/'catalogo.json',dump(catalog,True)+'\n')
 table='\n'.join(f'<tr><td><a href="graficas/{e["slug"]}.html">{html.escape(e["title"])}</a></td><td>{html.escape(str(e["period"]))}</td><td>{html.escape(e["kind"])}</td></tr>' for e in entries)
 write(output/'index.html',f'<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Figuras de Introducción</title><link rel="stylesheet" href="assets/clase.css"><main><h1>Figuras de Introducción</h1><p>17 sustituciones locales de destinos Chart Studio. Cada vista incluye datos, fuentes, unidades y método. No se autentican los objetos originales desaparecidos.</p><p><a href="README.md">Método y límites</a> · <a href="catalogo.json">Catálogo</a></p><table><thead><tr><th>Figura</th><th>Periodo</th><th>Elaboración</th></tr></thead><tbody>{table}</tbody></table></main></html>\n')
 md=['# Figuras de Introducción procedentes de Chart Studio','','Las 17 vistas sustituyen funcionalmente los destinos externos de Introducción. Abrir `index.html` conservando la carpeta. Se usan datos, código docente archivado y dos reconstrucciones comprobadas. No se autentica ninguno de los originales desaparecidos.','','La generación no requiere red ni bibliotecas adicionales de Python:','','```sh','python scripts/generar_introduccion_chartstudio.py','```','','Las exportaciones se crean con `--export`, Playwright y Chromium. `--output` permite repetir la generación en una carpeta separada. CSV y JSON representan la vista inicial y todos los fotogramas, respectivamente. `iguzmanvt-168_paises.csv` conserva los 150 promedios nacionales que se agrupan en la figura de escolaridad.','','Las muestras del código archivado se llaman grupo 1 y grupo 2 porque no constituyen clasificaciones homogéneas de desarrollo. Las razones de consumo e inversión se calculan a precios nacionales corrientes. Las razones capital/producto utilizan `rnna/rgdpna` a precios nacionales constantes. `W/(W+0.05K)` es una aproximación con rendimiento de capital supuesto de 5%, no una participación de costos observada.','','| Destino histórico | Sustitución | Método y límite principal |','| --- | --- | --- |']
 for e in entries:md.append(f'| {e["identity"]} | [{e["title"]}](graficas/{e["slug"]}.html) | {e["formula"]} |')
 md.extend(['','Fuentes archivadas en `fuentes/`, con URL y SHA-256 en sus manifiestos. Para PWT se reconoce a Feenstra, Inklaar y Timmer (2015), *The Next Generation of the Penn World Table*, American Economic Review 105(10), 3150–3182. PWT 10.0 y 10.01 se distribuyen bajo CC BY 4.0. El código de StudyGuide conserva su licencia MIT. Maddison 2010 se identifica por su edición y sus dólares internacionales Geary-Khamis de 1990.',''])
 write(output/'README.md','\n'.join(md))
 return catalog


def export_images(output,catalog):
 from playwright.sync_api import sync_playwright
 import base64
 records=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  context=browser.new_context(viewport={'width':1280,'height':900},device_scale_factor=1)
  context.route('**/*',lambda route:route.abort() if route.request.url.startswith(('http:','https:')) else route.continue_())
  page=context.new_page()
  for e in catalog['entries']:
   errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
   slug=e['slug'];page.goto((output/'graficas'/f'{slug}.html').as_uri());page.wait_for_function('window.graficaLista === true',timeout=45000)
   assert not page.evaluate('window.errorGrafica || null'),slug
   assert page.locator('.js-plotly-plot').count()==1,slug
   for ext in ('png','svg'):
    uri=page.evaluate('(format)=>window.exportarGrafica(format)',ext);encoded=uri.split(',',1)[1]
    raw=base64.b64decode(encoded) if ';base64,' in uri else __import__('urllib.parse',fromlist=['unquote_to_bytes']).unquote_to_bytes(encoded)
    (output/'imagenes'/f'{slug}.{ext}').write_bytes(raw)
   if e['frames']:
    page.select_option('#fotograma',index=e['frames']-1);page.click('#mostrar');page.wait_for_function('window.ultimoFotograma !== undefined')
   assert not errors,(slug,errors)
   records.append({'slug':slug,'traces':e['traces'],'frames':e['frames'],'png_sha256':sha(output/'imagenes'/f'{slug}.png'),'svg_sha256':sha(output/'imagenes'/f'{slug}.svg'),'network_blocked':True})
  browser.close()
 write(output/'verificacion_navegador.json',dump({'date':'2026-11-12','count':len(records),'environment':'Windows, Chromium Playwright, file://, solicitudes HTTP(S) bloqueadas','records':records},True)+'\n')


if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'introduccion_local/chartstudio');parser.add_argument('--export',action='store_true');args=parser.parse_args()
 cat=generate(args.output)
 if args.export:export_images(args.output.resolve(),cat)
 print(dump({'count':len(cat['entries']),'output':str(args.output),'exported':args.export}))
