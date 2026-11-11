# Discrepancia de capital PWT: procedencia e impacto comprobado

Auditoría de sólo lectura del 11 de noviembre de 2026. Repositorio iguzmanvt/Crecimiento, commit d8613e6a2fe63c1b7b3659ab3211895686c14dce. No se modificó ni publicó el repositorio.

**El Excel original conserva los valores de Data del XLSX/DTA oficial actual. La diferencia real está entre esa entrega y el objeto CRAN pwt10.0: 35 valores de capital de Estados Unidos. Con las fórmulas y redondeos originales, los 240 puntos de las cuatro trazas de 1960–2019 son idénticos.** La operación upstream que originó las diferencias no pudo demostrarse; no corresponde atribuirla sin prueba a edición del Excel, conversión a R, redondeo o revisión económica.

## Comparación realizada

| Comparación | Alcance | Resultado |
|---|---|---|
| Data del Excel del curso ↔ XLSX oficial | 12 810 filas × 52 columnas | 666 120 celdas iguales |
| XLSX oficial ↔ DTA oficial | Mismos país/año y 52 columnas | 666 120 celdas iguales |
| rnna USA de k_aggregate.dta oficial ↔ DTA final | 70 años, 1950–2019 | 70 iguales |
| Excel del curso ↔ pwt10.0 instalado | Seis columnas USA | Código, año, rgdpna, pop, hc iguales; rnna difiere en 35/70 |
| RDA descargado CRAN ↔ objeto instalado | Objeto completo, 12 810 × 52 | identical() verdadero |
| Script aislado ↔ chunk calculos publicado | Expresiones R parseadas | Iguales; Rmd no ejecutado |
| Resultados de Excel, oficial XLSX/DTA y CRAN ↔ cálculo instalado | 60 años × 4 trazas; además 12 variables derivadas | 0 diferencias exactas |

La comparación de tablas decodifica etiquetas del DTA y normaliza cadenas vacías a faltantes. La primera lectura sin etiquetas produjo aparentes diferencias de indicadores (código numérico frente a etiqueta); al comparar su significado declarado, todas coinciden. Se verifica igualdad de valores, **no identidad binaria de XLSX/DTA**. Los dos libros tienen distinta estructura: el del curso incorpora dos hojas adicionales, sin cambiar los valores comparados de Data.

[Resultados de las tablas](numeric_input_audit.json), [columnas USA](USA_input_column_comparison.json), [script de comparación](pwt_inputs_audit.py).

## Celdas, unidades y precisión

El Excel contiene USA en Data, filas 12112–12181 (1950–2019); el ejemplo usa filas 12122–12181 (1960–2019). Columnas: A=countrycode, D=year, G=pop, J=hc, S=rgdpna, V=rnna. El objeto R llama isocode a la clave de país.

Según Legend!B27 y Legend!B30, rgdpna y rnna están en millones de US$ de 2017 a precios nacionales constantes de 2017. Pop está en millones (Legend!B11); hc es un índice de capital humano (Legend!B14). No se sustituyen rgdpe/cn, usados en una hoja añadida de México, por las variables del ejemplo.

| Año | Celda original | Excel/oficial rnna | CRAN rnna | CRAN − Excel | Distancia float32 |
|---|---|---:|---:|---:|---:|
| 1960 | Data!V12122 | 14 711 919 | 14 711 917 | -2 | 2 |
| 1970 | Data!V12132 | 21 404 620 | 21 404 616 | -4 | 2 |
| 2010 | Data!V12172 | 61 054 676 | 61 054 668 | -8 | 2 |
| 2013 | Data!V12175 | 63 232 928 | 63 232 936 | +8 | 2 |

Las 35 discrepancias incluyen 30 en la muestra 1960–2019. El máximo absoluto es 8 millones de US$ de 2017; el relativo es 1.8687554369103494e-7 (0.0000186876 %, año 1970, Data!V12132). Las 70 observaciones de ambos lados son representables exactamente como float32. Hay 27 diferencias de una unidad de la última posición binaria (ULP) y 8 de dos ULP; 35 pares coinciden. El DTA oficial y su insumo de capital ya almacenan rnna como float32.

