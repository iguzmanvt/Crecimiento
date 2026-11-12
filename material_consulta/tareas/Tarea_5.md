# Tarea 5. Gasto público, tasas de interés y modelo de Lucas

Enunciado histórico del archivo del curso localizado en la carpeta Primavera 2023. Esta edición se ofrece para consulta y no fija una fecha de entrega vigente.

[Banco de tareas](index.html) · [Consulta por tema](../index.html)

## Convenciones de esta edición

- En la parte Ramsey, $k,c$ se miden por unidad de trabajo efectivo; $g_A$ es el crecimiento de la tecnología y $n$ el crecimiento poblacional.
- En la restricción escrita, $\gamma$ es un flujo de gasto por unidad de trabajo efectivo. La cota 0--1 es una normalización del ejercicio, no una participación del PIB.
- Use $\theta>0,\ \theta\neq1$; el caso logarítmico se obtiene con $u(c)=\ln c$. Para la BGP de Ramsey con utilidad agregada finita, suponga además $\rho-n-(1-\theta)g_A>0$.

####

1.  Guerras, crecimiento y tasas de interés - 15 puntos

Lean ["Government Spending, Interest Rates, Prices, and Budget Deficits in the United Kingdom" (Barro, 1987)](https://itam.instructure.com/courses/4305/files/511325?module_item_id=113020) disponible en Canvas.

- Expliquen la dinámica entre el gasto gubernamental y las tasas de interés real. ¿Cuáles son las diferencias entre el gasto temporal y el permanente? ¿Cómo afecta el gasto militar en tiempo de guerra a las tasas de corto y de largo plazo? ¿Por qué? En este contexto, detallen la información de la Tabla 1 y la Figura 4 en función de los objetivos del paper.

- Con base en lo anterior, explique cómo Barro prueba que las tasas de interés son más altas durante los períodos de gasto gubernamental termporalmente alto. ¿Qué pasa cuando se excluye a la I Guerra Mundial del análisis?

- ¿Cuáles son las conclusiones más relevantes? ¿Qué deja Barro como preguntas abiertas?

Podemos modelar el análisis de Barro con el Modelo de Ramsey.

- Consideren un modelo de Ramsey para una economía con un gasto militar elevado, temporal y no previsto en épocas de guerra. Supongan que el presupuesto del gobierno siempre está equilibrado y que el desarrollo del modelo implica las siguientes ecuaciones diferenciales:

**$\dot k_t=f(k_t)-c_t-\gamma-(\delta+g_A+n)k_t$**

**$\dot c_t=\frac{1}{\theta}[(f^\prime (k_t)-\delta) -\rho-\theta g_A]c_t$**

Con la condición:

**$\displaystyle \lim_{t\to\infty} k_t\exp\left\{-\int_0^t\left[f^\prime(k_s)-\delta-g_A-n\right]\,ds\right\}=0$**

Todos los parámetros son positivos y se asume que **$\rho>n$**.

El gobierno controla **$\gamma$** la cual está entre 0 y 1.

- Interpreten brevemente las tres primeras ecuaciones, incluidos los parámetros.

- Grafiquen un diagrama de fases e ilustre el camino que sigue la economía cuando el gasto gubernamental aumenta de forma temporal, como lo ilustra Barro en el paper.

- Grafique la evolución del consumo y el capital en el periodo considerado. ¿Cómo se comportan las tasas de interés? ¿Coincide este análisis con lo establecido en el paper de Barro?

####

2.  Desarrollo del problema representativo del modelo de Lucas

El modelo de Lucas busca explicar la generación de rendimientos constantes a escala en el capital humano. Como hemos visto en el curso, si esto es cierto significa que la acumulación de conocimiento como factor de producción garantiza una tasa de crecimiento económico positiva al largo plazo.

Para enfocarnos en el análisis económico en la clase, les pongo en la tarea parte del desarrollo algebráico del modelo que no está muy complicado pero toma mucho tiempo.

En en modelo de Lucas, el agente representativo tiene una función de utilidad con horizonte infinito en la que descuenta su consumo en periodos futuros, además de tomar en cuenta el crecimiento poblacional, de la siguiente forma:

$U=\int_0^\infty u(c_t) e^{-(\rho-g_L)t}dt$

con la utilidad del consumo definida como una CES de a siguiente forma\_

$u(c_t)=\frac{c_t^{1-\theta}}{1-\theta}$

Lucas pone sus restricciones presupuestales de tal forma que el capital físico y humano tengan un nivel de complementariedad, en vez de ser totalmente sustitutos como lo veremos en el modelo de Mankiw, Romer y Weil. Para ello, Lucas define a 2 sectores relevantes en el modelo:

- Un sector dedicado a la producción de bienes y servicios con rendimientos decrecientes a escala. La restricción presupuestal de este sector esta definida como:

$\dot k_t=Ak_{t}^\alpha (u_th_{t})^{1-\alpha}-c_t-(\delta+g_L)k_t$

- Un sector dedicado a la acumulación de conocimiento, con rendimientos constantes a escala, cuya restricción está dada por:

$\dot h_t=B(1-u_t)h_t-(\delta+g_L)h_t$

En donde las variables son las usuales utilizadas en elc urso, además de $B$ que es la productividad del sector de creación de conocimiento y $u_t$ que es la fracción del trabajo destinada a producir bienes y servicios; la fracción $1-u_t$ se dedica a formar capital humano.

En estas dos restricciones, las variables de control (que se pueden determinar en todo momento) son $c_t$ y $u_t$, mientras que las variables de estado (determinadas desde un inicio) son $k_t$ y $h_t$ con $\upsilon_t$ como la variable de coestado de valor presente asociada a la primera restricción, y $\lambda_t$ como el de la segunda restricción

- Plantee el Hamiltoniano de valor presente. Suponga una solución interior, con $c_t>0$ y $0<u_t<1$, y defina $r_t=\partial F/\partial k_t$ como el producto marginal bruto del capital, donde $F=A k_t^\alpha(u_t h_t)^{1-\alpha}$.

- Obtenga las condiciones de primer orden de $c_t$, $u_t$, $k_t$ y $h_t$

- Utilizando la CPO de $c_t$, siguiendo la Regla de Keynes Ramsey obtenga la siguiente ecuación:

$\frac{\dot c_t}{c_t}=\frac{1}{\theta}(-\frac{\dot \upsilon_t}{\upsilon_t}-(\rho - g_L))$

- Utilizando la ecuación anterior y la CPO de $k_t$, obtenga la ecuación de Euler:

$\frac{\dot c_t}{c_t}=\frac{1}{\theta}({r_t}-\delta - \rho)$

- Finalmente, utilizando las CPO de $u_t$ y $h_t$, obtenga la siguiente ecuación:

$- \frac{\dot \lambda_t}{\lambda_t}=B-(g_L +\delta)$

Esta demostraciones harán menos pesada la explicación del modelo de Lucas en la clase.

## Edición para consulta

Se corrigieron errores de transcripción y notación para que las ecuaciones coincidan con el modelo escrito. [Detalle de los ajustes](../EDICION_ENUNCIADOS.html).
