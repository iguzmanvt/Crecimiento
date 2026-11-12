# Generación de los 15 módulos de Crecimiento

## Actualización de las gráficas reconstruidas

Las 40 figuras están en `graficas_reconstruidas/`, con datos, fórmulas y generadores por grupo. El renderizador copia esa carpeta a la raíz común de la salida y ajusta los enlaces relativos, incluida la fuente anidada CE-Ideas. Conservar la salida completa para abrir notas y presentaciones.

Los [13 materiales ya generados](materiales_actualizados/README.md) usan las reconstrucciones. Para repetir sólo los módulos afectados:

```sh
Rscript scripts/renderizar_modulos.R /ruta/externa/vacia Solow Accounting Ideas Taxes Energy Slowdown
```

Las nuevas gráficas funcionan sin conexión. Las referencias externas del curso y MathJax conservan su dependencia de red. [Método y comprobación](RECONSTRUCCION_GRAFICAS.md).


Corte del 11 de noviembre de 2026. Esta entrega permite generar las 34 fuentes R Markdown de los 15 módulos posteriores a Introducción: 17 presentaciones con dos formatos, 16 notas HTML y un ejemplo calculado. Son 51 salidas, organizadas por módulo, ID de fuente y formato. El [manifiesto](scripts/modulos.csv) mantiene las variantes y resuelve la nota de Medio ambiente que vive en Energy.

## Estado por módulo

| Módulo | Rmd | Salidas | Comprobación |
| --- | ---: | ---: | --- |
| [Estudios de caso con el modelo de Solow](Clases_Crecimiento_Economico/Solow/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Convergencia y políticas públicas para el crecimiento](Clases_Crecimiento_Economico/Convergence/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Contabilidad del crecimiento](Clases_Crecimiento_Economico/Accounting/README.md) | 3 | 4 | Aprobada para recursos locales |
| [Ideas, productividad e investigación y desarrollo](Clases_Crecimiento_Economico/Ideas/README.md) | 3 | 5 | Aprobada para recursos locales |
| [Patentes](Clases_Crecimiento_Economico/Patents/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Competencia y modelo schumpeteriano](Clases_Crecimiento_Economico/Competition/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Difusión tecnológica](Clases_Crecimiento_Economico/Technological_Diffusion/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Transformación sectorial y crecimiento](Clases_Crecimiento_Economico/Structural_Transformation/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Desaceleración del crecimiento en países desarrollados](Clases_Crecimiento_Economico/Slowdown/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Cambio tecnológico y sustitución laboral](Clases_Crecimiento_Economico/Labor/README.md) | 3 | 4 | Aprobada para recursos locales |
| [Cambio tecnológico, género y migración](Clases_Crecimiento_Economico/Labor_2/README.md) | 3 | 5 | Aprobada para recursos locales |
| [Sistemas de pensiones y crecimiento económico](Clases_Crecimiento_Economico/Pensions/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Energía, población y crecimiento](Clases_Crecimiento_Economico/Energy/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Medio ambiente y crecimiento](Clases_Crecimiento_Economico/Environment/README.md) | 2 | 3 | Aprobada para recursos locales |
| [Política fiscal y crecimiento](Clases_Crecimiento_Economico/Taxes/README.md) | 2 | 3 | Aprobada para recursos locales |

## Generación

Requiere R, Pandoc y los paquetes `rmarkdown`, `knitr`, `png`, `gridExtra`, `plotly`, `shiny` y `jsonlite`; el ejemplo añade `pwt10`. RStudio incorpora Pandoc. El entorno comprobado fue Windows, R 4.3.3, Pandoc 3.10, rmarkdown 2.28, knitr 1.46, png 0.1.8, gridExtra 2.3, plotly 4.10.4, shiny 1.8.1.1, jsonlite 2.0.0 y pwt10 10.1.0 (DESCRIPTION 10.01-0).

Desde la raíz del repositorio, indicando una carpeta externa vacía:

```sh
Rscript scripts/renderizar_modulos.R /ruta/externa/vacia
```

Para seleccionar módulos:

```sh
Rscript scripts/renderizar_modulos.R /ruta/externa/vacia Solow Convergence Accounting
```

En PowerShell del equipo comprobado:

```powershell
$env:RSTUDIO_PANDOC = "C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools"
& "C:\Program Files\R\R-4.3.3\bin\Rscript.exe" scripts/renderizar_modulos.R "$env:TEMP\Crecimiento_15_modulos"
```

La ruta de salida (primer argumento) debe estar vacía y fuera del repositorio. Después pueden indicarse módulos o IDs de dos dígitos del manifiesto; por ejemplo `09 10 20` selecciona tres notas. El script fija la carpeta de cada fuente como raíz de evaluación, separa intermedios y copia el CSS y las recuperaciones necesarias. Los HTML se llaman `Material.html`; la jerarquía e ID evitan colisiones. Conservar cada carpeta completa. `resultados.json` registra estado, avisos, tiempo y versiones. Un error de cualquier salida provoca salida distinta de cero al finalizar.

## Correcciones realizadas

