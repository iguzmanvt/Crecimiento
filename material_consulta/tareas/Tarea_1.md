# Tarea 1. Medición, PWT, convergencia y series de tiempo

Enunciado histórico del archivo del curso localizado en la carpeta Primavera 2023. Esta edición se ofrece para consulta y no fija una fecha de entrega vigente.

[Banco de tareas](README.md) · [Consulta por tema](../README.md).

1: Para las Tareas y Exámenes vamos a utilizar la información de las Penn World Tables (PWT) para hacer diversos análisis de crecimiento. Las PWT son un conjunto de datos de cuentas nacionales desarrollados y actualizados por académicos de la Universidad de California y el Growth Development Center de la Universidad de Groningen para medir el PIB real en diferentes países y a lo largo del tiempo. Estas tablas proporcionan variables de cuentas nacionales de ingresos convertidas a precios internacionales para permitir comparaciones válidas de ingresos entre países al homogeneizar las cuentas nacionales a un numerario común.

Para introducirla, lean [Capital,	labor and	TFP	in	PWT8.0](https://www.rug.nl/ggdc/docs/capital_labor_and_tfp_in_pwt80.pdf) (Inklaar y Timmer, 2013). El paper proporciona un análisis de los niveles relativos de ingresos, producción, insumos y productividad a nivel mundial, utilizando la base de las PWT. Este se enfoca en la productividad total de los factores (TFP) y en la relación entre TFP, capital, así como la mano de obra, y describe las fuentes, métodos y resultados de los datos de TFP en PWT y cómo los economistas pueden usar el TFP para medir el crecimiento económico y la eficiencia de los insumos de capital y mano de obra.

Con base en la lectura respondan a las siguientes preguntas:

- ¿Cómo construyen los indicadores de paridad de poder de compra (PPP)?

- ¿Cómo miden los niveles de acervo de capital por país? ¿Qué diferencias existen en la metodología de medición del acervo de capital con otras metodologías tradicionales, o estándares? ¿Cómo abordan el problema de medir la depreciación? ¿Por qué estiman un acervo de capital mayor en economías en desarrollo que lo propuesto por la literatura tradicional?

- ¿Cómo miden la participación del trabajo en el PIB por país? ¿Por qué es relevante ara el análisis? ¿Cómo difiere el indicador entre los países considerandos? ¿Cuál ha sido la evolución reciente del indicador y cuál que impacto ha generado?

- ¿Cómo miden el capital humano? ¿Les parece un indicador construido apropiadamente?

## 2. Convergencia entre los países de la OCDE


Utilicemos las PWT para replicar la gráfica 25 del paper [The facts of Economic Growth](https://web.stanford.edu/~chadj/facts.pdf) (Jones, 2016) vista en clase.

Para ello descarguen los datos de la Penn World Tables (PWT versión 10.0 - [https://www.rug.nl/ggdc/productivity/pwt/](https://www.rug.nl/ggdc/productivity/pwt/)).

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

Consideren las variables para **los países de la OCDE** el periodo 1950-2019. La lista de países miembros de la OCDE está [disponible en su página de internet](https://www.oecd.org/about/)

Nota: pueden utilizar otra versión pero la notación de las variables va a cambiar, chequen que estén utilizando las correctas.

Para replicar la gráfica de convergencia realicen lo siguiente:

- Utilicen `rgdpe` (PIB real por el lado del gasto a PPA encadenadas, en millones de US$ de 2017) y `pop` (Número de personas en millones) para obtener el logaritmo del PIB per cápita de los países mencionados.

- Utilicen 1960 como el año inicial y obtenga el logaritmo del PIB per cápita de cada país en este año.

- Obtengan el crecimiento anual para cada país y utilicelo para obtener el promedio del crecimiento anual por país.

- Utilicen esta información para hacer la gráfica de convergencia de los países de la OCDE.

## 3. Suavización de series de tiempo y cambios absolutos

Utilice la serie de PIB real per cápita de [FRED](https://fred.stlouisfed.org/series/A939RX0Q048SBEA). Si utiliza la serie trimestral, forme una serie anual mediante el promedio de los cuatro trimestres. Incluya 1949 para calcular el primer cambio de 1950 y presente los resultados de 1950–2021.

Sea $Y_t>0$ el nivel anual del PIB real per cápita. Para trabajar con una medida aditiva y comparable entre ventanas, use el crecimiento logarítmico anual:

$$g_t^{(1)}=100[\ln Y_t-\ln Y_{t-1}].$$

El crecimiento logarítmico anual medio en una ventana de $T$ años se define como:

$$g_t^{(T)}=\frac{100}{T}[\ln Y_t-\ln Y_{t-T}].$$

- Grafique el crecimiento anual y el crecimiento anual medio a diez años. Calcule el crecimiento logarítmico anual medio de cada década, de 1950–1960 a 2010–2020, y represéntelo.
- Interprete la trayectoria, identifique posibles cambios de tendencia y discuta hipótesis que podrían explicar la desaceleración observada. Distinga la descripción de la serie de una explicación causal.

Para analizar variaciones absolutas, defina $D_t=Y_t-Y_{t-1}$ y construya el índice:

$$I_t=\frac{Y_t-Y_{t-1}}{Y_{2000}-Y_{1999}},$$

siempre que el denominador sea distinto de cero. Así $I_{2000}=1$. El índice compara cada aumento absoluto con el aumento absoluto de 2000. Dividir los niveles por $Y_{2000}$ no produce esa misma comparación.

- Grafique $I_t$ para 1950–2021 y contraste sus conclusiones con las de las tasas de crecimiento.
- Como ejemplo de interpretación, un valor de 0.75 indicaría un cambio absoluto equivalente a tres cuartas partes del cambio de 2000; no se atribuye ese valor a un año concreto sin calcularlo.

Si elige la tasa anual compuesta, use $100[(Y_t/Y_{t-T})^{1/T}-1]$ e identifíquela como tal. Esta medida no es exactamente igual al crecimiento logarítmico anual medio.

## Edición para consulta

Esta copia incorpora ajustes de metadatos o de notación descritos en la [nota de edición](../EDICION_ENUNCIADOS.md).
