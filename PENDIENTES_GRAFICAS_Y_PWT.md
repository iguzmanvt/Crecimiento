# Seguimiento de las gráficas y la diferencia PWT

11 de noviembre de 2026. Continuación del commit `d8613e6a2fe63c1b7b3659ab3211895686c14dce`.

## Resultado

- **Capital del ejemplo USA:** la hoja Data del Excel coincide con XLSX/DTA oficiales, 666 120 celdas. El objeto R `pwt10.0` conserva 35 valores distintos de `rnna`; el máximo absoluto es 8 millones de US$ de 2017. Las cuatro trazas 1960–2019 y los doce derivados coinciden exactamente bajo las fórmulas y redondeos originales: 240 puntos y 720 valores por fuente. Se cierra el riesgo de reproducción de este ejemplo; la operación upstream concreta que originó las diferencias sigue sin demostrarse. [Informe y celdas](verificacion/pendientes_20261111/pwt/pwt_discrepancy_audit.md).
- **Respaldo local del curso:** se recuperó el objeto `fig` de un workspace localizado en Otoño 2021: 265 pares, nueve países, obsTime 1981–2019, título y atributos conservados. La fecha de carpeta no autentica la creación y su identificador Chart Studio sigue indeterminado. Difiere del widget temáticamente parecido de StudyGuide; se conserva como una figura distinta.
- **Apoyo docente disponible:** [44 vistas locales](recursos_graficas/README.md), formadas por 43 widgets del material fuente y el objeto local. Los widgets se fijan a `dvollrath/StudyGuide@3a8c79f20022ef7b985b392d73921839a4317883`, con licencia MIT y atribución a Dietz Vollrath. Se conservan sus datos, etiquetas y todos los fotogramas. Estas vistas no acreditan identidad con los originales pendientes.
- **40 originales de Chart Studio:** ninguno fue autenticado en esta continuación. La historia Git, los archivos del curso y las vías públicas revisadas no aportaron sus payloads con identidad demostrable. Los fallos de algunos índices de archivo dejan parte de la cobertura indeterminada. [Historia Git](verificacion/pendientes_20261111/graficas/git_history_findings.md) · [Archivos públicos](verificacion/pendientes_20261111/graficas/public_archives.md).

No se modificaron Rmd, imágenes, HTML históricos, productos de las recuperaciones 42/223, Excel ni fórmulas del ejemplo. Las alternativas tienen acceso propio desde los README; los enlaces históricos se mantienen para conservar procedencia.

## Consulta y reproducción

Descargar o clonar el repositorio y abrir `recursos_graficas/index.html` con su carpeta completa. GitHub muestra código HTML; la interacción ocurre en la copia local. Las vistas usan Plotly.js 2.11.1 local y funcionan sin conexión. Los enlaces a fuentes externas mantienen su función de procedencia.

El [catálogo](recursos_graficas/catalogo.json) fija archivo, commit, blob y SHA-256. La [matriz verificable](recursos_graficas/matriz_identidades.json) conserva usuario e ID completos, incluidos `iguzmanv:198` y `iguzmanvt:198`, y los dos contextos de `iguzmanvt:48`. El material original de StudyGuide puede utilizar una versión estadística diferente del código actual; no se actualizaron los datos ni se hizo una asignación por parecido.

Para regenerar la galería en una carpeta vacía externa:

```sh
python scripts/generar_recursos_graficas.py recursos_graficas /ruta/externa/vacia
```

Para repetir el contraste del ejemplo con las entradas USA archivadas y las fórmulas del Rmd, con R, jsonlite y pwt10 instalados:

```sh
Rscript scripts/verificar_discrepancia_PWT.R
```

El segundo control usa las entradas guardadas en la auditoría y el objeto `pwt10.0` instalado; no vuelve a descargar las tablas oficiales completas. El [manifiesto de fuentes](verificacion/pendientes_20261111/pwt/source_manifest.json) conserva URL y huellas de las descargas utilizadas. La igualdad de este cálculo no se extiende a otros países, fórmulas o cálculos sin esos redondeos.

## Escala y animaciones

`oecd-rd-logrd` archiva valores ya transformados a ln y un eje logarítmico adicional. Su vista muestra una advertencia y permite consultar explícitamente un eje lineal para los valores ln o restaurar la configuración archivada. No se alteran sus JSON ni se presenta la configuración archivada como una recomendación docente sin revisión.

