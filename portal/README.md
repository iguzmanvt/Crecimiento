# Portal de Crecimiento Económico

Abre `index.html` desde una copia completa del repositorio, o abre el índice de la raíz. El portal reúne las notas, presentaciones, lecturas y tareas por tema, con enlaces relativos que también funcionan bajo una subruta web.

La búsqueda incluye títulos, lecturas y apartados de ejercicios e ignora mayúsculas y acentos. Los enunciados históricos no fijan entregas vigentes. Sin JavaScript, todos los temas y tareas siguen disponibles.

El portal y las figuras locales funcionan sin conexión. Los enlaces a libros, artículos y fuentes estadísticas conservan sus condiciones de acceso editorial o institucional.

## Generación y comprobación

Desde la raíz del repositorio:

```sh
python scripts/generar_portal.py
python scripts/verificar_entrega.py --report entrega_estatica.json
```

El generador toma el orden y las relaciones de `material_consulta/catalogo.json`, las rutas de `materiales_actualizados/catalogo.json` y los catálogos de las dos colecciones de Introducción. Actualiza los índices del portal, Introducción y la raíz. `manifest.json` conserva las huellas de entrada y salida. El verificador comprueba destinos y anclas locales, recursos HTML/CSS, catálogos, huellas de datos y carga local de fórmulas; no consulta los enlaces externos.

Para comprobar además las vistas con Chromium, las fórmulas SVG, las figuras y la navegación, con internet externo bloqueado:

```sh
python -m pip install -r scripts/requirements_verificacion.txt
python -m playwright install chromium
python scripts/verificar_entrega_navegador.py --report entrega_navegador.json
```

En Windows también se puede indicar un Chrome instalado con `--browser-executable`. La comprobación abre las vistas desde disco y bajo `/Crecimiento/`. Los informes describen su alcance y conservan los fallos observados.

El flujo `.github/workflows/curso.yml` ejecuta estas comprobaciones en cada propuesta de cambio y actualización de `main`. Sólo publica en Pages después de que pasen; una propuesta de cambio no despliega el sitio. La publicación requiere que GitHub Pages esté configurado para GitHub Actions en el repositorio.

El flujo también recalcula las 40 figuras previamente reconstruidas, las dos colecciones de Introducción y los recursos esenciales de los otros temas desde sus insumos archivados. No vuelve a ejecutar R en el servidor. Las huellas de las fuentes R Markdown detectan cambios sin regenerar los materiales canónicos.

El renderizado completo de las 33 notas, presentaciones y ejemplo se ejecuta explícitamente mediante `scripts/construir_entrega.py` y `scripts/renderizar_entrega.R`, en una carpeta separada que conserve los originales. Requiere R, Pandoc, `rmarkdown`, `jsonlite` y los paquetes de cada fuente (incluidos `knitr`, `png`, `jpeg`, `gridExtra`, `plotly`, `shiny`, `kableExtra` y `pwt10`). La versión y el resultado del entorno Windows utilizado se registran en `verificacion/estable_20261112/renderizado.json`; esos resultados no garantizan igualdad byte por byte con otras versiones de R o Pandoc.
