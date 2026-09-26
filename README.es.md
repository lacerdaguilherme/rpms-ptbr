# RPMS-PT/BR: datos y análisis de concordancia

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22730156.svg)](https://doi.org/10.5281/zenodo.22730156)
<!-- El badge queda roto hasta el primer release en Zenodo. Cambiar el DOI arriba cuando exista. -->

[🇧🇷 Português](README.md) · [🇺🇸 English](README.en.md) · 🇪🇸 Español (este archivo)

Material de reproducción de los análisis estadísticos del estudio de
adaptación transcultural de la *Refugee Post-Migration Stress Scale*
(RPMS) al portugués brasileño.

Autor de los análisis y de los scripts: **Guilherme Lacerda de Avila**

Este repositorio existe para que cualquier persona pueda partir de los
datos brutos y llegar, por sí misma, exactamente a los mismos
coeficientes reportados en el artículo y en el póster. No hace falta
confiar en nuestra palabra: los datos están aquí, los scripts están
aquí, y ejecutarlos toma menos de un minuto.

## Resultado que deberías obtener

| Panel | Ítems | Evaluadores | AC1 de Gwet | S-CVI/Ave | S-CVI/UA |
|---|---|---|---|---|---|
| Jueces expertos | 21 | 4 | 0,895 | 0,952 | 0,810 |
| Población objetivo | 21 | 4 | 0,976 | 0,988 | 0,952 |

Coeficientes calculados como verificación de robustez, que no van en el
cuerpo del artículo por los motivos explicados más adelante:

| Panel | Kappa de Fleiss | Alfa de Krippendorff |
|---|---|---|
| Jueces expertos | −0,050 | −0,046 |
| Población objetivo | −0,012 | −0,008 |

Si al ejecutar obtienes otro resultado, es un bug: por favor abre un
issue.

## Cómo ejecutar

Requiere [uv](https://docs.astral.sh/uv/) y Python 3.11 o superior. `uv`
resuelve las dependencias solo en la primera ejecución; no hace falta
crear un entorno virtual ni instalar nada manualmente.

```bash
git clone https://github.com/lacerdaguilherme/rpms-ptbr.git
cd rpms-ptbr

# coeficiente principal, el que va en el artículo
uv run estatistica/ac1_epmr.py
uv run estatistica/ac1_rpms.py

# validez de contenido (CVI) junto al AC1
uv run estatistica/cvi_ac1_epmr.py
uv run estatistica/cvi_ac1_rpms.py

# verificaciones de robustez
uv run estatistica/fleiss_kappa_epmr.py
uv run estatistica/fleiss_kappa_rpms.py
uv run estatistica/krippendorff_alpha_epmr.py
uv run estatistica/krippendorff_alpha_rpms.py

# texto y tablas de la sección de Resultados, con los números de arriba
uv run estatistica/gerar_texto_resultados.py

# verificación independiente de la concordancia de traducción/retrotraducción
# (no necesita las planillas privadas, solo el CSV público en dados/)
uv run estatistica/verificar_concordancia_traducao.py
uv run estatistica/verificar_concordancia_retrotraducao.py
```

Cada script imprime el resultado en la terminal y guarda tres archivos en
`estatistica/resultados/`, con la misma marca de fecha y hora: un `.txt`
con el informe completo, un `.png` con la tabla-resumen lista para el
artículo, y un `.html` con la misma tabla como página web.

Para ejecutar contra otro archivo de datos, pasa la ruta como argumento:

```bash
uv run estatistica/ac1_epmr.py ruta/a/otros_datos.csv
```

## Los datos

```
dados/
├── avaliacao_epmr.csv                          panel de jueces expertos
├── avaliacao_rpms.csv                           panel de población objetivo
├── concordancia_traducao_por_item.csv           % de concordancia entre traducciones, por ítem
└── concordancia_retrotraducao_por_item.csv      % de concordancia en la retrotraducción, por ítem
```

Una fila por respuesta, 84 filas por archivo (21 ítems × 4 jueces):

| Columna | Contenido |
|---|---|
| `item` | número del ítem en la escala, de 1 a 21 |
| `juiz` | identificador secuencial del evaluador, de 1 a 4 |
| `resposta` | `Sim` o `Não` (Sí/No), tal como se marcó en la columna binaria de la planilla |
| `tem_ressalva` | `1` si el evaluador escribió algo en el campo de justificación |
| `ressalva` | el texto que escribió, cuando escribió algo |

El diccionario de datos completo, con el enunciado de cada ítem y lo que
exactamente se les preguntó a los jueces, está en
[`estatistica/CODEBOOK.md`](estatistica/CODEBOOK.md).

### Qué no está publicado, y por qué

Las planillas de Excel originales **no** están en este repositorio. El
nombre de cada hoja contiene el nombre real del evaluador, y desde la
fila 28 hay nombre completo, edad y país de origen. En el panel de
población objetivo los evaluadores son personas refugiadas, lo que hace
ese dato especialmente sensible. Los CSV publicados tienen toda la
información necesaria para reproducir los cálculos y ninguna que
identifique quién respondió.

El script `estatistica/exportar_dados_brutos.py` documenta exactamente
cómo se extrajeron los CSV a partir de las planillas. Solo funciona para
quien tiene los archivos originales, es decir, el equipo de
investigación. Está aquí para que el procedimiento de anonimización sea
auditable, no para que lo ejecute quien clona el repositorio.

## Cómo se codificaron las respuestas

Este es el punto metodológico que más importa para quien vaya a
reanalizar los datos, y está abierto a inspección.

Junto a la respuesta binaria, la planilla tiene un campo libre donde el
evaluador podía escribir. En nueve casos del panel de expertos y uno del
panel de población objetivo, alguien escribió algo ahí. Esas anotaciones
no son todas de la misma naturaleza:

- **Sugerencia de mejora de un ítem que el evaluador aprobó.** Del tipo
  "tal vez cambiar 'estatus social' por 'condiciones sociales'" u
  "Obs.: mencionar el acento". El evaluador no objeta el ítem, propone
  mejorarlo. Cuentan como concordancia, porque eso fue lo que respondió.
- **Objeción que señala una falla en el ítem tal como está redactado.**
  Ocurre una única vez en todo el estudio, en el ítem 6 del panel de
  población objetivo, donde la evaluadora registró que la palabra
  "deslocamento" ("desplazamiento/traslado") no es comprendida por la
  mayoría de los extranjeros. Cuenta como discordancia, porque el ítem
  no cumplió su función con esa respondiente.

Esta decisión está declarada explícitamente al inicio de cada script, en
la constante `ITENS_COM_RESSALVA_RECLASSIFICADA`, y no escondida en la
lógica:

```python
# en los scripts del panel de expertos
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset()

# en los scripts del panel de población objetivo
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset({6})
```

**Puedes probar el efecto de esta decisión.** Como los CSV publican la
columna `tem_ressalva`, basta con cambiar la constante y ejecutar de
nuevo:

| Configuración | Expertos | Población objetivo |
|---|---|---|
| `frozenset()` | AC1 = 0,895 | AC1 indefinido (unanimidad: Pa = 1, Pe = 0) |
| `frozenset({6})` | AC1 = 0,895 | AC1 = 0,976 |
| toda objeción reclasificada | AC1 = 0,735 | AC1 = 0,976 |

La tercera fila es relevante históricamente: fue la regla vigente entre
el 21/08 y el 11/09/2026, generalizada por error a cualquier campo
completado. La auditoría que corrigió esto está documentada en
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), sección 16.

## Por qué AC1 de Gwet, y no Kappa de Fleiss

El Kappa de Fleiss y el Alfa de Krippendorff dan valores **negativos**
en los dos paneles, a pesar de que la concordancia bruta es alta: en el
panel de población objetivo, solo 1 de las 84 respuestas divergió de las
demás.

Esto no es un error de cálculo ni discordancia real entre los jueces. Es
la **paradoja del kappa** (Feinstein & Cicchetti, 1990): las fórmulas
que corrigen la concordancia por la varianza de las categorías
marginales se vuelven inestables cuando la prevalencia de las
respuestas está muy desbalanceada, que es exactamente el caso de una
evaluación de validez de contenido, en la que la mayoría de los ítems
son aprobados.

El AC1 de Gwet (2008) fue construido para no tener ese comportamiento.
Los dos coeficientes inestables se siguen calculando y publicando aquí a
propósito: son la evidencia de que la elección del AC1 no fue
conveniencia, sino consecuencia de la estructura de los datos. Dos
fórmulas matemáticamente distintas que convergen en el mismo valor
negativo muestran que el problema está en la familia de estadísticos, no
en uno de ellos.

La explicación completa, con las matemáticas, está en
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), secciones 9 y
11.

