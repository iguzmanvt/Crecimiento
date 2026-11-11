# Referencias externas de los 15 módulos de Crecimiento

Captura de sólo lectura: **34 Rmd**, excluido Introduction, en `github-growth-modules-20261111/repo`. HEAD base `df1639e97f20b9e6b386b14d4edfe2ef3b84efac`; lectura UTC `2026-11-11T20:22:59.549919+00:00`. Se inspeccionó el **árbol de trabajo**, que ya integra las recuperaciones 42/223: las líneas del informe corresponden a esa captura y no necesariamente al commit base. Ningún archivo cambió durante la captura. Las huellas de los archivos leídos están en el JSON.

**136 referencias externas**: 94 iframes y 42 enlaces Markdown. Son 100 URL literales únicas: 79 de Chart Studio, 20 OWID y 1 FRED. Las 100 URL se comprobaron mediante GET público; 79 terminaron en HTTP 410 y 21 en HTTP 200. Esta comprobación mide respuesta HTTP, no ejecución de gráficas ni validez de datos.

La tabla agrupa por **módulo lógico según scripts/modulos.csv**, cotejado en el clon. La Nota de Medio Ambiente permanece físicamente en Energy, pero pertenece a Environment: ambos módulos tienen dos Rmd. El JSON conserva module_physical y module_logical.

| Módulo | Rmd | Referencias | Iframes | Identidades Plotly | URL OWID | URL FRED |
|---|---:|---:|---:|---:|---:|---:|
| Accounting | 3 | 12 | 6 | 6 | 0 | 0 |
| Competition | 2 | 0 | 0 | 0 | 0 | 0 |
| Convergence | 2 | 0 | 0 | 0 | 0 | 0 |
| Energy | 2 | 18 | 16 | 2 | 7 | 0 |
| Environment | 2 | 20 | 20 | 0 | 10 | 0 |
| Ideas | 3 | 27 | 18 | 9 | 0 | 0 |
| Labor | 3 | 0 | 0 | 0 | 0 | 0 |
| Labor_2 | 3 | 9 | 9 | 0 | 3 | 0 |
| Patents | 2 | 0 | 0 | 0 | 0 | 0 |
| Pensions | 2 | 0 | 0 | 0 | 0 | 0 |
| Slowdown | 2 | 10 | 5 | 6 | 0 | 0 |
| Solow | 2 | 34 | 17 | 17 | 0 | 0 |
| Structural_Transformation | 2 | 0 | 0 | 0 | 0 | 0 |
| Taxes | 2 | 6 | 3 | 2 | 0 | 1 |
| Technological_Diffusion | 2 | 0 | 0 | 0 | 0 | 0 |

Las identidades y URL de la tabla pueden repetirse entre módulos. Globalmente hay **40 identidades Chart Studio** (`usuario:ID`) y 91 apariciones. Se preservan los dos usuarios, `iguzmanv` e `iguzmanvt`. Los prefijos `//` se solicitaron con HTTPS; los `http://` explícitos se comprobaron por separado. Los 40 HTTP iniciales redirigieron con 308 a HTTPS; las 79 solicitudes de URL terminaron en 410.

Ninguna de esas 40 identidades tiene una sustitución local integrada en los Rmd capturados. Esto no equivale a afirmar que carezcan de datos o respaldos: ese inventario no se realizó en esta subauditoría. Las vistas locales 42 y 223 sí están integradas, con 10 referencias HTML/SVG en cinco fuentes, y los 10 destinos existen. Ya no aparecen como referencias externas.

