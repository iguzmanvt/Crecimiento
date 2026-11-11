# Revisión final de fuentes: 15 módulos de Crecimiento

**Resultado: PASS.** No se detectaron defectos materiales en el alcance revisado. Baseline `df1639e97f20b9e6b386b14d4edfe2ef3b84efac`; cotejo del 11 de noviembre de 2026 en el clon Windows de trabajo. No se editó el repositorio ni se ejecutó Rmd, knitr, render o publicación.

## Alcance del diff

Se revisaron los 34 Rmd fuera de Introduction. Los 34 cambian configuración, pero **26 cuerpos permanecen idénticos** después del YAML, normalizando únicamente CRLF/LF. Los ocho cuerpos restantes tienen sólo los cambios previstos:

| Grupo | Fuentes afectadas | Diferencia comprobada |
|---|---:|---|
| Solow, gráfica 42 | 2 | Referencia remota sustituida por SVG local y enlace a la vista con datos/límites |
| Labor_2, gráfica 223 | 3 | Iframe remoto sustituido por SVG local y enlace a la vista con datos/límites |
| Ejemplo Estados Unidos | 1 | Dependencias y labels explícitos; salida local visible en lugar de publicación |
| Medio Ambiente, IDs 10 y 11 | 2 | Cierre del iframe co-emissions-per-capita antes de la sección Factores |

En los cinco Rmd de recuperación se comprobó una transformación exhaustiva: sustituir exactamente el bloque anterior reproduce todo el cuerpo actual, sin diferencias adicionales ni alteración del final de archivo. **Los cinco ya usan `<img src="recuperado/grafica_ID.svg" … />`**; no queda la versión Markdown de imagen. Los SVG y HTML enlazados existen en las carpetas correspondientes.

En la actualización final se comprobaron dos cierres mínimos: una línea `</iframe>` y su separador vacío en la nota de Energy (L69, ID10) y la presentación de Environment (L71, ID11), antes de `## Factores`. Al retirar exactamente esa inserción, cada cuerpo reproduce el hash anterior; no cambia ningún otro contenido. Ambas fuentes pasan de diez aperturas y nueve cierres a diez y diez. Sus blobs actuales son `d0c8d8abbd4b8da0b1468f6507728be6da308374` y `f4c0ee519456f32d19fb87c53c0bcb8937cfa2d1`.

Los 34 blobs permanecieron estables en la relectura final. En el cotejo inicial, fuera de los Rmd sólo aparecían modificados entre los archivos ya versionados los README de recuperación de Solow y Labor_2. Esta revisión no constituye aprobación de archivos nuevos ajenos a ese alcance.

## Ejemplo USA

Blob actual: `11b1ce3dc5f4981e788e5bf9d41bd274f12af5bc`.

- El chunk completo de cálculos permanece idéntico: alpha 0.3, referencia inicial de 1960, filtro posterior a 1959, selección USA y seis redondeos a dos decimales.
- La construcción de las cuatro series y el layout están intactos.
- Declara `library(plotly)` y `data("pwt10.0", package="pwt10")`.
- Tiene labels únicos `datos`, `calculos` y `grafica`.
- El chunk final usa `echo=FALSE`, ya no declara `include=FALSE`, y devuelve `fig`.
- No queda `api_create`.

La comparación exhaustiva del archivo sólo encuentra esos cambios y los del YAML. Se mantiene la distinción previamente documentada entre las entradas del objeto R y el XLSX; conservar fórmulas no prueba validez económica.

## Recursos preservados

| Recursos versionados | Cantidad | Resultado |
|---|---:|---|
| PNG | 268 | Idénticos byte a byte |
| JPG | 2 | Idénticos byte a byte |
| SVG recuperados | 2 | Idénticos byte a byte |
| XLSX | 1 | Idéntico byte a byte |
| HTML, incluidos históricos y vistas recuperadas | 18 | Contenido Git intacto |

En los 16 HTML históricos, Windows usa CRLF mientras los blobs Git usan LF. Sus hashes coinciden al normalizar sólo esos finales de línea; no es una modificación de contenido. Los dos HTML recuperados coinciden también byte a byte. No se regeneró ningún HTML histórico durante esta revisión. Esta comprobación de activos se reutiliza del cotejo inicial; las actualizaciones posteriores revisan sólo fuentes y script, sin repetir el cotejo XLSX/PWT.

## Configuración

Los 34 YAML se analizan correctamente. Declaran 34 opciones HTML y 17 opciones ioslides, todas con `self_contained: false`; ioslides conserva `smaller` y `widescreen`. Ya no aparece `runtime` como formato.

Se comprobó que la actualización de los IDs09 (Energía Nota), 10 (Medio Ambiente Nota en Energy) y 20 (Labor_2 Nota) añadió exactamente `css: ../curso.css` a sus cabeceras, sin cambios de cuerpo en ese paso. Hay **37 referencias CSS**: 34 de los dos formatos de las 17 presentaciones y tres de esas notas. Todas resuelven al archivo existente `Clases_Crecimiento_Economico/curso.css`, incluido el nivel adicional de `Ideas/CE-Ideas`.

## Selección por módulo o ID

La lectura estática de `scripts/renderizar_modulos.R` no detectó defectos materiales con el manifiesto actual. Lee los IDs como texto, valida selectores antes de crear la salida y aplica la unión entre módulos e IDs sin duplicar filas. El manifiesto tiene 34 IDs únicos, fuentes existentes y 51 destinos módulo/ID/formato distintos. Por ejemplo, `09 10 20` selecciona esas tres fuentes; `Environment` selecciona 10 y 11 según el módulo declarado, aunque la nota 10 resida en Energy; combinar `Accounting` y `03` selecciona 01–03 una sola vez.

El script conserva el rechazo de salidas dentro del repositorio o no vacías, copia CSS cuando el YAML lo requiere y registra errores y advertencias por rendición. SHA256 revisado: `ae94f2af9b1c9fa16a8aac3ef84943fe0b50514aa717ca3ee99c5241617e34de`. No se ejecutó el script en esta revisión.

## Evidencia y límites

La comprobación cubre fuentes, alcance del diff, resolución local e integridad de activos. Las rendiciones, navegación y apariencia final corresponden a las pruebas separadas del coordinador; no se infieren de este cotejo.

- [final_source_review.json](final_source_review.json): cierre y criterios.
- [final_source_snapshot.json](final_source_snapshot.json): blobs de los 34 Rmd, diff de cuerpos y 291 comprobaciones de activos.
- [final_recovery_exact.json](final_recovery_exact.json): cinco sustituciones exhaustivas, rutas y relectura final.
- [final_example_review.json](final_example_review.json): comprobación independiente del ejemplo USA.
- [final_header_refresh.json](final_header_refresh.json): tres adiciones CSS, 37 rutas y revisión de selección.
- [final_iframe_refresh.json](final_iframe_refresh.json): dos cierres mínimos y estabilidad de los 34 Rmd.