## Organización del repositorio

```
dados/
├── avaliacao_epmr.csv                          datos brutos, panel de expertos
├── avaliacao_rpms.csv                           datos brutos, panel de población objetivo
├── concordancia_traducao_por_item.csv           % de concordancia entre traducciones, por ítem (sin texto)
└── concordancia_retrotraducao_por_item.csv      % de concordancia en la retrotraducción, por ítem (sin texto)

estatistica/
├── ac1_epmr.py                            AC1 de Gwet aislado (va en el artículo)
├── ac1_rpms.py
├── cvi_ac1_epmr.py                        CVI y AC1 lado a lado
├── cvi_ac1_rpms.py
├── fleiss_kappa_epmr.py                   verificación de robustez
├── fleiss_kappa_rpms.py
├── krippendorff_alpha_epmr.py             verificación de robustez
├── krippendorff_alpha_rpms.py
├── concordancia_traducao.py               % de concordancia entre traducciones (necesita la planilla privada)
├── concordancia_retrotraducao.py          % de concordancia en la retrotraducción (necesita la planilla privada)
├── verificar_concordancia_traducao.py     reproduce el % de arriba solo con el CSV público
├── verificar_concordancia_retrotraducao.py  reproduce el % de arriba solo con el CSV público
├── exportar_dados_brutos.py               genera los CSV a partir de las planillas
├── gerar_texto_resultados.py               arma el texto de la sección de Resultados
├── CODEBOOK.md                             diccionario de datos
├── EXPLICACAO.md                           explicación línea por línea de cada script
├── RESULTADOS_PARA_ARTIGO.md               texto, tablas y referencias
└── resultados/                             salida de cada ejecución
```

