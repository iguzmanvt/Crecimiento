#!/usr/bin/env python3
"""Genera 21 vistas esenciales desde insumos archivados, sin red.
Uso: python scripts/generar_recursos_esenciales.py [RAIZ] [--export] [--chrome RUTA]
La exportación requiere Playwright y Chrome. Generación: biblioteca estándar.
"""
from pathlib import Path
from collections import defaultdict
import argparse, csv, hashlib, html, json, math, shutil, sys

DATE="2026-11-12"
COLORS=["#1368a4","#cb4b16","#21825e","#774da0","#b57d10","#199a9b","#b53c69","#596572","#8c652f","#6b8e23","#d46b4e","#6172b8"]
COUNTRIES=["United States","China","India","South Korea","United Kingdom","Japan","Mexico","Germany"]
SPANISH={"United States":"Estados Unidos","China":"China","India":"India","South Korea":"Corea del Sur","United Kingdom":"Reino Unido","Japan":"Japón","Mexico":"México","Germany":"Alemania","World":"Mundo","Nigeria":"Nigeria","Bangladesh":"Bangladés","Ghana":"Ghana","France":"Francia","England and Wales":"Inglaterra y Gales","United Arab Emirates":"Emiratos Árabes Unidos","Equatorial Guinea":"Guinea Ecuatorial","Africa":"África","Asia":"Asia","Europe":"Europa","North America":"América del Norte","South America":"América del Sur","Oceania":"Oceanía","London":"Londres","Delhi":"Delhi","Slovenia":"Eslovenia","Monaco":"Mónaco","Ecuador":"Ecuador","Afghanistan":"Afganistán","Gambia":"Gambia","Peru":"Perú","Bulgaria":"Bulgaria","Senegal":"Senegal"}
ENVNOTE="Alternativa de exposición a PM2.5, distinta de la mortalidad del enlace histórico. Mide concentración media anual ponderada por población (µg/m³). No calcula muertes atribuibles ni su proporción. La OMS vincula la exposición a partículas finas con daños cardiovasculares y respiratorios; esa evidencia de salud no se deriva de esta gráfica."
WHO="https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health"

def es(x):return SPANISH.get(x,x)
def status_es(x):return x.replace("In policy document","En documento de política").replace("Proposed / in discussion","Propuesta / en discusión").replace("In law","En ley").replace("No target","Sin meta").replace("Declaration / pledge","Declaración / compromiso")
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf8",newline="\n")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(x):
 try:
  v=float(x);return v if math.isfinite(v) else None
 except (ValueError,TypeError):return None
def read(root,slug):
 with (root/"originales"/(slug+".csv")).open(encoding="utf-8-sig",newline="") as f:rows=list(csv.DictReader(f))
 keys=[(r["Entity"],r["Year"]) for r in rows]
 if len(keys)!=len(set(keys)):raise ValueError("Claves repetidas: "+slug)
 for r in rows:r["Year"]=int(r["Year"])
 return rows
def selected(rows,names,start,end,field):
 vals=[dict(entity=r["Entity"],code=r.get("Code",""),year=r["Year"],value=finite(r.get(field))) for r in rows if r["Entity"] in names and start<=r["Year"]<=end]
 return sorted([r for r in vals if r["value"] is not None],key=lambda r:(r["entity"],r["year"]))
def lines(rows,names=None):
 grouped=defaultdict(list)
 for r in rows:grouped[r["entity"]].append(r)
 result=[]
 for n in names or sorted(grouped):
  if n not in grouped:continue
  known={r["year"]:r for r in grouped[n]}
  points=[known.get(y,{"year":y,"value":None}) for y in range(min(known),max(known)+1)]
  result.append({"type":"scatter","mode":"lines+markers","marker":{"size":2.5},"name":es(n),"x":[r["year"] for r in points],"y":[r["value"] for r in points],"line":{"width":2.5},"connectgaps":False,"hovertemplate":"%{x}: %{y:,.2f}<extra>%{fullData.name}</extra>"})
 return result
def scatter(rows,fieldx,fieldy,year):
 vals=[]
 for r in rows:
  x,y=finite(r.get(fieldx)),finite(r.get(fieldy))
  if r["Year"]==year and len(r.get("Code",""))==3 and x is not None and y is not None and x>0:vals.append(dict(entity=r["Entity"],code=r["Code"],year=year,x=x,y=y))
 vals.sort(key=lambda r:r["entity"])
 if len(vals)<30:raise ValueError("Muestra insuficiente para dispersión")
 return vals,[{"type":"scatter","mode":"markers","name":str(year),"x":[r["x"] for r in vals],"y":[r["y"] for r in vals],"text":[es(r["entity"]) for r in vals],"marker":{"size":8,"opacity":0.78,"color":"#1368a4","line":{"color":"white","width":0.5}},"hovertemplate":"%{text}<br>x: %{x:,.2f}<br>y: %{y:,.2f}<extra></extra>"}]
