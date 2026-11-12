# Reconstrucción de las gráficas de Crecimiento

11 de noviembre de 2026. Continuación de `8265d179322918f035cc4102f1bc9403cbcbb1dc`.

## Resultado para la clase

**40 de 40 destinos docentes cuentan con una gráfica reconstruida**, con datos CSV, especificación JSON completa, SVG y PNG. Las cuatro animaciones conservan sus estados. Las figuras mantienen fondo blanco, tipografía legible y líneas, marcadores y colores coherentes con el material de clase. Se recalcularon series PWT, modelos y ajustes estadísticos cuando había insumos; los datos archivados de StudyGuide se adaptaron con atribución y sus límites de edición.

Las reconstrucciones se incorporaron en **13 Rmd y 91 referencias** de seis módulos. Se generaron y comprobaron **21 salidas** de esas fuentes, incluidas las variantes conservadas; se ofrece una selección de **13 materiales listos para abrir**: seis notas, seis presentaciones y el ejemplo calculado USA. Los HTML históricos y las imágenes previas permanecen como antecedentes.

- [Notas y presentaciones actualizadas](materiales_actualizados/README.md).
- [Guía de las 40 gráficas locales](graficas_reconstruidas/README.md).
- [Catálogo, fuentes, fórmulas y ediciones](graficas_reconstruidas/catalogo.json).
- [Integración de las fuentes y cambios de contexto](verificacion/reconstruccion_20261111/integracion_fuentes.json).

Abrir los HTML desde una copia completa del repositorio. GitHub muestra su código; las imágenes PNG de la tabla siguiente se pueden consultar directamente. Las nuevas gráficas funcionan sin conexión; otras referencias externas del curso conservan sus dependencias de red.

## Decisiones que cambian la lectura

- **Solow:** las líneas BGP se identifican como ajustes OLS con ventanas explícitas. Se actualizaron los parámetros y cálculos de ejemplo que las acompañan. La transición de China es un modelo calibrado, separado de los datos observados; las simulaciones no se presentan como series empíricas.
- **Contabilidad:** 104 conserva la fórmula y los redondeos del ejemplo original y coincide exactamente con sus 240 valores de referencia. 110 descompone el crecimiento logarítmico medio a diez años; sus componentes suman el total con error numérico menor que 2×10⁻¹⁴. La PTF publicada por PWT se distingue del residuo simplificado del ejercicio.
- **Capital:** `iguzmanv:198` representa una aproximación de participación del capital en costos con renta supuesta de 5%. `iguzmanvt:198` representa el complemento no laboral de la remuneración laboral en el PIB. El destino de la presentación de Desaceleración usa este último para ser coherente con su explicación del PIB. Los conceptos y ambas identidades permanecen separados.
- **I+D:** la evolución de la productividad no se presenta como una prueba estadística de asociación con el esfuerzo investigador. Investigadores FTE no equivalen a personas físicas. Como la moneda, multiplicador y base del gasto archivado no quedan acreditados, 102 usa un índice 2000=100 y 100 usa ln(gasto/gasto de 2000), con eje lineal. Se comparan trayectorias relativas, no montos absolutos entre países. Se distinguen relaciones de niveles y de crecimiento; un rezago de diez observaciones con huecos no se llama automáticamente una tasa anual de diez años.
- **Política fiscal:** las dispersiones muestran consumo del gobierno/PIB, no tasas impositivas, y no identifican un efecto causal.
- **Energía:** intensidad física = energía primaria/PIB real; participación del gasto = gasto nominal/PIB nominal. Las series EIA usan la edición de octubre de 2026 y se muestran para 1970–2019.
- **Demografía:** se separan natalidad, ocupados/población total y dependencia. Los grupos 0–19, 20–64 y 65+ no se solapan. La dependencia mayor aumenta, pero esa evolución no equivale a un aumento continuo de la dependencia total. Se retiró la afirmación prospectiva a 2030 que la reconstrucción histórica no demuestra. La captura WDI cubre 1960–2024 y está fechada el 11 de noviembre de 2026.

