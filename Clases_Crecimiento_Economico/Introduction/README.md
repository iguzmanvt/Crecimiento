# Introducción: consulta y generación

## Uso vigente

Las tres fuentes editables usan ahora 32 vistas locales y corrigen las interpretaciones que no correspondían a las variables. [Abrir las figuras, datos y fuentes](../../introduccion_local/index.html). La entrega canónica usa la variante con tabla tanto para notas como presentación, con fórmulas y recursos locales; véase la [generación vigente](../../REPRODUCCION_MODULOS.md).

Los 17 destinos Chart Studio son reconstrucciones por contexto docente, con límites explícitos. Las 15 vistas OWID identifican la edición descargada y la sustitución de mortalidad por exposición PM2.5. Se corrigieron el enlace duplicado 172 por 176, la extensión `.embe`, el umbral de pobreza y las interpretaciones de fecundidad, obesidad, población por edad, grupos de países y costos laborales. Los HTML históricos permanecen intactos.

## Registro técnico anterior

Lo que sigue documenta las comprobaciones del 11 de noviembre de 2026, anteriores a las sustituciones y correcciones docentes. Sus pendientes y declaraciones de contenido sin cambios describen aquel corte.


## Materiales del tema

[Notas](../../materiales_actualizados/Introduction/notas/Material.html) · [Presentación](../../materiales_actualizados/Introduction/presentacion/Material.html) · [Material de consulta](../../material_consulta/Introduction.md).

La [nota HTML histórica](Crecimiento-Economico-1-Nota.html) conserva la entrega original del curso. Las fuentes `Crecimiento Economico 1.Rmd` y `Crecimiento Economico Intro.Rmd` son variantes de la presentación: la primera incorpora una tabla inicial adicional con los bloques del temario. Se mantienen ambas.

## Corrección de configuración del 11 de noviembre de 2026

Las dos fuentes declaraban `runtime: shiny` dentro de `output`, junto a los formatos, y dependían de un `air.css` ausente. Sus bloques de R construyen imágenes y tablas; no se encontraron entradas, salidas reactivas ni una aplicación Shiny. Se retiró esa entrada mal ubicada y se conservaron `ioslides_presentation`, `html_document`, `smaller` y `widescreen`.

Se usa la apariencia predeterminada de ioslides y Bootstrap con [ajustes locales](introduction.css) para limitar el ancho de los contenidos incrustados y permitir desplazarse por las láminas largas. Este CSS es una corrección actual, no una recuperación del diseño histórico de `air.css`. No cambia tipografías, cifras ni textos.

La prueba de navegador detectó que las dependencias de tablas de `kableExtra` buscaban jQuery en ioslides. Se añadió una línea de metadatos en el bloque `setup` para incluir la dependencia local suministrada por `rmarkdown`; no se usa una CDN ni se cambia la construcción de las tablas. El resto del cuerpo de ambos Rmd permanece idéntico.

Los dos formatos usan `self_contained: false`: cada HTML se distribuye con sus carpetas de recursos. Así se evita intentar incorporar las páginas externas al archivo. Esto no recupera los contenidos remotos ni convierte la presentación en un documento autónomo sin conexión.

## Generar una copia separada

Se requieren R, Pandoc y los paquetes `rmarkdown`, `knitr`, `plotly`, `shiny`, `png`, `jpeg`, `gridExtra` y `kableExtra`, que utilizan las fuentes. El script carga la configuración corregida de cada Rmd y genera sus dos formatos. Rechaza salidas dentro del repositorio y carpetas que ya contengan archivos.

Desde la raíz del repositorio:

```sh
Rscript scripts/renderizar_introduccion.R /ruta/fuera/del/repositorio/introduccion
```

En el Windows comprobado, desde PowerShell:

```powershell
$env:RSTUDIO_PANDOC = 'C:\Program Files\RStudio\resources\app\bin\quarto\bin\tools'
& 'C:\Program Files\R\R-4.3.3\bin\Rscript.exe' --vanilla scripts/renderizar_introduccion.R "$env:TEMP\Introduccion_revision"
```

La carpeta de salida debe estar vacía o no existir. Se crean cuatro subcarpetas: `con_tabla_ioslides_presentation`, `con_tabla_html_document`, `sin_tabla_ioslides_presentation` y `sin_tabla_html_document`. Abre `Introduccion.html` dentro de cada una y conserva todos sus archivos asociados. En ioslides, usa las flechas para avanzar y desplázate verticalmente cuando una lámina exceda la altura disponible.

El script fija `knit_root_dir` a esta carpeta, copia el CSS local a cada salida y escribe los resultados e intermedios fuera del repositorio. No sustituye la nota histórica. Para una generación manual, conserva esas mismas condiciones.

## Alcance de la comprobación

| Criterio | Comprobación |
| --- | --- |
| Configuración estática válida | Dos formatos por fuente; sin `runtime` tratado como formato |
| Contenido conservado | Cuerpo idéntico salvo la declaración local de jQuery en `setup`; imágenes y HTML históricos sin modificaciones |
| Generación reproducible | Ambas variantes en ioslides y HTML, fuera del repositorio |
| Recursos locales visibles | 13 figuras por salida, estilos locales presentes y tablas conservadas |
| Navegación y lectura | Avance con teclado y acceso vertical a láminas largas |

La comprobación en Windows aprobó las cuatro salidas: 64/63 láminas de ioslides, incluidas las portadas; dos/una tablas; 13 figuras por salida con PNG idénticos al control anterior. Chrome 155.0.8059.86 no reportó errores de JavaScript ni desbordamiento horizontal, y se comprobó el acceso vertical al contenido largo. Se usaron R 4.3.3, rmarkdown 2.28, knitr 1.46 y jQuery local 3.6.0. El aviso de Pandoc 3.10 sobre `--no-highlight` no impidió generar los HTML.

Los 32 iframes de cada variante —15 de Our World in Data y 17 de Chart Studio— se conservan. La prueba local bloquea su contenido remoto; también pueden requerir conexión recursos como MathJax. Esta comprobación no acredita su disponibilidad ni actualiza sus datos. Las referencias de Chart Studio siguen pendientes de recuperación, incluidas sus URL relativas al protocolo. La nota HTML histórica y la fuente `Crecimiento Economico 1 Nota.Rmd` no se modifican en esta entrega.

Referencias de configuración: [formatos y directorios de render](https://pkgs.rstudio.com/rmarkdown/reference/render.html), [opciones y CSS de ioslides](https://pkg.yihui.org/rmarkdown-book/ioslides-presentation#custom-css).

## Respaldo de referencias externas

El [catálogo de referencias](referencias_externas/README.md) identifica los 32 recursos de las presentaciones, conserva las configuraciones archivadas de 13 recursos OWID y documenta la búsqueda de datos originales. Estas configuraciones no contienen observaciones numéricas. La recuperación de las gráficas permanece pendiente; el catálogo incluye una solicitud preparada para el respaldo de Chart Studio.