Cada script es independiente y puede leerse de principio a fin sin
consultar los demás. Esto duplica algunas funciones entre archivos, y es
intencional: el objetivo es que alguien sin experiencia en Python pueda
seguir un archivo completo, no que el código sea lo más corto posible.
`EXPLICACAO.md` acompaña esa lectura línea por línea.

### Los dos scripts de concordancia entre traducciones

`concordancia_traducao.py` y `concordancia_retrotraducao.py` calculan el
porcentaje de concordancia entre las versiones traducidas del
instrumento. Leen planillas con el texto completo de la escala en las
tres versiones, que **no están publicadas aquí**: la RPMS es un
instrumento de Malm et al. (2020), y redistribuir el texto íntegro
depende de una autorización que todavía no ha sido formalizada. Los
scripts permanecen en el repositorio para documentar el método; para
ejecutarlos hace falta tener las planillas.

Lo que **sí** está publicado es el resultado numérico de la comparación,
ítem por ítem (`dados/concordancia_traducao_por_item.csv`,
`dados/concordancia_retrotraducao_por_item.csv`): etiqueta del ítem,
idéntico/diferente y % de similitud — sin ninguna columna de texto. Un
porcentaje de similitud calculado a partir del texto es un dato derivado
nuestro, no el texto en sí, así que publicarlo no redistribuye el
instrumento de Malm et al. Los scripts
`verificar_concordancia_traducao.py` y
`verificar_concordancia_retrotraducao.py` leen solo esos CSV y
reproducen los porcentajes reportados en el artículo (46,4% y 6,7%) sin
depender de las planillas privadas — es el camino pensado para quien
quiera auditar esos dos números sin necesitar acceso al instrumento
original.