## Comprobación

Los tres generadores recalcularon las **40 especificaciones**, con insumos archivados y sólo la biblioteca estándar de Python. La comprobación final en Windows obtuvo las mismas coordenadas y fotogramas, sin diferencias numéricas, y archivos idénticos al normalizar los saltos de línea a LF. Las cifras, fórmulas, unidades, filtros, valores ausentes y supuestos constan por figura. Los generadores rechazan cambios de huella de los insumos.

Chrome comprobó valores x/y y CSV de las 40 vistas, el último estado de las cuatro animaciones —incluidos cambios de disposición visual—, las descargas, vistas embebidas y ajuste a 720 píxeles. Se exportaron y comprobaron **40 SVG y 40 PNG**. El ajuste final de notas al pie se volvió a probar en sus seis gráficas afectadas; se conservaron los controles de los otros 34 casos. No se intentaron solicitudes externas en las vistas de las nuevas gráficas; se abrió además una vista mediante `file://`. La inspección visual usa muestras; los controles de contenido y recursos cubren las 40.

Las 21 salidas de clase cargaron las nuevas imágenes y los nuevos iframes locales. Los 13 materiales seleccionados también se abrieron desde sus rutas finales mediante el protocolo de archivo local: [comprobación del paquete](verificacion/reconstruccion_20261111/paquete_navegador.json). Se comprobó la navegación de las presentaciones, ancho y recursos locales. Las figuras PNG generadas desde las imágenes históricas se compararon con los controles anteriores en el mismo entorno. Las referencias externas y MathJax se bloquearon o sustituyeron por una página de prueba: su contenido no queda acreditado como offline ni nuevamente validado.

[Navegador de las 40 gráficas](verificacion/reconstruccion_20261111/galeria_navegador.json) · [Navegador de las 21 salidas](verificacion/reconstruccion_20261111/materiales_navegador.json) · [Recálculo final en Windows](verificacion/reconstruccion_20261111/recalculo_final_windows.json) · [Conservación de originales](verificacion/reconstruccion_20261111/conservacion_originales.json) · [Ajustes de interpretación](verificacion/reconstruccion_20261111/revision_de_interpretacion.json).

## Requisitos y aceptación

| Requisito | Aceptación | Evidencia | Estado |
| --- | --- | --- | --- |
| R-005: reconstruir los 40 destinos | AC-005: 40 identidades distintas con datos, imagen y vista local | Catálogo, 40 SVG, 40 PNG, CSV y JSON | Comprobado |
| R-006: integrar el material de clase | AC-006: sustituir las referencias caídas y abrir cada salida afectada | 13 Rmd, 91 referencias, 21 salidas, 13 materiales seleccionados | Comprobado |
| R-007: conservar significado económico | AC-007: documentar fórmulas, muestras y supuestos y ajustar textos incompatibles | Manifiestos, insumos y ajustes exactos de Solow, Contabilidad, Ideas, Fiscal, Energía y Desaceleración | Comprobado dentro de las reconstrucciones |
| R-008: figuras legibles y utilizables | AC-008: ejes y recursos visibles, animaciones y descargas funcionales | Navegador y revisión visual de muestras | Comprobado |
| R-009: conservar antecedentes | AC-009: mantener activos originales y cálculos R fuera del cambio | Cotejo de objetos Git, chunks R e imágenes históricas | Comprobado antes de publicar |

## Límites y continuidad

Se resolvió la ausencia funcional de las gráficas mediante reconstrucciones autorizadas. **No se autenticó ni recuperó el payload de los 40 objetos originales de Chart Studio**. Los identificadores organizan sus destinos docentes; no prueban que las nuevas figuras reproduzcan exactamente apariencia, muestra o cifras antiguas. El respaldo del soporte deja de ser una dependencia de uso de la clase.

La diferencia upstream de `rnna` entre Excel oficial y objeto R conserva la conclusión ya demostrada para el ejemplo: no altera sus cuatro trazas con los redondeos originales. Su causa concreta no se atribuye sin evidencia. [Auditoría previa](verificacion/pendientes_20261111/pwt/pwt_discrepancy_audit.md).