- Se sustituyó la referencia al ausente `air.css` por un [ajuste local de lectura](Clases_Crecimiento_Economico/curso.css), documentado como nuevo. Permite desplazar láminas largas, ajustar imágenes/iframes al ancho disponible y envolver bloques de texto preformateados que se salían del ancho de Solow.
- Se retiró `output.runtime: shiny`, que estaba mal anidado. Los documentos no contienen lógica reactiva. Se conserva la carga histórica de paquetes usada en sus setups.
- Las salidas declaran `self_contained: false`: recursos locales acompañan al HTML y los recursos remotos siguen siendo externos.
- Las notas de Ideas y Competencia corrigen títulos YAML copiados de otros temas. El cuerpo docente permanece, salvo las sustituciones locales de las gráficas 42/223 y las correcciones técnicas del ejemplo USA.
- Solow y Labor_2 muestran los SVG ya recuperados y enlazan sus vistas completas. El uso de HTML para estas imágenes evita la incompatibilidad de `Figure` del escritor ioslides de rmarkdown 2.28 con Pandoc 3.10.
- Las tres notas con iframes utilizan también el ajuste de ancho. En las dos fuentes de Medio ambiente se cerró un iframe abierto que ocultaba la primera figura y la sección siguiente; los doce PNG de cada salida son ahora accesibles.
- El ejemplo USA declara datos y paquetes, usa tres etiquetas de chunk distintas y muestra la figura local. La llamada de publicación `api_create` se eliminó; se conservaron sus cálculos.

## Evidencia y aceptación

Los criterios son: generar los 51 destinos sin errores; conservar los originales protegidos; mantener las figuras rasterizadas de cada fuente; cargar los recursos locales en navegador sin errores JavaScript ni archivos ausentes; navegar las 17 presentaciones y llegar al final de las láminas largas; mostrar ambas recuperaciones y las cuatro trazas del ejemplo.

Se compararon las figuras con 33 renders de control de las fuentes anteriores en el mismo entorno. El control usa un formato HTML estático explícito para sortear el YAML/CSS defectuoso, sin cambiar el cuerpo ni las imágenes de entrada. El ejemplo USA se evalúa por separado: se comprobaron conservación exacta de sus fórmulas y 60 puntos en cada una de sus cuatro trazas. Esto es una regresión técnica, no una validación independiente del modelo económico.

La [verificación de navegador](verificacion/modulos_20261111/render.json) registra cada salida; las figuras locales coinciden por SHA-256 con su control. La revisión visual usa muestras por módulo y comprobaciones automáticas de todas las salidas; no implica lectura manual de cada lámina. Los [cambios de fuentes](verificacion/modulos_20261111/cambios_fuentes.json) fijan blobs anteriores y posteriores. La [comparación de entradas USA](verificacion/modulos_20261111/entradas_accounting.json) documenta la discrepancia con el Excel. Los HTML históricos, imágenes originales, XLSX y productos numéricos de recuperación se preservan en Git.

La [revisión independiente de fuentes](verificacion/modulos_20261111/final_source_review.md) comprueba 26 cuerpos intactos y ocho con los ajustes declarados, incluidos los dos cierres de iframe. Pandoc avisa que `--no-highlight` está obsoleto; el aviso no impidió generar las salidas. Los datos, inferencias y cifras de las imágenes históricas no se actualizaron.

## Recursos externos y límites

El [catálogo de referencias externas](verificacion/modulos_20261111/referencias_externas.md) distingue URL, usuario e identificador. Las solicitudes Chart Studio comprobadas responden HTTP 410; el render no recupera su contenido. Se conserva `iguzmanv` donde así aparece en Accounting, sin convertirlo en `iguzmanvt` por suposición. Las recuperaciones locales 42 y 223 provienen de los respaldos históricos y mantienen sus límites documentados.

Our World in Data, FRED y otros enlaces conservan su alcance separado. Una respuesta HTTP favorable no demuestra igualdad con la edición del curso. MathJax y algunos recursos remotos requieren conexión. Durante la prueba de navegador se bloquearon las solicitudes externas: se verificó funcionamiento y contenido local, no la representación remota de fórmulas o gráficas ni funcionamiento completamente offline.

Las variantes idénticas de Labor/Labor_2 y la fuente anidada Ideas/CE-Ideas se conservan. La nota de Medio ambiente sigue físicamente en Energy; el manifiesto la agrupa con Environment. Introducción mantiene su [procedimiento propio](Clases_Crecimiento_Economico/Introduction/README.md).

## Seguimiento de Chart Studio y PWT

El [informe de seguimiento](PENDIENTES_GRAFICAS_Y_PWT.md) cierra el efecto de la diferencia de capital sobre el ejemplo USA y ofrece [44 vistas locales de apoyo](recursos_graficas/README.md). Los 40 identificadores originales mantienen su estado sin autenticar; las alternativas preservan procedencia y límites.

## Repetir el recálculo y el contraste

Con Python 3.10+ y sin red:

```sh
python scripts/verificar_recalculo_graficas.py graficas_reconstruidas /salida/informe_recalculo.json
```

El control comprueba las huellas de los insumos, vuelve a calcular los tres grupos y compara coordenadas, fotogramas y especificaciones. Registra por separado igualdad numérica e igualdad del archivo después de normalizar LF. La tolerancia general es 1e-12; la ejecución final guardada en Windows tuvo diferencia numérica cero.

Si R no detecta un Pandoc ya instalado, definir la variable de la sesión `RSTUDIO_PANDOC` con la carpeta que contiene su ejecutable antes de renderizar. La generación final usó R 4.3.3 y Pandoc 3.13.
