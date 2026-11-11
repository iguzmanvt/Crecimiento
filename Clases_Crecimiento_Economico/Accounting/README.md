# Contabilidad del crecimiento

Las 3 fuentes de este módulo pueden generarse mediante la [guía común](../../REPRODUCCION_MODULOS.md). Se conservan las variantes y los HTML históricos; las salidas nuevas se escriben fuera del repositorio.

| ID | Fuente | Formatos |
| --- | --- | --- |
| 01 | [Crecimiento Economico - Contabilidad del crecimiento Nota.Rmd](Crecimiento%20Economico%20-%20Contabilidad%20del%20crecimiento%20Nota.Rmd) | html_document |
| 02 | [Crecimiento Economico - Contabilidad del crecimiento.Rmd](Crecimiento%20Economico%20-%20Contabilidad%20del%20crecimiento.Rmd) | ioslides_presentation · html_document |
| 03 | [Ejemplo Estados Unidos.Rmd](Ejemplo%20Estados%20Unidos.Rmd) | html_document |

Desde la raíz del repositorio:

```sh
Rscript scripts/renderizar_modulos.R /ruta/externa/vacia Accounting
```

Conservar cada carpeta de salida completa. La verificación cubre generación, figuras locales y funcionamiento del navegador; no replica las estimaciones contenidas en imágenes ni actualiza sus cifras.

## Ejemplo de Estados Unidos

El ejemplo usa explícitamente `pwt10::pwt10.0`, cargado con `data("pwt10.0", package="pwt10")`, y `plotly`. Genera cuatro trazas locales, 60 observaciones por traza (1960–2019), sin publicar en Chart Studio. Conserva α=0.3, referencia 1960, fórmulas y redondeos del código anterior.

El paquete comprobado identifica DESCRIPTION `10.01-0` (`packageVersion()` lo representa como `10.1.0`); el objeto cargado es **pwt10.0**, no pwt10.01. El resultado depende de esta entrada, no de las hojas editadas del Excel.

El XLSX conserva `Info`, `Legend`, `Data` y dos hojas añadidas para México. `Hoja1 (2)` tiene entradas vacías y 132 fórmulas con caché cero; no se presenta como ejercicio terminado ni se recalculó el libro. En `Data`, USA tiene 70 años (1950–2019). Código ISO, año, `rgdpna`, `pop` y `hc` coinciden con el objeto R instalado; `rnna` difiere en 35 años, 30 dentro de 1960–2019, con máximo absoluto de 8 millones de US$ de 2017. No se determinó la causa. [Cotejo de entradas](../../verificacion/modulos_20261111/entradas_accounting.json).

PWT 10.0: [página oficial y descarga](https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100?lang=en), DOI `10.15141/S5Q94M`, licencia CC BY 4.0. Atribución: Feenstra, Robert C., Robert Inklaar y Marcel P. Timmer (2015), “The Next Generation of the Penn World Table”, American Economic Review 105(10), 3150–3182. [Documentación del objeto R](https://search.r-project.org/CRAN/refmans/pwt10/html/pwt10.0.html).

## Seguimiento de gráficas externas

La [galería local](../../recursos_graficas/README.md) ofrece material fuente archivado y una figura del curso recuperada. La [matriz de los originales pendientes](../../PENDIENTES_GRAFICAS_Y_PWT.md) distingue alternativas y límites. No se ha demostrado una correspondencia con los identificadores antiguos.

El cotejo posterior confirmó que Data del Excel coincide con la versión oficial. Pese a las 35 diferencias brutas de rnna frente a CRAN, las cuatro trazas del ejemplo conservan exactamente sus 240 valores; los doce derivados también coinciden. Se mantienen datos y fórmulas. [Auditoría de capital](../../verificacion/pendientes_20261111/pwt/pwt_discrepancy_audit.md).