## Figuras y datos

| Destino histórico | Módulo | Imagen reconstruida | Datos y vista |
| --- | --- | --- | --- |
| `iguzmanv:195` | Contabilidad | [Estados Unidos: productividad total de los factores](graficas_reconstruidas/imagenes/iguzmanv-195.png) | [CSV](graficas_reconstruidas/datos/iguzmanv-195.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanv-195.html) |
| `iguzmanv:196` | Contabilidad | [Estados Unidos: capital por persona empleada](graficas_reconstruidas/imagenes/iguzmanv-196.png) | [CSV](graficas_reconstruidas/datos/iguzmanv-196.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanv-196.html) |
| `iguzmanv:197` | Contabilidad | [Estados Unidos: capital y producción por persona empleada](graficas_reconstruidas/imagenes/iguzmanv-197.png) | [CSV](graficas_reconstruidas/datos/iguzmanv-197.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanv-197.html) |
| `iguzmanv:198` | Contabilidad | [Estados Unidos: participación del capital en los costos](graficas_reconstruidas/imagenes/iguzmanv-198.png) | [CSV](graficas_reconstruidas/datos/iguzmanv-198.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanv-198.html) |
| `iguzmanvt:44` | Solow | [Japón: distintas sendas de crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-44.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-44.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-44.html) |
| `iguzmanvt:46` | Solow | [Estados Unidos: senda de crecimiento ajustada](graficas_reconstruidas/imagenes/iguzmanvt-46.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-46.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-46.html) |
| `iguzmanvt:48` | Solow | [Estados Unidos: crecimiento antes y después de 2000](graficas_reconstruidas/imagenes/iguzmanvt-48.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-48.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-48.html) |
| `iguzmanvt:50` | Solow | [Alemania: senda de crecimiento desde 1991](graficas_reconstruidas/imagenes/iguzmanvt-50.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-50.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-50.html) |
| `iguzmanvt:52` | Solow | [Alemania: relación capital/producto](graficas_reconstruidas/imagenes/iguzmanvt-52.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-52.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-52.html) |
| `iguzmanvt:54` | Solow | [Corea del Sur: cambio en la senda de crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-54.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-54.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-54.html) |
| `iguzmanvt:56` | Solow | [China: crecimiento y referencia de Corea del Sur](graficas_reconstruidas/imagenes/iguzmanvt-56.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-56.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-56.html) |
| `iguzmanvt:58` | Solow | [China: crecimiento de la población](graficas_reconstruidas/imagenes/iguzmanvt-58.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-58.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-58.html) |
| `iguzmanvt:60` | Solow | [China: transición hacia una senda de crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-60.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-60.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-60.html) |
| `iguzmanvt:62` | Solow | [China: distintas etapas de crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-62.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-62.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-62.html) |
| `iguzmanvt:72` | Ideas e I+D | [Investigadores y crecimiento: comparación internacional](graficas_reconstruidas/imagenes/iguzmanvt-72.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-72.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-72.html) |
| `iguzmanvt:76` | Ideas e I+D | [Modelo de I+D: convergencia del crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-76.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-76.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-76.html) |
| `iguzmanvt:78` | Solow | [Dinámica de la productividad: dos condiciones iniciales](graficas_reconstruidas/imagenes/iguzmanvt-78.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-78.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-78.html) |
| `iguzmanvt:82` | Solow | [Nivel del PIB per cápita: transición en el modelo de Solow](graficas_reconstruidas/imagenes/iguzmanvt-82.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-82.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-82.html) |
| `iguzmanvt:96` | Ideas e I+D | [Investigadores en I+D](graficas_reconstruidas/imagenes/iguzmanvt-96.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-96.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-96.html) |
| `iguzmanvt:100` | Ideas e I+D | [Evolución del gasto en I+D en logaritmos relativos](graficas_reconstruidas/imagenes/iguzmanvt-100.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-100.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-100.html) |
| `iguzmanvt:102` | Ideas e I+D | [Evolución relativa del gasto en I+D](graficas_reconstruidas/imagenes/iguzmanvt-102.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-102.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-102.html) |
| `iguzmanvt:104` | Contabilidad | [Estados Unidos: contabilidad del crecimiento](graficas_reconstruidas/imagenes/iguzmanvt-104.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-104.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-104.html) |
| `iguzmanvt:110` | Contabilidad | [Estados Unidos: contribuciones al crecimiento en diez años](graficas_reconstruidas/imagenes/iguzmanvt-110.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-110.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-110.html) |
| `iguzmanvt:112` | Ideas e I+D | [Crecimiento de la productividad](graficas_reconstruidas/imagenes/iguzmanvt-112.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-112.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-112.html) |
| `iguzmanvt:116` | Ideas e I+D | [Investigadores y productividad: nueve países](graficas_reconstruidas/imagenes/iguzmanvt-116.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-116.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-116.html) |
| `iguzmanvt:118` | Ideas e I+D | [Cambio de investigadores y crecimiento de productividad](graficas_reconstruidas/imagenes/iguzmanvt-118.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-118.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-118.html) |
| `iguzmanvt:120` | Ideas e I+D | [Investigadores y nivel de productividad](graficas_reconstruidas/imagenes/iguzmanvt-120.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-120.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-120.html) |
| `iguzmanvt:122` | Solow | [Corea del Sur: relación capital/producto](graficas_reconstruidas/imagenes/iguzmanvt-122.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-122.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-122.html) |
| `iguzmanvt:124` | Solow | [Corea del Sur: crecimiento de la población](graficas_reconstruidas/imagenes/iguzmanvt-124.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-124.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-124.html) |
| `iguzmanvt:126` | Solow | [China: relación capital/producto](graficas_reconstruidas/imagenes/iguzmanvt-126.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-126.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-126.html) |
| `iguzmanvt:132` | Política fiscal | [Gasto del gobierno y crecimiento del PIB per cápita](graficas_reconstruidas/imagenes/iguzmanvt-132.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-132.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-132.html) |
| `iguzmanvt:134` | Política fiscal | [Gasto del gobierno y nivel del PIB per cápita](graficas_reconstruidas/imagenes/iguzmanvt-134.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-134.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-134.html) |
| `iguzmanvt:160` | Solow | [Inversión y nivel del PIB per cápita](graficas_reconstruidas/imagenes/iguzmanvt-160.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-160.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-160.html) |
| `iguzmanvt:162` | Solow | [Población y nivel del PIB per cápita](graficas_reconstruidas/imagenes/iguzmanvt-162.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-162.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-162.html) |
| `iguzmanvt:190` | Energía | [Estados Unidos: intensidad energética](graficas_reconstruidas/imagenes/iguzmanvt-190.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-190.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-190.html) |
| `iguzmanvt:192` | Energía | [Estados Unidos: gasto energético / PIB](graficas_reconstruidas/imagenes/iguzmanvt-192.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-192.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-192.html) |
| `iguzmanvt:198` | Desaceleración | [Estados Unidos: participación no laboral del PIB](graficas_reconstruidas/imagenes/iguzmanvt-198.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-198.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-198.html) |
| `iguzmanvt:211` | Desaceleración | [Estados Unidos: tasa bruta de natalidad](graficas_reconstruidas/imagenes/iguzmanvt-211.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-211.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-211.html) |
| `iguzmanvt:213` | Desaceleración | [Estados Unidos: ocupados / población total](graficas_reconstruidas/imagenes/iguzmanvt-213.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-213.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-213.html) |
| `iguzmanvt:216` | Desaceleración | [Estados Unidos: dependencia demográfica](graficas_reconstruidas/imagenes/iguzmanvt-216.png) | [CSV](graficas_reconstruidas/datos/iguzmanvt-216.csv) · [Vista](graficas_reconstruidas/graficas/iguzmanvt-216.html) |
