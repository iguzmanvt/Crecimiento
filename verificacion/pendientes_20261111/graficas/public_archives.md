# Respaldos públicos de Chart Studio: resultado y límites

**No se recuperó ningún gráfico ni conjunto de datos de las 40 identidades objetivo.** La búsqueda del 11 de noviembre de 2026 encontró referencias auténticas del autor para dos identidades, pero no sus contenidos. Parte de los índices de archivo falló; por ello, este resultado **no demuestra que no existan copias archivadas**.

Alcance: `targets.json`, baseline `d8613e6a2fe63c1b7b3659ab3211895686c14dce`, 4 identidades de `iguzmanv` y 36 de `iguzmanvt`. Se conserva la clave compuesta `usuario:id`: `iguzmanv:198` y `iguzmanvt:198` son objetivos distintos. El SHA-256 de la lista de entrada es `f9e4fb05333911d7ce6d5c67f3bf454ac4fef8f6fe79b315e2cd068e6b4ca481`.

## Consultas de archivo

Se hicieron **10 intentos HTTP** a índices o disponibilidad de archivos desde Windows: 6 recibieron respuesta HTTP y 4 terminaron sin respuesta por timeout o conexión interrumpida. Las consultas por prefijo cubren los dos nombres de usuario conjuntamente; no se hicieron 40 consultas individuales. Tampoco se repitieron las 79 URL de Chart Studio que ya habían devuelto 410.