Las cuatro animaciones conservan 250, 30, 7 y 7 fotogramas. Los CSV contienen la vista inicial y distinguen atributos ausentes; los JSON conservan el contenido completo. Se comprobaron valores x/y de las 44 vistas, selección del último fotograma de cada animación, cambio/restauración de escala, recursos locales, JavaScript y ajuste de ancho. [Resultado de navegador](verificacion/pendientes_20261111/galeria_navegador.json). La revisión visual usa muestras; la comprobación automática cubre todas las vistas. No se validaron independientemente las estimaciones económicas del material fuente.

## Matriz de los 40 identificadores

Hay 14 alternativas temáticas, 10 condicionadas, nueve conjuntos ambiguos y siete casos sin candidato directo. Todas mantienen el estado de original sin autenticar. Una razón capital/producto no sustituye capital por trabajador; gasto público no equivale a tasa impositiva; empleados/población no equivale a dependencia demográfica. Cada fila conserva el límite específico.

| Identidad | Tema | Alternativa | Vistas de apoyo | Límite |
| --- | --- | --- | --- | --- |
| `iguzmanv:195` | TFP en nivel de Estados Unidos | Sin candidato directo | — | Una contribución de productividad al PIB, una tasa de crecimiento de TFP o una comparación transversal no reproduce un nivel de TFP. |
| `iguzmanv:196` | Capital por trabajador de Estados Unidos | Sin candidato directo | — | K/Y e inversión/PIB tienen denominadores distintos; no transformar ni recombinar datos para aparentar una recuperación. |
| `iguzmanv:197` | Capital y producción por trabajador de Estados Unidos | Sin candidato directo | — | PIB per cápita, K/Y y sus contribuciones no equivalen a producción y capital por trabajador. |
| `iguzmanv:198` | Participación del capital en costos de Estados Unidos | Sin candidato directo | — | La identidad iguzmanv:198 es distinta de iguzmanvt:198. W/(W+RK) no es RK/(W+RK); el complemento exigiría una transformación nueva y revisar definiciones. |
| `iguzmanvt:44` | Japón: distintos BGP | Condicionada | [pwt-apply-gtfp-jpn](recursos_graficas/graficas/pwt-apply-gtfp-jpn.html) | El eje es log de productividad, no log de PIB per cápita. La etiqueta original no especifica variable ni fechas; conservar esa diferencia. |
| `iguzmanvt:46` | Estados Unidos: BGP 1 | Ambigua | [pwt-apply-usa](recursos_graficas/graficas/pwt-apply-usa.html) | No asignar BGP 1/2 a cada línea por orden. Para 48, la aparición adicional en Slowdown no prueba una caída de productividad ni una ruptura causal desde 2000. |
| `iguzmanvt:48` | Estados Unidos: BGP 2 | Ambigua | [pwt-apply-usa](recursos_graficas/graficas/pwt-apply-usa.html) | No asignar BGP 1/2 a cada línea por orden. Para 48, la aparición adicional en Slowdown no prueba una caída de productividad ni una ruptura causal desde 2000. |
| `iguzmanvt:50` | Alemania: BGP | Apoyo temático | [pwt-apply-deu](recursos_graficas/graficas/pwt-apply-deu.html) | El widget usa log PIB per cápita; periodo y ajuste BGP son los del curso, no los del ID perdido. |
| `iguzmanvt:52` | Alemania: proporción K/Y | Apoyo temático | [pwt-apply-ky-deu](recursos_graficas/graficas/pwt-apply-ky-deu.html) | No confundir el stock K/Y con formación de capital/PIB; mantener años y definición originales del curso. |
| `iguzmanvt:54` | Corea del Sur: BGP | Apoyo temático | [pwt-apply-kor](recursos_graficas/graficas/pwt-apply-kor.html) | La existencia de dos líneas no identifica las rupturas ni datos de la gráfica histórica. |
| `iguzmanvt:56` | China: BGP | Apoyo temático | [pwt-apply-chn](recursos_graficas/graficas/pwt-apply-chn.html) | La línea de comparación coreana debe conservarse y explicarse; no presentarla como ajuste chino adicional. |
| `iguzmanvt:58` | China: crecimiento poblacional | Apoyo temático | [pwt-apply-gl-chn](recursos_graficas/graficas/pwt-apply-gl-chn.html) | La ventana de crecimiento debe conservarse como la del curso; no llamarla variación anual sin comprobar fórmula. |
| `iguzmanvt:60` | China: transición al BGP | Condicionada | [pwt-apply-chn](recursos_graficas/graficas/pwt-apply-chn.html) · [pwt-apply-comp](recursos_graficas/graficas/pwt-apply-comp.html) | Son alternativas distintas: trayectoria con BGP o comparación de países. No se conoce cuál correspondía al ID histórico. |
| `iguzmanvt:62` | China: diferentes BGP | Ambigua | [pwt-apply-chn](recursos_graficas/graficas/pwt-apply-chn.html) · [pwt-apply-gtfp-chn](recursos_graficas/graficas/pwt-apply-gtfp-chn.html) | El primero muestra log PIB per cápita; el segundo log productividad. No son intercambiables ni se puede elegir variable sólo por la etiqueta. |
| `iguzmanvt:72` | China y otros países: investigadores y crecimiento de productividad | Ambigua | [pwt-oecd-rd-tfp](recursos_graficas/graficas/pwt-oecd-rd-tfp.html) · [pwt-oecd-rd-gtfp](recursos_graficas/graficas/pwt-oecd-rd-gtfp.html) | rd-tfp usa nivel log de trabajadores FTE frente a crecimiento de productividad; rd-gtfp usa crecimiento de FTE frente a crecimiento de productividad. El primero se aproxima más al texto literal, pero no permite asignar IDs. pwt-oecd-level-rd es sólo material relacionado porque cambia la variable dependiente a nivel de productividad. |
| `iguzmanvt:76` | Simulación R/A y crecimiento de productividad | Apoyo temático | [me-gA-dynamics](recursos_graficas/graficas/me-gA-dynamics.html) | No es observación de países. Revisar parámetros, convergencia a R/A=2 y tasa 0.02 antes de afirmar réplica del texto; conservar todos los frames. |
| `iguzmanvt:78` | Dinámica de productividad | Condicionada | [me-gA-dynamics](recursos_graficas/graficas/me-gA-dynamics.html) | La etiqueta Rmd es amplia: no identifica esta simulación. Es crecimiento frente a R/A, no nivel de productividad contra tiempo; 250 frames. |
| `iguzmanvt:82` | Nivel del PIB per cápita | Condicionada | [me-lny-animated](recursos_graficas/graficas/me-lny-animated.html) | Simulación A/B/BGP, eje log PIB per cápita y tiempo abstracto; no corresponde a una serie empírica ni identifica país; 30 frames. |
| `iguzmanvt:96` | Trabajadores de I+D en el tiempo | Apoyo temático | [oecd-rd-fte](recursos_graficas/graficas/oecd-rd-fte.html) | Son trabajadores equivalentes a tiempo completo (FTE), no necesariamente número de personas. Los periodos difieren por país. |
| `iguzmanvt:100` | Gasto de I+D en logaritmos | Condicionada | [oecd-rd-logrd](recursos_graficas/graficas/oecd-rd-logrd.html) | REVISIÓN OBLIGATORIA: Guide_OECD_RD.r:71/77 ya transforma y a ln(OBS_VALUE), y :80 además configura yaxis.type=log; el payload confirma ambos. No presentarlo sin advertencia como log simple ni corregirlo silenciosamente. |
| `iguzmanvt:102` | Gasto real de I+D en el tiempo | Apoyo temático | [oecd-rd-levelrd](recursos_graficas/graficas/oecd-rd-levelrd.html) | No inventar moneda, PPP o año base desde el título; la fuente filtra PRICE_BASE=Q pero exige metadatos de unidades. La ventana «últimos veinte años» no es estable entre versiones. |
| `iguzmanvt:104` | Cálculo del residuo de Solow | Condicionada | [pwt-account-basic-usa](recursos_graficas/graficas/pwt-account-basic-usa.html) · [pwt-growth-acct-usa](recursos_graficas/graficas/pwt-growth-acct-usa.html) | No son una demostración intercambiable del mismo residuo. El Rmd sólo etiqueta el cálculo; seleccionar modelo, país y fórmula antes de insertar una alternativa. |
| `iguzmanvt:110` | Tasa de crecimiento anualizada de 10 años | Condicionada | [pwt-usa-growth-rate](recursos_graficas/graficas/pwt-usa-growth-rate.html) | La etiqueta Rmd no especifica aquí variable o país. El widget catalogado tiene x=1950–2009; verificar anclaje inicial/final de ventana y fórmula antes de afirmar equivalencia. |
| `iguzmanvt:112` | Esfuerzo de I+D y crecimiento de productividad | Apoyo temático | [pwt-growth-tfp-comp](recursos_graficas/graficas/pwt-growth-tfp-comp.html) | Muestra evolución temporal en seis países, no una prueba causal ni una correlación por sí sola. Leer junto con trabajadores/gasto de I+D; no afirmar ausencia estadística de asociación sin análisis. |
| `iguzmanvt:116` | China y otros países: investigadores y crecimiento de productividad | Ambigua | [pwt-oecd-rd-tfp](recursos_graficas/graficas/pwt-oecd-rd-tfp.html) · [pwt-oecd-rd-gtfp](recursos_graficas/graficas/pwt-oecd-rd-gtfp.html) | rd-tfp usa nivel log de trabajadores FTE frente a crecimiento de productividad; rd-gtfp usa crecimiento de FTE frente a crecimiento de productividad. El primero se aproxima más al texto literal, pero no permite asignar IDs. pwt-oecd-level-rd es sólo material relacionado porque cambia la variable dependiente a nivel de productividad. |
| `iguzmanvt:118` | China y otros países: investigadores y crecimiento de productividad | Ambigua | [pwt-oecd-rd-tfp](recursos_graficas/graficas/pwt-oecd-rd-tfp.html) · [pwt-oecd-rd-gtfp](recursos_graficas/graficas/pwt-oecd-rd-gtfp.html) | rd-tfp usa nivel log de trabajadores FTE frente a crecimiento de productividad; rd-gtfp usa crecimiento de FTE frente a crecimiento de productividad. El primero se aproxima más al texto literal, pero no permite asignar IDs. pwt-oecd-level-rd es sólo material relacionado porque cambia la variable dependiente a nivel de productividad. |
| `iguzmanvt:120` | China y otros países: investigadores y crecimiento de productividad | Ambigua | [pwt-oecd-rd-tfp](recursos_graficas/graficas/pwt-oecd-rd-tfp.html) · [pwt-oecd-rd-gtfp](recursos_graficas/graficas/pwt-oecd-rd-gtfp.html) | rd-tfp usa nivel log de trabajadores FTE frente a crecimiento de productividad; rd-gtfp usa crecimiento de FTE frente a crecimiento de productividad. El primero se aproxima más al texto literal, pero no permite asignar IDs. pwt-oecd-level-rd es sólo material relacionado porque cambia la variable dependiente a nivel de productividad. |
| `iguzmanvt:122` | Corea del Sur: proporción K/Y | Condicionada | [pwt-catchup-ky](recursos_graficas/graficas/pwt-catchup-ky.html) | solow/apply.md:81 apunta a pwt-apply-si-kor, cuyo eje es formación de capital/PIB: NO sirve como K/Y. Usar el widget multicountry intacto y señalar el país, o mantener pendiente. |
| `iguzmanvt:124` | Corea del Sur: crecimiento poblacional | Apoyo temático | [pwt-apply-gl-kor](recursos_graficas/graficas/pwt-apply-gl-kor.html) | Verificar fórmula de tasa y periodo; no equiparar automáticamente con natalidad o empleo. |
| `iguzmanvt:126` | China: proporción K/Y | Condicionada | [pwt-catchup-ky](recursos_graficas/graficas/pwt-catchup-ky.html) | solow/apply.md:102 apunta a pwt-apply-si-chn, cuyo eje es formación de capital/PIB: NO sirve como K/Y. No seleccionar por proximidad de orden en la página. |
| `iguzmanvt:132` | Gobierno y crecimiento del PIB per cápita | Apoyo temático | [pwt-all-cshg-growth](recursos_graficas/graficas/pwt-all-cshg-growth.html) | Gasto del gobierno no es tasa impositiva; no inferir causalidad. El periodo por punto no se obtiene de la posición x. |
| `iguzmanvt:134` | Gobierno y nivel del PIB per cápita | Apoyo temático | [pwt-all-cshg-level](recursos_graficas/graficas/pwt-all-cshg-level.html) | Nivel se muestra en logaritmos. No sustituir por pwt-test-chsg-level sin comparar payload; mantener versión no test y procedencia. |
| `iguzmanvt:160` | Correlación con la inversión | Apoyo temático | [pwt-corr-si](recursos_graficas/graficas/pwt-corr-si.html) | Son proporciones de inversión, no stock K ni K/Y. Hay 7 frames: el año y la muestra cambian; no convertir una animación a una única instantánea sin etiquetar. |
| `iguzmanvt:162` | Correlación con crecimiento poblacional | Apoyo temático | [pwt-corr-gl](recursos_graficas/graficas/pwt-corr-gl.html) | Conservar ventana y 7 frames; asociación no prueba efecto causal. |
| `iguzmanvt:190` | Datos sobre uso de energía | Ambigua | [wdi-energy-gdpe](recursos_graficas/graficas/wdi-energy-gdpe.html) · [eia-energy-share](recursos_graficas/graficas/eia-energy-share.html) · [eia-energy-price](recursos_graficas/graficas/eia-energy-price.html) · [eia-energy-intensity](recursos_graficas/graficas/eia-energy-intensity.html) | Son variables diferentes, no cuatro réplicas: kg equivalente de petróleo/PIB; gasto energético/PIB (%); precio implícito; uso de energía/PIB. En widgets EIA la traza no nombra país; no inferirlo por proveedor. La etiqueta no permite asignar 190/192 ni elegir unidades monetarias. |
| `iguzmanvt:192` | Datos sobre uso de energía | Ambigua | [wdi-energy-gdpe](recursos_graficas/graficas/wdi-energy-gdpe.html) · [eia-energy-share](recursos_graficas/graficas/eia-energy-share.html) · [eia-energy-price](recursos_graficas/graficas/eia-energy-price.html) · [eia-energy-intensity](recursos_graficas/graficas/eia-energy-intensity.html) | Son variables diferentes, no cuatro réplicas: kg equivalente de petróleo/PIB; gasto energético/PIB (%); precio implícito; uso de energía/PIB. En widgets EIA la traza no nombra país; no inferirlo por proveedor. La etiqueta no permite asignar 190/192 ni elegir unidades monetarias. |
| `iguzmanvt:198` | Participación del capital en la producción | Sin candidato directo | — | Mantener separado de iguzmanv:198. Compensación/PIB y compensación/costos son denominadores diferentes; no restar de 1 ni atribuir beneficios sin revisión. |
| `iguzmanvt:211` | Natalidad, preferencias familiares y envejecimiento | Sin candidato directo | — | wdi-fert-test es tasa global de fecundidad de Brasil, México, Nigeria y Viet Nam: variable, geografía y población distintas. No prueba preferencias ni causalidad. |
| `iguzmanvt:213` | Trabajadores/población y desaceleración | Condicionada | [pwt-catchup-emppop](recursos_graficas/graficas/pwt-catchup-emppop.html) | Observaciones hasta 2019, no proyecciones. Empleados/población no es proporción de adultos en edad laboral; el widget no prueba la causa por dependencia ni el «seguirá disminuyendo». |
| `iguzmanvt:216` | Adultos en edad laboral frente a dependientes 0–20 y 65+ | Sin candidato directo | — | No sustituir con empleados/población, crecimiento poblacional o fecundidad: cambian numerador, denominador y edades. |

