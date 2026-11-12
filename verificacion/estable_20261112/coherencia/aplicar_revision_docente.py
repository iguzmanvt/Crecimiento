from pathlib import Path
import argparse, re, json, hashlib, math, subprocess

ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);args=ap.parse_args()
root=Path(args.repo); report=[]

def digest(x): return hashlib.sha256(x.encode()).hexdigest()
def invariants(s):
    return {'r_chunks':re.findall(r'```\{r.*?```',s,re.S),
            'images':re.findall(r'(?:readPNG|readJPEG)\([^\n]+|<img[^>]+>',s)}

def edit(module,pairs,fn=None):
    for p in sorted((root/'Clases_Crecimiento_Economico'/module).rglob('*.Rmd')):
        before=p.read_text(encoding='utf-8-sig');after=before;changes=[]
        for old,new,reason in pairs:
            count=after.count(old)
            if count: after=after.replace(old,new);changes.append({'reason':reason,'matches':count})
        if fn: after,extra=fn(after,'Nota' not in p.stem);changes.extend(extra)
        if after!=before:
            assert invariants(before)==invariants(after),(p,'changed R chunks or images')
            p.write_text(after,encoding='utf-8',newline='\n')
            report.append({'path':p.relative_to(root).as_posix(),'before_sha256':digest(before),'after_sha256':digest(after),'r_chunks_preserved':len(invariants(before)['r_chunks']),'images_preserved':len(invariants(before)['images']),'changes':changes})

edit('Taxes',[
('la proporción de personas en el 1% ha aumentado','la proporción del ingreso recibida por el 1% de mayores ingresos ha aumentado','El grupo sigue siendo 1% de las unidades; cambia su participación del ingreso'),
('El efecto de los impuestos no siempre es igual. En la gráfica, el recorte a los impuestos en 2003 no tuvo un efecto tan fuerte en el cambio del crecimiento promedio del PIB como en el empleo.','La gráfica describe el crecimiento del PIB y del empleo alrededor de 2003. Comparar sus trayectorias no permite aislar el efecto causal del recorte fiscal frente a otros cambios de la economía.','Distinguir asociación temporal de identificación causal'),
('Yagan estudió el efecto de este recorte de 2003. Con un recorte en la tasa de impuestos a los dividendos, podríamos esperar que las corporaciones C (que pagan dividendos) incrementaran su gasto de inversión en relación con las corporaciones S (que no los pagan) pero no encontró ningún efecto en sus gastos de inversión.','[Yagan (2015)](https://www.aeaweb.org/articles?id=10.1257/aer.20130098) compara corporaciones C, afectadas por el recorte de 2003 al impuesto sobre dividendos, con corporaciones S, cuyo ingreso se atribuye fiscalmente a sus accionistas. La diferencia relevante es el tratamiento tributario. Estima un efecto nulo sobre inversión y remuneración de empleados para la muestra y el periodo estudiados.','Corregir definición C/S y alcance del resultado de Yagan'),
('Ufuk, Akcigit, Grigsby, Nicholas y Stantcheva','Ufuk Akcigit, John Grigsby, Tom Nicholas y Stefanie Stantcheva','Ufuk Akcigit es un autor, no dos'),
('Otra afectación puede ser vía el mercado laboral: esperaríamos que a medida que las tasas del impuesto sobre la renta de las personas físicas disminuyan, los trabajadores estarán más dispuestos a proporcionar trabajo.','Una reducción del impuesto al ingreso puede afectar la oferta laboral mediante efectos de sustitución e ingreso que operan en direcciones opuestas. La respuesta neta debe analizarse, en lugar de suponerse positiva.','Distinguir efectos ingreso y sustitución'),
('Una reducción en la tasa impositiva puede lograr crecimiento en el empleo, pero solo si se hace a los hogares de medianos y bajos ingresos. Esto se debe a 2 razones:','[Zidar (2015, NBER WP 21035)](https://www.nber.org/papers/w21035) encuentra que la relación positiva entre recortes fiscales y crecimiento del empleo en Estados Unidos se concentra en los grupos de menores ingresos; el efecto estimado para el 10% superior es pequeño. Se consideran dos mecanismos posibles:','Evitar regla universal sobre efectos de recortes'),
('La oferta laboral de los hogares de altos ingresos no se ve modificada por las tasas impositivas, mientras que si afecta la de los hogares de mediano y bajo ingreso.','Las respuestas de oferta laboral pueden diferir por nivel de ingreso y por el margen de participación u horas trabajadas.','Evitar respuesta laboral nula universal'),
('Los ricos ahorrarían el recorte de impuestos, mientras que los siguientes estratos lo gastan.','Una mayor propensión a consumir puede aumentar el efecto de demanda de un recorte. El resultado depende también de su financiación y del contexto macroeconómico.','Explicar mecanismo como hipótesis condicional')])

