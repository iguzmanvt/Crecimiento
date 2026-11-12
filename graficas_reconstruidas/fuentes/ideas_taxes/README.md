# Reconstrucciones docentes de Ideas y Política Fiscal

Este paquete produce **11 gráficas nuevas** para los destinos `iguzmanvt:72`, `76`, `96`, `100`, `102`, `112`, `116`, `118`, `120`, `132` y `134`. La elección de fuentes y variantes es una adaptación docente autorizada. No se afirma que estas vistas recuperen la apariencia ni la identidad de los antiguos objetos de Chart Studio.

Se conservan los datos y los periodos archivados. No se descargan series actualizadas, no se ejecutan los scripts R originales y no se modifica ningún HTML histórico.

## Generación y comprobación

Con Python 3 y su biblioteca estándar:

```sh
python generar.py --output carpeta_salida
python verificar.py
```

El generador resuelve `inputs/` junto a su propio archivo, por lo que puede ejecutarse desde otro directorio. No utiliza red, R, Windows, Plotly para Python ni otras dependencias. Verifica primero las 19 huellas de los archivos de entrada y produce las 11 especificaciones Plotly, `manifest.json` y `validation.json`. Sin argumento de salida, escribe junto al generador.

`verificar.py` comprueba datos, metadatos, huellas, estados del modelo y reproducción idéntica de 13 archivos en una copia temporal aislada. Se limita a archivos dentro de esta carpeta y borra su copia temporal al terminar. No realiza la revisión visual del renderizador final HTML/SVG.

## Contenido de las gráficas

| ID | Variables y adaptación | Puntos |
|---|---|---:|
| 72 | ln de investigadores FTE y crecimiento de productividad; seis países StudyGuide | 201 |
| 76 | Dos economías simuladas: proporción R/A y crecimiento de productividad | 500 |
| 96 | Investigadores FTE por año; cobertura desigual por país | 210 |
| 100 | ln(gasto de I+D / gasto del mismo país en 2000), eje lineal | 227 |
| 102 | Índice de gasto de I+D por país, 2000 = 100 | 227 |
| 112 | Crecimiento anual medio de productividad en ventanas de 10 años | 355 |
| 116 | ln de investigadores FTE y crecimiento de productividad; objeto local de nueve países | 265 |
| 118 | Diferencia de ln(FTE) entre observaciones separadas por 10 filas, dividida entre 10; crecimiento de productividad | 141 |
| 120 | ln de investigadores FTE y nivel logarítmico de productividad | 201 |
| 132 | Consumo del gobierno/PIB y crecimiento anual medio del PIB per cápita | 355 |
| 134 | Consumo del gobierno/PIB y nivel logarítmico del PIB per cápita | 415 |

Total: **3,097 puntos** en las trazas principales. Las siete gráficas archivadas sin transformación conservan exactamente sus coordenadas; 100 y 102 conservan los años y transforman los niveles monetarios originales de forma explícita. El objeto local 116 conserva sus 265 coordenadas, país, año y códigos de unidad. El modelo 76 se calcula de nuevo a partir de su fórmula documentada.

## Transformaciones y límites

**Gasto de I+D, 100 y 102.** El año 2000 está presente con valor positivo en las seis series. Se calculan `ln(gasto_t / gasto_2000)` e `100 × gasto_t / gasto_2000` desde el archivo de niveles, sin redondeo intermedio. La primera gráfica tiene base 0 y eje lineal; la segunda tiene base 100. No se atribuyen moneda, PPA, multiplicador o base de precios no acreditados. Los índices comparan evolución relativa, no niveles monetarios entre países; la normalización tampoco prueba continuidad metodológica dentro de cada serie. El archivo de logaritmos original se conserva como evidencia: sus 227 valores coinciden con `round(ln(nivel),2)`, pero el original aplicaba además eje logarítmico. La reconstrucción evita esa segunda transformación.

**Investigadores.** FTE significa equivalentes a tiempo completo, no necesariamente personas físicas. En 96, China termina en 2,405,509.4 FTE en 2021; Estados Unidos termina en 2020 y Reino Unido en 2017. No deben compararse los últimos puntos como si pertenecieran a un año común. El código de 118 utiliza un rezago de 10 observaciones, con posibles huecos temporales: su eje horizontal no se presenta como una tasa anual inequívoca a 10 años.

**Dispersiones.** Los archivos StudyGuide usados en 72, 118, 120, 132 y 134 no conservan el año de cada punto. No se deducen fechas del orden ni de las coordenadas. El objeto local de 116 sí conserva `obsTime` (1981–2019) y nueve países: Argentina, Chile, China, Alemania, Reino Unido, Japón, Corea del Sur, México y Estados Unidos. Es una muestra distinta de los seis países StudyGuide; no se fusionan ni se asume que sus ediciones estadísticas coincidan.

**Modelo 76.** Se utiliza `gA = theta × R^lambda / A^(1−phi)`, con `theta=0.01`, `lambda=1`, `phi=0`, `gR=0.02`, `R_1=10`, `A_A,1=2` y `A_B,1=10`. Después de cada observación, `A` y `R` crecen según sus respectivas tasas. Son 250 periodos simulados y dos economías hipotéticas; las 500 coordenadas coinciden con las archivadas dentro de una tolerancia absoluta de `1e-12` (máxima diferencia observada: `4.884981308350689e-15`). El límite es `R/A=2` y crecimiento de productividad de 2%. Las trayectorias completas se conservan en las trazas principales; los 250 estados animados mueven resaltados en la disposición visual y no duplican las observaciones. La vista estática sigue mostrando ambas trayectorias.

**Política fiscal.** `csh_g` se describe como participación del consumo del gobierno en el PIB. No equivale a una tasa impositiva y sus asociaciones con PIB per cápita no identifican efectos causales.

## Procedencia y atribución

Los archivos fuente de StudyGuide se fijan en el commit [`3a8c79f20022ef7b985b392d73921839a4317883`](https://github.com/dvollrath/StudyGuide/tree/3a8c79f20022ef7b985b392d73921839a4317883), de Dietz Vollrath. Se incluye su licencia MIT íntegra en `LICENSE-StudyGuide` y los cuatro scripts R de referencia con sus bytes originales. El uso de los datos conserva las limitaciones de metadatos de los archivos archivados; la atribución del repositorio no añade unidades ausentes ni autentica los IDs de Chart Studio.

Los Rmd del curso y la tabla local de 2021 se fijan en [`iguzmanvt/Crecimiento@8265d179322918f035cc4102f1bc9403cbcbb1dc`](https://github.com/iguzmanvt/Crecimiento/tree/8265d179322918f035cc4102f1bc9403cbcbb1dc). `manifest.json` registra fórmulas, unidades, periodos, límites, rutas, enlaces fijados, huellas y número de observaciones por serie. `inputs/source_catalog.json` conserva la procedencia de los objetos gráficos de referencia. Los archivos R se incluyen para inspección y atribución: el generador no los ejecuta.

## Ajustes propuestos a las fuentes docentes

`ajustes_texto.json` contiene 32 reemplazos exactos `{path, old, new, reason}` en los cinco Rmd de Ideas y Taxes. Aclaran unidades FTE, normalización del gasto, variantes de dispersión, muestra local y consumo del gobierno; además corrigen el encabezado de crecimiento de la gráfica 132. Los enlaces originales se conservan en estas propuestas para que el integrador pueda sustituirlos después. `ajustes_texto_provenance.json` registra las huellas y la comprobación de unicidad y aplicación secuencial. Estos archivos no aplican modificaciones al repositorio.
