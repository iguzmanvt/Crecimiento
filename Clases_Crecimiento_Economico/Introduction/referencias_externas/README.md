# Referencias externas de Introducción

El [catálogo por recurso](catalogo.md) organiza las 32 referencias de las dos presentaciones de Introducción: 17 de Chart Studio y 15 de Our World in Data (OWID). Esta entrega conserva las configuraciones archivadas de 13 recursos OWID. **No se recuperaron series numéricas nuevas.**

| Resultado al 11 de noviembre de 2026 | Cantidad | Alcance |
| --- | ---: | --- |
| Referencias de las presentaciones | 32 | 17 identificadores Chart Studio y 15 URL OWID |
| Configuraciones OWID extraídas del HTML histórico | 13 | Título, diseño, dimensiones, identificadores de variables, fuentes y entidades disponibles; sin observaciones |
| Recursos OWID sin página incrustada en la nota histórica | 2 | Las presentaciones añaden las referencias sobre PIB por habitante y pobreza para China, India y África subsahariana |
| Series numéricas recuperadas en este bloque | 0 | No se sustituyeron por cifras actuales ni por otras gráficas |

## Consulta y reproducción

- [Catálogo legible](catalogo.md): orden, contexto docente, URL y estado de cada recurso.
- [CSV](referencias.csv): las 32 referencias para seguimiento.
- [JSON](catalogo.json): referencias, ocurrencias por fuente, huellas y 13 configuraciones completas extraídas.
- [Comprobación remota](verificacion_remota_20261111.json): resultado fechado de las consultas a Chart Studio.
- [Solicitud preparada para Plotly](solicitud_respaldo.md): cuenta e identificadores que permitirían pedir los datos originales.

Desde la raíz del repositorio, con Python 3:

```sh
python Clases_Crecimiento_Economico/Introduction/referencias_externas/auditar_referencias.py
```

También puede invocarse la ruta absoluta del script desde otro directorio. No necesita paquetes adicionales, conexión ni credenciales. Lee las tres fuentes R Markdown y el HTML histórico, comprueba sus blobs del commit `44f93109beda966ec5ea4717135897bf57fd5e97` y regenera JSON, CSV y catálogo Markdown. Si cambian esas fuentes, se detiene para que se revise su procedencia. Los archivos de entrada permanecen intactos.

La correspondencia de las 13 configuraciones con la nota Rmd se hace por el orden de sus 13 iframes. Se guardan tanto la URL de esa nota como la URL canónica del respaldo y la línea del HTML. Esta asociación documental no demuestra que versiones actuales de los datos sean equivalentes a las de la clase. La configuración conserva el crédito `sourceDesc` cuando existe; no incorpora los valores que OWID cargaba desde sus servicios externos.

## Búsqueda y límites comprobados

En el repositorio se inspeccionaron las 16 notas HTML anteriores a estas entregas: 35 páginas HTML incrustadas. Sólo aparecieron datos Plotly identificables para las gráficas 42 y 223, recuperadas previamente en sus módulos. Ninguna de las 17 gráficas Chart Studio de Introducción conservaba allí un respaldo numérico.

En los materiales docentes locales se revisaron 238 archivos —54 Rmd, 132 HTML, seis JSON, 38 R y ocho historiales— y dos espacios de trabajo de R con 42 objetos. Se resolvieron 14 archivos con codificación Windows-1252. No se encontró un respaldo vinculado a los 17 identificadores. El único objeto Plotly observado no conserva esos IDs; no se le atribuye una gráfica de Introducción. No se ejecutaron los historiales ni se enviaron datos al proveedor.

Las 17 páginas `.embed` respondieron HTTP 410. Una consulta `.json` de la gráfica 150 también devolvió 410; la prueba del endpoint antiguo `api.plot.ly` terminó con error de conexión, sin una respuesta HTTP que permita concluir ausencia de datos allí. El registro conserva la fecha y URL exactas.

Plotly [informa que cerró Chart Studio el 31 de octubre de 2025 y permite solicitar los datos al soporte](https://plotly.com/chart-studio-updates/). La solicitud preparada se limita a estos 17 IDs. No acredita que el proveedor conserve todos los archivos ni que ya haya entregado un respaldo.

La nota histórica repite el ID 172 donde las dos presentaciones usan 176, y contiene `158.embe` frente a `158.embed` en ambas presentaciones. El catálogo conserva las referencias y documenta la diferencia; las notas y presentaciones mantienen sus bytes originales. Las gráficas archivadas de OWID también pueden usar consultas como `time=latest`; la existencia de un enlace no fija su edición estadística.

## Criterios de cierre y continuación

| Criterio | Resultado |
| --- | --- |
| Identificar cada referencia y su localizador | 32 recursos, con ocurrencias en las tres fuentes |
| Distinguir configuración de observaciones | 13 configuraciones conservadas, cero series nuevas recuperadas |
| Conservar títulos, fuentes y procedencia | Configuraciones completas, blobs y SHA-256 del respaldo |
| Regenerar sin red | Script de biblioteca estándar; JSON/CSV/Markdown con finales LF |
| Cotejar el contenido extraído | 94 ocurrencias y 13 configuraciones iguales al respaldo; CSV de 32 filas |
| Detectar una fuente cambiada | Una copia alterada del Rmd fue rechazada antes de generar salidas |
| Preservar el material docente | Rmd, imágenes, HTML históricos y recuperaciones anteriores intactos |
| Recuperar las 17 gráficas Chart Studio | Pendiente de un respaldo original identificable |

El siguiente paso es obtener el respaldo del proveedor. Con datos, diseño y un identificador verificable, podrá reconstruirse cada gráfica local y cotejar sus valores antes de sustituir una referencia. Una actualización con estadísticas recientes sería una entrega separada con fecha, unidades, fuente y edición propias.