edit('Competition',[
('Estructura de monopsonio.','Ejemplo de duopolio de oferentes, no de un único comprador.','Distinguir monopsonio y duopolio'),
('cobrará 2.9, tomará todo el negocio y, por lo tanto, cobrará un margen de beneficio de aproximadamente 3/2 = 1.5.','podría cobrar 2.9 y obtener un markup precio/costo de 2.9/2 = 1.45. En el límite, con un precio apenas inferior a 3, ese cociente se aproxima a 1.5.','Markup exacto frente a límite')])

edit('Patents',[
('Otorga un monopolio temporal.','Otorga un derecho temporal y territorial de excluir usos de la invención protegida; su existencia no garantiza por sí sola un monopolio en el mercado.','Derecho de exclusión y poder de mercado son distintos'),
('Acuerdo sobre aspectos de derecho de propiedad intelectual relacionados con el comercio que garantiza que el proceso para otorgar patentes sea igual en todo el mundo para cualquier producto en cualquier campo de la tecnología.','El [Acuerdo sobre los ADPIC (TRIPS), artículo 27](https://www.wto.org/english/docs_e/legal_e/trips_e.htm), establece requisitos mínimos de patentabilidad y no discriminación, con las excepciones que prevé el propio acuerdo. Los procedimientos y el alcance territorial dependen de cada jurisdicción.','ADPIC no unifica todos los procedimientos'),
('El plazo de protección por un periodo de 20 años mínimo.','El artículo 33 de los ADPIC exige que el plazo disponible no termine antes de 20 años contados desde la fecha de presentación de la solicitud.','Precisar inicio del plazo ADPIC'),
('**Objetivo**: dar prioridad al aplicante que concibió primero el invento si es que dos aplican para la misma patente.','**Cambio de prioridad**: la AIA sustituyó el sistema de primero en inventar por el de **primer inventor en presentar la solicitud**, aplicable según la fecha efectiva de presentación de la invención reivindicada.','Corregir dirección del cambio de AIA'),
('**First to file (primer aplicante en hacer el registro tiene prioridad)** - afecta diferente a las compañías dependiendo del tamaño, industria y otras variables.','**First-inventor-to-file**: las disposiciones entraron en vigor el 16 de marzo de 2013. Se aplican los requisitos de autoría, prioridad y excepciones correspondientes; véase [USPTO, recursos FITF](https://www.uspto.gov/patents/first-inventor-file-fitf-resources).','Precisar fecha y alcance first-inventor-to-file'),
('Las patentes pueden pertenecer hasta a 7 clases del IPC.','La IPC tiene ocho secciones principales y múltiples niveles de clasificación. Una patente puede recibir varios símbolos según sus características; el número de símbolos no mide por sí solo el alcance jurídico. [OMPI, estructura de la IPC](https://www.wipo.int/en/web/classification-ipc/preface).','Eliminar supuesto límite universal de siete clases')])

