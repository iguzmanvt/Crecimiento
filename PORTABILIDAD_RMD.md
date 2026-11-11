# Rutas e imágenes de las fuentes R Markdown

Las fuentes utilizaban rutas del Escritorio del equipo original para cargar sus imágenes. La corrección del 11 de noviembre de 2026 sustituye 604 literales de `readPNG` y `readJPEG` en 34 Rmd por rutas relativas al directorio de cada documento. Se conservaron contenido docente, código restante, opciones, variantes, imágenes y notas HTML históricas.

## Alcance

Se revisaron los 37 archivos Rmd versionados. Las 604 referencias afectadas corresponden a 598 llamadas a `readPNG` y seis a `readJPEG`. Resuelven 261 archivos gráficos, 259 PNG y dos JPG, con sus nombres y mayúsculas exactos. La coincidencia de contenido de dos imágenes con nombres distintos no elimina la necesidad de conservar ambas rutas.

| Relación con la fuente | Referencias | Ruta corregida |
| --- | ---: | --- |
| Imagen en la misma carpeta que el Rmd | 586 | Nombre del archivo |
| Nota de medio ambiente ubicada en `Energy` | 12 | `../Environment/` y nombre del archivo |
| Fuente anidada en `Ideas/CE-Ideas` | 6 | `../` y nombre del archivo |

No fue necesario mover o copiar imágenes. Las rutas relativas deben interpretarse desde la carpeta del Rmd. El ejemplo de render fija esa carpeta mediante `knit_root_dir`, incluso cuando los archivos intermedios se guardan en otro directorio. Si se ejecuta un chunk manualmente, el directorio de trabajo debe ser la carpeta correspondiente.

## Comprobación reproducible

El [verificador](scripts/verificar_rutas_imagenes.py) inspecciona los literales de lectura en los Rmd versionados, comprueba su destino exacto contra el índice de Git y decodifica cada imagen con R. No ejecuta los chunks ni accede a recursos remotos. Requiere Python 3, Git, R y los paquetes `png` y `jpeg`.

Desde la raíz del repositorio, con `Rscript` disponible en PATH

```sh
python scripts/verificar_rutas_imagenes.py
```

En el Windows verificado, desde PowerShell

```powershell
python scripts/verificar_rutas_imagenes.py --rscript "C:\Program Files\R\R-4.3.3\bin\Rscript.exe" --report "$env:TEMP\Crecimiento_imagenes.json"
```

El resultado esperado para este corte es 37 Rmd revisados, 34 con lecturas de imagen, 604 referencias verificadas y 261 imágenes decodificadas. El informe opcional conserva rutas, dimensiones y avisos del lector. La comprobación exige que los archivos estén versionados y detecta nombres que sólo coincidirían por ignorar mayúsculas en Windows.

## Renderizado de comprobación

La nota de Introducción permite comprobar imágenes y tablas del cambio. Para generar una copia separada desde la raíz del repositorio, en R

```r
repo <- normalizePath(".", winslash = "/")
salida <- tempfile("Introduccion_revision_")
dir.create(salida)
intermedios <- file.path(salida, "intermedios")
dir.create(intermedios)
fuente <- file.path(repo, "Clases_Crecimiento_Economico", "Introduction",
                    "Crecimiento Economico 1 Nota.Rmd")
rmarkdown::render(
  fuente,
  output_format = "html_document",
  output_file = "Introduccion_revision.html",
  output_dir = salida,
  intermediates_dir = intermedios,
  knit_root_dir = dirname(fuente),
  output_options = list(self_contained = FALSE)
)
```

Además de los lectores de imagen, esta nota utiliza `rmarkdown`, `knitr`, `plotly`, `shiny`, `gridExtra` y `kableExtra`. Su salida conserva referencias externas. `self_contained = FALSE` permite comprobar la generación local sin intentar incorporar esas páginas al documento. La nota HTML histórica se mantiene en su ubicación original.

La comparación controlada utiliza el Rmd anterior con sus lecturas redirigidas a los mismos archivos gráficos verificados, y el Rmd corregido con sus rutas relativas. El criterio es que los 13 PNG locales producidos coincidan byte por byte. Esto comprueba que el cambio de rutas conserva esas figuras en el mismo entorno, sin atribuir equivalencia al render histórico de otro entorno.

La comprobación del 11 de noviembre de 2026 aprobó las 604 referencias y la lectura de las 261 imágenes sin avisos. Los 13 PNG de la comparación controlada coincidieron por SHA-256. La revisión sintáctica de los 632 chunks de los 37 Rmd pasó antes y después del cambio, sin ejecutarlos. Se usaron Python 3.13.3, R 4.3.3, `png` 0.1.8, `jpeg` 0.1.10, `rmarkdown` 2.28, `knitr` 1.46 y Pandoc 3.10 en Windows. El aviso de Pandoc sobre la opción obsoleta `--no-highlight` no impidió generar la nota.

## Límites y pendientes

- Las fuentes conservan sus dependencias, configuraciones y referencias externas. La primera entrega verificó las rutas literales y su lectura. La comprobación posterior de los 15 módulos genera 51 salidas de sus 34 fuentes; véase la guía enlazada abajo.
- Las dos presentaciones de Introducción cuentan ahora con configuración estática corregida y CSS local, conservando la variante con tabla inicial adicional. Su [guía de generación](Clases_Crecimiento_Economico/Introduction/README.md) permite crear ambos formatos fuera del repositorio. El alcance de aquella corrección era Introducción. La comprobación posterior de los 15 módulos se documenta por separado.
- La nota de Introducción mantiene 13 iframes de Our World in Data y 17 referencias de Chart Studio. Entre estas últimas hay una URL terminada en `.embe` y un identificador repetido. No se sustituyeron o reconstruyeron esos contenidos sin respaldo.
- Los HTML históricos conservan respaldos que algunas fuentes Rmd sólo enlazan. Toda prueba de render debe escribir una salida separada. Las recuperaciones de las gráficas 42 y 223 permanecen disponibles en sus carpetas.
- La verificación técnica no revisa las fuentes estadísticas ni actualiza las cifras de las imágenes.

## Comprobación posterior de los 15 módulos

La [guía de reproducción](REPRODUCCION_MODULOS.md) documenta las 34 fuentes, 51 salidas, controles de figuras y navegador, integración local de las gráficas 42/223 y ejemplo USA. Sustituye el límite anterior de falta de render para estos módulos. Mantiene los límites estadísticos y de recursos externos.
