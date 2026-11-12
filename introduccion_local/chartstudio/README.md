# Figuras de Introducción procedentes de Chart Studio

Las 17 vistas sustituyen funcionalmente los destinos externos de Introducción. Abrir `index.html` conservando la carpeta. Se usan datos, código docente archivado y dos reconstrucciones comprobadas. No se autentica ninguno de los originales desaparecidos.

La generación no requiere red ni bibliotecas adicionales de Python:

```sh
python scripts/generar_introduccion_chartstudio.py
```

Las exportaciones se crean con `--export`, Playwright y Chromium. `--output` permite repetir la generación en una carpeta separada. CSV y JSON representan la vista inicial y todos los fotogramas, respectivamente. `iguzmanvt-168_paises.csv` conserva los 150 promedios nacionales que se agrupan en la figura de escolaridad.

Las muestras del código archivado se llaman grupo 1 y grupo 2 porque no constituyen clasificaciones homogéneas de desarrollo. Las razones de consumo e inversión se calculan a precios nacionales corrientes. Las razones capital/producto utilizan `rnna/rgdpna` a precios nacionales constantes. `W/(W+0.05K)` es una aproximación con rendimiento de capital supuesto de 5%, no una participación de costos observada.

| Destino histórico | Sustitución | Método y límite principal |
| --- | --- | --- |
| iguzmanvt:150 | [PIB per cápita: trayectorias del grupo 1](graficas/iguzmanvt-150.html) | ln(rgdpna/pop). Las dos variables están en millones, que se cancelan; cálculo sin redondeo previo. |
| iguzmanvt:152 | [PIB per cápita: trayectorias del grupo 2](graficas/iguzmanvt-152.html) | ln(rgdpna/pop). Las dos variables están en millones, que se cancelan; cálculo sin redondeo previo. |
| iguzmanvt:66 | [PIB por habitante de regiones históricas, 1820–2008](graficas/iguzmanvt-66.html) | ln(gdppc) de agregados regionales archivados de la hoja PerCapita GDP; no se interpolan ausencias. |
| iguzmanvt:154 | [Ingreso inicial y crecimiento posterior: muestra de países](graficas/iguzmanvt-154.html) | x=ln(PIBpc[t−10]); y=(ln(PIBpc[t])−ln(PIBpc[t−10]))/10. Ventanas móviles por país y calendario exacto. |
| iguzmanvt:170 | [Consumo privado como proporción del PIB: grupo 1](graficas/iguzmanvt-170.html) | v_c/v_gdp, sin redondeo previo, con numerador y denominador en la misma moneda y precios corrientes. |
| iguzmanvt:172 | [Consumo privado como proporción del PIB: grupo 2](graficas/iguzmanvt-172.html) | v_c/v_gdp, sin redondeo previo, con numerador y denominador en la misma moneda y precios corrientes. |
| iguzmanvt:174 | [Formación bruta de capital como proporción del PIB: grupo 1](graficas/iguzmanvt-174.html) | v_i/v_gdp, sin redondeo previo, con numerador y denominador en la misma moneda y precios corrientes. |
| iguzmanvt:176 | [Formación bruta de capital como proporción del PIB: grupo 2](graficas/iguzmanvt-176.html) | v_i/v_gdp, sin redondeo previo, con numerador y denominador en la misma moneda y precios corrientes. |
| iguzmanvt:202 | [Participación laboral en el PIB: grupo 1](graficas/iguzmanvt-202.html) | labsh, sin transformación. |
| iguzmanvt:205 | [Participación laboral en el PIB: grupo 2](graficas/iguzmanvt-205.html) | labsh, sin transformación. |
| iguzmanvt:207 | [Participación laboral en costos: aproximación del grupo 1](graficas/iguzmanvt-207.html) | phi_L=(labsh×rgdpna)/(labsh×rgdpna+0.05×rnna). |
| iguzmanvt:209 | [Participación laboral en costos: aproximación del grupo 2](graficas/iguzmanvt-209.html) | phi_L=(labsh×rgdpna)/(labsh×rgdpna+0.05×rnna). |
| iguzmanvt:156 | [Relación capital/producto: grupo 1](graficas/iguzmanvt-156.html) | rnna/rgdpna; ambas magnitudes a precios nacionales constantes de 2017. |
| iguzmanvt:158 | [Relación capital/producto: grupo 2](graficas/iguzmanvt-158.html) | rnna/rgdpna; ambas magnitudes a precios nacionales constantes de 2017. |
| iguzmanvt:168 | [Distribución entre países del promedio de escolaridad, 2010](graficas/iguzmanvt-168.html) | Se agrupan los 150 promedios nacionales yr_sch disponibles en 2010 en intervalos [0,2), [2,4), …, [14,16). Cada país recibe el mismo peso. |
| iguzmanvt:118 | [Cambio de investigadores y crecimiento de productividad](graficas/iguzmanvt-118.html) | x = (ln(FTE_i) − ln(FTE_(i−10)))/10, con i como fila dentro del país; y = g10.accttfp archivado. El código utiliza rezagos de 10 observaciones; no se recalculan ni se imputan datos. |
| iguzmanvt:160 | [Inversión y nivel del PIB per cápita](graficas/iguzmanvt-160.html) | y=round(ln(rgdpna/pop),2); inversión=round(csh_i,2); g_L=[ln(pop_t)−ln(pop_(t−10))]/10. Filtros: 0<inversión<0.6 y −0.01<g_L<0.06. |

Fuentes archivadas en `fuentes/`, con URL y SHA-256 en sus manifiestos. Para PWT se reconoce a Feenstra, Inklaar y Timmer (2015), *The Next Generation of the Penn World Table*, American Economic Review 105(10), 3150–3182. PWT 10.0 y 10.01 se distribuyen bajo CC BY 4.0. El código de StudyGuide conserva su licencia MIT. Maddison 2010 se identifica por su edición y sus dólares internacionales Geary-Khamis de 1990.