edit('Ideas',[
('Bienes no rivales producen rendimientos crecientes a escala al ser excluibles','La no rivalidad permite reutilizar una idea y genera rendimientos crecientes al considerar conjuntamente ideas e insumos rivales. La exclusión parcial afecta la posibilidad de apropiarse de rendimientos e incentivar su producción','Separar no rivalidad de exclusión'),
('Sin protección de patentes nadie querrá innovar.','Sin patentes puede haber innovación por otros incentivos, como la ventaja de entrar primero, el secreto o la financiación pública. En el modelo, la apropiación de rendimientos sostiene la inversión privada en ideas.','No convertir supuesto de modelo en ausencia universal de innovación'),
('Los factores rivales de la producción no tienen retornos constantes o crecientes a escala.','Manteniendo fijas las ideas, la producción tiene rendimientos constantes a escala en los factores rivales.','Enunciar correctamente agotamiento del producto'),
('Para Romer, las primeras dos son ciertas: (1) ejemplo de replicación de la fábrica; (2) sustenta su teoría; (3) no puede ser verdad. Si los propietarios de los factores no rivales son compensados de alguna manera, será menos que su producto marginal.','Con rendimientos constantes en los factores rivales, pagar a cada uno su producto marginal agota el producto (teorema de Euler). Un pago positivo adicional a las ideas exige apartarse de alguna de esas condiciones. Romer utiliza competencia monopolística y apropiación parcial de las rentas de innovación.','Corregir lógica Euler y remuneración de ideas'),
('Para Lucas, la 1 y la 3 son verdaderas: Esto puede ser verdadero si sólo hay factores rivales y el crecimiento balanceado se explica con la adquisición de conocimiento.','En la lectura de Lucas con externalidades del capital humano, las empresas pueden remunerar los factores rivales a su producto marginal privado, mientras el efecto externo del conocimiento no recibe un pago separado.','Distinguir capital humano rival y externalidad'),
('Bloom, Jones, Van Reene, Web (BJVW), 2019','Bloom, Jones, Van Reenen y Webb (BJVW), AER 2020','Autores y edición publicada'),
('se necesitan 78 veces más investigadores para descubrir cómo duplicar la densidad de los transistores que en 1970.','el esfuerzo de investigación de semiconductores es más de 18 veces mayor que a principios de los años setenta para sostener la duplicación de densidad estudiada. [Bloom et al. (2020), resumen](https://www.aeaweb.org/articles?id=10.1257/aer.20180338).','Corregir 78 a más de 18 según fuente primaria'),
('si la población que proporciona investigadores comienza a crecer más lentamente, entonces el esfuerzo crece más lentamente y la tasa de crecimiento a largo plazo de las ideas continúa.','si la población que proporciona investigadores crece más lentamente, el esfuerzo aumenta más despacio y el crecimiento de largo plazo de las ideas disminuye bajo los supuestos del modelo semiendógeno.','Corregir dirección de predicción semiendógena')])