| Vía y alcance | Resultado observado | Qué permite concluir |
|---|---|---|
| Wayback CDX: [plotly.com, capturas 200](https://web.archive.org/cdx/search/cdx?url=plotly.com%2F~iguzmanv%2A&output=json&filter=statuscode%3A200&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) | HTTP 200, `[]\n` | Esa consulta no devolvió capturas exitosas. |
| Wayback CDX: [plotly.com, sin filtro de estado](https://web.archive.org/cdx/search/cdx?url=plotly.com%2F~iguzmanv&matchType=prefix&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) | HTTP 200, `[]\n` | No devolvió registros para el prefijo solicitado, incluidos otros estados. |
| Wayback [disponibilidad de iguzmanvt:96](https://archive.org/wayback/available?url=plotly.com%2F~iguzmanvt%2F96&timestamp=20251201), fecha solicitada 2025-12-01 | HTTP 200, `archived_snapshots: {}` | No ofreció una captura para esa consulta representativa; no equivale a revisar individualmente los otros 39 gráficos. |
| Wayback CDX: [plot.ly](https://web.archive.org/cdx/search/cdx?url=plot.ly%2F~iguzmanv&matchType=prefix&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) | HTTP 503, página de servicio temporalmente fuera de línea | Resultado indeterminado. |
| Wayback CDX: [chart-studio.plotly.com](https://web.archive.org/cdx/search/cdx?url=chart-studio.plotly.com%2F~iguzmanv&matchType=prefix&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) | Timeout de 25 segundos | Resultado indeterminado. |
| Wayback CDX: [api.plot.ly](https://web.archive.org/cdx/search/cdx?url=api.plot.ly%2Fv2%2Fplots%2Figuzmanv&matchType=prefix&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) y [api.plotly.com](https://web.archive.org/cdx/search/cdx?url=api.plotly.com%2Fv2%2Fplots%2Figuzmanv&matchType=prefix&output=json&collapse=urlkey&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Cdigest) | HTTP 503; misma página y hash que el fallo anterior | Resultado indeterminado. |
| Arquivo.pt CDX: [plotly.com](https://arquivo.pt/wayback/cdx?url=plotly.com%2F~iguzmanv&matchType=prefix&output=json&limit=1000) | Timeout de 15 segundos | Resultado indeterminado. |
| Arquivo.pt CDX: [plot.ly](https://arquivo.pt/wayback/cdx?url=plot.ly%2F~iguzmanv&matchType=prefix&output=json&limit=1000) y [chart-studio.plotly.com](https://arquivo.pt/wayback/cdx?url=chart-studio.plotly.com%2F~iguzmanv&matchType=prefix&output=json&limit=1000) | Conexión interrumpida, WinError 10054 | Resultado indeterminado. |

Las consultas de expansión se lanzaron en lotes limitados. Al observar los fallos de servicio/acceso, se detuvo cada vía sin reintentos ni expansión a consultas por gráfico. El conector de navegación tampoco podía abrir las dos primeras URL de Wayback; se distinguió esa limitación del resultado HTTP obtenido después en Windows.

La [documentación oficial de Arquivo.pt](https://github.com/arquivo/pwa-technologies/wiki/URL-search:-CDX-server-API) confirma el significado de `matchType=prefix` y distingue una respuesta vacía exitosa de un error. No se interpretaron los errores como ausencia de capturas.

## Referencias públicas del autor, sin recuperación de contenidos

Se revisó el HTML completo de dos versiones del mismo artículo del **19 de julio de 2022**, firmado por **Isaac Guzmán Valdivia Tovar**:

- [México, ¿cómo vamos?](https://mexicocomovamos.mx/animal-politico/2022/07/las-oportunidades-de-crecimiento-de-america-latina-estan-en-la-inversion-en-innovacion-y-desarrollo/)
- [Grupo Animal](https://grupoanimal.mx/opinion/oportunidades-crecimiento-america-latina-inversion-innovacion-desarrollo)

Ambas conservan enlaces exactos a:

| Identidad | Enlace conservado | Valor de la evidencia |
|---|---|---|
| `iguzmanvt:116` | [Referencia Chart Studio](https://chart-studio.plotly.com/~iguzmanvt/116/#/) | Vincula al autor y el argumento sobre I&D con esa identidad; no aporta sus datos ni figura. |
| `iguzmanvt:118` | [Referencia Chart Studio](https://chart-studio.plotly.com/~iguzmanvt/118/#/) | Confirma otra identidad utilizada por el autor; no aporta sus datos ni figura. |

Esos enlaces se extrajeron del HTML; **no se solicitaron de nuevo sus destinos Chart Studio**. No se encontraron llamadas `Plotly.newPlot`/`Plotly.react` ni payloads de los gráficos objetivo en estas páginas. En MCV, el único script `application/json` es `wp-emoji-settings`, configuración de emojis. Los tres iframe Datawrapper corresponden a composición parlamentaria y mapas de electricidad municipal/estatal dentro de ventanas de la plantilla. Se excluyeron porque no tienen conexión demostrada con ninguna identidad objetivo. Tampoco se aceptaron las imágenes de cabecera como respaldos de gráficos.

Las búsquedas específicas por los nombres de usuario, algunos pares usuario/ID, términos de los contextos y publicaciones del autor no localizaron otro respaldo atribuible. El JSON conserva las consultas; los resultados genéricos o de personas homónimas se descartaron.

## Trazabilidad

Las horas exactas de consulta, URL final, estados, errores, tamaños y hashes de todos los cuerpos recibidos están en [public_archives.json](public_archives.json). Los hashes siguientes corresponden a **los bytes recibidos**, no a un gráfico recuperado:

| Evidencia | Fecha y hora UTC | Bytes | SHA-256 |
|---|---|---:|---|
| CDX de plotly.com, sin filtro | 2026-11-11T21:05:06.986377+00:00 | 3 | `37517e5f3dc66819f61f5a7bb8ace1921282415f10551d2defa5c3eb0985b570` |
| Disponibilidad representativa :96 | 2026-11-11T21:04:05.417324+00:00 | 86 | `4adeb7198f12666c3a41dc72981f8d3784f74031e24edcc6669041b4a59a32ba` |
| Página de error 503 de Wayback | 2026-11-11T21:05:06.993598+00:00 | 11.832 | `e084d527921708642a79724e9f0210da659bbc0905c6ce9a3a1f416e4628091c` |
| Artículo MCV | 2026-11-11T21:05:18.007854+00:00 | 372897 | `2e89442b75abafd1ebc8af4a372df939e2a327e9a853c9450f378c3cd591135e` |
| Artículo Grupo Animal | 2026-11-11T21:05:26.653740+00:00 | 22515 | `aa11c98bac28a5a1525c66e2b8f694526e163706fa3bcbaa7db68a7b002335e0` |

Las respuestas crudas y los registros de inspección quedaron en un directorio temporal separado de Windows, indicado en el JSON. No hay hash de respuesta para consultas que no devolvieron cuerpo. Ninguna identidad tiene URL o fecha de captura recuperada: esos campos son `null`, no valores inferidos.

## Límites y vía oficial pendiente

La revisión del historial Git y sus HTML guardados corresponde a otra subtarea; tampoco se duplicó la búsqueda de archivos locales del curso. No se agotaron otros dominios, formas alternativas de URL, repositorios externos, archivos no indexados o exportaciones privadas. Los errores de Wayback y Arquivo.pt dejan parte de la cobertura abierta.

La [página oficial de Plotly](https://plotly.com/chart-studio-updates/), consultada el 11 de noviembre, confirma el cierre de Chart Studio el **31 de octubre de 2025** y describe una vía de recuperación de datos por correo a soporte. **No se contactó a nadie**. Esa vía no se cuenta como recuperación realizada.

No se editó ni publicó ningún repositorio, no se enviaron mensajes externos y no se generaron réplicas. Una reconstrucción posterior con fuentes nuevas deberá identificarse por separado; no puede presentarse como el gráfico original recuperado.