## Dependencias

Declaradas en `pyproject.toml` y resueltas automáticamente por `uv`:

| Biblioteca | Para qué |
|---|---|
| `statsmodels` | cálculo del Kappa de Fleiss |
| `openpyxl` | lectura de las planillas de Excel originales |
| `matplotlib` | generación de las tablas-resumen en PNG |
| `pandas` | manipulación tabular auxiliar |

El AC1 de Gwet, el CVI y el Alfa de Krippendorff están implementados
directamente en los scripts, a partir de las fórmulas publicadas, y no
dependen de bibliotecas de terceros. `EXPLICACAO.md` muestra cada paso
del cálculo.

## Referencias

Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low
kappa: I. The problems of two paradoxes. *Journal of Clinical
Epidemiology, 43*(6), 543–549.

Fleiss, J. L. (1971). Measuring nominal scale agreement among many
raters. *Psychological Bulletin, 76*(5), 378–382.

Gwet, K. L. (2008). Computing inter-rater reliability and its variance in
the presence of high agreement. *British Journal of Mathematical and
Statistical Psychology, 61*(1), 29–48.

Krippendorff, K. (2019). *Content analysis: An introduction to its
methodology* (4th ed.). Sage.

Landis, J. R., & Koch, G. G. (1977). The measurement of observer
agreement for categorical data. *Biometrics, 33*(1), 159–174.

Lynn, M. R. (1986). Determination and quantification of content validity.
*Nursing Research, 35*(6), 382–385.

Malm, A., Tinghög, P., Narusyte, J., & Saboonchi, F. (2020). The refugee
post-migration stress scale (RPMS): Development and validation among
refugees from Syria recently resettled in Sweden. *Conflict and Health,
14*, Article 2.

Polit, D. F., Beck, C. T., & Owen, S. V. (2007). Is the CVI an acceptable
indicator of content validity? Appraisal and recommendations. *Research
in Nursing & Health, 30*(4), 459–467.

## Estado y licencia

Proyecto de Iniciación Científica en curso. Los coeficientes aquí son
los reportados en el artículo en preparación y en el póster presentado;
las etapas psicométricas del instrumento (consistencia interna,
estructura factorial) todavía no se han realizado.

Licencia de uso de los datos todavía no definida formalmente. Para
reutilizar los datos en otra investigación, contáctanos antes.

## Cómo citar

Este repositorio es citable vía CITATION.cff (el propio GitHub muestra
el botón "Cite this repository" en la página del repo) y vía el DOI
permanente emitido por Zenodo — ver el badge al inicio de este archivo.

**APA 7ª edición:**

> Avila, G. L. de. (2026). *rpms-ptbr: Dados e rotinas de análise de
> concordância da adaptação transcultural da RPMS para o português
> brasileiro* (Version 1.0.0) [Computer software]. Zenodo.
> https://doi.org/10.5281/zenodo.22730156

**ABNT (NBR 6023):**

> ÁVILA, Guilherme Lacerda de. **rpms-ptbr**: dados e rotinas de análise
> de concordância da adaptação transcultural da RPMS para o português
> brasileiro. Versão 1.0.0. [*S. l.*]: Zenodo, 2026. Disponível em:
> https://doi.org/10.5281/zenodo.22730156. Acesso em: [fecha de acceso].

ORCID del autor: [0009-0006-3063-4030](https://orcid.org/0009-0006-3063-4030).