edit('Pensions',[
('son un pago entregado de manera regular por un gobierno o empresa a una persona de un fondo de inversión a la que la persona (o su patrón) contribuyó durante sus años laborales.','son pagos regulares durante el retiro. Pueden financiarse con contribuciones de trabajadores activos, recursos presupuestarios o activos acumulados; la definición no presupone una cuenta de inversión individual.','Incluir reparto en definición de pensiones'),
('Nuevo saldo = (Saldo anterior x tasa de interés) + Nueva aportación','Nuevo saldo = Saldo anterior × (1 + tasa de rendimiento neta) + Nueva aportación. Se supone que la aportación se realiza al final del periodo.','Conservar principal y precisar momento de aporte'),
('z^{k}_{t+1}=Rb^{k}_{t+1}','z^{k}_{t+1}=Rb^{k}_{t}','El ahorro realizado en t genera pago en t+1'),
('Pensión mínima garantizada tras 10 años de contribuciones.','La Ley de 1973 requiere un mínimo de 500 semanas reconocidas, además de los requisitos de edad, baja y conservación de derechos. [IMSS, pensión de vejez](https://www.imss.gob.mx/pensiones/preguntas-frecuentes/quien-puede-solicitar-pension-de-vejez).','Semanas reconocidas no diez años consecutivos'),
('no acumulaban 10 años seguidos de contribuciones','no reunían las semanas reconocidas requeridas o no conservaban vigentes sus derechos','Eliminar exigencia falsa de cotización consecutiva'),
('Se añade una fracción por cada año adicional de contribuciones después del mínimo (10 años).','Se añaden incrementos por cotizaciones reconocidas posteriores a las primeras 500 semanas, según las reglas del esquema.','Alinear descripción con unidad legal'),
('Pensión mínima garantizada después de 25 años de contribuciones.','En el diseño original de 1997, el requisito era de 1,250 semanas de cotización. Este parámetro es histórico: fue modificado por la reforma de 2020.','Distinguir diseño histórico de requisito vigente'),
('El total de contribuciones para el retiro, ahora representa alrededor del 13.5% del salario del trabajador promedio.','La referencia histórica al 13.5% depende de los conceptos incluidos y del salario considerado; no debe usarse como una tasa uniforme de aportación al retiro ni como parámetro vigente.','No presentar agregado histórico como tasa universal actual')])

edit('Labor',[
('Esto tratado así, es falso:','El desplazamiento en un sector no basta para predecir desempleo masivo permanente:','Evitar negar fricciones o pérdidas individuales'),
('Así que la economía va a encontrar algo que estas personas puedan hacer.','La creación histórica de empleos muestra capacidad de ajuste, pero no garantiza que cada trabajador desplazado encuentre de inmediato un empleo equivalente.','No deducir garantía individual de una serie agregada'),
('**límite de las máquinas pues no tienen conocimiento tácito.** Todo debe especificarse con precisión para que funcionen. Mientras haya tareas como esa, los robots no pueden reemplazar a los trabajadores, y requerirá que estos, junto con las máquinas, realicen juntos el trabajo.','**obstáculo para automatizar mediante instrucciones explícitas**. El propio [Autor (2014), resumen](https://www.nber.org/papers/w20485), considera el aprendizaje a partir de ejemplos como vía para superar parte de ese obstáculo. La complementariedad y la sustitución dependen de las tareas.','Polanyi no constituye imposibilidad permanente frente al aprendizaje automático')])

edit('Environment',[
('The Environment and Directed Climate Change (Acemoglu, Aghion; 2012)','The Environment and Directed Technical Change (Acemoglu, Aghion, Bursztyn y Hemous; 2012)','Título y autores de fuente primaria'),
('Los países desarrollados son los que más contaminan.','La figura compara emisiones territoriales de CO₂ por habitante. Debe distinguirse esta medida de las emisiones totales y de la contaminación local del aire.','Evitar confundir CO2 per cápita con contaminación total'),
('La política óptima consiste en impuestos al carbón y subsidios a la I&D de\nenergías limpias temporales que dirigen la innovación al sector limpio','En el modelo, impuestos al carbono y subsidios a la I+D orientan la innovación al sector limpio. Cuando los insumos son suficientemente sustituibles, una intervención temporal puede sostener el crecimiento. [Acemoglu et al. (2012), resumen](https://www.aeaweb.org/articles?id=10.1257/aer.102.1.131).','Precisar condición suficiente de sustitución')])

