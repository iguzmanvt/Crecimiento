# Historia Git y fuentes alternativas de las gráficas pendientes

La revisión no recuperó un payload con identidad demostrada para ninguno de los 40 IDs pendientes. Sí localizó widgets archivados del curso fuente, adecuados para una galería de alternativas separada, con su autor, fecha, idioma, datos y límites propios. No deben presentarse como los originales españoles de Chart Studio ni sustituirlos silenciosamente.

| Repositorio | Alcance comprobado | Resultado |
|---|---|---|
| `iguzmanvt/Crecimiento` | `d8613e6a2fe63c1b7b3659ab3211895686c14dce`; una rama anunciada, sin tags anunciados; 10 commits alcanzables; 465 blobs únicos, 149 de tipos pertinentes inspeccionados (64,469,625 bytes). | Los únicos `plot-fid` con datos localizados son 42 y 223, ya recuperados. Los 18 HTML únicos incluyen las 16 notas históricas y las dos vistas recuperadas. No aparece un payload de los 40 IDs pendientes. |
| `iguzmanvt/CE-Ideas` | `389acd5e7444539f619822b61b5c28d505465d44`; una rama; 4 commits y 16 blobs. | Los nueve IDs de Ideas aparecen como enlaces históricos. No hay HTML, CSV, JSON, ZIP ni RData en la historia alcanzable. El archivo con extensión `.rds` es texto Rmd, no un objeto R. |
| `iguzmanvt/Crecimiento-Economico---Intro` | `7c5ea1b022defc3af7f8be644e3a171867d871e5`; una rama, un commit inicial. | No contiene material docente ni datos de las gráficas. |
| `iguzmanvt/Introduccion` | `2ee4c9e26bbf12bc8f0cf5af50c040e9b1890c60`; una rama, tres commits; árboles completos por API. | Las dos versiones Rmd contienen enlaces a los pendientes 160 y 118; no contienen su generador ni payload. Los recursos de imagen no prueban correspondencia con esos IDs. |
| `iguzmanvt/StudyGuide` y `dvollrath/StudyGuide` | Fork `44927f3925b7f4de4803a76a703a5281b1a774fd` y upstream `bc0cce025e6bc418b2015b22c508fdaeeecf48fc`; 564 commits alcanzables y 2,201 blobs. | Se encontraron widgets con datos Plotly, código R y datos de origen. El inventario actual contiene 105 widgets; se extrajeron 41 payloads principales y dos adicionales pertinentes, en carpetas separadas. No aparecen identificadores `iguzmanv`/`iguzmanvt` que prueben asignación a los 40 pendientes. |

La historia alcanzable de Crecimiento comienza en junio de 2025 con un commit descrito como una carga limpia de materiales. No se afirma que Git conserve el trabajo docente anterior no subido. La inspección suplementaria de nombres `.RData` y variantes no encontró objetos ocultos con esos nombres; un `.rds` comparte blob con un Rmd y se inspeccionó como texto. El Excel de Accounting sí está versionado; el antiguo archivo de bloqueo de Excel no es una fuente de datos.

## Evidencia que sí permite avanzar

- **Widgets fuente archivados:** `studyguide_widgets.json` registra archivo, blob, SHA-256, título, ejes, trazas, recuentos, rangos y referencias documentales de código/página. `studyguide_payloads/` conserva el JSON widget original y una extracción mínima `data/layout/frames` para 41 widgets. `payload_validation_review.json` comprueba independientemente sus hashes y la igualdad de `data` y `layout`. En 37 mínimos, la ausencia de `frames` se representa con `[]`; cuatro listas de frames existentes permanecen completas.
- **Procedencia y licencia:** los 41 widgets coinciden con los blobs del repositorio primario `dvollrath/StudyGuide` fijado al commit `3a8c79f20022ef7b985b392d73921839a4317883`. Sólo 13 siguen idénticos en el upstream actual; usar el commit fijo. La licencia del repositorio es MIT, con aviso `Copyright (c) 2020 Dietz Vollrath`; conservar licencia y atribución. Los registros de datos y código son evidencia documental del curso, no una certificación de haber reproducido todos los cálculos con el software actual.
- **Control 42 positivo:** la traza USA de `plotly/pwt-apply-usa.html`, blob `af16ae626f119e8409001998a9f642212bebd1ff`, coincide exactamente con los 70 pares de 1950–2019 recuperados de 42. Hay otras coincidencias de esa serie en widgets del curso. No demuestra que las trazas BGP sean los IDs 46/48.
- **Control 223 negativo:** la historia HTML de StudyGuide no produjo coincidencia exacta con los 58 pares de 223. Las versiones con tema similar difieren en periodo y/o valores. No reemplazar la recuperación existente por esas variantes.
- **Objeto local de 2021 distinto:** `fig_2021_vs_studyguide.json` compara las 265 filas y nueve países del fig local con 201 puntos y seis países de `pwt-oecd-rd-tfp`. No hay ninguna pareja x/y exactamente igual; sólo dos coinciden dentro de tolerancia absoluta `1e-12`. El archivo recibido para esa comparación contiene `COUNTRY`, `lnrdworker` y `g10.accttfp`, sin columna temporal. Conservar ese fig como objeto de 2021 con identificador Chart Studio indeterminado, sin asignarlo a 116/118/120/72.

