# RPMS-PT/BR: dados e análises de concordância

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22730156.svg)](https://doi.org/10.5281/zenodo.22730156)
<!-- Badge fica quebrado até o primeiro release no Zenodo. Trocar o DOI acima quando existir. -->

Material de reprodução das análises estatísticas do estudo de adaptação
transcultural da *Refugee Post-Migration Stress Scale* (RPMS) para o
português brasileiro.

Autor das análises e dos scripts: **Guilherme Lacerda de Avila**

Este repositório existe para que qualquer pessoa possa partir dos dados
brutos e chegar, sozinha, exatamente aos mesmos coeficientes reportados
no artigo e no pôster. Não é preciso confiar na nossa palavra: os dados
estão aqui, os scripts estão aqui, e rodar leva menos de um minuto.

## Resultado que você deve obter

| Painel | Itens | Avaliadores | AC1 de Gwet | S-CVI/Ave | S-CVI/UA |
|---|---|---|---|---|---|
| Juízes especialistas | 21 | 4 | 0,895 | 0,952 | 0,810 |
| População-alvo | 21 | 4 | 0,976 | 0,988 | 0,952 |

Coeficientes calculados como verificação de robustez, que não vão para o
corpo do artigo pelos motivos explicados adiante:

| Painel | Kappa de Fleiss | Alpha de Krippendorff |
|---|---|---|
| Juízes especialistas | −0,050 | −0,046 |
| População-alvo | −0,012 | −0,008 |

Se você rodar e obter outra coisa, é bug: por favor abra uma issue.

## Como rodar

Requer [uv](https://docs.astral.sh/uv/) e Python 3.11 ou superior. O `uv`
resolve as dependências sozinho na primeira execução, não é preciso criar
ambiente virtual nem instalar nada na mão.

```bash
git clone https://github.com/lacerdaguilherme/rpms-ptbr.git
cd rpms-ptbr

# coeficiente principal, o que vai no artigo
uv run estatistica/ac1_epmr.py
uv run estatistica/ac1_rpms.py

# validade de conteúdo (CVI) junto do AC1
uv run estatistica/cvi_ac1_epmr.py
uv run estatistica/cvi_ac1_rpms.py

# verificações de robustez
uv run estatistica/fleiss_kappa_epmr.py
uv run estatistica/fleiss_kappa_rpms.py
uv run estatistica/krippendorff_alpha_epmr.py
uv run estatistica/krippendorff_alpha_rpms.py

# texto e tabelas da seção de Resultados, preenchidos com os números acima
uv run estatistica/gerar_texto_resultados.py
```

Cada script imprime o resultado no terminal e salva três arquivos em
`estatistica/resultados/`, com o mesmo carimbo de data e hora: um `.txt`
com o relatório completo, um `.png` com a tabela-resumo pronta para o
artigo e um `.html` com a mesma tabela em página web.

Para rodar contra outro arquivo de dados, passe o caminho como argumento:

```bash
uv run estatistica/ac1_epmr.py caminho/para/outros_dados.csv
```

## Os dados

```
dados/
├── avaliacao_epmr.csv    painel de juízes especialistas
└── avaliacao_rpms.csv    painel da população-alvo
```

Uma linha por resposta, 84 linhas por arquivo (21 itens × 4 juízes):

| Coluna | Conteúdo |
|---|---|
| `item` | número do item na escala, de 1 a 21 |
| `juiz` | identificador sequencial do avaliador, de 1 a 4 |
| `resposta` | `Sim` ou `Não`, exatamente como marcado na coluna binária da planilha |
| `tem_ressalva` | `1` se o avaliador escreveu algo no campo de justificativa |
| `ressalva` | o texto que ele escreveu, quando escreveu |

O dicionário de dados completo, com o enunciado de cada item e o que
exatamente foi perguntado aos juízes, está em
[`estatistica/CODEBOOK.md`](estatistica/CODEBOOK.md).

### O que não está publicado, e por quê

As planilhas Excel originais **não** estão neste repositório. O nome de
cada aba contém o nome real do avaliador, e a partir da linha 28 há nome
completo, idade e país de origem. No painel da população-alvo os
avaliadores são pessoas refugiadas, o que torna esse dado especialmente
sensível. Os CSVs publicados têm toda a informação necessária para
reproduzir os cálculos e nenhuma que identifique quem respondeu.

O script `estatistica/exportar_dados_brutos.py` documenta exatamente como
os CSVs foram extraídos das planilhas. Ele só roda para quem tem os
arquivos originais, ou seja, a equipe de pesquisa. Está aqui para que o
procedimento de anonimização seja auditável, não para ser executado por
quem clonou.

## Como as respostas foram codificadas

Este é o ponto metodológico que mais importa para quem for reanalisar os
dados, e ele está aberto à inspeção.

A planilha tem, ao lado da resposta binária, um campo livre onde o
avaliador podia escrever. Em nove casos no painel de especialistas e um
no painel da população-alvo, alguém escreveu algo ali. Essas anotações
não são todas da mesma natureza:

- **Sugestão de aprimoramento de um item que o avaliador aprovou.** Do
  tipo "talvez trocar 'status social' por 'condições sociais'" ou "Obs:
  falar sobre sotaque". O avaliador não contesta o item, propõe
  melhorá-lo. Contam como concordância, porque foi isso que ele
  respondeu.
- **Ressalva que aponta falha no item como está redigido.** Acontece uma
  única vez em todo o estudo, no item 6 do painel da população-alvo, em
  que a avaliadora registrou que a palavra "deslocamento" não é
  compreendida pela maioria dos estrangeiros. Conta como discordância,
  porque o item não cumpriu sua função com aquela respondente.

Essa decisão está declarada de forma explícita no topo de cada script, na
constante `ITENS_COM_RESSALVA_RECLASSIFICADA`, e não escondida na lógica:

```python
# nos scripts do painel de especialistas
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset()

# nos scripts do painel da população-alvo
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset({6})
```

**Você pode testar o efeito dessa escolha.** Como os CSVs publicam a
coluna `tem_ressalva`, basta alterar a constante e rodar de novo:

| Configuração | Especialistas | População-alvo |
|---|---|---|
| `frozenset()` | AC1 = 0,895 | AC1 indefinido (unanimidade: Pa = 1, Pe = 0) |
| `frozenset({6})` | AC1 = 0,895 | AC1 = 0,976 |
| toda ressalva reclassificada | AC1 = 0,735 | AC1 = 0,976 |

A terceira linha é relevante historicamente: foi a regra que vigorou
entre 21/08 e 11/09/2026, generalizada por engano para qualquer campo
preenchido. A auditoria que corrigiu isso está documentada em
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), seção 16.

## Por que AC1 de Gwet, e não Kappa de Fleiss

O Kappa de Fleiss e o Alpha de Krippendorff dão valores **negativos**
nos dois painéis, apesar de a concordância bruta ser alta: no painel da
população-alvo, apenas 1 das 84 respostas divergiu das demais.

Isso não é erro de cálculo nem discordância real entre os juízes. É o
**paradoxo do kappa** (Feinstein & Cicchetti, 1990): fórmulas que
corrigem a concordância pela variância das categorias marginais ficam
instáveis quando a prevalência das respostas é muito desbalanceada, que
é exatamente o caso de uma avaliação de validade de conteúdo, em que a
maioria dos itens é aprovada.

O AC1 de Gwet (2008) foi construído para não ter esse comportamento. Os
dois coeficientes instáveis continuam sendo calculados e publicados aqui
de propósito: eles são a evidência de que a escolha do AC1 não foi
conveniência, e sim consequência da estrutura dos dados. Duas fórmulas
matematicamente distintas convergindo para o mesmo valor negativo mostram
que o problema está na família de estatísticas, não em uma delas.

A explicação completa, com a matemática, está em
[`estatistica/EXPLICACAO.md`](estatistica/EXPLICACAO.md), seções 9 e 11.

## Organização do repositório

```
dados/
├── avaliacao_epmr.csv               dados brutos, painel de especialistas
└── avaliacao_rpms.csv               dados brutos, painel da população-alvo

estatistica/
├── ac1_epmr.py                      AC1 de Gwet isolado (vai no artigo)
├── ac1_rpms.py
├── cvi_ac1_epmr.py                  CVI e AC1 lado a lado
├── cvi_ac1_rpms.py
├── fleiss_kappa_epmr.py             verificação de robustez
├── fleiss_kappa_rpms.py
├── krippendorff_alpha_epmr.py       verificação de robustez
├── krippendorff_alpha_rpms.py
├── concordancia_traducao.py         % de concordância entre traduções
├── concordancia_retrotraducao.py    % de concordância na retrotradução
├── exportar_dados_brutos.py         gera os CSVs a partir das planilhas
├── gerar_texto_resultados.py        monta o texto da seção de Resultados
├── CODEBOOK.md                      dicionário de dados
├── EXPLICACAO.md                    explicação linha a linha de cada script
├── RESULTADOS_PARA_ARTIGO.md        texto, tabelas e referências
└── resultados/                      saída das execuções
```

Cada script é independente e pode ser lido do começo ao fim sem consultar
os outros. Isso duplica algumas funções entre arquivos, e é intencional:
o objetivo é que alguém sem familiaridade com Python consiga acompanhar
um arquivo inteiro, não que o código seja o mais curto possível. O
`EXPLICACAO.md` acompanha essa leitura linha por linha.

### Os dois scripts de concordância entre traduções

`concordancia_traducao.py` e `concordancia_retrotraducao.py` calculam a
porcentagem de concordância entre as versões traduzidas do instrumento.
Eles leem planilhas com o texto completo da escala nas três versões, que
**não estão publicadas aqui**: a RPMS é instrumento de Malm et al.
(2020), e a redistribuição do texto integral depende de autorização que
ainda não foi formalizada. Os scripts ficam no repositório para
documentar o método; para executá-los é preciso ter as planilhas.

## Dependências

Declaradas em `pyproject.toml` e resolvidas automaticamente pelo `uv`:

| Biblioteca | Para quê |
|---|---|
| `statsmodels` | cálculo do Kappa de Fleiss |
| `openpyxl` | leitura das planilhas Excel originais |
| `matplotlib` | geração das tabelas-resumo em PNG |
| `pandas` | manipulação tabular auxiliar |

O AC1 de Gwet, o CVI e o Alpha de Krippendorff são implementados
diretamente nos scripts, a partir das fórmulas publicadas, e não dependem
de biblioteca de terceiros. O `EXPLICACAO.md` mostra cada passo da conta.

## Referências

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

## Status e licença

Estudo de Iniciação Científica em andamento. Os coeficientes aqui são os
reportados no artigo em preparação e no pôster apresentado; as etapas
psicométricas do instrumento (consistência interna, estrutura fatorial)
ainda não foram realizadas.

Licença de uso dos dados ainda não definida formalmente. Para reutilizar
os dados em outra pesquisa, entre em contato antes.

## Como citar

Este repositório é citável via CITATION.cff (o próprio GitHub mostra o
botão "Cite this repository" na página do repo) e, depois do primeiro
release, via DOI permanente emitido pelo Zenodo — ver o badge no topo
deste arquivo assim que existir.

> Avila, G. L. de. (2026). *rpms-ptbr: Dados e rotinas de análise de
> concordância da adaptação transcultural da RPMS para o português
> brasileiro* [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22730156

ORCID do autor: [0009-0006-3063-4030](https://orcid.org/0009-0006-3063-4030).
