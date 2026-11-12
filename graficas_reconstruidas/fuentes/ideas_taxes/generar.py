#!/usr/bin/env python3
"""Reconstrucciones docentes reproducibles. Sólo biblioteca estándar, sin red ni R.

Uso: python generar.py --output CARPETA
Los IDs identifican el destino docente, no una identidad histórica autenticada.
"""
import argparse
import copy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'inputs'
SOURCE_COMMIT = '3a8c79f20022ef7b985b392d73921839a4317883'
TARGET_COMMIT = '8265d179322918f035cc4102f1bc9403cbcbb1dc'
PRIMARY = 'https://github.com/dvollrath/StudyGuide/blob/' + SOURCE_COMMIT + '/'
TARGET = 'https://github.com/iguzmanvt/Crecimiento/blob/' + TARGET_COMMIT + '/'
COUNTRIES = {'ARG':'Argentina','CHL':'Chile','CHN':'China','DEU':'Alemania','GBR':'Reino Unido','JPN':'Japón','KOR':'Corea del Sur','MEX':'México','USA':'Estados Unidos'}
ALIASES = {'China':'CHN','Germany':'DEU','Japan':'JPN','Republic of Korea':'KOR','South Korea':'KOR','Mexico':'MEX','United States of America':'USA','United States':'USA'}
COLORS = {'USA':'#1764A0','CHN':'#D26932','DEU':'#3895B5','GBR':'#536A9C','JPN':'#719C84','KOR':'#8864A5','MEX':'#1D8668','ARG':'#B38A35','CHL':'#B45F83','A':'#1764A0','B':'#D26932'}
EXPECTED = [72,76,96,100,102,112,116,118,120,132,134]

