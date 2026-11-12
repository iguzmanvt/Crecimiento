# Tarea 2. México: modelo de Solow y contabilidad del crecimiento

Enunciado histórico del archivo del curso localizado en la carpeta Primavera 2023. Esta edición se ofrece para consulta y no fija una fecha de entrega vigente.

[Banco de tareas](README.md) · [Consulta por tema](../README.md).

## 1. Evolución del PIB per cápita de México.

Descargue los datos de la Penn World Tables (PWT versión 10.0 - [https://www.rug.nl/ggdc/productivity/pwt/](https://www.rug.nl/ggdc/productivity/pwt/)) considere las variables para **México** el periodo 1950-2019.

Alternativamente, pueden utilizar el siguiente código en R:

```r
# Librería necesaria
################################################################################
library(pwt10)
# Usar tablas de PWT
################################################################################
data("pwt10.0")
################################################################################
```

Nota: pueden utilizar otra versión pero la notación de las variables va a cambiar, chequen que estén utilizando las correctas.

## 1.1. Modelo de Solow y contabilidad del crecimiento

Para estudiar la evolución temporal de México, utilice variables de PWT 10.0 con una base de precios coherente: $Y_t=rgdpna_t$ y $K_t=rnna_t$, ambas a precios nacionales constantes de 2017; población $pop_t$ y capital humano $h_t=hc_t$.

Las variables $rgdpe$ y $cn$ tienen otras definiciones: la primera mide PIB real por el lado del gasto a PPA encadenadas y la segunda capital a PPA corrientes. No se emplean aquí como sustitutos de las dos series nacionales constantes. Las definiciones se pueden comprobar en la hoja Legend del [libro de datos del curso](../../Clases_Crecimiento_Economico/Accounting/Ejemplo%20Estados%20Unidos.xlsx), celdas B9, B21, B27 y B30.

### Senda de crecimiento balanceado

- Construya $y_t=Y_t/pop_t$ y grafique $\ln y_t$ para 1950–2019.
- Grafique las sendas de crecimiento balanceado utilizadas para describir la trayectoria de México. Indique los periodos del ajuste e interprete sus diferencias con base en lo visto en clase.

### Contabilidad del crecimiento

Defina $k_t=K_t/pop_t$, $h_t=hc_t$ y use $\alpha=0.45$ como parámetro fijo del ejercicio. No alterne esta elasticidad con una participación anual variable. La identidad con tecnología aumentadora del trabajo es:

$$\ln y_t=\alpha\ln k_t+(1-\alpha)\ln h_t+(1-\alpha)\ln A_t.$$

- Despeje $\ln A_t$ como residuo y realice el ejercicio de contabilidad para México.
- Grafique el logaritmo del PIB por habitante y los contrafactuales en los que cambia un componente mientras los demás permanecen en el año inicial elegido. Declare ese año.

Para cada tramo, calcule las tasas logarítmicas anuales medias como $g_z=100\Delta\ln z/T$. Construya una tabla desde 1960 hasta 2019 por décadas; el último tramo 2010–2019 tiene nueve años y debe identificarse así.

Distinga la tasa de un factor de su contribución al crecimiento:

$$c_K=\alpha g_k,\qquad c_H=(1-\alpha)g_h,\qquad c_A=g_y-c_K-c_H.$$

Con la tecnología definida en esta identidad, $c_A=(1-\alpha)g_A$, por lo que $g_A=c_A/(1-\alpha)$. Las cuatro columnas principales serán $g_y$, $c_K$, $c_H$ y $c_A$.

- Compare las contribuciones por periodo e interprete sus diferencias.
- El ejercicio es por habitante y utiliza una función simplificada. El residuo absorbe factores omitidos, incluido el cociente empleo/población; no se identifica automáticamente con una medida pura de tecnología ni con la PTF publicada por PWT.

## 1.2. Perspectiva de México.

Lean los siguientes artículos de [Noah Smith](https://itam.instructure.com/courses/8563/files/1231969?module_item_id=289232) de Bloomberg y de [Beijing Channel](https://beijingchannel.substack.com/p/is-vietnam-india-or-mexico-replacing). Utilice esto para complementar el análisis de Contabilidad de Crecimiento para México. Realice un análisis de máximo una cuartilla sobre la información relevante para el crecimiento de la economía mexicana. Incluyan con base en el análisis sus conclusiones y perspectivas hacia los próximos años.

## 2. Ejercicios del modelo de Solow.

- David Romer. Advanced Macroeconomics. Capítulo 1. Problemas: 1.3, 1.4, 1.6, 1.9.

- Charles Jones. Introduction to Economic Growth. Capítulo 2. Problemas: 3, 5.

## Edición para consulta

Esta copia incorpora ajustes de metadatos o de notación descritos en la [nota de edición](../EDICION_ENUNCIADOS.md).