# La nota de Environment está ubicada históricamente en Energy.
edit('Energy',[
('The Environment and Directed Climate Change (Acemoglu, Aghion; 2012)','The Environment and Directed Technical Change (Acemoglu, Aghion, Bursztyn y Hemous; 2012)','Título y autores de fuente primaria'),
('Los países desarrollados son los que más contaminan.','La figura compara emisiones territoriales de CO₂ por habitante. Debe distinguirse esta medida de las emisiones totales y de la contaminación local del aire.','Evitar confundir CO2 per cápita con contaminación total'),
('La relación entre reservas y producción aumentó, lo que indica que los descubrimientos de reservas de combustibles fósiles aumentaban más rápido que el uso de energía.','La relación entre reservas y producción aumentó en el periodo de la figura. El cambio puede reflejar descubrimientos, reclasificación económica de reservas o cambios en la extracción; esa razón no identifica por sí sola nuevos descubrimientos.','Distinguir reservas económicas y recurso físico descubierto'),
('La política óptima consiste en impuestos al carbón y subsidios a la I&D de\nenergías limpias temporales que dirigen la innovación al sector limpio','En el modelo, impuestos al carbono y subsidios a la I+D orientan la innovación al sector limpio. Cuando los insumos son suficientemente sustituibles, una intervención temporal puede sostener el crecimiento. [Acemoglu et al. (2012), resumen](https://www.aeaweb.org/articles?id=10.1257/aer.102.1.131).','Precisar condición suficiente de sustitución')])

edit('Slowdown',[
('2.7 trillones','2.7 billones (millones de millones)','Traducir trillion anglosajón a billón español'),
('$17-26 billones de dólares','$17–26 mil millones de dólares','Traducir billions anglosajones'),
('$96 billones de dólares','$96 mil millones de dólares','Traducir billions anglosajones'),
('$54-73 billones de dólares','$54–73 mil millones de dólares','Traducir billions anglosajones'),
('$132 billones de dólares','$132 mil millones de dólares','Traducir billions anglosajones'),
('$995 billones de dólares','$995 mil millones de dólares','Traducir billions anglosajones')])