## Código y límites de reproducción

En Crecimiento, `Accounting/Ejemplo Estados Unidos.Rmd`, blob histórico `94a026433aebb4e180fd7cc4fd670fec2a4c4bd4`, genera `kyonly`, `hconly` y `tfponly` y termina con `api_create(fig, filename="pwt-account-usa")` en L58. No registra una URL de retorno que lo asigne a un ID. Se conservó una copia exacta como contexto; no se ejecutó esa instrucción. Su versión publicada ya fue adaptada para renderizar sin publicar.

La nota de Solow, blob `39267ed7b55d42e0beae2a3e3edb4bafd6b0a3ed`, documenta parámetros de un ejemplo: `g_A=0.0208` (L51), `alpha≈0.3`, `delta≈0.05`, `n=0.011`, `s=0.249`, intercepto 9.58 y `A_0=8,955`. Las fórmulas numéricas de L66/L72 usan `.02`. Son hechos del texto archivado; no se corrigieron ni se impuso una equivalencia con las curvas ausentes. El código actual del curso `Guide_PWT_Apply.r` usa `pwt10.01`; el ejemplo histórico de Crecimiento usa `pwt10.0`. No mezclar versiones o recalibrar para hacer coincidir una gráfica sin evidencia.

Hay animaciones y controles que deben conservarse o describirse explícitamente en una vista alternativa: `me-gA-dynamics` tiene 250 frames, `me-lny-animated` 30, y las correlaciones de inversión/población contienen siete frames cada una. Dibujar sólo `data` inicial omitiría parte del contenido.

Para cada ID, la propuesta temática deberá conservar el estado «original no identificado» y citar cualquier widget alternativo como material del curso fuente. Un parecido de título, país, variables, orden de diapositivas o nombre de exportación no acredita igualdad de valores ni la identidad de Chart Studio.

## Evidencia y método

- `history_scan.py` y `crecimiento_history_scan.json`: recorrido por `git rev-list --all`, árboles de todos los commits, lectura de blobs y parseo de HTML/JSON anidado; sin checkout, ejecución ni solicitudes a Chart Studio.
- `ceideas_history.json/.md` e `intro_history.json`: alcance y resultado de los repositorios relacionados.
- `studyguide_inventory.json`, `studyguide_scan.json`, `studyguide_widgets.json`, `studyguide_control_comparison.json`: inventario histórico, fuentes y controles.
- `source_context/`: copias exactas del ejemplo Accounting y la nota Solow, comprobadas mediante hash de blob Git.

Se consultaron las refs anunciadas y los commits alcanzables. Commits eliminados no anunciados, objetos nunca versionados, repositorios fuera del alcance y originales no encontrados quedan fuera de esta conclusión. No se editó ni publicó contenido remoto, no se ejecutaron scripts del repositorio y no se repitieron las peticiones HTTP 410.

La matriz final `history_status_matrix.json` conserva las 40 identidades, sus referencias verificadas en el commit publicado d8613e6 y alternativas separadas. La propuesta temática está en `thematic_proposal.json/.md`: 14 candidatas temáticas, 10 condicionadas, nueve ambiguas y siete sin candidata directa. Los 31 widgets propuestos están extraídos entre el conjunto principal y los dos adicionales (`metadata_extra.json`); esto no acredita ninguno de los 40 IDs como original.