Ese perfil numérico **describe la escala**, sin demostrar el mecanismo causal. No es simplemente una diferencia de decimales impresos: son números distintos, y ambos son representables exactamente al ampliarlos a doble precisión. [Los 35 casos](rnna_35_differences_USA.csv) y [los 70 pares con bits y celdas](rnna_pairs_USA.json) permiten comprobar cada valor.

## Efecto sobre el ejemplo

Se ejecutó una función aislada y revisada con las mismas expresiones del chunk calculos; el script se detiene si no coinciden después de parsear. Se conservan alpha=0.3, referencia 1960, redondeo de log(PIB/población), ky y trazas a dos decimales, filtro desde 1960 y fórmulas originales.

La igualdad ocurre ya en ky = round(rnna / rgdpna, 2). El resto de entradas relevantes coincide. Los doce derivados (ky, acctky, accthc, accttfp, inittfp, inithc, initky, kyonly, hconly, tfponly, lngdppc, input) son exactamente iguales, 720 valores por fuente.

| Traza | Años | Valores diferentes | Máxima diferencia absoluta |
|---|---|---:|---:|
| kyonly | 1960–2019 | 0/60 | 0 |
| hconly | 1960–2019 | 0/60 | 0 |
| tfponly | 1960–2019 | 0/60 | 0 |
| lngdppc | 1960–2019 | 0/60 | 0 |

Se comprobaron Excel del curso, XLSX oficial, DTA oficial, exportación instalada y RDA descargado contra el cálculo sobre el objeto instalado completo. [Resultado R](trace_effect_audit.json), [240 puntos por fuente](USA_trace_comparison_1960_2019.csv), [función y aserciones](pwt_trace_effect.R).

La lectura aislada del workspace localizado por el coordinador también encontró un pwt10.0 completo idéntico al instalado y un usa de 60 × 64 con las mismas entradas, derivados y cuatro trazas. SHA256: 84eecbdd279dedbb35241539bb522ef507647b41945ea8e52ed7451c9d00cdbb. Esto refuerza la continuidad del cálculo, pero la carpeta Otoño 2021 no autentica su fecha de creación ni demuestra identidad con el gráfico remoto fid104.

## Procedencia y límite causal