def converge(s,slides):
    changes=[]
    # Este bloque no contiene código R ni figuras. Conservar cuatro secciones de la presentación.
    start=s.find('<span style="color:blue">**Velocidad de convergencia**</span>')
    end=s.find('<span style="color:blue">**Convergencia condicional:**</span>',start)
    if start>=0 and end>start:
        h='## CÁLCULO DE LA CONVERGENCIA\n\n' if slides else ''
        sections=[
        r'''<span style="color:blue">**Velocidad de convergencia**</span>

- La regresión de Barro relaciona el crecimiento anual medio durante una ventana fija $T$ con el ingreso inicial:

$$\frac{\ln y_T-\ln y_0}{T}=a+\beta_T\ln y_0.$$

- Un coeficiente $\beta_T<0$ describe convergencia beta en esa muestra. No garantiza por sí solo convergencia futura ni una reducción de la dispersión sigma.
''',
        r'''<span style="color:blue">**Coeficiente y velocidad**</span>

- Si dos economías comparten intercepto, al restar sus ecuaciones desaparece $aT$:

$$\ln(y_T^p/y_T^r)=(1+T\beta_T)\ln(y_0^p/y_0^r).$$

- El coeficiente depende de la ventana. Bajo el supuesto adicional de una brecha logarítmica que se cierra a velocidad constante $b$, $1+T\beta_T=e^{-bT}$ y $b=-\ln(1+T\beta_T)/T$. Esta conversión exige $0<1+T\beta_T<1$.
''',
        r'''<span style="color:blue">**Ejemplo de cierre de una brecha**</span>

- Supongamos, sólo para ilustrar, $b=0.005$ al año y ausencia de nuevos choques o diferencias de tendencia:

$$\ln(y_t^p/y_t^r)=e^{-bt}\ln(0.1).$$

- Llegar de una razón de ingreso de 0.1 a 0.9 requiere:

$$t=-\frac{1}{b}\ln\left(\frac{\ln(0.9)}{\ln(0.1)}\right)\approx617\text{ años}.$$
''',
        r'''<span style="color:blue">**Límite de la extrapolación**</span>

- Los 617 años son el resultado de un supuesto ilustrativo de velocidad constante, no una predicción del estudio empírico.

- Sustituir un coeficiente transversal fijo $\beta=-0.005$ en una fórmula lineal para cualquier horizonte producía aproximadamente 190 años. Esa extrapolación confunde el coeficiente de una ventana con una ley dinámica permanente.

''']
        s=s[:start]+('\n'+h).join(sections)+s[end:];changes.append({'reason':'Corregir cancelación de intercepto y distinguir coeficiente transversal de dinámica de convergencia','matches':1})
    pairs=[
    ('Correlación entre PIB per cápita inicial y final es 0 - predice la convergencia condicional.','La convergencia condicional relaciona el crecimiento con el ingreso inicial al controlar por determinantes del estado estacionario; no exige correlación cero entre los niveles inicial y final.'),
    ('Las políticas públicas no influenciarán fácilmente el ingreso de las economías que están en el BGP.','En Solow, un cambio permanente en la tasa de ahorro modifica el nivel de la senda y el crecimiento durante la transición; la tasa de crecimiento de largo plazo depende del progreso tecnológico exógeno.'),
    ('Sustentando así que la divergencia regional no se explique por diferencias en  factores estructurales.','Esto motiva controlar las diferencias estructurales al distinguir convergencia condicional de convergencia absoluta.'),
    ('$(\\frac{1}{t})Ln (y_{i,t})-Ln(y_{i,t-1})=', '$\\ln(y_{i,t}/y_{i,t-1})='),
    ('Las políticas públicas aumentan el PIB potencial, no el PIB real, abriendo una brecha entre estos dos. ¿Por qué?','Para ilustrar una reforma de oferta, supondremos un aumento de la senda potencial y una aproximación gradual del PIB observado. Otras políticas pueden afectar también la demanda y el producto en el corto plazo.'),
    ('Para dar una idea de lo poco que un efecto de las políticas públicas en el crecimiento, utilicemos la siguiente ecuación:','Utilicemos una trayectoria ilustrativa de ajuste, con $0\\leq\\lambda\\leq1$ y $y_t^*=(1+g)^t y_0^*$:'),
    (r'$y_t=(1+g)^t[\lambda^t y_0^* + (1-\lambda^t)y_0]$',r'$y_t=(1+g)^t[(1-\lambda)^t y_0 + (1-(1-\lambda)^t)y_0^*]$'),
    (r'$\lambda$ es la velocidad de convergencia (asumimos la velocidad de la literatura: 2% anual)',r'$\lambda$ es la fracción de la brecha que se cierra por periodo; usamos 0.02 como supuesto ilustrativo'),
    (r'$y_{t+1}=(1+g)^t[ y_t +\lambda (y_t^* -y_t)]$',r'$y_{t+1}=(1+g)[y_t+\lambda(y_t^*-y_t)]$'),
    (r'$\lambda=2$ (por la literatura)',r'$\lambda=0.02$ (2% por año, supuesto del ejercicio)'),
    ('16 trillones','16 billones de dólares (millones de millones)'),
    ('17 trillones','17 billones de dólares'),
    ('1 trillón','1 billón'),
    (r']-1=2.13$',r']-1=0.021275=2.1275\%$'),
    (r']-1=2.25$',r']-1=0.02255=2.255\%$'),
    ('0.12 puntos porcentuales mayor en el periodo.','0.1275 puntos porcentuales más en el periodo. Son valores supuestos, no cifras observadas de Estados Unidos.'),
    ('Pero ninguna reforma hará una diferencia realmente apreciable para el crecimiento económico de un año a otro.','La velocidad del efecto depende de la reforma y de los canales de transmisión. Este ejemplo de ajuste gradual no establece un límite general a sus efectos de corto plazo.'),
    ('Esa es la única forma de aumentar considerablemente la tasa de crecimiento a corto plazo. **¿Es lo deseable? No:**','Su efecto depende de la capacidad ociosa, la financiación y la respuesta de precios y política monetaria. Para evaluarlo deben considerarse:'),
    ('El efecto sólo es en un periodo.','La duración del efecto y su relación con la senda potencial.'),
    ('Incremento en el gasto público de 2019 suficiente para que el PIB potencial sea igual al PIB real.','Se supone un cierre inicial de la brecha de producto: $y_0=y_0^*=17$. El ejercicio no calcula el gasto necesario para conseguirlo.'),
    (r'$y_1=(1+0.02)^t[0.02^1 (17) + (1-0.021)(17)]=17.34$',r'$y_1=1.02[(1-0.02)17+0.02(17)]=17.34$'),
    (r'$y_1=(1+0.02)^t[0.02^1 (18) + (1-0.021)(16)]=16.36$',r'$y_1=1.02[(1-0.02)16+0.02(18)]=16.3608$')]
    for old,new in pairs:
        if old in s:
            count=s.count(old);s=s.replace(old,new);changes.append({'reason':'Coherencia algebraica, unidades y alcance del ejemplo de convergencia','matches':count,'old':old})
    return s,changes