def csvwrite(p,rows):
 if not rows:raise ValueError("Sin datos: "+str(p))
 with p.open("w",newline="",encoding="utf8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
def layout(title,period,xlabel,ylabel,source,xlog=False):
 return {"title":{"text":title,"x":0.03,"xanchor":"left","font":{"size":21}},"font":{"family":"Arial, sans-serif","size":14,"color":"#253746"},"paper_bgcolor":"white","plot_bgcolor":"white","colorway":COLORS,"margin":{"l":90,"r":30,"t":88,"b":200},"height":620,"autosize":True,"xaxis":{"title":{"text":xlabel},"type":"log" if xlog else "linear","gridcolor":"#e5e9ec","zeroline":False},"yaxis":{"title":{"text":ylabel},"gridcolor":"#e5e9ec","zeroline":False,"automargin":True},"legend":{"orientation":"h","y":-0.22,"x":0,"font":{"size":12}},"annotations":[{"xref":"paper","yref":"paper","x":0,"y":1.075,"text":period,"showarrow":False,"xanchor":"left","font":{"size":13,"color":"#556575"}},{"xref":"paper","yref":"paper","x":0,"y":-0.40,"text":source,"showarrow":False,"xanchor":"left","font":{"size":10,"color":"#556575"}}],"hovermode":"closest"}
def htmlpage(row,figure,links):
 title=html.escape(row["title"]);src=html.escape(row["source"])
 refs="".join('<li><a href="'+html.escape(u,quote=True)+'">'+html.escape(label)+'</a></li>' for label,u in links)
 payload=json.dumps(figure,ensure_ascii=False,allow_nan=False).replace("</","<\\/")
 return '<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><link rel="stylesheet" href="../recursos.css"><script src="../../recursos_graficas/assets/plotly.min.js"></script></head><body><main><nav><a href="../index.html">Recursos esenciales</a> · <a href="../../portal/index.html">Curso</a></nav><h1>'+title+'</h1><div id="chart" role="img" aria-label="'+title+'"></div><section class="metadata"><p>'+html.escape(row["note"])+'</p><p><strong>Fuente:</strong> '+src+'</p><p><strong>Periodo:</strong> '+html.escape(row["period"])+'. <strong>Unidad:</strong> '+html.escape(row["unit"])+'. Descarga de insumos: 12 de noviembre de 2026.</p><p><strong>Correspondencia:</strong> '+html.escape(row["equivalence"])+'</p><ul>'+refs+'</ul></section></main><script>if(new URLSearchParams(location.search).has("embed"))document.body.classList.add("embed");window.recurso_figure='+payload+';if(document.body.classList.contains("embed")){recurso_figure.layout.height=Math.max(360,innerHeight);recurso_figure.layout.margin={l:85,r:20,t:70,b:140};recurso_figure.layout.title.font.size=18;recurso_figure.layout.legend.font.size=10;recurso_figure.layout.annotations[0].font.size=11;recurso_figure.layout.annotations[1].font.size=9;}Plotly.newPlot("chart",recurso_figure.data,recurso_figure.layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:["sendDataToCloud"]}).then(()=>{window.recursoReady=true;document.documentElement.dataset.ready="true"});</script></body></html>\n'
def build(repo):
 root=repo/"recursos_esenciales"
 for name in ("datos","graficas","imagenes","metadatos"):(root/name).mkdir(parents=True,exist_ok=True)
 rawcache={}
 def get(slug):
  if slug not in rawcache:rawcache[slug]=read(root,slug)
  return rawcache[slug]
 entries=[]
 def add(ident,module,slug,title,data,period,unit,xlabel,ylabel,source,note,equiv,original_url,traces=None,xlog=False,source_slugs=None):
  if not data:raise ValueError("Recurso vacío: "+ident)
  traces=traces if traces is not None else lines(data)
  if ident=="longevidad_ingreso":
   note+=" La fuente descargada reporta 18.8177 años para República Centroafricana (CAF), 2022: observación atípica que se conserva y marca para revisión, sin imputar otro valor."
   traces[0]["marker"]["color"]=["#c23e33" if r["code"]=="CAF" else "#1368a4" for r in data]
   traces[0]["text"]=[es(r["entity"])+(" (dato atípico en fuente)" if r["code"]=="CAF" else "") for r in data]
  fig={"data":traces,"layout":layout(title,period,xlabel,ylabel,"Fuente: "+source+" · insumos "+DATE,xlog)}
  if ident=="energia_ingreso":
   fig["layout"]["yaxis"]["type"]="log";fig["layout"]["yaxis"]["title"]["text"]+=" (escala log)"
  if ident=="longevidad_ingreso":
   fig["layout"]["annotations"].append({"xref":"paper","yref":"paper","x":0.98,"y":0.03,"xanchor":"right","showarrow":False,"text":"CAF, 2022: 18.82 años. Dato atípico de la fuente.","font":{"size":10,"color":"#a13b31"},"bgcolor":"white"})
  row={"id":ident,"slug":ident,"source_slug":slug,"title":title,"module":module,"original_url":original_url,"html":"recursos_esenciales/graficas/"+ident+".html","csv":"recursos_esenciales/datos/"+ident+".csv","json":"recursos_esenciales/datos/"+ident+".json","png":"recursos_esenciales/imagenes/"+ident+".png","svg":"recursos_esenciales/imagenes/"+ident+".svg","source":source,"period":period,"unit":unit,"equivalence":equiv,"note":note,"observations":len(data),"source_slugs":source_slugs or [slug]}
  csvwrite(repo/row["csv"],data);dump(repo/row["json"],fig)
  links=[("Datos de la figura (CSV)","../datos/"+ident+".csv"),("Especificación (JSON)","../datos/"+ident+".json"),("Imagen PNG","../imagenes/"+ident+".png"),("Imagen SVG","../imagenes/"+ident+".svg"),("Fuente o referencia histórica",original_url)]
  if "pm25" in ident:links.append(("OMS: efectos de la contaminación exterior",WHO))
  (repo/row["html"]).write_text(htmlpage(row,fig,links),encoding="utf8",newline="\n");entries.append(row)
 wdi="energy-use-per-capita-vs-gdp-per-capita";energy=get(wdi)
 cfg=json.loads((root/"metadatos"/(wdi+".config.json")).read_text(encoding="utf8"))
 display=next(d["display"] for d in cfg["dimensions"] if d["variableId"]==1293798)
 assert display["unit"]=="kWh" and display["conversionFactor"]==11.63,display
 for r in energy:
  val=finite(r.get("Energy use per capita"))
  if val is not None:r["Energy use per capita"]=val/display["conversionFactor"]
 pc=selected(energy,COUNTRIES+["World"],1990,2023,"Energy use per capita");total=[]
 for r in energy:
  if r["Entity"] in COUNTRIES and 1990<=r["Year"]<=2023:
   en,pop=finite(r.get("Energy use per capita")),finite(r.get("Population"))
   if en is not None and pop is not None:total.append(dict(entity=r["Entity"],code=r["Code"],year=r["Year"],energy_kg_oil_eq_per_capita=en,population=pop,value=en*pop/1e9))
 total.sort(key=lambda r:(r["entity"],r["year"]))
 add("energia_total","Energy","primary-energy-cons","Uso total de energía",total,"1990–2023","millones de toneladas equivalentes de petróleo","Año","Millones de tep","WDI (2026); población UN WPP (2024), vía OWID","Cálculo propio: CSV Grapher (kWh por persona) / 11.63 para recuperar kg equivalentes de petróleo por persona; luego × población UN WPP / 1,000,000,000. La población puede diferir de la usada internamente por WDI: es una estimación docente del total. No se rellenan años faltantes. La fuente y la unidad difieren de Energy Institute (TWh).","Alternativa abierta; cambia fuente, cobertura y unidad frente al enlace histórico.","https://ourworldindata.org/grapher/primary-energy-cons",traces=lines(total,COUNTRIES),source_slugs=[wdi])
 add("energia_por_persona","Energy","per-capita-energy-use","Uso de energía por persona",pc,"1990–2023","kg equivalentes de petróleo por persona","Año","kg equivalentes de petróleo/persona","Banco Mundial, WDI (2026) / OWID","Uso de energía primaria antes de su transformación en otros combustibles finales. Serie WDI EG.USE.PCAP.KG.OE: se revierte el factor de presentación de Grapher (kWh / 11.63 = kg equivalentes de petróleo). La unidad sustituye kWh por kg equivalentes de petróleo.","Alternativa abierta; no conserva las cifras ni la metodología de Energy Institute.","https://ourworldindata.org/grapher/per-capita-energy-use",traces=lines(pc,COUNTRIES+["World"]),source_slugs=[wdi])
 d,t=scatter(energy,"GDP per capita","Energy use per capita",2015)
 add("energia_ingreso","Energy",wdi,"Energía e ingreso por habitante",d,"2015; ambos indicadores en el mismo año","energía: kg equivalentes de petróleo/persona; PIB: $ internacionales de 2021, PPA","PIB por habitante ($ internacionales de 2021, escala log)","kg equivalentes de petróleo/persona","Banco Mundial, WDI (2026) / OWID","Corte transversal del último año de la ventana 1990–2015 del enlace. Se revierte el factor de presentación de Grapher: kWh / 11.63 = kg equivalentes de petróleo. Mismo país y año por punto. Asociación descriptiva, sin identificación causal.","Mismas variables actuales y año explícito; corte local 2015.","https://ourworldindata.org/grapher/energy-use-per-capita-vs-gdp-per-capita?yScale=log&time=1990..2015",t,True)
 slug="birth-rate-the-number-of-births-per-1000-people-in-the-population";names=["China","United States","Mexico","France","Japan","England and Wales"];d=selected(get(slug),names,1750,2023,"Birth rate")
 add("natalidad","Energy",slug,"Tasa bruta de natalidad",d,"1751–2023; cobertura variable según país","nacimientos por 1,000 habitantes","Año","Nacimientos por 1,000 habitantes","HMD (2025); UN WPP (2024) / OWID","Antes de 1950: datos históricos; desde 1950: UN WPP. La edición actual no contiene la desagregación racial de Estados Unidos del enlace antiguo: se muestra el total nacional. No se ajusta por estructura de edad.","Misma variable con fuente actual; omite desagregaciones raciales ausentes.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="children-per-woman-un";names=["World","Bangladesh","Nigeria","Ghana","Germany","India","United Kingdom","United States","China","South Korea","Japan"];d=selected(get(slug),names,1950,2023,"Fertility rate")
 add("fecundidad","Energy",slug,"Tasa global de fecundidad",d,"1950–2023; estimaciones, sin proyecciones","nacimientos por mujer","Año","Nacimientos por mujer","UN WPP (2024) / OWID","Resume las tasas de fecundidad por edad del año. Difiere de la tasa de crecimiento de la población. Los datos descargados terminan en 2023; no se añaden proyecciones.","Misma variable y selección de países, con edición explícita.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="children-per-woman-by-gdp-per-capita";d,t=scatter(get(slug),"GDP per capita","Births per woman",2023)
 add("fecundidad_ingreso","Energy",slug,"Fecundidad e ingreso por habitante",d,"2023; ambos indicadores en el mismo año","nacimientos por mujer; PIB en $ internacionales de 2021, PPA","PIB por habitante ($ internacionales de 2021, escala log)","Nacimientos por mujer","UN WPP (2024); PWT 11.0 (2025) / OWID","Corte del mismo año, sin interpolación. La asociación entre países no demuestra la respuesta de la fecundidad a un cambio de ingreso.","Mismas variables actuales; PIB a precios de 2021.","https://ourworldindata.org/grapher/"+slug,t,True)
 slug="life-expectancy-vs-gdp-per-capita";d,t=scatter(get(slug),"GDP per capita","Life expectancy at birth",2022)
 add("longevidad_ingreso","Energy",slug,"Esperanza de vida e ingreso por habitante",d,"2022; último año común de las dos series","esperanza de vida: años; PIB: $ internacionales de 2011, PPA","PIB por habitante ($ internacionales de 2011, escala log)","Esperanza de vida al nacer (años)","UN WPP (2024); Maddison Project Database 2023 / OWID","Corte 2022: esperanza de vida UN WPP, PIB Maddison Project. No se mezclan años ni se infiere causalidad de la correlación.","Mismas variables; edición y corte explícitos.","https://ourworldindata.org/grapher/"+slug,t,True)
 slug="average-exposure-pm25-pollution";pm=get(slug);pmcol="PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)";pm_source="Banco Mundial, WDI (2026) / OWID"
 oldurls=["https://ourworldindata.org/grapher/number-of-deaths-by-risk-factor","https://ourworldindata.org/grapher/share-deaths-air-pollution","https://ourworldindata.org/grapher/share-deaths-air-pollution?tab=chart&country=ARE~High-middle+SDI~Middle+SDI~GNQ~High+SDI~Low+SDI~Low-middle+SDI","https://ourworldindata.org/grapher/death-rate-from-air-pollution-per-100000?tab=map"]
 d=selected(pm,["World"],1990,2023,pmcol)
 add("pm25_mundo","Environment",slug,"Exposición mundial a partículas finas",d,"1990–2023","µg/m³","Año","PM2.5: exposición media anual (µg/m³)",pm_source,ENVNOTE,"Cambio de medida: exposición, sustituyendo conteo de muertes por riesgo.",oldurls[0])
 names=COUNTRIES+["Nigeria"];d=selected(pm,names,2023,2023,pmcol);d.sort(key=lambda r:r["value"]);t=[{"type":"bar","orientation":"h","x":[r["value"] for r in d],"y":[es(r["entity"]) for r in d],"marker":{"color":"#1368a4"},"hovertemplate":"%{y}: %{x:.2f} µg/m³<extra></extra>"}]
 add("pm25_comparacion","Environment",slug,"Exposición a PM2.5 en países seleccionados",d,"2023; selección docente","µg/m³","PM2.5: exposición media anual (µg/m³)","",pm_source,ENVNOTE,"Cambio de medida: exposición de países, no porcentaje de muertes.",oldurls[1],t)
 names=["United Arab Emirates","Equatorial Guinea","World"];d=selected(pm,names,1990,2023,pmcol)
 add("pm25_trayectorias","Environment",slug,"Trayectorias de exposición a PM2.5",d,"1990–2023","µg/m³","Año","PM2.5: exposición media anual (µg/m³)",pm_source,ENVNOTE+" Se conservan Emiratos Árabes Unidos y Guinea Ecuatorial. Se omiten grupos SDI porque no forman parte de este conjunto.","Cambio de medida y clasificación: dos países y mundo, no mortalidad por SDI.",oldurls[2],traces=lines(d,names))
 gdp={(r["Code"],r["Year"]):r.get("GDP per capita") for r in energy if len(r.get("Code",""))==3};combined=[dict(r,**{"GDP per capita":gdp.get((r.get("Code",""),r["Year"]),"")}) for r in pm];d,t=scatter(combined,"GDP per capita",pmcol,2023)
 add("pm25_ingreso","Environment",slug,"Exposición a PM2.5 e ingreso por habitante",d,"2023; ambos indicadores en el mismo año","PM2.5: µg/m³; PIB: $ internacionales de 2021, PPA","PIB por habitante ($ internacionales de 2021, escala log)","PM2.5: exposición media anual (µg/m³)",pm_source,ENVNOTE+" Cruce por código ISO y año. No demuestra una curva causal de contaminación e ingreso.","Cambio de medida: exposición e ingreso, sustituyendo mapa de mortalidad.",oldurls[3],t,True,[slug,wdi])
 slug="co-emissions-per-capita";names=["World"]+COUNTRIES;d=selected(get(slug),names,1960,2025,"CO₂ emissions per capita")
 add("co2_por_persona","Environment",slug,"Emisiones territoriales de CO₂ por persona",d,"1960–2025","toneladas de CO₂ por persona","Año","t CO₂/persona","Global Carbon Budget (2026) / OWID","Combustibles fósiles e industria, sin cambio de uso del suelo. Las emisiones territoriales no se ajustan por el carbono incorporado al comercio.","Misma variable actual; selección de países y edición de 2026 explícitas.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="annual-co2-emissions-per-country";names=["China","United States","India","United Kingdom","South Korea","Japan"];d=selected(get(slug),names,1750,2025,"Annual CO₂ emissions")
 for r in d:r["value"]/=1e6
 add("co2_total","Environment",slug,"Emisiones territoriales anuales de CO₂",d,"1750–2025; cobertura variable","millones de toneladas de CO₂","Año","Millones de t CO₂","Global Carbon Budget (2026) / OWID","Conversión propia de toneladas a millones de toneladas. Fósiles e industria, sin cambio de uso del suelo. Los totales reflejan el tamaño de población y economía.","Misma variable y selección del enlace; edición actual explícita.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="so-emissions-by-world-region-in-million-tonnes";so=get(slug);names=["United States","United Kingdom","Germany","China","India","Japan","Mexico"];d=selected(so,names,1750,2022,"Sulfur dioxide")
 for r in d:r["value"]/=1e6
 add("so2_paises","Environment","so-emissions-tonnes-per-year","Emisiones de dióxido de azufre por país",d,"1750–2022","millones de toneladas de SO₂","Año","Millones de t SO₂","CEDS (2024) / OWID","El destino original devuelve 404. Se usa el mismo indicador de emisiones de todos los sectores de CEDS de la vista regional OWID; el archivo incluye países. Conversión de t a millones de t. Difiere de la concentración ambiental.","Mismo contaminante y datos CEDS verificables; no se autentica el objeto antiguo.","https://ourworldindata.org/grapher/so-emissions-tonnes-per-year",traces=lines(d,names),source_slugs=[slug])
 names=["Africa","Asia","Europe","North America","South America","Oceania"];d=selected(so,names,1750,2022,"Sulfur dioxide")
 for r in d:r["value"]/=1e6
 add("so2_regiones","Environment",slug,"Emisiones de dióxido de azufre por región",d,"1750–2022","millones de toneladas de SO₂","Año","Millones de t SO₂","CEDS (2024) / OWID","Regiones del archivo original. Conversión de toneladas a millones. No se suman grupos de ingreso o entidades que se solapan con las regiones.","Misma variable y agrupación territorial disponible.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="net-zero-targets";names=["Slovenia","Monaco","Ecuador","Afghanistan","Gambia","Peru","Bulgaria","Senegal"];d=[{"entity":r["Entity"],"code":r["Code"],"year":r["Year"],"status":r["Status of net-zero carbon emissions targets"]} for r in get(slug) if r["Entity"] in names];d.sort(key=lambda r:names.index(r["entity"]))
 t=[{"type":"table","header":{"values":["País","Situación del compromiso (fuente)"],"fill":{"color":"#e4edf4"},"align":"left","font":{"size":15},"height":36},"cells":{"values":[[es(r["entity"]) for r in d],[status_es(r["status"]) for r in d]],"fill":{"color":"white"},"align":"left","font":{"size":14},"height":34},"columnwidth":[180,500]}]
 add("metas_neto_cero","Environment",slug,"Situación de metas de emisiones netas cero",d,"2026; estado del registro","categoría declarada en la fuente","","","Net Zero Tracker (2026) / OWID","La categoría describe la formalización del compromiso; no acredita emisiones netas cero. Cobertura de gases, sectores y compensaciones difiere. Dataset CC BY-NC 4.0: uso docente no comercial, con atribución.","Misma variable categórica y selección del enlace; no equivale a cumplimiento.","https://ourworldindata.org/grapher/"+slug,t)
 slug="air-pollution-london-vs-delhi";names=["London","Delhi"];d=selected(get(slug),names,1700,2016,"Suspended Particulate Matter (SPM) (Fouquet and DPCC (2011))")
 add("londres_delhi_particulas","Environment",slug,"Partículas suspendidas: Londres y Delhi",d,"1700–2016; periodos distintos por ciudad","µg/m³ de partículas suspendidas totales","Año","Partículas suspendidas (µg/m³)","Fouquet (2011); Gobierno de India (2012–13) / OWID","Serie histórica de partículas suspendidas totales (SPM), distinta de PM2.5 y SO₂. Los periodos y procedimientos de medición difieren entre ciudades. No se interpreta como trayectoria causal universal ni se interpolan años faltantes.","Misma serie histórica publicada; no son mediciones actuales.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 slug="ratio-of-female-to-male-labor-force-participation-rates-ilo-wdi";names=COUNTRIES+["Nigeria","Bangladesh","United Arab Emirates"];d=selected(get(slug),names,2025,2025,"Ratio of female to male labor force participation rate");d.sort(key=lambda r:r["value"]);t=[{"type":"bar","orientation":"h","x":[r["value"] for r in d],"y":[es(r["entity"]) for r in d],"marker":{"color":"#1368a4"},"hovertemplate":"%{y}: %{x:.2f}%<extra></extra>"}]
 add("participacion_relativa_mujeres","Labor_2",slug,"Participación laboral femenina respecto de la masculina",d,"2025; selección de países","100 × tasa femenina / tasa masculina, en %","Razón de tasas (%)","","OIT modelada; WDI (2026) / OWID","Cada tasa se calcula respecto de su población de 15 años o más. 100 indica igualdad de tasas. El cociente difiere del porcentaje de mujeres dentro de la fuerza laboral.","Misma variable; países seleccionados en vez de mapa.","https://ourworldindata.org/grapher/"+slug,t)
 slug="female-labor-force-participation-rates-by-national-per-capita-income";d,t=scatter(get(slug),"GDP per capita","Female labor force participation rate",2025)
 add("participacion_femenina_ingreso","Labor_2",slug,"Participación laboral femenina e ingreso",d,"2025; ambos indicadores en el mismo año","tasa femenina de 15+ (%); PIB: $ internacionales de 2021, PPA","PIB por habitante ($ internacionales de 2021, escala log)","Tasa de participación femenina (%)","OIT modelada; WDI (2026) / OWID","La fuerza laboral incluye ocupadas y desocupadas que buscan trabajo. El patrón entre países no identifica la trayectoria de un país ni un efecto causal del ingreso.","Mismas variables actuales; mismo año, sin promediar o extrapolar.","https://ourworldindata.org/grapher/"+slug,t,True)
 slug="female-employment-to-population-ratio";names=["United States","United Kingdom","Germany","Japan","Mexico","India","China"];d=selected(get(slug),names,1980,2016,"Female employment rate")
 add("empleo_femenino","Labor_2",slug,"Mujeres ocupadas respecto de la población femenina",d,"1980–2016; cobertura nacional variable","ocupadas de 15+ / población femenina de 15+, en %","Año","Relación empleo/población femenina (%)","Estimaciones nacionales, WDI (2026) / OWID","Estimación nacional de empleo, distinta de participación modelada OIT de figuras anteriores. Países con datos en la ventana histórica, sin rellenar faltantes. Diferencias metodológicas limitan comparaciones exactas.","Misma variable de empleo nacional; ventana histórica y cobertura explícitas.","https://ourworldindata.org/grapher/"+slug,traces=lines(d,names))
 ident="tasa_marginal_maxima_historica";title="Tasa marginal máxima del impuesto al ingreso en Estados Unidos"
 row={"id":ident,"slug":ident,"source_slug":"FRED-FOJf","title":title,"module":"Taxes","original_url":"https://fred.stlouisfed.org/graph/?g=FOJf","html":"recursos_esenciales/graficas/"+ident+".html","csv":None,"json":None,"png":"recursos_esenciales/imagenes/"+ident+".png","svg":None,"source":"IRS, serie IITTRHB, vía FRED; imagen histórica del curso","period":"1949–2018 aproximadamente, según imagen histórica; última observación FRED: 2018","unit":"porcentaje; anual, sin ajuste estacional","equivalence":"PNG histórico exacto del curso; FOJf identifica IITTRHB. No se digitalizan valores ni se presenta como actualización de 2026.","note":"La tasa máxima legal difiere de la tasa media efectiva y no mide la carga fiscal de todos los hogares. Los años son fiscales. Última observación FRED: 2018, actualización: 14-ene-2021. El descenso de una tasa no identifica por sí solo efectos sobre crecimiento.","observations":None,"source_slugs":[]}
 (repo/row["html"]).write_text('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><link rel="stylesheet" href="../recursos.css"></head><body><main><nav><a href="../index.html">Recursos esenciales</a></nav><h1>'+html.escape(title)+'</h1><img class="historical" src="../imagenes/'+ident+'.png" alt="Gráfica histórica FRED: tasa marginal máxima legal IITTRHB"><section class="metadata"><p>'+html.escape(row["note"])+'</p><p>'+html.escape(row["period"])+'</p><p>'+html.escape(row["equivalence"])+'</p><p><a href="https://fred.stlouisfed.org/series/IITTRHB">Fuente y notas IITTRHB</a></p></section></main><script>if(new URLSearchParams(location.search).has("embed"))document.body.classList.add("embed");document.documentElement.dataset.ready="true";</script></body></html>\n',encoding="utf8",newline="\n");entries.append(row)
 assert len(entries)==21,len(entries)
 for row in entries:row["units"]=row["unit"]
 inputs={p.relative_to(repo).as_posix():{"bytes":p.stat().st_size,"sha256":sha(p)} for p in sorted((root/"originales").glob("*.csv"))}
 catalog={"count":len(entries),"generated_from":"scripts/generar_recursos_esenciales.py","input_date":DATE,"network_required":False,"entries":entries,"inputs":inputs,"rights":"Condiciones por indicador en metadatos/. No se incluyen observaciones IHME de mortalidad ni Energy Institute. Net Zero Tracker: CC BY-NC 4.0 para uso docente no comercial."};dump(root/"catalogo.json",catalog)
 css='body{font:16px/1.5 Arial,sans-serif;color:#253746;margin:0;background:white}main{max-width:1200px;margin:24px auto;padding:0 24px}a{color:#12629a}nav{font-size:14px}h1{font-size:27px;font-weight:500;line-height:1.25}#chart{width:100%;height:620px}.metadata{border-top:1px solid #dce2e6;padding-top:10px;font-size:15px}.historical{width:100%;height:auto;object-fit:contain}.embed main{margin:0;padding:0;max-width:none}.embed nav,.embed h1,.embed .metadata{display:none}.embed #chart{height:100vh}.embed .historical{height:100vh;object-fit:contain}table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:9px;border-bottom:1px solid #dde3e8}@media(max-width:600px){main{padding:0 10px}h1{font-size:22px}#chart{height:580px}}\n';(root/"recursos.css").write_text(css,encoding="utf8",newline="\n")
 tr="".join('<tr><td>'+html.escape(e["module"])+'</td><td><a href="graficas/'+e["id"]+'.html">'+html.escape(e["title"])+'</a></td><td>'+html.escape(e["period"])+'</td></tr>' for e in entries)
 (root/"index.html").write_text('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Recursos esenciales del curso</title><link rel="stylesheet" href="recursos.css"></head><body><main><nav><a href="../portal/index.html">Materiales del curso</a></nav><h1>Recursos esenciales para consulta local</h1><p>Figuras de energía, medio ambiente, participación laboral y política fiscal. Cada vista conserva datos, fuentes, unidades y periodos. Las sustituciones cambian de medida cuando lo indica su página.</p><table><thead><tr><th>Módulo</th><th>Figura</th><th>Periodo</th></tr></thead><tbody>'+tr+'</tbody></table><p><a href="README.md">Fuentes, método y límites</a></p></main></body></html>\n',encoding="utf8",newline="\n")
 (root/"README.md").write_text("# Recursos esenciales del curso\n\n21 vistas locales, insumos archivados el 12 de noviembre de 2026. Abrir [el índice](index.html) desde la copia completa del repositorio. 20 figuras generadas incluyen HTML, CSV, JSON, PNG y SVG. La tasa marginal máxima reutiliza exactamente la imagen histórica del curso, sin datos digitalizados.\n\n## Correspondencia y fuentes\n\n- Energía: las dos vistas Energy Institute se sustituyen por WDI EG.USE.PCAP.KG.OE, CC BY 4.0. El CSV Grapher aplica factor de presentación 11.63 para mostrar kWh; se divide por 11.63 para recuperar kg equivalentes de petróleo. Total = energía por habitante × población UN WPP / 1e9, en millones de toneladas equivalentes de petróleo. Cobertura 1990–2023 y unidad difieren de los TWh originales. No se redistribuyen observaciones Energy Institute.\n- Cuatro referencias de mortalidad IHME pasan a exposición media anual PM2.5 (WDI, CC BY 4.0), que no mide fallecimientos ni mortalidad. Salud: [OMS]("+WHO+"). No se incluyen las observaciones restringidas de mortalidad.\n- Dispersión: mismo año por variables y países ISO; excluye agregados y registros incompletos. Líneas sin interpolación de faltantes.\n- CO₂: Global Carbon Budget 2026, CC BY 4.0, emisiones territoriales fósiles e industriales sin uso del suelo. Totales convertidos a millones de toneladas /1e6.\n- SO₂: CEDS 2024, CC BY 4.0, vía OWID. URL antigua por país 404; archivo regional también incluye países. Datos originales en toneladas aunque el slug mencione millones: conversión explícita.\n- Cero neto: Net Zero Tracker 2026, CC BY-NC 4.0. Uso docente no comercial, sin equiparar compromisos a cumplimiento.\n- Londres y Delhi: partículas suspendidas totales históricas, Fouquet (2011) y Gobierno de India (2012–13), compiladas por OWID. Difiere de PM2.5 y de observaciones actuales. Metadata del proveedor sin licencia específica: no se atribuye una licencia abierta al origen.\n- Laboral: WDI, CC BY 4.0. Razón femenina/masculina y participación femenina: OIT modelada. Empleo/población: estimaciones nacionales. Población femenina de 15+.\n- FRED: identidad IITTRHB verificada en FOJf y en imagen archivada. Serie anual, %, sin ajuste estacional, última observación 2018, actualización 14-ene-2021. Imagen histórica, no edición de 2026.\n\n## Regeneración\n\nEjecutar python scripts/generar_recursos_esenciales.py. Reproduce figuras y catálogos sin red; --export produce imágenes mediante Playwright/Chrome. JSON alimenta efectivamente cada gráfica; CSV conserva observaciones seleccionadas. Metadatos API: edición, unidad, actualización y condiciones por indicador. catalogo.json registra hashes de los CSV de entrada.\n\nApariencia y selección son reconstrucciones locales. No se acredita igualdad de píxeles con los iframes históricos, salvo el PNG FRED reutilizado. Fuentes externas: consulta opcional.\n",encoding="utf8",newline="\n")
 return catalog
def export(repo,catalog,chrome=None):
 from playwright.sync_api import sync_playwright
 import base64
 from urllib.parse import unquote_to_bytes
 with sync_playwright() as p:
  kwargs={"headless":True}
  if chrome:kwargs["executable_path"]=chrome
  elif Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe").exists():kwargs["executable_path"]=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
  browser=p.chromium.launch(**kwargs);page=browser.new_page(viewport={"width":1240,"height":900});external=[]
  def route(request):
   if request.request.url.startswith("file:"):request.continue_()
   else:external.append(request.request.url);request.abort()
  page.route("**/*",route)
  for e in catalog["entries"]:
   if e["json"] is None:continue
   page.goto((repo/e["html"]).as_uri(),wait_until="load");page.wait_for_function("window.recursoReady===true")
   for fmt in ("svg","png"):
    data=page.evaluate("(fmt)=>Plotly.toImage(document.getElementById('chart'),{format:fmt,width:1200,height:700})",fmt);header,payload=data.split(",",1);(repo/e[fmt]).write_bytes(base64.b64decode(payload) if ";base64" in header else unquote_to_bytes(payload))
   print("EXPORTED",e["id"],flush=True)
  browser.close()
 if external:raise ValueError("Red inesperada: "+str(external))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("root",nargs="?",type=Path);p.add_argument("--export",action="store_true");p.add_argument("--chrome");p.add_argument("--output",type=Path,help="Raíz temporal vacía para regenerar sin sobrescribir archivos canónicos");a=p.parse_args();repo=(a.root or Path(__file__).resolve().parents[1]).resolve()
 if a.output:
  target=a.output.resolve()
  if target==repo or repo in target.parents:raise ValueError("--output debe estar fuera del repositorio")
  if target.exists() and any(target.iterdir()):raise ValueError("--output debe estar vacío")
  target.mkdir(parents=True,exist_ok=True)
  for folder in ("originales","metadatos"):
   shutil.copytree(repo/"recursos_esenciales"/folder,target/"recursos_esenciales"/folder)
  (target/"recursos_esenciales/imagenes").mkdir(exist_ok=True)
  shutil.copy2(repo/"recursos_esenciales/imagenes/tasa_marginal_maxima_historica.png",target/"recursos_esenciales/imagenes/tasa_marginal_maxima_historica.png")
  (target/"recursos_graficas/assets").mkdir(parents=True,exist_ok=True)
  shutil.copy2(repo/"recursos_graficas/assets/plotly.min.js",target/"recursos_graficas/assets/plotly.min.js")
  repo=target
 catalog=build(repo)
 if a.export:export(repo,catalog,a.chrome)
 print(json.dumps({"count":catalog["count"],"generated_figures":20,"historic_images":1,"output":"recursos_esenciales/index.html","exported":a.export},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
