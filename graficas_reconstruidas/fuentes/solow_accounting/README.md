# Reconstrucciones de Solow y Accounting

Esta entrega contiene 23 especificaciones Plotly nuevas, con títulos, ejes y series en español. Son reconstrucciones didácticas autorizadas, no copias autenticadas de los gráficos Chart Studio desaparecidos.

## Regeneración

Requiere Python 3.10 o posterior; utiliza sólo la biblioteca estándar.

    python generar.py /ruta/a/una/salida-vacia
    python verificar.py /ruta/a/una/salida-vacia

La primera orden produce 23 JSON y manifest.json. La segunda comprueba integridad, cobertura de IDs, series y frames no vacíos, números finitos, normalizaciones y un control independiente calculado previamente en R. La salida debe estar vacía y ser distinta de esta carpeta. No se usa red ni se publican gráficos ni se ejecutan los documentos Rmd.

## Cobertura

| Módulo | Identidades |
|---|---|
| Accounting | iguzmanv:195, 196, 197, 198; iguzmanvt:104, 110 |
| Solow | iguzmanvt:44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 78, 82, 122, 124, 126, 160, 162 |

Las identidades iguzmanv:198 e iguzmanvt:198 son distintas. Esta entrega sólo reconstruye la primera: participación del capital en costos. La figura 48 también se usa en Slowdown.

## Insumos y procedencia

- inputs/pwt100_cases.csv: 350 filas de USA, Alemania, Japón, Corea del Sur y China, 1950–2019. Conserva faltantes, nombres de columnas originales y número de fila del Excel.
- inputs/pwt100_cross_sections.csv: 1 647 filas para nueve años seleccionados, incluidos los rezagos necesarios para siete cortes internacionales.
- Fuente: hoja Data de Clases_Crecimiento_Economico/Accounting/Ejemplo Estados Unidos.xlsx, SHA256 e5a4816e51cf2d9caf4d415668fd5e0c8c966c1467ee6874c1cc0a47204ba5e7. Sus valores Data coinciden con la descarga oficial actual de PWT 10.0, revisión de junio de 2021.
- inputs/source_manifest.json: huellas, filas, campos y contexto de los Rmd del commit 8265d179322918f035cc4102f1bc9403cbcbb1dc. Los contextos archivados sólo normalizan CRLF a LF; se conservan ambas huellas.
- inputs/reference_R_104.csv: control independiente de las cuatro trazas USA, ejecutado en R 4.3.3 durante la auditoría. Su procedencia y huellas se conservan junto al archivo.
- context/: copias de lectura de los Rmd empleados para elegir ejes y fórmulas. No se ejecutan.

extraer_insumos.py acepta como argumento un checkout con el libro esperado. Comprueba la huella del libro y entrega un bundle base64 por stdout; no descarga ni modifica el repositorio. La regeneración habitual usa los insumos pequeños ya archivados y no necesita este extractor ni un checkout.

## Decisiones de cálculo

**BGP.** Las rectas son ajustes OLS explícitos sobre ln(PIB por habitante), no observaciones ni pronósticos. Fuera de sus ventanas son extrapolaciones descriptivas. Se conservan los coeficientes completos en el manifiesto.

| Figura | Ventanas de ajuste |
|---|---|
| 44 Japón | 1950–1990 y 2000–2019 |
| 46 USA | 1950–2019 |
| 48 USA | 1950–2000 y 2001–2019 |
| 50 Alemania | 1991–2019 |
| 54 Corea del Sur | 1953–1962 y 2010–2019 |
| 56 China | China 1952–1969 y referencia Corea del Sur 2010–2019 |
| 62 China | 1963–1977, 1978–2007 y 2008–2019 |

**Figura 60.** Modelo Solow en tiempo continuo, anclado en China 1978 y calibrado hasta 2019. α=0.3 y δ=0.05 son supuestos. La inversión utiliza el promedio de csh_i como aproximación; el crecimiento de población y del residual de productividad usa los extremos. El modelo y la serie observada se rotulan por separado.

**Figuras 78 y 82.** Simulaciones explícitas, sin observaciones ficticias. La 78 resuelve la dinámica R/A del modelo de ideas con θ=0.01 y crecimiento de investigadores de 2%; contiene 250 frames. La 82 compara dos transiciones Solow con capital inicial distinto y los mismos parámetros de largo plazo. Todos los parámetros y ecuaciones están en manifest.json.

**Figuras 160 y 162.** Siete cortes de 1960 a 2015, con filtros explícitos y la misma muestra por corte. El número de países aumenta de 55 a 179 según disponibilidad. Los faltantes no se interpolan. El tamaño de burbuja corresponde a población. La correlación no acredita causalidad.

**Accounting.** 195 usa rtfpna de PWT (2017=100); 196 calcula rnna/emp; 197 compara índices 1960=100 de capital y PIB por persona empleada. La 198 calcula RK/(W+RK), con R=0.05 y W≈labsh·rgdpna, y distingue esta aproximación de 1−labsh, participación en el PIB.

104 conserva exactamente la fórmula del ejemplo de la clase: α=0.3, referencia 1960, redondeos originales y capital humano ln(hc), sin añadir emp/pop. Sus 240 valores coinciden exactamente con el control R. 110 aplica la identidad a diferencias de diez años; el error numérico máximo de suma de contribuciones es inferior a 2e-14. El residual de este ejercicio no es la PTF rtfpna publicada por PWT.

## Ajustes del texto de clase

ajustes_texto.json propone sustituciones exactas de lectura; no se aplicaron al repositorio. Cada entrada incluye path, old, new, reason y expected_occurrences=1. Se verificaron secuencialmente las 50 sustituciones en cuatro Rmd.

Aplicarlas antes de reemplazar enlaces e iframes: algunas entradas conservan el embed original y añaden la especificación de ventanas o parámetros. Las propuestas corrigen los antiguos números BGP, las fechas de cobertura, la omisión del capital humano en la explicación y la confusión entre participación del capital en costos y en PIB. preparar_ajustes_texto.py regenera estas propuestas desde las copias de contexto.

## Validación y límites

verificar.py comprueba los datos y el contrato Plotly. La comprobación visual en navegador corresponde a la integración de estas especificaciones con el generador común. Ninguna afirmación de esta entrega identifica el payload histórico ni valida causalmente los modelos económicos.

