# Recursos esenciales del curso

21 vistas locales, insumos archivados el 12 de noviembre de 2026. Abrir [el índice](index.html) desde la copia completa del repositorio. 20 figuras generadas incluyen HTML, CSV, JSON, PNG y SVG. La tasa marginal máxima reutiliza exactamente la imagen histórica del curso, sin datos digitalizados.

## Correspondencia y fuentes

- Energía: las dos vistas Energy Institute se sustituyen por WDI EG.USE.PCAP.KG.OE, CC BY 4.0. El CSV Grapher aplica factor de presentación 11.63 para mostrar kWh; se divide por 11.63 para recuperar kg equivalentes de petróleo. Total = energía por habitante × población UN WPP / 1e9, en millones de toneladas equivalentes de petróleo. Cobertura 1990–2023 y unidad difieren de los TWh originales. No se redistribuyen observaciones Energy Institute.
- Cuatro referencias de mortalidad IHME pasan a exposición media anual PM2.5 (WDI, CC BY 4.0), que no mide fallecimientos ni mortalidad. Salud: [OMS](https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health). No se incluyen las observaciones restringidas de mortalidad.
- Dispersión: mismo año por variables y países ISO; excluye agregados y registros incompletos. Líneas sin interpolación de faltantes.
- CO₂: Global Carbon Budget 2026, CC BY 4.0, emisiones territoriales fósiles e industriales sin uso del suelo. Totales convertidos a millones de toneladas /1e6.
- SO₂: CEDS 2024, CC BY 4.0, vía OWID. URL antigua por país 404; archivo regional también incluye países. Datos originales en toneladas aunque el slug mencione millones: conversión explícita.
- Cero neto: Net Zero Tracker 2026, CC BY-NC 4.0. Uso docente no comercial, sin equiparar compromisos a cumplimiento.
- Londres y Delhi: partículas suspendidas totales históricas, Fouquet (2011) y Gobierno de India (2012–13), compiladas por OWID. Difiere de PM2.5 y de observaciones actuales. Metadata del proveedor sin licencia específica: no se atribuye una licencia abierta al origen.
- Laboral: WDI, CC BY 4.0. Razón femenina/masculina y participación femenina: OIT modelada. Empleo/población: estimaciones nacionales. Población femenina de 15+.
- FRED: identidad IITTRHB verificada en FOJf y en imagen archivada. Serie anual, %, sin ajuste estacional, última observación 2018, actualización 14-ene-2021. Imagen histórica, no edición de 2026.

## Regeneración

Ejecutar python scripts/generar_recursos_esenciales.py. Reproduce figuras y catálogos sin red; --export produce imágenes mediante Playwright/Chrome. JSON alimenta efectivamente cada gráfica; CSV conserva observaciones seleccionadas. Metadatos API: edición, unidad, actualización y condiciones por indicador. catalogo.json registra hashes de los CSV de entrada.

Apariencia y selección son reconstrucciones locales. No se acredita igualdad de píxeles con los iframes históricos, salvo el PNG FRED reutilizado. Fuentes externas: consulta opcional.