edit('Convergence',[],converge)

out=root/'verificacion/estable_20261112/coherencia';out.mkdir(parents=True,exist_ok=True)
# Controles de comportamiento: t=0, pesos, recurrencia, límites lambda y reproducción de resultados publicados en texto.
checks=[]
def check(name,condition,actual):
    assert condition,(name,actual); checks.append({'check':name,'passed':bool(condition),'actual':actual})
def path(t,y0,star,g,l): return (1+g)**t*((1-l)**t*y0+(1-(1-l)**t)*star)
for l in (0,.02,.3,1):
    check(f'Condicion inicial lambda={l}',abs(path(0,16,17,.02,l)-16)<1e-12,path(0,16,17,.02,l))
    for t in (0,1,5,50):
        y=path(t,16,17,.02,l);next_y=path(t+1,16,17,.02,l);rec=1.02*(y+l*(1.02**t*17-y))
        check(f'Recurrencia t={t},lambda={l}',abs(next_y-rec)<1e-10,{'closed_form':next_y,'recurrence':rec})
check('Sin ajuste lambda=0 conserva distancia relativa',abs(path(20,16,17,.02,0)/1.02**20-16)<1e-12,path(20,16,17,.02,0)/1.02**20)
check('Ajuste completo lambda=1 alcanza senda al primer paso',abs(path(1,16,17,.02,1)-1.02*17)<1e-12,path(1,16,17,.02,1))
gain17=100*(path(1,16,17,.02,.02)/16-1);gain18=100*(path(1,16,18,.02,.02)/16-1)
check('Crecimiento supuesto 17',abs(gain17-2.1275)<1e-9,gain17)
check('Crecimiento supuesto 18',abs(gain18-2.255)<1e-9,gain18)
check('Incremento en puntos porcentuales',abs(gain18-gain17-.1275)<1e-9,gain18-gain17)
t90=-math.log(math.log(.9)/math.log(.1))/.005;ratio=math.exp(math.exp(-.005*t90)*math.log(.1))
check('Brecha 10% a 90% bajo velocidad supuesta',abs(ratio-.9)<1e-12,{'years':t90,'ratio':ratio,'b':.005})
check('Pension sin rendimiento conserva principal',100*(1+0)+10==110,100*(1+0)+10)
check('Pension con rendimiento y aportacion final',100*(1+.05)+10==115,100*(1+.05)+10)
check('Ahorro t paga en t+1',1.05*100==105,{'b_t':100,'R':1.05,'z_t_plus_1':1.05*100})
(out/'parches.json').write_text(json.dumps({'date':'2026-11-12','files':report,'invariants':'Bloques R completos y llamadas/etiquetas de imagen idénticos antes y después'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'formulas.json').write_text(json.dumps({'date':'2026-11-12','checks':checks,'all_passed':True},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files_changed':len(report),'paths':[x['path'] for x in report],'checks':len(checks),'all_passed':True},ensure_ascii=True))