El [paquete CRAN](https://cran.r-project.org/src/contrib/pwt10_10.01-0.tar.gz), versión DESCRIPTION 10.01-0, contiene tanto pwt10.0 como otro objeto pwt10.01. Esta auditoría usó explícitamente **pwt10.0**. La representación abreviada de packageVersion() en R (10.1.0) no es una selección de datos 10.01.

El archivo data/pwt10.0.rda tiene el mismo blob Git 8526f6a8bcc34307975840d8c5ff1fc874ee368a en las entregas CRAN del 21-ene-2021 y 27-feb-2023. El RDA descargado tiene ese mismo blob y MD5 6f6a527f2a00a3a010e53f73150d09a1; su objeto completo es idéntico al instalado. El Excel del curso declara “Revision of June 2021” en Info!A10 y coincide con los archivos que hoy entrega [GGDC para PWT 10.0](https://www.rug.nl/ggdc/productivity/pwt/pwt-releases/pwt100?lang=en).

El [changelog oficial](https://www.rug.nl/ggdc/docs/pwt100-changelog.pdf) documenta revisiones posteriores a enero, pero no atribuye expresamente cambios de rnna a USA. La revisión de capital de junio menciona China y Sudán; los efectos en otros países se describen para determinadas medidas de TFP. No se infiere de ahí la causa de los 35 casos USA.

El [programa oficial](https://www.rug.nl/ggdc/docs/pwt100-program-package.zip) incorpora capital ya calculado desde Data/k_aggregate.dta (gen_pwt100.do:129). Sus 70 valores USA coinciden con el DTA y XLSX finales. El ZIP no incluye el generador de ese insumo y las fuentes CRAN examinadas no contienen el importador del RDA. DTA y XLSX se guardan consecutivamente (gen_final_pwt.do:115–116). La presencia de compress tampoco prueba pérdida de precisión: [Stata documenta que la conserva](https://www.stata.com/manuals/dcompress.pdf), p. 2.

**Falta evidencia para identificar la operación upstream concreta.** Haría falta el importador CRAN, una entrega oficial anterior al 21-ene-2021 cotejable o el generador/documentación de capital que explique USA. La búsqueda primaria y sus límites están en [pwt_provenance.md](pwt_provenance.md); el cotejo del insumo está en [capital_program_boundary.json](capital_program_boundary.json).

## Recomendación mínima

Preservar Excel y fórmulas, y mantener la carga explícita de pwt10.0. Añadir una nota que distinga entregas y sustituya cualquier afirmación de igualdad de las seis columnas brutas por el resultado exacto: cinco columnas iguales, 35 diferencias de rnna y cero diferencias en los resultados USA bajo los redondeos históricos.

Se puede cerrar el riesgo de reproducción de **este ejemplo** con evidencia de efecto nulo. Debe quedar declarada la causa upstream no resuelta. No sustituir silenciosamente datos, usar pwt10.01, extender la conclusión a otros países/cálculos sin redondear ni presentarla como validación económica. No hace falta añadir otros originales completos al repositorio para documentar este hallazgo.

## Fuentes e integridad

| Archivo original de evidencia | Bytes | SHA256 |
|---|---:|---|
| repo_ejemplo_estados_unidos.xlsx | 6,613,816 | e5a4816e51cf2d9caf4d415668fd5e0c8c966c1467ee6874c1cc0a47204ba5e7 |
| official_pwt100.xlsx | 6,561,820 | 1a13ca27ada7bcab29c15430b3fe7f4d6c3cf0d2ee3eef3aed31d0fc0a2085d3 |
| official_pwt100.dta | 3,452,645 | 51d0b44fab4535e2c38ea5b2cab10ede548525e5488b4fafa166776723db4100 |
| official_pwt100_changelog.pdf | 165,635 | 3e438de5f339433a9be08869697d270d8d28fcfdad58f7db17a7f1f8e4fa2486 |
| cran_pwt10_10.01-0.tar.gz | 2,722,315 | 5b47ad8b46e97c923ed4eaa9ca0d86ab032212e27136cd6ba76dad093f28dc94 |
| pwt10/data/pwt10.0.rda | 1 359 272 | 1e51143c37a726c745e4655a460481be93ed36a20243e5e671bd4160d93c35f6 |
| official_pwt100_program_package.zip | 2 666 447 | a3ec39f199e889e0759a1c920ef1a3c87af966ec749603f8a8f774d32fcf9b65 |
| Data/k_aggregate.dta dentro del ZIP | 399 527 | 8915aa1ed27b0f2935f032937d150f3a6d1c48be33dc84f348d926b083e0b34e |

URLs, método de descarga, hashes y errores de transporte resueltos: [source_manifest.json](source_manifest.json). La validación TLS permaneció activada. No se han alterado los archivos originales, el checkout sigue limpio y HEAD sigue en el commit auditado: [post_audit_integrity.json](post_audit_integrity.json).

Entorno: R 4.3.3, paquete pwt10 DESCRIPTION 10.01-0; comparación XLSX/DTA con Python 3.13 y pandas 3.0.0. No se ejecutaron el documento Rmd, api_create, Stata ni una recalculación del libro. Sí se ejecutaron los scripts de auditoría enumerados en [pwt_discrepancy_audit.json](pwt_discrepancy_audit.json).

Reproducción del cálculo aislado, después de exportar y comparar las entradas con los scripts conservados:

    Rscript --vanilla pwt_trace_effect.R AUDIT_ROOT HISTORICAL_RDATA REPO_PATH

AUDIT_ROOT debe contener cran_pwt100.rda y USA_inputs_for_R.json; HISTORICAL_RDATA es el workspace autorizado y REPO_PATH el checkout del commit auditado. Los scripts de adquisición/comparación conservan las rutas de auditoría Windows utilizadas, fuera del repositorio. Los resultados son datos públicos o métricas derivadas; no se incluye el workspace completo ni sus otros objetos.