| Identidad Chart Studio | Apariciones | Módulos | URL pública representativa | Resultado |
|---|---:|---|---|---|
| `iguzmanv:195` | 2 | Accounting | [Abrir](https://plotly.com/~iguzmanv/195.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanv:196` | 2 | Accounting | [Abrir](https://plotly.com/~iguzmanv/196.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanv:197` | 2 | Accounting | [Abrir](https://plotly.com/~iguzmanv/197.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanv:198` | 3 | Accounting, Slowdown | [Abrir](https://plotly.com/~iguzmanv/198.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:44` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/44.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:46` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/46.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:48` | 4 | Slowdown, Solow | [Abrir](https://plotly.com/~iguzmanvt/48.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:50` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/50.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:52` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/52.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:54` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/54.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:56` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/56.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:58` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/58.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:60` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/60.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:62` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/62.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:72` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/72.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:76` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/76.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:78` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/78.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:82` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/82.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:96` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/96.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:100` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/100.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:102` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/102.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:104` | 2 | Accounting | [Abrir](https://plotly.com/~iguzmanvt/104.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:110` | 2 | Accounting | [Abrir](https://plotly.com/~iguzmanvt/110.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:112` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/112.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:116` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/116.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:118` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/118.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:120` | 3 | Ideas | [Abrir](https://plotly.com/~iguzmanvt/120.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:122` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/122.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:124` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/124.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:126` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/126.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:132` | 2 | Taxes | [Abrir](https://plotly.com/~iguzmanvt/132.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:134` | 2 | Taxes | [Abrir](https://plotly.com/~iguzmanvt/134.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:160` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/160.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:162` | 2 | Solow | [Abrir](https://plotly.com/~iguzmanvt/162.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:190` | 2 | Energy | [Abrir](https://plotly.com/~iguzmanvt/190.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:192` | 2 | Energy | [Abrir](https://plotly.com/~iguzmanvt/192.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:198` | 1 | Slowdown | [Abrir](http://plotly.com/~iguzmanvt/198.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:211` | 2 | Slowdown | [Abrir](https://plotly.com/~iguzmanvt/211.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:213` | 2 | Slowdown | [Abrir](https://plotly.com/~iguzmanvt/213.embed) | HTTP 410 en todas sus variantes comprobadas |
| `iguzmanvt:216` | 2 | Slowdown | [Abrir](https://plotly.com/~iguzmanvt/216.embed) | HTTP 410 en todas sus variantes comprobadas |

**Diferencia que requiere conservar la procedencia:** Slowdown presentación L48 usa `iguzmanv/198`; Slowdown Nota L41 usa `iguzmanvt/198`. Aunque el texto cercano trata la participación del capital, son identidades distintas. Accounting utiliza `iguzmanv` en 195,196,197,198 y `iguzmanvt` en 104,110. No se corrigió ni fusionó ninguna referencia.

No contar únicamente iframes: estas cinco fuentes contienen enlaces externos y cero iframes. Energy Nota también mezcla enlaces Markdown con iframes; sus referencias se incluyeron.

| Fuente sin iframe | Enlaces | Líneas de la captura |
|---|---:|---|
| `Clases_Crecimiento_Economico/Accounting/Crecimiento Economico - Contabilidad del crecimiento Nota.Rmd` | 6 | 81, 98, 142, 144, 146, 156 |
| `Clases_Crecimiento_Economico/Ideas/Crecimiento Economico - Ideas Nota.Rmd` | 9 | 94, 99, 104, 108, 113, 117, 122, 258, 262 |
| `Clases_Crecimiento_Economico/Slowdown/Crecimiento Economico - Desaceleración Nota.Rmd` | 5 | 35, 41, 400, 409, 416 |
| `Clases_Crecimiento_Economico/Solow/Crecimiento Economico 2 Nota.Rmd` | 17 | 20, 22, 24, 26, 36, 38, 88, 90, 92, 94, 96, 98, 100, 102, 104, 106, 108 |
| `Clases_Crecimiento_Economico/Taxes/Crecimiento Economico - Politica Fiscal y crecimiento Nota.Rmd` | 3 | 15, 21, 41 |

**Duplicados:** hay 36 apariciones adicionales sobre la primera de cada URL literal. Las dos presentaciones de Labor_2, con y sin `(1)`, son idénticas byte a byte; las dos Notas de Labor también. El JSON conserva los archivos separados, su SHA256 y todas las líneas. Repetir una URL en una nota/presentación o módulo no implica que los documentos completos sean duplicados.

**OWID y FRED:** las 21 URL únicas terminaron en HTTP 200: 43 apariciones OWID y 2 FRED. Se conservaron 20 consultas OWID distintas, incluido el mismo gráfico `share-deaths-air-pollution` con y sin selección de países. Las 10 URL ambientales se repiten en las dos fuentes lógicas de Environment, aunque una permanezca en la carpeta Energy. Las tres URL de participación laboral de Labor_2 se repiten en sus tres fuentes. Son dependencias de red; no se identificó una sustitución local integrada para ellas.

| URL pública original | Módulos | Apariciones | HTTP final | Redirección |
|---|---|---:|---:|---|
| [graph-landing.php ? g=FOJf&width=1000&height=475](https://fred.stlouisfed.org/graph/graph-landing.php?g=FOJf&width=1000&height=475) | Taxes | 2 | 200 | Sin redirección |
| [air-pollution-london-vs-delhi](https://ourworldindata.org/grapher/air-pollution-london-vs-delhi) | Environment | 2 | 200 | Sin redirección |
| [annual-co2-emissions-per-country ? tab=chart&country=CHN~USA~IND~GBR~KOR~JPN](https://ourworldindata.org/grapher/annual-co2-emissions-per-country?tab=chart&country=CHN~USA~IND~GBR~KOR~JPN) | Environment | 2 | 200 | Sin redirección |
| [birth-rate-the-number-of-births-per-1000-people-in-the-population ? country=CHN~USA+%28blacks%29~USA+%28whites%29~MEX~FRA~JPN~England+and+Wales](https://ourworldindata.org/grapher/birth-rate-the-number-of-births-per-1000-people-in-the-population?country=CHN~USA+%28blacks%29~USA+%28whites%29~MEX~FRA~JPN~England+and+Wales) | Energy | 2 | 200 | [Destino final](https://ourworldindata.org/grapher/long-run-birth-rate?country=CHN%7EUSA+%28blacks%29%7EUSA+%28whites%29%7EMEX%7EFRA%7EJPN%7EEngland+and+Wales) |
| [children-per-woman-by-gdp-per-capita](https://ourworldindata.org/grapher/children-per-woman-by-gdp-per-capita) | Energy | 2 | 200 | [Destino final](https://ourworldindata.org/grapher/children-per-woman-fertility-rate-vs-level-of-prosperity) |
| [children-per-woman-un ? tab=chart&time=1950..latest&country=OWID_WRL~BGD~NGA~GHA~DEU~IND~GBR~USA~CHN~KOR~JPN](https://ourworldindata.org/grapher/children-per-woman-un?tab=chart&time=1950..latest&country=OWID_WRL~BGD~NGA~GHA~DEU~IND~GBR~USA~CHN~KOR~JPN) | Energy | 2 | 200 | Sin redirección |
| [co-emissions-per-capita](https://ourworldindata.org/grapher/co-emissions-per-capita) | Environment | 2 | 200 | Sin redirección |
| [death-rate-from-air-pollution-per-100000 ? tab=map](https://ourworldindata.org/grapher/death-rate-from-air-pollution-per-100000?tab=map) | Environment | 2 | 200 | Sin redirección |
| [energy-use-per-capita-vs-gdp-per-capita ? yScale=log&time=1990..2015](https://ourworldindata.org/grapher/energy-use-per-capita-vs-gdp-per-capita?yScale=log&time=1990..2015) | Energy | 2 | 200 | Sin redirección |
| [female-employment-to-population-ratio](https://ourworldindata.org/grapher/female-employment-to-population-ratio) | Labor_2 | 3 | 200 | Sin redirección |
| [female-labor-force-participation-rates-by-national-per-capita-income](https://ourworldindata.org/grapher/female-labor-force-participation-rates-by-national-per-capita-income) | Labor_2 | 3 | 200 | Sin redirección |
| [life-expectancy-vs-gdp-per-capita](https://ourworldindata.org/grapher/life-expectancy-vs-gdp-per-capita) | Energy | 2 | 200 | Sin redirección |
| [net-zero-targets ? country=SVN~MCO~ECU~AFG~GMB~PER~BGR~SEN](https://ourworldindata.org/grapher/net-zero-targets?country=SVN~MCO~ECU~AFG~GMB~PER~BGR~SEN) | Environment | 2 | 200 | Sin redirección |
| [number-of-deaths-by-risk-factor](https://ourworldindata.org/grapher/number-of-deaths-by-risk-factor) | Environment | 2 | 200 | Sin redirección |
| [per-capita-energy-use ? tab=chart&country=CHN~IND~JPN~GBR~USA~KOR~OWID_WRL~MEX~DEU](https://ourworldindata.org/grapher/per-capita-energy-use?tab=chart&country=CHN~IND~JPN~GBR~USA~KOR~OWID_WRL~MEX~DEU) | Energy | 2 | 200 | [Destino final](https://ourworldindata.org/grapher/energy-mix?metric=per_capita&source=total&tab=chart&country=CHN%7EIND%7EJPN%7EGBR%7EUSA%7EKOR%7EOWID_WRL%7EMEX%7EDEU) |
| [primary-energy-cons ? tab=chart&country=USA~CHN~IND~KOR~GBR~JPN~MEX~DEU](https://ourworldindata.org/grapher/primary-energy-cons?tab=chart&country=USA~CHN~IND~KOR~GBR~JPN~MEX~DEU) | Energy | 2 | 200 | [Destino final](https://ourworldindata.org/grapher/energy-mix?metric=total&source=total&tab=chart&country=USA%7ECHN%7EIND%7EKOR%7EGBR%7EJPN%7EMEX%7EDEU) |
| [ratio-of-female-to-male-labor-force-participation-rates-ilo-wdi](https://ourworldindata.org/grapher/ratio-of-female-to-male-labor-force-participation-rates-ilo-wdi) | Labor_2 | 3 | 200 | Sin redirección |
| [share-deaths-air-pollution](https://ourworldindata.org/grapher/share-deaths-air-pollution) | Environment | 2 | 200 | Sin redirección |
| [share-deaths-air-pollution ? tab=chart&country=ARE~High-middle+SDI~Middle+SDI~GNQ~High+SDI~Low+SDI~Low-middle+SDI](https://ourworldindata.org/grapher/share-deaths-air-pollution?tab=chart&country=ARE~High-middle+SDI~Middle+SDI~GNQ~High+SDI~Low+SDI~Low-middle+SDI) | Environment | 2 | 200 | Sin redirección |
| [so-emissions-by-world-region-in-million-tonnes](https://ourworldindata.org/grapher/so-emissions-by-world-region-in-million-tonnes) | Environment | 2 | 200 | Sin redirección |
| [so-emissions-tonnes-per-year](https://ourworldindata.org/grapher/so-emissions-tonnes-per-year) | Environment | 2 | 200 | [Destino final](https://ourworldindata.org/explorers/air-pollution) |

Cinco URL OWID redirigen con 301. Destaca `so-emissions-tonnes-per-year`, cuyo destino es el explorador general de contaminación sin una selección específica en la URL. Ese HTTP 200 no acredita que conserve la gráfica docente. El JSON registra destinos, parámetros, títulos parciales y observaciones para las cinco redirecciones.

Las consultas temporales requieren atención: `children-per-woman-un` incluye `time=1950..latest`; su extremo final puede cambiar. `energy-use-per-capita-vs-gdp-per-capita` fija `time=1990..2015`. También se conservaron las selecciones de país, `tab`, `yScale` y demás parámetros sin afirmar que sigan aceptándose o produzcan la misma serie.

La búsqueda estática capturó los 136 marcadores HTTP/protocolo relativo encontrados. La comprobación adicional no encontró direcciones iniciadas en `www.`, FTP o `mailto:` en esas fuentes. El JSON ofrece cada referencia con archivo, línea, forma original, tipo y contexto; también separa los estados HTTP de la evidencia local.

Método y límites: Windows, GET sin autenticación, concurrencia máxima 3 por grupo, timeout 7 s; lectura final limitada a 2 KB para Chart Studio y 8 KB para OWID/FRED. Los cuerpos de redirección intermedios de urllib no se instrumentaron. No hubo errores de solicitud. No se ejecutaron HTML, Rmd ni scripts, no se consultaron datasets grandes, ni se modificó o publicó contenido. La disponibilidad es una observación del 11 de noviembre de 2026; no acredita recuperación, contenido estadístico, funcionamiento del iframe o equivalencia histórica.