def load(name):
    return json.loads((INPUTS/name).read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def country_key(name):
    return ALIASES.get(name, name)

def title_text(value):
    return value.get('text','') if isinstance(value,dict) else value or ''

def layout(title, xlabel, ylabel, temporal=False, xpercent=False, ypercent=False):
    axis = {'type':'linear','automargin':True,'showline':True,'linecolor':'#BAC7D1','gridcolor':'#E5EBF0','zerolinecolor':'#B6C3CC','tickfont':{'size':12},'title':{'text':''}}
    xaxis=copy.deepcopy(axis);yaxis=copy.deepcopy(axis)
    xaxis['title']={'text':xlabel,'font':{'size':14},'standoff':14}
    yaxis['title']={'text':ylabel,'font':{'size':14},'standoff':14}
    if temporal:xaxis.update(tickformat='d',dtick=10)
    if xpercent:xaxis['tickformat']='.0%'
    if ypercent:yaxis['tickformat']='.1%'
    return {'title':{'text':title,'x':0.025,'xanchor':'left','font':{'size':20}},'paper_bgcolor':'#FFFFFF','plot_bgcolor':'#FFFFFF','font':{'family':'Arial, sans-serif','size':14,'color':'#243B50'},'margin':{'l':100,'r':35,'t':75,'b':125},'height':560,'xaxis':xaxis,'yaxis':yaxis,'hovermode':'x unified' if temporal else 'closest','legend':{'orientation':'h','x':0,'y':-0.22,'xanchor':'left','yanchor':'top','font':{'size':12},'traceorder':'normal'},'hoverlabel':{'bgcolor':'#FFFFFF','font':{'color':'#243B50'}},'showlegend':True}

def style_traces(data, temporal=False, xpercent=False, ypercent=False):
    result=[]
    for old in data:
        key=country_key(old.get('name'))
        name=COUNTRIES.get(key,old.get('name') or 'Serie archivada')
        color=COLORS.get(key,'#1764A0')
        mode='lines+markers' if temporal else 'markers'
        xformat='.0f' if temporal else '.2%' if xpercent else '.3f'
        yformat='.2%' if ypercent else '.4f'
        trace={'type':'scatter','mode':mode,'name':name,'legendgroup':str(key or name),'x':copy.deepcopy(old['x']),'y':copy.deepcopy(old['y']),'marker':{'color':color,'size':5 if temporal else 7,'opacity':0.86,'line':{'color':'#FFFFFF','width':0.4}},'line':{'color':color,'width':2},'connectgaps':False,'hovertemplate':'<b>%{fullData.name}</b><br>'+('Año' if temporal else 'x')+': %{x:'+xformat+'}<br>y: %{y:'+yformat+'}<extra></extra>','meta':{'source_series':old.get('name'),'country_code':key}}
        result.append(trace)
    return result

DEFINITIONS = {
72: dict(source='pwt-oecd-rd-tfp',title='Investigadores y crecimiento: comparación internacional',x='ln(investigadores equivalentes a tiempo completo)',y='Crecimiento de la productividad (ventana de 10 años)',yp=True,
 description='Reconstrucción del contraste entre intensidad de investigación y crecimiento de productividad en seis países del archivo StudyGuide. Se mantiene separada del objeto local de nueve países usado para 116.',
 formula='x = lnrdworker archivado = ln(FTE); y = g10.accttfp archivado. El código fuente documenta g10.accttfp = round((accttfp_t − accttfp_(t−10))/10, 4). No se recalculan los datos.',
 units='x: logaritmo natural de investigadores FTE. y: tasa decimal archivada; las etiquetas porcentuales cambian sólo la presentación.',code='Guide_PWT_Account.r'),
96: dict(source='oecd-rd-fte',title='Investigadores en I+D',x='Año',y='Investigadores equivalentes a tiempo completo',temporal=True,
 description='Evolución del personal investigador en seis países, conservando todos los años y valores del objeto gráfico archivado.',
 formula='x = Time; y = ObsValue. Los comentarios del código OECD documentan filtros FTE, investigadores, todos los sectores y ambos géneros; el eje archivado indica FTE.',
 units='Investigadores equivalentes a tiempo completo (FTE); no son necesariamente personas físicas.',code='Guide_OECD_RD.r'),
100: dict(source='oecd-rd-levelrd',title='Evolución del gasto en I+D en logaritmos relativos',x='Año',y='ln(gasto / gasto de 2000)',temporal=True,
 description='Se calcula el logaritmo natural del gasto relativo a 2000 en cada país. El eje es lineal: no se aplica un segundo logaritmo. Se comparan trayectorias relativas, sin comparar tamaños monetarios entre países.',
 formula='y = ln(OBS_VALUE_t / OBS_VALUE_2000), por país, calculado desde los niveles originales sin redondeo intermedio; eje y lineal. En 2000, y = 0.',
 units='Logaritmo natural de una razón sin unidades, base 2000 = 0. No mide una tasa anual; una diferencia entre años mide cambio logarítmico acumulado.',code='Guide_OECD_RD.r'),
102: dict(source='oecd-rd-levelrd',title='Evolución relativa del gasto en I+D',x='Año',y='Índice del gasto en I+D (2000 = 100)',temporal=True,
 description='Índice del gasto de I+D con base 2000 = 100 en cada uno de seis países. Permite comparar la evolución relativa del gasto; no permite comparar niveles monetarios absolutos entre países.',
 formula='y = 100 × OBS_VALUE_t / OBS_VALUE_2000, por país. El año 2000 está presente y tiene valor positivo en las seis series archivadas.',
 units='Índice sin unidades, base propia de cada país en 2000 = 100. Se conservan las unidades originales sólo en los archivos de entrada, sin atribuir moneda, PPA ni base de precios.',code='Guide_OECD_RD.r'),
112: dict(source='pwt-growth-tfp-comp',title='Crecimiento de la productividad',x='Año final de la ventana de 10 años',y='Tasa anual media de crecimiento de productividad',temporal=True,yp=True,
 description='Evolución temporal de la productividad para leer junto a las gráficas de trabajadores y gasto de I+D. La figura no estima por sí sola una relación causal.',
 formula='accttfp = round(ln(rgdpna/pop),2) − (0.3/0.7)ln(round(rnna/rgdpna,2)) − ln(hc) − ln(emp/pop); g10.accttfp = round((accttfp_t − accttfp_(t−10))/10,4). Se reutiliza la serie archivada.',
 units='Tasa decimal anual media de variación logarítmica en una ventana de 10 años; etiquetas en porcentaje.',code='Guide_PWT_Account.r'),
118: dict(source='pwt-oecd-rd-gtfp',title='Cambio de investigadores y crecimiento de productividad',x='Variación de ln(FTE) / 10 (rezago de 10 observaciones)',y='Crecimiento anual medio de productividad (10 años)',xp=True,yp=True,
 description='Variante específica de dispersión que compara tasas de crecimiento, en lugar de niveles. Se conserva la muestra de seis países del archivo fuente.',
 formula='x = (ln(FTE_i) − ln(FTE_(i−10)))/10, con i como fila dentro del país; y = g10.accttfp archivado. El código utiliza rezagos de 10 observaciones; no se recalculan ni se imputan datos.',
 units='Valores decimales, mostrados como porcentajes. En x, la diferencia logarítmica se divide entre 10 aunque el rezago es de 10 observaciones: con huecos temporales no equivale necesariamente a 10 años. En y, crecimiento anual medio de productividad a 10 años según el código del curso.',code='Guide_PWT_Account.r'),
120: dict(source='pwt-oecd-level-rd',title='Investigadores y nivel de productividad',x='ln(investigadores equivalentes a tiempo completo)',y='Nivel logarítmico de productividad (residuo)',
 description='Variante de niveles para distinguirla de las gráficas de crecimiento. La elección para este destino es editorial: el texto Rmd repetido no identifica la gráfica histórica.',
 formula='x = ln(FTE); y = accttfp archivado = ln(Y/N) − (0.3/0.7)ln(K/Y) − ln(hc) − ln(emp/pop), con los redondeos incorporados en la fuente.',
 units='x: logaritmo natural de FTE. y: residuo logarítmico de contabilidad del crecimiento; no es un índice TFP con base 100.',code='Guide_PWT_Account.r'),
132: dict(source='pwt-all-cshg-growth',title='Gasto del gobierno y crecimiento del PIB per cápita',x='Participación del consumo del gobierno en el PIB',y='Crecimiento anual medio del PIB per cápita (10 años)',xp=True,yp=True,
 description='Comparación de participación del gobierno y crecimiento del PIB per cápita en seis países. La participación del gasto no se presenta como una tasa impositiva.',
 formula='x = round(csh_g,3); y = [round(ln(rgdpna/pop),3)_t − round(ln(rgdpna/pop),3)_(t−10)]/10. Datos del objeto gráfico archivado, sin recalcular con otra PWT.',
 units='x: proporción del PIB (etiquetas en porcentaje). y: tasa decimal anual media de variación logarítmica a 10 años (etiquetas en porcentaje).',code='Guide_PWT_Topics.r'),
134: dict(source='pwt-all-cshg-level',title='Gasto del gobierno y nivel del PIB per cápita',x='Participación del consumo del gobierno en el PIB',y='ln(PIB per cápita archivado)',xp=True,
 description='Comparación de participación del gobierno y nivel logarítmico del PIB per cápita. Conserva los puntos del archivo y se distingue del crecimiento mostrado en 132.',
 formula='x = round(csh_g,3); y = round(ln(rgdpna/pop),3). Se preservan los valores archivados.',
 units='x: proporción del PIB, mostrada como porcentaje. y: logaritmo natural del PIB per cápita de la fuente; no se atribuye moneda o base de precios no verificada.',code='Guide_PWT_Topics.r')
}

def observations(data):
    by=[]
    for d in data:
        pairs=[(x,y) for x,y in zip(d['x'],d['y']) if isinstance(x,(int,float)) and isinstance(y,(int,float)) and math.isfinite(x) and math.isfinite(y)]
        by.append({'series':d['name'],'array_length':len(d['x']),'effective_pairs':len(pairs)})
    return {'total_effective_pairs':sum(x['effective_pairs'] for x in by),'by_series':by}

def temporal_period(data):
    by={d['name']:[min(d['x']),max(d['x'])] for d in data if d['x']}
    years=[x for d in data for x in d['x']]
    return f'{min(years)}–{max(years)}; cobertura desigual por país',by

def model_spec(params):
    R=float(params['R0']);A={k:float(v) for k,v in params['A0'].items()};rows=[]
    for t in range(1,params['periods']+1):
        for key in ['A','B']:
            growth=params['theta']*R**params['lambda']/A[key]**(1-params['phi'])
            rows.append({'t':t,'scenario':key,'ratio':growth/params['theta'],'growth':growth})
            A[key]=(1+growth)*A[key]
        R=(1+params['gR'])*R
    by={k:[r for r in rows if r['scenario']==k] for k in ['A','B']}
    data=[]
    for key in ['A','B']:
        data.append({'type':'scatter','mode':'lines','name':'Economía '+key,'x':[r['ratio'] for r in by[key]],'y':[r['growth'] for r in by[key]],'customdata':[[r['t']] for r in by[key]],'line':{'color':COLORS[key],'width':3},'hovertemplate':'<b>%{fullData.name}</b><br>Periodo: %{customdata[0]}<br>R/A: %{x:.4f}<br>Crecimiento: %{y:.3%}<extra></extra>'})
    lay=layout('Modelo de I+D: convergencia del crecimiento','Investigadores por unidad de productividad (R/A)','Tasa de crecimiento de productividad',ypercent=True)
    lay['height']=630
    lay['margin']['b']=195
    lay['xaxis']['range']=[0.8,5.2];lay['yaxis']['range']=[0,0.06]
    equilibrium=[{'type':'line','xref':'x','yref':'y','x0':0.8,'x1':5.2,'y0':0.02,'y1':0.02,'line':{'color':'#8E9EAA','width':1.2,'dash':'dash'}},{'type':'line','xref':'x','yref':'y','x0':2,'x1':2,'y0':0,'y1':0.06,'line':{'color':'#8E9EAA','width':1.2,'dash':'dash'}}]
    def frame_layout(t):
        shapes=copy.deepcopy(equilibrium)
        for k in ['A','B']:
            r=by[k][t-1];shapes.append({'type':'circle','xref':'x','yref':'y','x0':r['ratio']-.045,'x1':r['ratio']+.045,'y0':r['growth']-.00065,'y1':r['growth']+.00065,'fillcolor':COLORS[k],'line':{'color':'#FFFFFF','width':1.5}})
        return {'shapes':shapes,'annotations':[{'xref':'paper','yref':'paper','x':0.98,'y':0.98,'xanchor':'right','yanchor':'top','showarrow':False,'text':f'Periodo {t} / 250<br>Límite: R/A = 2; crecimiento = 2%','font':{'size':12,'color':'#4B6071'},'bgcolor':'rgba(255,255,255,0.9)'}]}
    lay.update(frame_layout(1))
    lay['updatemenus']=[{'type':'buttons','direction':'right','x':0,'y':-0.30,'showactive':False,'buttons':[{'label':'Reproducir','method':'animate','args':[None,{'fromcurrent':True,'frame':{'duration':40,'redraw':False},'transition':{'duration':0},'mode':'immediate'}]},{'label':'Pausar','method':'animate','args':[[None],{'mode':'immediate','frame':{'duration':0,'redraw':False},'transition':{'duration':0}}]}]}]
    lay['sliders']=[{'active':0,'x':0.35,'len':0.65,'y':-0.30,'currentvalue':{'prefix':'Periodo ','visible':True},'steps':[{'label':str(t),'method':'animate','args':[[str(t)],{'mode':'immediate','frame':{'duration':0,'redraw':False},'transition':{'duration':0}}]} for t in range(1,params['periods']+1)]}]
    return {'data':data,'layout':lay,'frames':[{'name':str(t),'layout':frame_layout(t)} for t in range(1,params['periods']+1)]},rows

def build(output):
    output.mkdir(parents=True,exist_ok=True)
    hashes=load('hashes.json')
    for name,expected in hashes.items():
        actual=digest(INPUTS/name)
        if actual!=expected:raise ValueError(f'Entrada modificada: {name}: {actual} != {expected}')
    catalogue={Path(w['path']).stem:w for w in load('source_catalog.json')['widgets']}
    sources=load('rmd_sources_capture.json')
    assert sources['head']==TARGET_COMMIT
    manifest=[];checks=[];specs={}
    for number,definition in DEFINITIONS.items():
        d=definition;source=load(d['source']+'.json')
        data=style_traces(source['data'],d.get('temporal',False),d.get('xp',False),d.get('yp',False))
        spec={'data':data,'layout':layout(d['title'],d['x'],d['y'],d.get('temporal',False),d.get('xp',False),d.get('yp',False)),'frames':[]}
        assert [(t['x'],t['y']) for t in data]==[(t['x'],t['y']) for t in source['data']]
        bases={}
        if number in [100,102]:
            for trace in data:
                assert trace['x'].count(2000)==1
                base=trace['y'][trace['x'].index(2000)]
                assert base>0 and all(y>0 for y in trace['y'])
                bases[trace['name']]=base
                trace['y']=[math.log(y/base) if number==100 else 100*(y/base) for y in trace['y']]
        period,period_by_country=temporal_period(data) if d.get('temporal') else ('El archivo gráfico de dispersión no conserva el año por observación; no se infiere del orden ni de x.',{})
        limitations=['Reconstrucción docente nueva; la correspondencia con la apariencia o datos del ID histórico no está autenticada.','Se preserva la edición archivada; no se incorporan observaciones nuevas.']
        if not d.get('temporal'):limitations.append('La dispersión no conserva un campo temporal; no se asignan años a los puntos.')
        if number in [72,118,120]:limitations.append('Los textos repetidos de Ideas no distinguen estas variantes. La elección de variables para este destino es una adaptación editorial explícita.')
        if number==100:limitations.append('Transformación nueva desde los niveles originales: ln(gasto/gasto de 2000), en eje lineal. El gráfico archivado usaba valores ln y además eje logarítmico; esta reconstrucción evita esa doble transformación.')
        if number in [100,102]:limitations.extend(['La normalización elimina la escala de cada serie y no permite comparar tamaños monetarios absolutos entre países.','No se acreditan moneda, multiplicador, PPA ni base de precios en los datos originales; tampoco se certifica la comparabilidad metodológica a lo largo del tiempo. No se interpretan a partir de PRICE_BASE=Q.'])
        if number in [132,134]:limitations.append('Consumo del gobierno/PIB no es una tasa impositiva. La nube de puntos no identifica un efecto causal.')
        info=catalogue[d['source']];input_names=[d['source']+'.json',d['code'],'source_catalog.json','rmd_sources_capture.json']
        entry={'identity':f'iguzmanvt:{number}','slug':f'iguzmanvt-{number}','title':d['title'],'module':'Taxes' if number in [132,134] else 'Ideas','description':d['description'],'formula':d['formula'],'units':d['units'],'period':period,'period_by_series':period_by_country,'source_urls':[info['primary_source_url'],PRIMARY+'code/'+d['code']],'source_paths':['inputs/'+n for n in input_names],'source_vintage':'StudyGuide archivado en '+SOURCE_COMMIT+'; se usan las coordenadas existentes, no una nueva versión de PWT/OECD.','limitations':limitations,'kind':'reconstruccion_datos_archivados','inputs_sha256':{'inputs/'+n:hashes[n] for n in input_names},'observations':observations(data),'historical_identity_authenticated':False,'source_blob':info['blob'],'source_file_sha256':info['source_sha256']}
        if bases:entry['normalization']={'year':2000,'base_values_in_archived_units':bases,'common_base_verified':True}
        manifest.append(entry);specs[number]=spec;checks.append({'identity':entry['identity'],'archived_x_equal':True,'archived_y_equal':number not in [100,102],'documented_normalization':number in [100,102],'effective_pairs':entry['observations']['total_effective_pairs'],'frames':0})
    # ID 116 uses the complete dated materialized local figure, including nine countries.
    local=load('fig_local_puntos_con_fecha.json');old=load('saved_fig_provenance.json')
    assert len(local)==265 and len({r['COUNTRY'] for r in local})==9
    data=[]
    for key in sorted({r['COUNTRY'] for r in local}):
        rows=[r for r in local if r['COUNTRY']==key]
        trace=style_traces([{'name':key,'x':[r['lnrdworker'] for r in rows],'y':[r['g10.accttfp'] for r in rows]}],ypercent=True)[0]
        trace['customdata']=[[r['obsTime'],r['UNIT'],r['MEASURE']] for r in rows]
        trace['hovertemplate']='<b>%{fullData.name}</b><br>Año: %{customdata[0]}<br>ln(FTE): %{x:.4f}<br>Crecimiento archivado: %{y:.3%}<extra></extra>'
        data.append(trace)
    title='Investigadores y productividad: nueve países'
    specs[116]={'data':data,'layout':layout(title,'ln(investigadores equivalentes a tiempo completo)','Crecimiento de la productividad (a 10 años)',ypercent=True),'frames':[]}
    names=['fig_local_puntos_con_fecha.json','saved_fig_provenance.json','rmd_sources_capture.json']
    periods={COUNTRIES[k]:[min(r['obsTime'] for r in local if r['COUNTRY']==k),max(r['obsTime'] for r in local if r['COUNTRY']==k)] for k in sorted({r['COUNTRY'] for r in local})}
    manifest.append({'identity':'iguzmanvt:116','slug':'iguzmanvt-116','title':title,'module':'Ideas','description':'Nueva presentación de las 265 observaciones del objeto gráfico local de 2021, con nueve países, años y códigos de unidad conservados. Se elige para este destino por su contexto docente; no se afirma que el objeto haya sido históricamente el ID 116.','formula':'x = lnrdworker y y = g10.accttfp materializados en el objeto local. Se conservan sin recalcular; la definición de la tasa no se amplía a partir de su nombre.','units':'x: ln de investigadores FTE (UNIT=FTE, POWERCODE=0, MEASURE=FTE); y: tasa decimal archivada denominada crecimiento a 10 años, mostrada como porcentaje.','period':'1981–2019; 265 observaciones; cobertura por país conservada en obsTime.','period_by_series':periods,'source_urls':[TARGET+'recursos_graficas/datos/fig-local-2021-puntos-originales.json',TARGET+'recursos_graficas/datos/fig-local-2021-procedencia.json'],'source_paths':['inputs/'+n for n in names],'source_vintage':'Objeto local del curso Otoño 2021, preservado en Crecimiento@'+TARGET_COMMIT+'; se utiliza su tabla materializada, sin ejecutar el objeto R.','limitations':['Asignación editorial al destino 116, no recuperación de identidad histórica.','El objeto local difiere en muestra y valores del objeto gráfico inglés de seis países; no se fusionan sus observaciones.','No se recalcula la tasa de productividad ni se atribuye una edición estadística no acreditada por el objeto.'],'kind':'reconstruccion_objeto_local_archivado','inputs_sha256':{'inputs/'+n:hashes[n] for n in names},'observations':observations(data),'historical_identity_authenticated':False})
    checks.append({'identity':'iguzmanvt:116','source_rows':len(local),'output_points':sum(len(t['x']) for t in data),'all_dated_records_preserved':True,'frames':0})
    # ID76 is a new execution of the documented model, not the archived R script.
    parameters=load('model76_parameters.json');model,rows=model_spec(parameters);reference=load('model76_reference.json')
    assert len(rows)==len(reference)==500
    differences=[abs(a[k]-b[k]) for a,b in zip(rows,reference) for k in ['ratio','growth']]
    assert all(a['scenario']==b['scenario'] and a['t']==b['t'] for a,b in zip(rows,reference))
    assert max(differences)<1e-12
    specs[76]=model;names=['model76_parameters.json','model76_reference.json','Guide_ME_gA.r','source_catalog.json','rmd_sources_capture.json']
    manifest.append({'identity':'iguzmanvt:76','slug':'iguzmanvt-76','title':model['layout']['title']['text'],'module':'Ideas','description':'Reconstrucción de dos economías con crecimiento de investigadores de 2%. Las trayectorias completas permanecen visibles; el control temporal resalta los puntos de cada periodo sin duplicar las observaciones en las trazas principales.','formula':'gA_t = theta·R_t^lambda/A_t^(1−phi); A_(t+1)=(1+gA_t)A_t; R_(t+1)=(1+gR)R_t. theta=0.01, lambda=1, phi=0, gR=0.02, R_1=10, A_A,1=2, A_B,1=10. R/A=gA/theta. Límite R/A=2 y gA=0.02.','units':'R/A: investigadores por unidad de productividad del modelo; crecimiento decimal por periodo, mostrado como porcentaje. Economías hipotéticas, sin países.','period':'250 periodos simulados, t=1…250; 500 observaciones, dos economías. No son años calendario.','source_urls':[PRIMARY+'code/Guide_ME_gA.r',PRIMARY+'plotly/me-gA-dynamics.html'],'source_paths':['inputs/'+n for n in names],'source_vintage':'Parámetros y regla dinámica del modelo archivado en StudyGuide@'+SOURCE_COMMIT+'.','limitations':['Simulación pedagógica, no evidencia de países ni estimación empírica.','Las coordenadas se recalculan en Python y coinciden con las 500 coordenadas archivadas dentro de tolerancia absoluta de 1e-12; no se afirma recuperación del antiguo ID 76.','La vista estática muestra las dos trayectorias completas; los 250 estados sólo mueven los resaltados mediante la disposición visual, sin añadir observaciones.'],'kind':'reconstruccion_modelo_documentado','inputs_sha256':{'inputs/'+n:hashes[n] for n in names},'observations':observations(model['data']),'frames':250,'historical_identity_authenticated':False})
    checks.append({'identity':'iguzmanvt:76','observations':500,'frames':250,'max_abs_difference_from_archived_model':max(differences),'tolerance':1e-12,'asymptote_ratio':2,'asymptote_growth':0.02})
    # Verify archived ln provenance and both new dimensionless normalizations.
    lev=load('oecd-rd-levelrd.json')['data'];logs=load('oecd-rd-logrd.json')['data'];errors=[]
    for a,b in zip(lev,logs):
        assert a['name']==b['name'] and a['x']==b['x']
        errors += [abs(round(math.log(v),2)-w) for v,w in zip(a['y'],b['y'])]
    assert max(errors)<1e-12 and specs[100]['layout']['yaxis']['type']=='linear'
    for raw,log,index in zip(lev,specs[100]['data'],specs[102]['data']):
        assert raw['x']==log['x']==index['x']
        at=raw['x'].index(2000)
        assert log['y'][at]==0 and index['y'][at]==100
        assert all(abs(a-math.log(b/100))<1e-12 for a,b in zip(log['y'],index['y']))
    checks.append({'identity':'iguzmanvt:100','linear_y_axis':True,'original_log_archive_matches_rounded_level_logs':True,'matched_level_observations':len(errors),'max_original_log_rounding_difference':max(errors),'new_definition':'ln(gasto/gasto de 2000)','base_year':2000,'base_value':0,'series':6})
    checks.append({'identity':'iguzmanvt:102','new_definition':'100*gasto/gasto de 2000','base_year':2000,'base_value':100,'series':6,'coordinates':227})
    assert sorted(specs)==EXPECTED and len(manifest)==len(EXPECTED)
    for number in EXPECTED:
        spec=specs[number]
        assert spec['data'] and title_text(spec['layout']['title'])
        for trace in spec['data']:
            assert len(trace['x'])==len(trace['y']) and len(trace['x'])>0
            assert all(v is None or isinstance(v,(int,float)) and math.isfinite(v) for v in trace['x']+trace['y'])
        write(output/f'iguzmanvt-{number}.json',spec)
    manifest.sort(key=lambda e:int(e['identity'].split(':')[1]))
    for entry in manifest:entry['output_sha256']=digest(output/(entry['slug']+'.json'))
    write(output/'manifest.json',{'schema_version':1,'generator':'generar.py','generator_sha256':digest(Path(__file__)),'baseline_commit':TARGET_COMMIT,'authorization_scope':'Reconstrucciones docentes nuevas de 11 destinos; no se atribuye autenticidad histórica.','source_license':'StudyGuide: MIT, Copyright (c) 2020 Dietz Vollrath; LICENSE-StudyGuide adjunta.','entries':manifest})
    write(output/'validation.json',{'expected_ids':['iguzmanvt:'+str(x) for x in EXPECTED],'input_hashes_verified':len(hashes),'checks':checks,'output_files':len(EXPECTED),'network_used':False,'R_or_archived_HTML_executed':False})
    return {'output':str(output),'figures':len(EXPECTED),'points_in_base_traces':sum(sum(len(t['x']) for t in spec['data']) for spec in specs.values()),'model_frames':250,'max_model_difference':max(differences)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination',nargs='?',help='Directorio de salida (también puede usar --output).')
    parser.add_argument('--output',dest='output',help='Directorio de salida.')
    args=parser.parse_args()
    if args.destination and args.output:parser.error('Use sólo destination o --output.')
    print(json.dumps(build(Path(args.output or args.destination or HERE).resolve()),ensure_ascii=False))