## Criterios de aceptación y estado

| Requisito | Criterio | Evidencia | Estado |
| --- | --- | --- | --- |
| R-001: acotar diferencia de capital | AC-001: cotejo oficial y efecto exacto en cuatro trazas | 666 120 celdas iguales; 240/240 puntos y 720/720 derivados iguales por fuente | Cerrado para este ejemplo; causa upstream pendiente |
| R-002: buscar originales | AC-002: identificar payload y usuario:ID antes de declarar recuperación | Matriz de 40 identidades; historia y archivos consultados | 0/40 autenticados; pendiente de respaldo adicional |
| R-003: ofrecer material local utilizable | AC-003: valores y fotogramas conservados, procedencia y prueba offline | 43 widgets + objeto local; catálogo y navegador | Implementado y comprobado |
| R-004: conservar los originales | AC-004: objetos Git anteriores intactos salvo documentación prevista | Cotejo de árbol y copia nueva al publicar | Comprobado en el cotejo de originales |

## Recuperación restante

Plotly informa que cerró Chart Studio el 31 de octubre de 2025 y ofrece solicitar datos al soporte mediante correo con asunto `Chart Studio data request`: [página oficial, sección Can I access my Chart Studio data?](https://plotly.com/chart-studio-updates/). Se preparó una [solicitud para revisión](solicitud_respaldo_Chart_Studio.md), sin enviar mensajes. Debe verificarse la propiedad de cada cuenta; la diferencia entre `iguzmanvt` e `iguzmanv` se conserva. La entrega de ese respaldo permitiría autenticar las gráficas originales y sustituir sólo las correspondencias demostradas.

[Integridad y reproducción de los 146 archivos de galería](verificacion/pendientes_20261111/integridad_y_reproduccion.json).
