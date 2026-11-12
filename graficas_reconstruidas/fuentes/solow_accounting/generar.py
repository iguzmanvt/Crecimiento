"""Reconstruye 23 gráficos didácticos desde insumos PWT10.0 archivados.
Uso: python generar.py DIRECTORIO_VACIO
Sólo biblioteca estándar; no red, publicación ni ejecución de Rmd.
"""
from pathlib import Path
import argparse,csv,json,math,hashlib,statistics,collections

ROOT=Path(__file__).resolve().parent
BLUE='#1f77b4';ORANGE='#ff7f0e';GREEN='#2ca02c';RED='#d62728';GRAY='#7f7f7f'
COLORS=[BLUE,ORANGE,GREEN,RED,'#9467bd']
PWT_URL='https://www.rug.nl/ggdc/docs/pwt100.xlsx'
GUIDE='https://github.com/dvollrath/StudyGuide/blob/3a8c79f20022ef7b985b392d73921839a4317883/'
COMMON_LIMIT='Reconstrucción didáctica autorizada; no se afirma identidad con el gráfico Chart Studio original.'
VINTAGE='PWT 10.0, libro con revisión de junio de 2021; copia del repositorio 8265d179322918f035cc4102f1bc9403cbcbb1dc.'
COUNTRIES={'USA':'Estados Unidos','DEU':'Alemania','KOR':'Corea del Sur','CHN':'China','JPN':'Japón'}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_rows(name):
    with (ROOT/'inputs'/name).open(encoding='utf8',newline='') as f:
        rows=list(csv.DictReader(f))
    for r in rows:
        for k in r:
            if k in ('countrycode','country'):continue
            r[k]=None if r[k]=='' else int(r[k]) if k in ('year','excel_row') else float(r[k])
    return rows
def valid(row,*keys):return all(row.get(k) is not None and math.isfinite(row[k]) and row[k]>0 for k in keys)
def line(xs,ys,name,color=BLUE,dash=None,mode='lines'):
    d={'type':'scatter','mode':mode,'x':list(xs),'y':list(ys),'name':name,'line':{'color':color,'width':2.5},'marker':{'color':color,'size':5},'connectgaps':False,'hovertemplate':'%{x}<br>%{y:.4f}<extra>%{fullData.name}</extra>'}
    if dash:d['line']['dash']=dash
    return d
def layout(title,xlabel,ylabel,simulation=False):
    return {'title':{'text':title,'x':0.02,'xanchor':'left'},'template':'plotly_white','paper_bgcolor':'white','plot_bgcolor':'white','colorway':COLORS,'font':{'family':'Arial, sans-serif','size':14,'color':'#2a3f5f'},'xaxis':{'title':{'text':xlabel},'showgrid':True,'gridcolor':'#e5ecf6','zeroline':False},'yaxis':{'title':{'text':ylabel},'showgrid':True,'gridcolor':'#e5ecf6','zeroline':True,'zerolinecolor':'#c8d3df'},'legend':{'orientation':'h','x':0,'y':-0.18},'margin':{'l':80,'r':30,'t':80,'b':120},'hovermode':'x unified','annotations':[{'text':'Simulación didáctica · no son observaciones' if simulation else 'Reconstrucción con PWT 10.0 · identidad histórica no acreditada','xref':'paper','yref':'paper','x':0,'y':1.04,'xanchor':'left','showarrow':False,'font':{'size':11,'color':'#586577'}}]}
def fit(rows,start,end,yfunc):
    selected=[r for r in rows if start<=r['year']<=end and valid(r,'rgdpna','pop')]
    xs=[r['year'] for r in selected];ys=[yfunc(r) for r in selected]
    assert len(xs)>=3
    mx=statistics.mean(xs);my=statistics.mean(ys)
    b=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs)
    a=my-b*mx
    return {'start':min(xs),'end':max(xs),'n':len(xs),'intercept_calendar_year':a,'slope':b,'growth_percent_annual_log':100*b}
