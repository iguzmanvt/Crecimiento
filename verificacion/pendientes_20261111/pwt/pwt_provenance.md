# Procedencia de pwt10.0 y límites de la explicación de diferencias

Auditoría de sólo lectura, 11 de noviembre de 2026. No se ejecutaron R, Rmd, Stata ni `api_create`; no se modificó ningún repositorio. La comparación numérica de Estados Unidos corresponde al coordinador y no se presenta aquí como comprobación propia.

## Resultado comprobado

**El objeto `pwt10.0` conservado por la versión del paquete `pwt10 10.01-0` procede del mismo archivo RDA que ya estaba publicado en enero de 2021.** Los dos árboles del espejo CRAN en GitHub contienen exactamente el mismo blob para `data/pwt10.0.rda`; sus manifiestos MD5 también coinciden. La versión de paquete 10.01-0 añade un objeto distinto, `pwt10.01`, según [NEWS](https://github.com/cran/pwt10/blob/957b298fd706a567af96ccb1663ad68d5e5d07ba/NEWS.md). Esto no acredita todavía por sí solo el contenido de la instalación local.

| Evidencia | 10.0-0 | 10.01-0 |
|---|---|---|
| Fecha de paquete | 21-ene-2021 | 27-feb-2023 |
| Commit del espejo CRAN | `ddab9e949de8f52619cdfdbc436c5ea558d16a11` | `957b298fd706a567af96ccb1663ad68d5e5d07ba` |
| Blob de pwt10.0.rda | `8526f6a8bcc34307975840d8c5ff1fc874ee368a` | Mismo blob |
| Tamaño de pwt10.0.rda | 1 359 272 bytes | Igual |
| MD5 declarado | `6f6a527f2a00a3a010e53f73150d09a1` | Igual |

Fuentes: [árbol de 2021](https://github.com/cran/pwt10/tree/ddab9e949de8f52619cdfdbc436c5ea558d16a11), [árbol de 2023](https://github.com/cran/pwt10/tree/957b298fd706a567af96ccb1663ad68d5e5d07ba), [MD5 anterior](https://github.com/cran/pwt10/blob/ddab9e949de8f52619cdfdbc436c5ea558d16a11/MD5), [MD5 actual](https://github.com/cran/pwt10/blob/957b298fd706a567af96ccb1663ad68d5e5d07ba/MD5). El historial del path RDA sólo registra el commit inicial. El [archivo oficial de CRAN](https://cran.r-project.org/src/contrib/Archive/pwt10/) confirma la entrega del 21 de enero de 2021. Estos MD5 se leyeron de los manifiestos; no se recalcularon en esta subtarea.

## Cronología de PWT 10.0

| Fecha | Hecho documentado |
|---|---|
| 14-ene-2021 | El catálogo oficial de Groningen registra producción y disponibilidad de PWT 10.0. |
| 15-ene-2021 | GGDC anuncia el lanzamiento. |
| 21-ene-2021 | Se publica el paquete CRAN 10.0-0. |
| 26-ene-2021 | Corrección de GDP nominal de la serie alternativa de China y variables dependientes. |
| 28-ene-2021 | Cambios de benchmarks de precios de 1996 y 2005 con información Eurostat/OCDE. |
| 18-feb-2021 | Corrección del tipo de cambio de Sudán y variables dependientes. |
| 18-jun-2021 | Recálculo de capital y productividad para China/Sudán; efectos multilaterales en determinadas medidas de TFP. |
| 27-feb-2023 | Paquete CRAN 10.01-0: añade pwt10.01 y conserva pwt10.0.rda. |

Fuentes: [catálogo institucional](https://research.rug.nl/en/datasets/penn-world-table-version-100/), [anuncio](https://www.rug.nl/ggdc/blog/pwt-100-has-been-launched-12-01-2021?lang=en), [changelog de GGDC, página 1](https://www.rug.nl/ggdc/docs/pwt100-changelog.pdf), CRAN/NEWS enlazados arriba.

El changelog identifica `rnna` entre las variables recalculadas para **China y Sudán**. Para otros países menciona efectos en `ctfp` y `cwtfp`; no documenta expresamente un cambio de `rnna` de Estados Unidos. Por tanto, este documento **no basta para atribuir a esa revisión las diferencias de USA**. Tampoco demuestra que no hubiera efectos numéricos adicionales no descritos.

## Fuentes originales y código publicado

La [página oficial de PWT 10.0](https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100?lang=en) enlaza [XLSX](https://www.rug.nl/ggdc/docs/pwt100.xlsx), [DTA](https://www.rug.nl/ggdc/docs/pwt100.dta) y [programas Stata](https://www.rug.nl/ggdc/docs/pwt100-program-package.zip). Los originales XLSX/DTA los está cotejando el coordinador.

Se descargó y leyó el ZIP de programas, sin ejecutar su código:

- Tamaño: **2 666 447 bytes**.
- SHA256: `a3ec39f199e889e0759a1c920ef1a3c87af966ec749603f8a8f774d32fcf9b65`.
- HTTP Last-Modified: 18-jun-2021, 10:16:44 GMT.
- 27 entradas, incluidos 11 scripts.

La cadena de código comprobada es:

| Archivo y línea | Operación |
|---|---|
| gen_pwt100.do:129 | Incorpora los stocks y servicios de capital ya calculados desde Data/k_aggregate.dta, por país y año. |
| gen_pwt100.do:304 | Llama al script de guardado final. |
| gen_final_pwt.do:6 y 52 | Conserva rnna y la etiqueta como capital a precios nacionales constantes de 2017, en millones de USD de 2017. |
| gen_final_pwt.do:113 | Ejecuta compress. |
| gen_final_pwt.do:115–116 | Guarda DTA y exporta XLSX, consecutivamente desde la misma tabla. |

El ZIP contiene `Data/k_aggregate.dta` (399 527 bytes; timestamp interno 9-jun-2021), pero **no contiene el código que lo genera**. No se encontró una conversión explícita de rnna a float/double en los scripts inspeccionados. Los timestamps describen archivos, no prueban cuándo se calcularon sus valores.

Además, el [manual oficial de Stata para compress, página 2](https://www.stata.com/manuals/dcompress.pdf) establece que el comando conserva la precisión de los datos. Su presencia no fundamenta una explicación de pérdida de precisión para las diferencias observadas.

En los dos árboles CRAN completos no hay scripts R ni carpeta data-raw: se distribuyen los RDA, documentación y metadatos. Una búsqueda acotada del importador en fuentes del autor/R-Forge no lo localizó. El [manual del objeto](https://github.com/cran/pwt10/blob/957b298fd706a567af96ccb1663ad68d5e5d07ba/man/pwt10.0.Rd) documenta 12 810 observaciones, 52 variables y nombres como isocode/currency, mientras que la exportación GGDC usa countrycode/currency_unit. Hay adaptación de esquema, pero no se identificaron el script, el lector o el formato de entrada utilizado para crear el RDA.

## Vía de archivo histórico y límite causal

El DOI [10.15141/S5Q94M](https://doi.org/10.15141/S5Q94M) resuelve actualmente a GGDC. La [API oficial de DataCite](https://api.datacite.org/dois/10.15141/S5Q94M) registra la URL de GGDC, `version: null` y ninguna relación a otros identificadores. Su fecha de registro, 8-ene-2021, corresponde al DOI y no demuestra la fecha del contenido de los archivos.

La consulta acotada a DataverseNL devolvió HTTP 404 con un mensaje de parámetro persistentId ausente, incluso al comprobar la URL efectiva. Ese resultado es inconcluso: no acredita inexistencia de un archivo histórico. No se recuperó un XLSX/DTA oficial anterior al 21 de enero de 2021 y no se realizó búsqueda amplia en Wayback.

**Conclusión:** está demostrada la conservación del RDA de enero dentro del paquete de 2023 y la existencia de revisiones posteriores de GGDC. El origen exacto de las diferencias de rnna USA sigue separado: requiere el importador CRAN, una entrega oficial de enero cotejable o evidencia adicional sobre la generación del capital agregado. No se etiqueta la causa como “redondeo” ni como “revisión económica” sin esa prueba.

Metadatos, hashes, líneas y alcance detallado: [pwt_provenance.json](pwt_provenance.json).
