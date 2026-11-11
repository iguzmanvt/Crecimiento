# Vistas locales de apoyo a Crecimiento

Abrir [index.html](index.html) desde una copia local de esta carpeta. Conservar `assets`, `datos`, `graficas` y `licencias` juntos. Las 44 vistas funcionan sin conexión; los enlaces de procedencia abren fuentes externas. GitHub muestra el código HTML: para interactuar hay que descargar o clonar el repositorio y abrir el archivo local.

Se incluyen 43 widgets archivados de StudyGuide y una reconstrucción del objeto `fig` del curso con 265 pares, nueve países y obsTime 1981–2019. No se ha autenticado ninguno de los 40 identificadores Chart Studio pendientes. La [matriz](matriz_identidades.json) ofrece alternativas temáticas y sus límites; no establece identidades por parecido.

Se conservan los datos, etiquetas y fotogramas. La adaptación ajusta el tamaño al navegador y usa Plotly.js 2.11.1 local. Las animaciones conservan 250, 30, 7 y 7 fotogramas. Los CSV contienen la vista inicial; los JSON conservan las animaciones completas. No se rellenan faltantes.

`oecd-rd-logrd` conserva valores en ln junto con un eje logarítmico. La vista advierte esa configuración y permite cambiar explícitamente a eje lineal para leer los valores ln; restaurar la escala no modifica las descargas originales.

Procedencia: Dietz Vollrath, StudyGuide, commit `3a8c79f20022ef7b985b392d73921839a4317883`, [licencia MIT original](licencias/LICENSE-StudyGuide). Plotly.js: [licencia MIT](licencias/LICENSE-Plotly.js). Los metadatos estadísticos son los disponibles en cada respaldo; el código actual del curso puede usar una edición diferente. No se actualizan cifras ni se replican todos los cálculos económicos.

[Informe de seguimiento](https://github.com/iguzmanvt/Crecimiento/blob/main/PENDIENTES_GRAFICAS_Y_PWT.md). [Catálogo y huellas](catalogo.json). Para regenerar en una salida vacía externa: `python scripts/generar_recursos_graficas.py recursos_graficas /ruta/externa/vacia`.