def predicted(model,years):return [model['intercept_calendar_year']+model['slope']*y for y in years]
def logypc(r):return round(math.log(r['rgdpna'])-math.log(r['pop']),2)
def controls(frames):
    return {'updatemenus':[{'type':'buttons','direction':'left','x':0,'y':1.14,'buttons':[{'label':'Reproducir','method':'animate','args':[None,{'fromcurrent':True,'frame':{'duration':350,'redraw':True},'transition':{'duration':0},'mode':'immediate'}]},{'label':'Pausar','method':'animate','args':[[None],{'frame':{'duration':0,'redraw':False},'mode':'immediate'}]}]}],'sliders':[{'currentvalue':{'prefix':'Periodo: '},'pad':{'t':35},'steps':[{'label':f['name'],'method':'animate','args':[[f['name']],{'frame':{'duration':0,'redraw':True},'transition':{'duration':0},'mode':'immediate'}]} for f in frames]}]}
def generate(output):
    output=Path(output).resolve()
    if output==ROOT or output in ROOT.parents:raise ValueError('La salida debe ser distinta de la carpeta de fuentes y sus ancestros.')
    output.mkdir(parents=True,exist_ok=True)
    if any(output.iterdir()):raise ValueError('La salida debe estar vacía.')
    provenance=json.loads((ROOT/'inputs/source_manifest.json').read_text(encoding='utf8'))
    for item in provenance['files']:
        p=ROOT/item['path']
        if p.exists() and sha(p)!=item['sha256']:raise ValueError('Insumo alterado: '+item['path'])
    rows=read_rows('pwt100_cases.csv');cross=read_rows('pwt100_cross_sections.csv')
    cases={co:sorted([r for r in rows if r['countrycode']==co],key=lambda r:r['year']) for co in COUNTRIES}
    hashes={f'inputs/{n}':sha(ROOT/'inputs'/n) for n in ['pwt100_cases.csv','pwt100_cross_sections.csv']}
    entries=[];models={};checks={}
    def save(identity,title,module,spec,description,formula,units,period,kind='recalculada',limitations=None,extra=None,guide=None):
        slug=identity.replace(':','-')
        spec.setdefault('frames',[])
        spec['layout']['meta']={'identity':identity,'kind':kind,'historical_identity_authenticated':False}
        (output/(slug+'.json')).write_text(json.dumps(spec,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf8',newline='\n')
        context='Clases_Crecimiento_Economico/'+module+'/';urls=[PWT_URL,'https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100?lang=en']
        if kind=='simulacion_didactica':urls=[]
        if guide:urls.append(GUIDE+'code/'+guide)
        note='Clases_Crecimiento_Economico/Solow/Crecimiento Economico 2 Nota.Rmd' if module=='Solow' else 'Clases_Crecimiento_Economico/Accounting/Crecimiento Economico - Contabilidad del crecimiento Nota.Rmd'
        source_paths=[note]+([] if kind=='simulacion_didactica' else [provenance['source_workbook']])
        if identity.endswith((':104',':110')):source_paths.append('Clases_Crecimiento_Economico/Accounting/Ejemplo Estados Unidos.Rmd')
        urls.extend('https://github.com/iguzmanvt/Crecimiento/blob/'+provenance['repo_commit']+'/'+path.replace(' ','%20') for path in source_paths if path.endswith('.Rmd'))
        input_hashes={'inputs/pwt100_cross_sections.csv':hashes['inputs/pwt100_cross_sections.csv']} if identity.endswith((':160',':162')) else {'inputs/pwt100_cases.csv':hashes['inputs/pwt100_cases.csv']}
        if kind=='simulacion_didactica':input_hashes={'generar.py':sha(ROOT/'generar.py')}
        entry={'identity':identity,'slug':slug,'title':title,'module':module,'description':description,'formula':formula,'units':units,'period':period,'source_urls':urls,'source_paths':source_paths,'source_vintage':VINTAGE if kind!='simulacion_didactica' else 'Modelo y parámetros explícitos en generar.py; datos simulados, no edición estadística.','limitations':[COMMON_LIMIT]+(limitations or []),'kind':kind,'inputs_sha256':input_hashes,'output_sha256':sha(output/(slug+'.json'))}
        if identity in ['iguzmanvt:48','iguzmanv:198']:entry['shared_modules']=[module,'Slowdown']
        if extra:entry.update(extra)
        entries.append(entry)
    # BGP: líneas OLS, no pronósticos estructurales ni parámetros originales recuperados.
    configs=[
      (44,'JPN',[('JPN',1950,1990),('JPN',2000,2019)],'Japón: distintas sendas de crecimiento'),
      (46,'USA',[('USA',1950,2019)],'Estados Unidos: senda de crecimiento ajustada'),
      (48,'USA',[('USA',1950,2000),('USA',2001,2019)],'Estados Unidos: crecimiento antes y después de 2000'),
      (50,'DEU',[('DEU',1991,2019)],'Alemania: senda de crecimiento desde 1991'),
      (54,'KOR',[('KOR',1953,1962),('KOR',2010,2019)],'Corea del Sur: cambio en la senda de crecimiento'),
      (56,'CHN',[('CHN',1952,1969),('KOR',2010,2019)],'China: crecimiento y referencia de Corea del Sur'),
      (62,'CHN',[('CHN',1963,1977),('CHN',1978,2007),('CHN',2008,2019)],'China: distintas etapas de crecimiento')]
    for fid,co,windows,title in configs:
        a=[r for r in cases[co] if valid(r,'rgdpna','pop')];years=[r['year'] for r in a]
        data=[line(years,[logypc(r) for r in a],'PIB per cápita observado',BLUE)]
        fitted=[]
        for j,(fitco,lo,hi) in enumerate(windows):
            m=fit(cases[fitco],lo,hi,logypc);m['countrycode']=fitco;fitted.append(m)
            label=f'Ajuste {COUNTRIES[fitco]} {m["start"]}–{m["end"]}'
            data.append(line(years,predicted(m,years),label,COLORS[(j+1)%len(COLORS)],'dash' if j==0 else 'dot'))
        models[str(fid)]={'fits':fitted}
        save('iguzmanvt:'+str(fid),title,'Solow',{'data':data,'layout':layout(title,'Año','Log natural del PIB per cápita')},'Comparación del logaritmo del PIB per cápita y tendencias lineales estimadas por ventanas declaradas.','ln y = round(ln(rgdpna) − ln(pop), 2); tendencia OLS ln y_t = a + b·año.','Log natural de US$ de 2017 por habitante',[min(years),max(years)],'adaptacion_modelo',['Las ventanas de ajuste son una elección documentada, no especificaciones originales autenticadas. Las rectas fuera de su ventana son extrapolaciones descriptivas, no observaciones ni pronósticos.','PWT rgdpna está a precios nacionales constantes; la referencia entre países no es una comparación de niveles a PPP corrientes.'],{'model_parameters':fitted},'Guide_PWT_Apply.r')
    # Capital/producto.
    for fid,co in [(52,'DEU'),(122,'KOR'),(126,'CHN')]:
        a=[r for r in cases[co] if r['year']>=1960 and valid(r,'rnna','rgdpna')]
        title=f'{COUNTRIES[co]}: relación capital/producto'
        save('iguzmanvt:'+str(fid),title,'Solow',{'data':[line([r['year'] for r in a],[r['rnna']/r['rgdpna'] for r in a],'K/Y')],'layout':layout(title,'Año','Capital / PIB anual (años)')},'Stock de capital dividido entre el flujo anual de producción.','K/Y = rnna / rgdpna.','Años de producción',[a[0]['year'],a[-1]['year']],limitations=['Se inicia en 1960 para reducir la dependencia de supuestos de stock inicial de PWT.'],guide='Guide_PWT_Apply.r')
    # Población: rezagos reales por año, sin interpolación.
    for fid,co in [(58,'CHN'),(124,'KOR')]:
        a={r['year']:r for r in cases[co]};years=[y for y in sorted(a) if y-1 in a and valid(a[y],'pop') and valid(a[y-1],'pop')]
        ys=[math.log(a[y]['pop']/a[y-1]['pop']) for y in years];title=f'{COUNTRIES[co]}: crecimiento de la población';lo=layout(title,'Año final','Crecimiento anual logarítmico');lo['yaxis']['tickformat']='.1%'
        save('iguzmanvt:'+str(fid),title,'Solow',{'data':[line(years,ys,'Población')],'layout':lo},'Variación anual del logaritmo de la población, calculada sólo con años consecutivos.','g_L,t = ln(pop_t) − ln(pop_(t−1)).','Tasa logarítmica anual; eje en porcentaje',[years[0],years[-1]],guide='Guide_PWT_Apply.r')
    # China: transición Solow con parámetros calibrados y supuestos declarados.
    a=[r for r in cases['CHN'] if 1978<=r['year']<=2019 and valid(r,'rgdpna','pop','rnna','csh_i')]
    start=a[0];last=a[-1];alpha=.3;delta=.05;span=last['year']-start['year'];ky0=start['rnna']/start['rgdpna']
    lnA=lambda r:math.log(r['rgdpna']/r['pop'])-(alpha/(1-alpha))*math.log(r['rnna']/r['rgdpna'])
    ga=(lnA(last)-lnA(start))/span;gl=math.log(last['pop']/start['pop'])/span;si=statistics.mean(r['csh_i'] for r in a);ss=si/(delta+ga+gl);speed=(1-alpha)*(delta+ga+gl)
    years=[r['year'] for r in a];ts=[y-start['year'] for y in years];ky=[ss+(ky0-ss)*math.exp(-speed*t) for t in ts]
    model=[alpha/(1-alpha)*math.log(k)+lnA(start)+ga*t for k,t in zip(ky,ts)];bgp=[alpha/(1-alpha)*math.log(ss)+lnA(start)+ga*t for t in ts]
    params={'alpha':alpha,'delta':delta,'s_mean_csh_i':si,'g_population':gl,'g_productivity_residual':ga,'KY_initial':ky0,'KY_steady_state':ss,'lnA_initial':lnA(start),'calibration_years':[start['year'],last['year']]}
    models['60']=params;title='China: transición hacia una senda de crecimiento'
    save('iguzmanvt:60',title,'Solow',{'data':[line(years,[math.log(r['rgdpna']/r['pop']) for r in a],'PIB per cápita observado'),line(years,model,'Transición del modelo',ORANGE,'dash'),line(years,bgp,'Senda de largo plazo del modelo',GRAY,'dot')],'layout':layout(title,'Año','Log natural del PIB per cápita')},'Solow en tiempo continuo, calibrado con China 1978–2019; comparación del modelo con los datos.','q*=s/(δ+g_A+g_L); q(t)=q*+(q0−q*)exp[−(1−α)(δ+g_A+g_L)t]; ln y(t)=α/(1−α)ln q(t)+ln A0+g_A t.','Log natural de US$ de 2017 por habitante',[years[0],years[-1]],'adaptacion_modelo',['δ=0.05 y α=0.3 son supuestos. s usa el promedio de csh_i como aproximación; la proporción a PPP corrientes no es contablemente idéntica a una tasa de inversión a precios nacionales constantes.','g_A se calibra al residual ln(Y/pop)−α/(1−α)ln(K/Y); no es la PTF publicada por PWT. Parámetros constantes e igual condición inicial no garantizan ajuste de toda la trayectoria.'],{'model_parameters':params},'Guide_Sim_Solow_Model.r')
    # 78: dinámica de conocimiento. Solución continua exacta de q'=q(gR-theta*q).
    theta=.01;gr=.02;time=list(range(250));q0s=[5.,1.]
    qs=[[gr/(theta+(gr/q0-theta)*math.exp(-gr*t)) for t in time] for q0 in q0s]
    xr=[.5+i*.05 for i in range(101)]
    data=[line(xr,[theta*x for x in xr],'g_A = θ·R/A',GRAY),line([.5,5.5],[gr,gr],'Crecimiento de investigadores',GREEN,'dash')]
    for j in range(2):data.append(line([qs[j][0]],[theta*qs[j][0]],f'Condición inicial {j+1}',COLORS[j],mode='markers'))
    frames=[{'name':str(t),'traces':[2,3],'data':[{'type':'scatter','x':[qs[j][t]],'y':[theta*qs[j][t]],'customdata':[[t]],'hovertemplate':'Tiempo: %{customdata[0]}<br>R/A: %{x:.3f}<br>g_A: %{y:.3%}<extra></extra>'} for j in range(2)]} for t in time]
    title='Dinámica de la productividad: dos condiciones iniciales';lo=layout(title,'Investigadores / productividad (R/A)','Crecimiento de la productividad',True);lo['xaxis']['range']=[.5,5.5];lo['yaxis'].update(range=[0,.06],tickformat='.1%');lo.update(controls(frames))
    save('iguzmanvt:78',title,'Solow',{'data':data,'layout':lo,'frames':frames},'Simulación del modelo de producción de ideas; ambas condiciones convergen a R/A=2 y g_A=2%.','Ȧ=θR; Ṙ=g_R R; q=R/A; q̇=q(g_R−θq); q(t)=g_R/[θ+(g_R/q0−θ)e^(−g_R t)]; g_A=θq.','R/A normalizado; crecimiento anual; tiempo del modelo',[0,249],'simulacion_didactica',['Parámetros ilustrativos θ=0.01, g_R=0.02 y q0=5 o 1. No son estimaciones ni datos de países.','La formulación continua es una adaptación documentada; no acredita la trayectoria del archivo remoto.'],{'model_parameters':{'theta':theta,'g_R':gr,'q0':q0s,'q_steady':gr/theta}},'Guide_Sim_Prod.r')
    # 82: nivel del PIB per cápita en dos transiciones Solow.
    alpha=.3;delta=.05;ga=.02;gl=.01;si=.2;a0=50.;ss=si/(delta+ga+gl);t=list(range(61));data=[]
    for j,k0 in enumerate([1.,4.]):
        k=[ss+(k0-ss)*math.exp(-(1-alpha)*(delta+ga+gl)*u) for u in t]
        vals=[alpha/(1-alpha)*math.log(ku)+math.log(a0)+ga*u for ku,u in zip(k,t)]
        data.append(line(t,vals,f'Transición: K/Y inicial = {k0:g}',COLORS[j]))
    data.append(line(t,[alpha/(1-alpha)*math.log(ss)+math.log(a0)+ga*u for u in t],'Senda de crecimiento equilibrado',GRAY,'dash'))
    title='Nivel del PIB per cápita: transición en el modelo de Solow'
    save('iguzmanvt:82',title,'Solow',{'data':data,'layout':layout(title,'Tiempo del modelo (años)','Log natural del PIB per cápita simulado',True)},'Dos economías simuladas con los mismos parámetros de largo plazo y diferente capital inicial.','q*=s/(δ+g_A+g_L); q(t)=q*+(q0−q*)exp[−(1−α)(δ+g_A+g_L)t]; ln y=α/(1−α)ln q+ln A0+g_A t.','Unidades normalizadas; log natural; no dólares observados',[0,60],'simulacion_didactica',['Parámetros didácticos elegidos explícitamente; no observaciones ni calibración a un país.'],{'model_parameters':{'alpha':alpha,'s':si,'delta':delta,'g_A':ga,'g_L':gl,'A0':a0,'KY0':[1.,4.],'KY_steady_state':ss}},'Guide_Sim_Solow_Model.r')
    # USA: PTF, capital por trabajador y costo del capital.
    usa=[r for r in cases['USA'] if r['year']>=1960]
    a=[r for r in usa if valid(r,'rtfpna')];years=[r['year'] for r in a];title='Estados Unidos: productividad total de los factores'
    save('iguzmanv:195',title,'Accounting',{'data':[line(years,[100*r['rtfpna'] for r in a],'PTF de PWT')],'layout':layout(title,'Año','Índice de PTF (2017 = 100)')},'PTF a precios nacionales constantes publicada por PWT 10.0.','Índice PTF = 100 · rtfpna.','Índice 2017=100',[years[0],years[-1]],limitations=['No es el residual simplificado del ejercicio de contabilidad de la clase ni una medida pura de tecnología.'])
    a=[r for r in usa if valid(r,'rnna','emp')];title='Estados Unidos: capital por persona empleada'
    save('iguzmanv:196',title,'Accounting',{'data':[line([r['year'] for r in a],[r['rnna']/r['emp'] for r in a],'Capital por persona empleada')],'layout':layout(title,'Año','US$ de 2017 por persona empleada')},'Stock de capital por persona empleada; millones monetarios y millones de personas se cancelan.','k = rnna / emp.','US$ de 2017 por persona empleada',[a[0]['year'],a[-1]['year']],limitations=['Emp mide personas empleadas, no horas ni población total.'])
    a=[r for r in usa if valid(r,'rnna','rgdpna','emp')];base=next(r for r in a if r['year']==1960);years=[r['year'] for r in a];title='Estados Unidos: capital y producción por persona empleada'
    ys1=[100*(r['rnna']/r['emp'])/(base['rnna']/base['emp']) for r in a];ys2=[100*(r['rgdpna']/r['emp'])/(base['rgdpna']/base['emp']) for r in a]
    save('iguzmanv:197',title,'Accounting',{'data':[line(years,ys1,'Capital por persona empleada'),line(years,ys2,'PIB por persona empleada',ORANGE)],'layout':layout(title,'Año','Índice (1960 = 100)')},'Comparación de la evolución relativa de capital y producción por empleado con una base común.','Índice k_t = 100·(rnna_t/emp_t)/(rnna_1960/emp_1960); análogo con rgdpna para y.','Índice 1960=100',[years[0],years[-1]],limitations=['Normalizar ambas series no equipara sus niveles monetarios ni estima elasticidades.'])
    a=[r for r in usa if valid(r,'rnna','rgdpna','labsh')];years=[r['year'] for r in a];title='Estados Unidos: participación del capital en los costos';rr=.05
    cost=[rr*r['rnna']/(r['labsh']*r['rgdpna']+rr*r['rnna']) for r in a];share=[1-r['labsh'] for r in a];lo=layout(title,'Año','Participación');lo['yaxis']['tickformat']='.0%'
    save('iguzmanv:198',title,'Accounting',{'data':[line(years,cost,'Capital en costos (R = 5%)'),line(years,share,'Participación no laboral del PIB',GRAY,'dash')],'layout':lo},'Aproximación al peso del costo del capital y comparación con la participación no laboral del PIB.','W ≈ labsh·rgdpna; RK = 0.05·rnna; participación en costos = RK/(W+RK). Referencia distinta: participación no laboral del PIB = 1−labsh.','Fracción del costo o PIB, respectivamente; eje en porcentaje',[years[0],years[-1]],'adaptacion_modelo',['R=0.05 es un supuesto de rendimiento/costo anual del capital; no es una tasa observada ni incorpora por separado todos los componentes del costo de uso.','labsh mide participación laboral en el PIB; 1−labsh no es automáticamente la participación del capital en costos.'],{'model_parameters':{'R':rr}},'Guide_PWT_Apply.r')
    # 104 y110: fórmula exacta del ejemplo de la clase (sin añadir emp/pop).
    accounting={}
    for r in cases['USA']:
        if not valid(r,'rgdpna','rnna','pop','hc'):continue
        y=logypc(r);ky=round(r['rnna']/r['rgdpna'],2);k=(.3/.7)*math.log(ky);h=math.log(r['hc']);accounting[r['year']]={'y':y,'k':k,'h':h,'a':y-k-h}
    initial=accounting[1960];years=[y for y in sorted(accounting) if y>=1960];title='Estados Unidos: contabilidad del crecimiento'
    values={'Sólo K/Y':[round(accounting[y]['k']+initial['h']+initial['a'],2) for y in years],'Sólo capital humano':[round(initial['k']+accounting[y]['h']+initial['a'],2) for y in years],'Sólo productividad residual':[round(initial['k']+initial['h']+accounting[y]['a'],2) for y in years],'PIB per cápita observado':[accounting[y]['y'] for y in years]}
    save('iguzmanvt:104',title,'Accounting',{'data':[line(years,v,n,COLORS[j]) for j,(n,v) in enumerate(values.items())],'layout':layout(title,'Año','Log natural del PIB per cápita')},'Contrafactuales del ejemplo original: cambia un componente y los demás permanecen en 1960.','ln y=round(ln rgdpna−ln pop,2); q=round(rnna/rgdpna,2); c_K=(0.3/0.7)ln q; c_H=ln hc; c_A=ln y−c_K−c_H. Cada contrafactual se redondea a 2 decimales.','Log natural de US$ de 2017 por habitante',[years[0],years[-1]],limitations=['Se conserva la convención del ejemplo: el término laboral es ln(hc), sin emp/pop. El residual absorbe otros factores omitidos; no equivale a rtfpna de PWT.'],extra={'model_parameters':{'alpha':.3,'reference_year':1960,'round_lngdppc':2,'round_KY':2,'round_traces':2}})
    years=[y for y in sorted(accounting) if y-10 in accounting];title='Estados Unidos: contribuciones al crecimiento en diez años';data=[]
    for j,(key,name) in enumerate([('k','Contribución K/Y'),('h','Contribución capital humano'),('a','Contribución productividad residual')]):
        data.append({'type':'bar','x':years,'y':[100*(accounting[y][key]-accounting[y-10][key])/10 for y in years],'name':name,'marker':{'color':COLORS[j]},'hovertemplate':'Década terminada en %{x}<br>%{y:.3f} puntos porcentuales/año<extra>%{fullData.name}</extra>'})
    actual=[100*(accounting[y]['y']-accounting[y-10]['y'])/10 for y in years];data.append(line(years,actual,'Crecimiento del PIB per cápita','#263746'))
    lo=layout(title,'Año final de la ventana de diez años','Contribución anual (puntos porcentuales logarítmicos)');lo['barmode']='relative'
    checks['accounting_growth_identity_max_abs_error']=max(abs(sum(data[j]['y'][i] for j in range(3))-actual[i]) for i in range(len(years)))
    save('iguzmanvt:110',title,'Accounting',{'data':data,'layout':lo},'Contribuciones de los componentes del ejercicio al crecimiento anualizado logarítmico en ventanas móviles de diez años.','Contribución de j = 100·[c_j(t)−c_j(t−10)]/10; suma = 100·[ln y_t−ln y_(t−10)]/10.','Puntos porcentuales anuales logarítmicos; no CAGR exacta',[years[0],years[-1]],limitations=['Ventanas móviles superpuestas. No se añaden emp/pop al término hc; se conserva el ejercicio de clase.','Las contribuciones no se redondean por separado para mantener su suma numéricamente igual al total.'])
    # Correlaciones internacionales, con la selección explícita del código de referencia.
    bykey={(r['countrycode'],r['year']):r for r in cross};frame_years=[1960,1970,1980,1990,2000,2010,2015];samples={}
    for y in frame_years:
        sample=[]
        for (co,yr),r in sorted(bykey.items()):
            if yr!=y:continue
            lag=bykey.get((co,y-10))
            if lag is None or not valid(r,'rgdpna','pop') or not valid(lag,'pop') or r['csh_i'] is None:continue
            si=round(r['csh_i'],2);gp=math.log(r['pop']/lag['pop'])/10
            if not (-.01<gp<.06 and 0<si<.6):continue
            sample.append({'iso':co,'country':r['country'],'year':y,'si':si,'gpop':gp,'lny':logypc(r),'pop':r['pop']})
        samples[y]=sample
    maxpop=max(r['pop'] for ss in samples.values() for r in ss);sizescale=2*maxpop/(42**2)
    for fid,key,xlabel,title in [(160,'si','Formación bruta de capital / PIB','Inversión y nivel del PIB per cápita'),(162,'gpop','Crecimiento anualizado de la población (diez años)','Población y nivel del PIB per cápita')]:
        def trace(sample):
            return {'type':'scatter','mode':'markers','x':[r[key] for r in sample],'y':[r['lny'] for r in sample],'text':[r['country'] for r in sample],'customdata':[[r['iso'],r['year'],r['pop']] for r in sample],'marker':{'color':BLUE,'opacity':.65,'size':[r['pop'] for r in sample],'sizemode':'area','sizeref':sizescale,'sizemin':4},'name':'Países PWT','hovertemplate':'%{text} (%{customdata[0]})<br>Año: %{customdata[1]}<br>x: %{x:.2%}<br>ln PIB/hab.: %{y:.2f}<br>Población: %{customdata[2]:.1f} millones<extra></extra>'}
        frames=[{'name':str(y),'data':[trace(samples[y])],'traces':[0]} for y in frame_years];lo=layout(title,xlabel,'Log natural del PIB per cápita');lo.update(controls(frames));lo['xaxis']['tickformat']='.0%';lo['hovermode']='closest';lo['showlegend']=False
        lo['xaxis']['range']=[0,.6] if key=='si' else [-.01,.06];lo['yaxis']['range']=[min(r['lny'] for ss in samples.values() for r in ss)-.2,max(r['lny'] for ss in samples.values() for r in ss)+.2]
        save('iguzmanvt:'+str(fid),title,'Solow',{'data':[trace(samples[1960])],'layout':lo,'frames':frames},'Cortes internacionales animados; tamaño de burbuja según población. Selección igual para las dos correlaciones.','y=round(ln(rgdpna/pop),2); inversión=round(csh_i,2); g_L=[ln(pop_t)−ln(pop_(t−10))]/10. Filtros: 0<inversión<0.6 y −0.01<g_L<0.06.','x proporción o tasa anual; y log de US$2017/habitante; tamaño población en millones',[1960,2015],limitations=['Correlación descriptiva, no efecto causal. Se omiten faltantes y observaciones fuera de los filtros declarados; no se rellenan países/años.','rgdpna a precios nacionales constantes puede limitar la comparación de niveles entre países; se conserva la convención didáctica del código de referencia.'],extra={'sample_sizes_by_frame':{str(y):len(samples[y]) for y in frame_years}},guide='Guide_PWT_Correlation.r')
    expected={'iguzmanv:'+str(i) for i in [195,196,197,198]}|{'iguzmanvt:'+str(i) for i in [44,46,48,50,52,54,56,58,60,62,78,82,104,110,122,124,126,160,162]}
    assert {e['identity'] for e in entries}==expected and len(entries)==23
    assert checks['accounting_growth_identity_max_abs_error']<1e-11
    checks.update({'count':23,'countries_case_rows':len(rows),'cross_section_input_rows':len(cross),'all_outputs_finite':True,'original_identities_authenticated':False,'network_used':False})
    manifest={'entries':sorted(entries,key=lambda e:(e['identity'].split(':')[0],int(e['identity'].split(':')[1]))),'count':len(entries),'source_vintage':VINTAGE,'source_workbook_sha256':provenance['workbook_sha256'],'runtime':'Python 3.10+; sólo biblioteca estándar; sin red','checks':checks,'models':models}
    (output/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,allow_nan=False,indent=2)+'\n',encoding='utf8',newline='\n')
    return manifest
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('salida',type=Path);args=parser.parse_args()
    result=generate(args.salida);print(json.dumps(result['checks'],ensure_ascii=False))

