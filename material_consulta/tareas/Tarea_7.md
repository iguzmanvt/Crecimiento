# Tarea 7. Propiedad intelectual y retornos sociales a la innovación

Enunciado histórico del archivo del curso localizado en la carpeta Primavera 2023. Esta edición se ofrece para consulta y no fija una fecha de entrega vigente.

[Banco de tareas](index.html) · [Consulta por tema](../index.html)

Para el apartado de retornos sociales, suponga $y>0,\ s>0,\ 0<g<r$. De esta forma, $q=(1+g)/(1+r)$ satisface $0<q<1$ y las series de valor presente convergen.

####

1.  Lean el artículo [It's Got a Great Beat, and You Can File a Lawsuit to It](https://www.nytimes.com/2020/01/06/arts/music/pop-music-songs-lawsuits.html?action=click&module=Editors%20Picks&pgtype=Homepage) (The Ney York Times, 2020) también disponible [aquí](https://itam.instructure.com/courses/5587/files/771997?module_item_id=170145) o [aquí](https://itam.instructure.com/courses/6202/files/783255?module_item_id=175409):

El artículo de The New York Times reporta el aumento reciente de las demandas millonarias por aplicación de derechos de autor en la indusria de la música, las cuales una buena parte están basadas en pruebas endebles de robo de música. Según el artículo, estas han aumentado tras el pago de 5.3 millones de dólares por parte de Robin Thicke, Pharrell Williams y T.I. al patrimonio de Marvin Gaye porque su canción [Blurred Lines](https://www.youtube.com/watch?v=yyDUC1LUXSU) infringe los derechos de autor de la canción [Got To Give lt Up](https://www.youtube.com/watch?v=Ayyy-03ITDg) .

El argumento económico de esto es que no hay incentivos suficientes para que los artistas compongan canciones porque estas se pueden copiar a un precio mínimo, por lo que es necesario otorgar a un creador los derechos de propiedad sobre su creación hace que sea rentable el componer.

- Utilicen el artículo para abordar en una cuartilla la necesidad de la exclusividad en la industria de la música para incentivar la creatividad, la necesidad de la propiedad intelectual para garantizar esta exclusividad y las trabas que esta puede poner al desarrollo creativo en esta industria.

####

2.  Lean [A calculation of the social returns to innovation](https://www.nber.org/system/files/working_papers/w27863/w27863.pdf) (Jones, Summers, 2020):

En su último paper, Jones y Summers intentan calcular el rendimiento social de la innovación y desarrolo (I&D) en Estados Unidos. El paper ha llamado la atención porque el argumento es tan directo (a la *r\>g* de Piketty) que [podría haberse desarrollado en cualquier momento en las décadas pasadas](https://marginalrevolution.com/marginalrevolution/2020/09/a-calculation-of-the-social-returns-to-innovation.html). Lo que hacen es replantear la pregunta, *¿cuánto valor crea un dólar adicional de gasto en I&D en un año?* (lo cuál es muy dificil de contestar) de forma inversa: *¿cuanto crecimiento tenemos si dejamos de invertir en I&D durante un año?*.

Derivemos los resultados claves del modelo. Definamos $y$ como el PIB per cápita en el año actual, $g$ el crecimiento del PIB per cápita cuando invertimos en I&D, $s=\frac{x}{y}$ como el gasto anual sobre el PIB realizado en I&D y $r$ como la tasa de interés.

Lo que hacen Jones y Summers es suponer que la economía deja de hacer I&D durante un año y después contrastan las diferencias con una economía que no deja de hacer investigación en I&D y obtienen el costo de oportunidad en forma de una relación costo-beneficio.

Para ello, primero calculan el valor presente de la economía cuando esta realiza I&D de la siguiente forma:

$V_I=y+y\frac{(1+g)}{(1+r)}+y\frac{(1+g)^2}{(1+r)^2}+y\frac{(1+g)^3}{(1+r)^3}+...$

Podemos separar un $\frac{(1+g)}{(1+r)}$ en esta ecuación para expresarla de la siguiente forma:

$V_I=y+\frac{1+g}{1+r}\left[y+y\frac{1+g}{1+r}+y\frac{(1+g)^2}{(1+r)^2}+\cdots\right]$

Para tener dentro de lo que está en los corchetes a $V_I$. Con esto tenemos la ecuación:

$V_I=y + \frac{(1+g)}{(1+r)}V_I$

- En este caso, primero **demuestren que la forma cerrada de esta ecuación puede expresarse como**:

$V_I=\frac{(1+r)}{(r-g)}y$

Ahora, suponen que la economía deja de hacer I&D en el primer año por lo que la economía no tiene crecimiento en el año posterior, generando la siguiente ecuación de valor presente de la misma:

$V_N=y+y\frac{1}{(1+r)}+y\frac{(1+g)}{(1+r)^2}+y\frac{(1+g)^2}{(1+r)^3}+...$

- Ahora **demuestren que la forma cerrada de esta ecuación puede expresarse como**:

$V_N=y+\frac{1}{(1+r)}V_I$

Por lo que al sustituir $V_I$ tenemos:

$V_N=\frac{(r-g)}{(1+r)}V_I+\frac{1}{(1+r)}V_I$

Calculemos los beneficios de hacer I&D durante un año. Esto lo hacen definiendo a los beneficios como $B=V_I-V_N$

- Sustituyan los resultados y lleguen a que $B=\frac{g}{(1+r)}V_I$

Para calcular los costos, suponemos que estos dependen de la fracción $s$ que gastamos del PIB por lo que en valor presente $V_{CI}=sV_I$.

Por último, necesitamos calcular el costo si dejamos de hacer I&D por un año. En la ecuación de valor presente, el costo del primer año será 0 por el supuesto y en el segundo año no crece la economía, por lo que esta queda:

$V_{CN}=0+sy\frac{1}{(1+r)}+sy\frac{(1+g)}{(1+r)^2}+sy\frac{(1+g)^2}{(1+r)^3}+...$

- **Demuestren que la forma cerrada de esta ecuación puede expresarse como**:

$V_{CN}=\frac{s}{(1+r)}V_I$

Con esto, se puede sacar el costo de hacer un año de I&D como el valor presente del costo de hacer I&D ($V_{CI}$) menos el valor presente del costo de no hacer I&D ($V_{CN}$) como $C=V_{CI}-V_{CN}$

- **Demuestren que los costos pueden expresarse como**:

$C=s\frac{r}{(1+r)}V_I$

Finalmente, teniendo los beneficios y costos de tener 1 año adicional de I&D podemos obtener el costo de oportunidad promedio de innovar un año. **Demuestren que esta se da por la ecuación**:

$\frac{B}{C}=\frac{g}{sr}$

o lo que es lo mismo, como lo expresan los autores en el paper: $\rho=\frac{\frac{g}{r}}{\frac{x}{y}}$

- Interpreten la ecuación y los resultados a los que llegan sobre el costo asociado a detener un año la I&D en Estados Unidos.

- En este contexto, según los autores, ¿qué supuestos son necesarios para el análisis?

- Con base a lo que hemos analizado en el curso, ¿que objeciones tendrían al resultado de Jones y Summers? (incluyendo objeciones a los supuestos, a la relación entre crecimiento e I&D, entre otros).

## Edición para consulta

Se corrigieron errores de transcripción y notación para que las ecuaciones coincidan con el modelo escrito. [Detalle de los ajustes](../EDICION_ENUNCIADOS.html).
