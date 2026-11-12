# Gráficas reconstruidas de Crecimiento

40 gráficas locales integradas en las fuentes Rmd de seis módulos. Abrir `index.html` conservando esta carpeta completa. GitHub muestra el código HTML: descargar o clonar para interactuar. Las vistas, las animaciones y las descargas funcionan sin conexión; los enlaces de procedencia abren fuentes externas.

Cada gráfica incluye CSV, especificación JSON completa, SVG, PNG y método de elaboración. El CSV describe la vista inicial; el JSON conserva todos los fotogramas. Las imágenes representan la vista inicial. El historial conserva las referencias originales de Chart Studio; los identificadores aquí organizan las sustituciones y no autentican los objetos desaparecidos.

Las fórmulas y los insumos archivados están en `fuentes/`. Ejecutar cada `generar.py` con una salida vacía para repetir el cálculo del grupo. El catálogo fija las huellas de las especificaciones integradas. Para reconstruir las vistas desde esta carpeta, ejecutar desde la raíz del repositorio:

```sh
python scripts/generar_graficas_reconstruidas.py graficas_reconstruidas /ruta/externa/vacia
```

Para repetir los cálculos sin red, con Python 3.10 o posterior y sólo su biblioteca estándar:

```sh
python graficas_reconstruidas/fuentes/solow_accounting/generar.py /salida/vacia/solow
python graficas_reconstruidas/fuentes/ideas_taxes/generar.py --output /salida/vacia/ideas
python graficas_reconstruidas/fuentes/energy_slowdown/generar.py --output /salida/vacia/energia
```

Los manifiestos de cada grupo describen los resultados del recálculo; `catalogo.json` contiene las rutas de las especificaciones integradas. Las tablas derivadas de energía y demografía, incluidos los numeradores y denominadores de dependencia, se conservan en `fuentes/energy_slowdown/derivados/`.

Las imágenes se exportan con el control de descarga de cada gráfico; `scripts/verificar_graficas_reconstruidas.py` permite regenerarlas en el navegador y comprobar datos, fotogramas y recursos locales. La construcción de HTML y CSV no requiere red. El navegador debe tener acceso a Plotly.js local, incluido con su licencia MIT.

Para notas y presentaciones, usar `scripts/renderizar_modulos.R` con el módulo deseado. El renderizador lleva las gráficas a la salida manteniendo los enlaces relativos. Los HTML históricos se conservan como antecedentes; las fuentes Rmd y los materiales actualizados usan las reconstrucciones.

No se interpolan valores ausentes ni se presentan asociaciones como causalidad. Las variaciones de especificación, muestra y unidades constan en el catálogo y las vistas individuales.
