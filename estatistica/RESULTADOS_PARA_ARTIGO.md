# Resultados de Confiabilidade entre Juízes, pronto pra colar no artigo

> **DECISÃO CONFIRMADA PELA ORIENTADORA (18/08/2026, refinada em
> 21/08/2026):** o coeficiente reportado no corpo do artigo pros
> **juízes** é o **AC1 de Gwet** (seção 1, isolado; seção 2 traz o AC1
> junto do CVI, como detalhamento). Kappa de Fleiss (seção 3) e Alpha de
> Krippendorff (seção 4) **saem do corpo principal do artigo** - ficam só
> como documentação técnica do processo de decisão metodológica (explicam
> por que o AC1 foi escolhido em vez do Kappa, via o paradoxo do kappa).
>
> **Regra de interpretação revisada (11/09/2026, após auditoria célula a
> célula):** discordância é o "Não" marcado na coluna binária (coluna C).
> Uma ressalva escrita na justificativa (coluna D) só é reclassificada
> como discordância quando aponta **falha do item como redigido**, não
> quando propõe aprimoramento de um item já julgado coerente. No estudo
> inteiro há **um único** caso reclassificado: o item 6 do RPMS, cuja
> ressalva diz que "deslocamento" não é entendível pela população-alvo.
>
> A versão anterior destes scripts (21/08 a 11/09/2026) reclassificava
> qualquer célula preenchida na coluna D, o que atingia também as cinco
> sugestões de aprimoramento do painel especialista (itens 4, 5, 8, 10 e
> 17) e derrubava o AC1 do EPMR de 0,895 para 0,735, divergindo do número
> apresentado no pôster. Os oito scripts foram corrigidos e **todos os
> números deste documento já refletem a regra revisada**. Ver
> `EXPLICACAO.md`, seção 16, para a auditoria completa. Pra
> tradução/retrotradução, a orientadora pediu porcentagem simples de
> concordância entre as versões traduzidas - **implementado em
> 18/08/2026**, ver seção 6 (não afetado por esta regra, que só vale pra
> avaliação de itens Sim/Não).

Este arquivo reúne tudo pra seção de Resultados/Métodos do artigo: texto
redigido, tabelas em Markdown e em LaTeX, e referências em texto, pros
quatro coeficientes de confiabilidade **calculados** neste estudo (mesmo
os que não vão pro corpo do artigo continuam documentados aqui, porque
justificam a escolha do AC1):

1. **AC1 de Gwet (isolado)**, seção 1 · **★ reportado no artigo**
2. **CVI (Content Validity Index) e AC1 de Gwet**, seção 2 · detalhamento complementar ao AC1
3. **Kappa de Fleiss**, seção 3 · *documentação técnica, não reportado no artigo*
4. **Alpha de Krippendorff**, seção 4 · *documentação técnica, não reportado no artigo*

As imagens já formatadas das tabelas estão em `estatistica/`, uma por
método (pode arrastar direto pro Word):

- `figura_tabela_ac1.png`. Tabela 1 (AC1 de Gwet, isolado)
- `figura_tabela_cvi_ac1.png`. Tabela 2 (CVI e AC1 de Gwet)
- `figura_tabela_resultados.png`. Tabela 3 (Kappa de Fleiss)
- `figura_tabela_krippendorff.png`. Tabela 4 (Alpha de Krippendorff)

> **Nota sobre os valores:** só reporto abaixo o que os scripts realmente
> calculam e validam (N, número de avaliadores, e as estatísticas de cada
> método). Não incluí Intervalo de Confiança (IC 95%) nem *p*-valor pra
> nenhum dos coeficientes porque os scripts atuais não calculam essas
> estatísticas, se você quiser incluí-las no artigo, me avisa que eu
> implemento o cálculo (e faço a conferência cruzada com o JASP antes de
> confiar no número).

---

## 0. Qual coeficiente usar no artigo (decisão confirmada)

Os quatro métodos foram calculados sobre os **mesmos dados brutos** (21
itens, 4 juízes, resposta binária Sim/Não, já com a regra "Sim +
sugestão = Não" de 21/08/2026 aplicada), então convergem ou divergem de
um jeito que conta uma história metodológica coerente:

- **Kappa de Fleiss (κ) e Alpha de Krippendorff (α)** deram valores
  baixos/negativos nos dois instrumentos (κ = −0,050 e α = −0,046 no
  EPMR; κ = −0,012 e α = −0,008 no RPMS), **não porque os juízes
  discordaram muito**, mas porque as duas fórmulas corrigem a
  concordância pela variância das categorias marginais, e isso as torna
  instáveis sob a prevalência fortemente desbalanceada dos nossos dados
  (a maioria "Sim", uma minoria "Não"). Esse fenômeno é conhecido na
  literatura como *paradoxo do kappa* (Feinstein & Cicchetti, 1990), ver
  `EXPLICACAO.md`, seções 9 e 11, pra explicação completa com a
  matemática por trás.
- **CVI e AC1 de Gwet** não sofrem desse problema e refletem melhor o que
  os dados realmente mostram: concordância alta a muito alta (S-CVI/Ave =
  0,952 e AC1 = 0,895 no EPMR; S-CVI/Ave = 0,988 e AC1 = 0,976 no RPMS).

**Decisão confirmada pela orientadora (18/08/2026):** reportar no corpo do
artigo **só o AC1 de Gwet** (Tabela 1/Tabela 2) como coeficiente de
concordância dos juízes. Kappa de Fleiss e Alpha de Krippendorff (Tabelas
3 e 4) **não entram no corpo do artigo** - ficam documentados aqui e em
`EXPLICACAO.md` só pra justificar metodologicamente, se um revisor
perguntar "por que não Kappa?", que a escolha do AC1 não foi arbitrária:
Kappa e Alpha convergem pro mesmo problema (paradoxo do kappa) sob a
prevalência desbalanceada dos nossos dados, então o AC1 é a medida
correta a reportar, não uma entre várias igualmente válidas.

**CVI (I-CVI, S-CVI/Ave, S-CVI/UA):** a orientadora pediu os dois
produtos (mensagem de 21/08/2026), o AC1 isolado (Tabela 1, o que
efetivamente vai no corpo do artigo) e o CVI junto do AC1 (Tabela 2, como
detalhamento/evidência complementar de validade de conteúdo).

### 0.1 Nota sobre o item 6 do RPMS (dúvida da orientadora de 18/08/2026, RESOLVIDA em 21/08/2026, escopo corrigido em 11/09/2026)

A orientadora perguntou se a Tabela 1 original (100% de concordância no
RPMS) estava arredondando ou ignorando um "Não" da última juíza.
Conferência célula a célula na planilha confirmou, em 18/08: **não havia
bug nem arredondamento**. No item 6 ("Dificuldades de compreender como
atividades cotidianas no Brasil funcionam..."), a Juíza 4 marcou **"Sim"**
na coluna de aprovação, mas deixou um comentário à parte sugerindo trocar
"deslocamento" por "transporte" e separar as atividades numa escala -
aprovou o item com sugestão de redação, o que a coluna binária Sim/Não da
planilha não tinha como distinguir de uma aprovação plena.

**Decisão da orientadora (21/08/2026):** essa ressalva específica conta
como reprovação. Consequência exatamente como prevista: o I-CVI do item 6
caiu de 1,00 para 0,75, e o RPMS deixou de ter 100% de concordância -
Kappa, Alpha e AC1 passaram a dar valores reais (deixaram de ser
indefinidos), porque passou a existir variação nos dados pra medir.

**Correção de escopo (11/09/2026).** A implementação feita em 21/08
generalizou a decisão para qualquer célula preenchida na coluna D, o que
atingiu outros 5 casos no EPMR (itens 4, 5, 8, 10 e 17, juízes 1 e 4) e
derrubou o AC1 do EPMR de 0,895 para 0,735. Auditoria célula a célula em
11/09 mostrou que esses 5 casos são de natureza diferente do item 6: são
**sugestões de aprimoramento em itens aprovados** ("talvez trocar status
social por condições sociais", "Obs: falar sobre sotaque", "...e o envio
de dinheiro ao país de origem"), não apontamentos de falha no item como
redigido. A orientadora confirmou que a decisão de 21/08 valia para um
único caso. Os scripts foram corrigidos: a reclassificação agora é
explícita, declarada na constante `ITENS_COM_RESSALVA_RECLASSIFICADA` de
cada script (vazia no EPMR, `{6}` no RPMS), em vez de disparar
automaticamente em qualquer justificativa preenchida. Com isso os
números voltaram a bater com os do pôster apresentado. Ver
`EXPLICACAO.md`, seção 16.

---

## 1. AC1 de Gwet (isolado)

Produto pedido explicitamente pela orientadora em 21/08/2026: o AC1 de
Gwet sozinho, sem o CVI ao lado (o CVI + AC1 juntos ficam na Tabela 2,
seção 2, como detalhamento). É esse número - e só ele - que vai no corpo
do artigo como medida de concordância entre juízes.

Gerado por `ac1_epmr.py` e `ac1_rpms.py`.

### 1.1 Texto redigido (Resultados)

**EPMR:**

> A concordância entre os quatro juízes especialistas na avaliação dos 21
> itens do EPMR foi analisada por meio do coeficiente AC1 de Gwet (Gwet,
> 2008), estatística corrigida pela concordância esperada ao acaso que,
> diferentemente do Kappa de Fleiss, não incorre no paradoxo do kappa
> (Feinstein & Cicchetti, 1990) sob prevalência de respostas
> desbalanceada. Obteve-se AC1 = 0,895 (concordância observada Pa = 0,905;
> concordância esperada ao acaso Pe = 0,091), classificado como
> concordância quase perfeita (Landis & Koch, 1977).

**RPMS:**

> Para o RPMS, os quatro juízes não especialistas apresentaram AC1 = 0,976
> (Pa = 0,976; Pe = 0,024), classificado como concordância quase perfeita
> (Landis & Koch, 1977), evidenciando forte concordância entre os
> avaliadores na análise dos 21 itens da escala.

### 1.2 Tabela (Markdown)

**Tabela 1.** *Concordância entre avaliadores segundo o coeficiente AC1 de Gwet para o EPMR e o RPMS (21 itens por instrumento).*

| Instrumento | Itens (N) | Avaliadores | Pa (observada) | Pe (esperada, AC1) | AC1 de Gwet | Interpretação |
|---|---|---|---|---|---|---|
| EPMR (juízes especialistas) | 21 | 4 | 0,905 | 0,091 | 0,895 | Concordância quase perfeita |
| RPMS (juízes não especialistas) | 21 | 4 | 0,976 | 0,024 | 0,976 | Concordância quase perfeita |

*Nota.* AC1 de Gwet (Gwet, 2008): estatística de concordância corrigida ao acaso, robusta a prevalência de respostas desbalanceada (não sofre do paradoxo do kappa - ver Tabela 3). Interpretação segundo a escala de Landis e Koch (1977), como usual na literatura para o AC1 (ex.: Wongpakaran et al., 2013).

### 1.3 Tabela (LaTeX)

```latex
\usepackage{booktabs} % no preâmbulo, se ainda não tiver

\begin{table}[h]
\centering
\caption{Concordância entre avaliadores segundo o coeficiente AC1 de Gwet para o EPMR e o RPMS (21 itens por instrumento).}
\label{tab:ac1-isolado}
\begin{tabular}{lcccccc}
\toprule
Instrumento & Itens (N) & Avaliadores & $P_a$ & $P_e$ & AC1 de Gwet & Interpretação$^{a}$ \\
\midrule
EPMR (juízes especialistas) & 21 & 4 & $0{,}905$ & $0{,}091$ & $0{,}895$ & Concordância quase perfeita \\
RPMS (juízes não especialistas) & 21 & 4 & $0{,}976$ & $0{,}024$ & $0{,}976$ & Concordância quase perfeita \\
\bottomrule
\end{tabular}

\vspace{4pt}
{\footnotesize
\textit{Nota.} AC1 de Gwet (Gwet, 2008): estatística de concordância corrigida ao acaso, robusta a prevalência de respostas desbalanceada.
$^{a}$ Interpretação qualitativa segundo a escala de Landis e Koch (1977).
}
\end{table}
```

---

## 2. CVI (Content Validity Index) e AC1 de Gwet

### 2.1 Texto redigido (Resultados)

**EPMR:**

> A validade de conteúdo do EPMR foi avaliada por meio do Índice de
> Validade de Conteúdo (CVI; Lynn, 1986; Polit & Beck, 2006). O I-CVI
> (proporção de juízes que classificou cada item como adequado) foi igual
> a 1,00 em 17 dos 21 itens; os itens 13, 15, 20 e 21 obtiveram I-CVI =
> 0,75, abaixo do critério mínimo recomendado para painéis de até cinco
> juízes (I-CVI ≥ 1,00; Lynn, 1986). Em nível de escala, obteve-se
> S-CVI/Ave = 0,952 e S-CVI/UA = 0,810, ambos acima dos critérios de
> aceitação de Polit, Beck e Owen (2007) (≥ 0,90 e ≥ 0,80,
> respectivamente). Complementarmente, calculou-se o coeficiente AC1
> de Gwet (Gwet, 2008), estatística corrigida pela concordância esperada
> ao acaso que não incorre no paradoxo do kappa (Feinstein & Cicchetti,
> 1990) observado no Kappa de Fleiss (Tabela 3). Obteve-se AC1 = 0,895,
> classificado como concordância quase perfeita (Landis & Koch, 1977).

**RPMS:**

> No RPMS, os quatro juízes não especialistas classificaram 20 dos 21
> itens como adequados por unanimidade (I-CVI = 1,00); o item 6 obteve
> I-CVI = 0,75, abaixo do critério mínimo (Lynn, 1986). Em nível de
> escala, obteve-se S-CVI/Ave = 0,988 e S-CVI/UA = 0,952, ambos acima dos
> critérios de aceitação de Polit, Beck e Owen (2007) (≥ 0,90 e ≥ 0,80,
> respectivamente). O coeficiente AC1 de Gwet obtido foi 0,976,
> classificado como concordância quase perfeita (Landis & Koch, 1977),
> confirmando validade de conteúdo satisfatória para o instrumento.

### 2.2 Tabela (Markdown)

**Tabela 2.** *Índice de Validade de Conteúdo (CVI) e coeficiente AC1 de Gwet para o EPMR e o RPMS (21 itens por instrumento).*

| Instrumento | Itens (N) | Avaliadores | S-CVI/Ave | S-CVI/UA | AC1 de Gwet | Interpretação |
|---|---|---|---|---|---|---|
| EPMR (juízes especialistas) | 21 | 4 | 0,952 | 0,810 | 0,895 | Concordância quase perfeita |
| RPMS (juízes não especialistas) | 21 | 4 | 0,988 | 0,952 | 0,976 | Concordância quase perfeita |

*Nota.* S-CVI/Ave = média dos I-CVI de todos os itens; critério de aceitação ≥ 0,90 (Polit, Beck & Owen, 2007). S-CVI/UA = proporção de itens com acordo universal (I-CVI = 1,00); critério de aceitação ≥ 0,80 (Polit, Beck & Owen, 2007). AC1 de Gwet: estatística de concordância corrigida ao acaso, robusta a prevalência desbalanceada (Gwet, 2008); interpretação segundo a escala de Landis e Koch (1977).

### 2.3 Tabela (LaTeX)

```latex
\usepackage{booktabs} % no preâmbulo, se ainda não tiver

\begin{table}[h]
\centering
\caption{Índice de Validade de Conteúdo (CVI) e coeficiente AC1 de Gwet para o EPMR e o RPMS (21 itens por instrumento).}
\label{tab:cvi-ac1}
\begin{tabular}{lcccccc}
\toprule
Instrumento & Itens (N) & Avaliadores & S-CVI/Ave$^{a}$ & S-CVI/UA$^{b}$ & AC1 de Gwet$^{c}$ & Interpretação$^{d}$ \\
\midrule
EPMR (juízes especialistas) & 21 & 4 & $0{,}952$ & $0{,}810$ & $0{,}895$ & Concordância quase perfeita \\
RPMS (juízes não especialistas) & 21 & 4 & $0{,}988$ & $0{,}952$ & $0{,}976$ & Concordância quase perfeita \\
\bottomrule
\end{tabular}

\vspace{4pt}
{\footnotesize
\textit{Nota.} $^{a}$ Média dos I-CVI de todos os itens; critério de aceitação $\geq 0{,}90$ (Polit, Beck \& Owen, 2007).
$^{b}$ Proporção de itens com acordo universal (I-CVI $= 1{,}00$); critério de aceitação $\geq 0{,}80$ (Polit, Beck \& Owen, 2007).
$^{c}$ Estatística de concordância corrigida ao acaso, robusta a prevalência desbalanceada (Gwet, 2008).
$^{d}$ Interpretação qualitativa segundo a escala de Landis e Koch (1977), também aplicada ao AC1 na literatura.
}
\end{table}
```

---

## 3. Kappa de Fleiss

### 3.1 Texto redigido (Resultados)

**EPMR:**

> A confiabilidade entre os quatro juízes especialistas na avaliação dos
> 21 itens do EPMR foi analisada por meio do coeficiente Kappa de Fleiss.
> Observou-se κ = −0,050, valor que indica concordância pior do que a
> esperada pelo acaso (Landis & Koch, 1977). Dos 21 itens avaliados, 17
> obtiveram concordância total entre os quatro juízes; os quatro itens
> restantes (itens 13, 15, 20 e 21) apresentaram divergência de um único
> juiz em relação aos demais.

**RPMS:**

> Para o RPMS, os quatro juízes não especialistas responderam "Sim" a 20
> dos 21 itens da escala por unanimidade; o item 6 apresentou divergência
> de um único juiz. Observou-se κ = −0,012, valor que, apesar de negativo,
> reflete quase ausência total de discordância real (apenas 1 de 84
> respostas divergiu), um caso clássico do paradoxo do kappa (Feinstein
> & Cicchetti, 1990), em que a fórmula do Kappa penaliza a alta
> prevalência de "Sim" mesmo havendo concordância bruta muito alta entre
> os avaliadores.

### 3.2 Tabela (Markdown)

**Tabela 3.** *Concordância entre avaliadores segundo o coeficiente Kappa de Fleiss para o EPMR e o RPMS (21 itens por instrumento).*

| Instrumento | Itens (N) | Avaliadores | Itens com concordância total | Kappa de Fleiss (κ) | Interpretação |
|---|---|---|---|---|---|
| EPMR (juízes especialistas) | 21 | 4 | 17 de 21 | −0,050 | Pior que o esperado ao acaso |
| RPMS (juízes não especialistas) | 21 | 4 | 20 de 21 | −0,012 | Pior que o esperado ao acaso |

*Nota.* Interpretação qualitativa segundo a escala de Landis e Koch (1977). Valores negativos ou baixos nos dois instrumentos refletem o paradoxo do kappa (Feinstein & Cicchetti, 1990) sob prevalência de respostas fortemente desbalanceada, não discordância real entre os juízes - ver CVI e AC1 de Gwet (Tabelas 1-2).

### 3.3 Tabela (LaTeX)

```latex
\usepackage{booktabs} % no preâmbulo, se ainda não tiver

\begin{table}[h]
\centering
\caption{Concordância entre avaliadores segundo o coeficiente Kappa de Fleiss para o EPMR e o RPMS (21 itens por instrumento).}
\label{tab:kappa-fleiss}
\begin{tabular}{lccccc}
\toprule
Instrumento & Itens (N) & Avaliadores & Itens c/ concordância total & Kappa de Fleiss ($\kappa$) & Interpretação$^{a}$ \\
\midrule
EPMR (juízes especialistas) & 21 & 4 & 17 de 21 & $-0{,}050$ & Pior que o esperado ao acaso \\
RPMS (juízes não especialistas) & 21 & 4 & 20 de 21 & $-0{,}012$ & Pior que o esperado ao acaso \\
\bottomrule
\end{tabular}

\vspace{4pt}
{\footnotesize
\textit{Nota.} $^{a}$ Interpretação qualitativa segundo a escala de Landis e Koch (1977). Valores negativos ou baixos refletem o paradoxo do kappa (Feinstein \& Cicchetti, 1990) sob prevalência de respostas desbalanceada, não discordância real - ver CVI e AC1 de Gwet (Tabelas 1--2).
}
\end{table}
```

---

## 4. Alpha de Krippendorff

### 4.1 Texto redigido (Resultados)

**EPMR:**

> Como medida complementar de robustez, calculou-se também o Alpha de
> Krippendorff (Krippendorff, 2019), coeficiente de confiabilidade mais
> geral que aceita qualquer número de avaliadores, dados faltantes e
> diferentes níveis de mensuração. Para o EPMR, obteve-se α = −0,046 (n..
> = 252 pares avaliador-avaliador), valor próximo ao Kappa de Fleiss (κ =
> −0,050; Tabela 3) e classificado como confiabilidade insuficiente
> segundo o critério do próprio Krippendorff (α ≥ 0,667 para conclusões
> tentativas; α ≥ 0,800 para conclusões definitivas). Esse resultado é
> consistente com o paradoxo do kappa (Feinstein & Cicchetti, 1990): como
> o Alpha de Krippendorff nominal também corrige a concordância pela
> variância das proporções marginais, ele está sujeito à mesma distorção
> sob prevalência de respostas desbalanceada. A convergência entre duas
> fórmulas matematicamente distintas (Kappa de Fleiss e Alpha de
> Krippendorff) reforça que o valor baixo não é uma peculiaridade de uma
> fórmula específica, e sustenta a adoção do AC1 de Gwet (Tabelas 1-2)
> como medida principal de confiabilidade neste estudo.

**RPMS:**

> Para o RPMS, obteve-se α = −0,008 (n.. = 252 pares avaliador-avaliador),
> também classificado como confiabilidade insuficiente pelo critério de
> Krippendorff, apesar da concordância bruta muito alta entre os
> avaliadores (apenas 1 de 84 respostas divergiu) - o mesmo fenômeno do
> paradoxo do kappa observado no Kappa de Fleiss (Tabela 3) para esse
> instrumento.

### 4.2 Tabela (Markdown)

**Tabela 4.** *Alpha de Krippendorff para o EPMR e o RPMS (21 itens por instrumento).*

| Instrumento | Itens (N) | Avaliadores | Pares avaliáveis (n..) | Alpha de Krippendorff (α) | Interpretação |
|---|---|---|---|---|---|
| EPMR (juízes especialistas) | 21 | 4 | 252 | −0,046 | Confiabilidade insuficiente |
| RPMS (juízes não especialistas) | 21 | 4 | 252 | −0,008 | Confiabilidade insuficiente |

*Nota.* Critério de Krippendorff (1980, 2004, 2019): α ≥ 0,800 para conclusões definitivas; α ≥ 0,667 apenas para conclusões tentativas/exploratórias; abaixo disso, confiabilidade insuficiente. Assim como o Kappa de Fleiss (Tabela 3), o Alpha reflete o paradoxo do kappa sob prevalência de respostas desbalanceada, não discordância real - ver CVI e AC1 de Gwet (Tabelas 1-2).

### 4.3 Tabela (LaTeX)

```latex
\usepackage{booktabs} % no preâmbulo, se ainda não tiver

\begin{table}[h]
\centering
\caption{Alpha de Krippendorff para o EPMR e o RPMS (21 itens por instrumento).}
\label{tab:krippendorff-alpha}
\begin{tabular}{lccccc}
\toprule
Instrumento & Itens (N) & Avaliadores & Pares avaliáveis ($n_{..}$) & Alpha ($\alpha$) & Interpretação$^{a}$ \\
\midrule
EPMR (juízes especialistas) & 21 & 4 & 252 & $-0{,}046$ & Confiabilidade insuficiente \\
RPMS (juízes não especialistas) & 21 & 4 & 252 & $-0{,}008$ & Confiabilidade insuficiente \\
\bottomrule
\end{tabular}

\vspace{4pt}
{\footnotesize
\textit{Nota.} $^{a}$ Critério de Krippendorff (1980, 2004, 2019): $\alpha \geq 0{,}800$ para conclusões definitivas; $\alpha \geq 0{,}667$ apenas para conclusões tentativas/exploratórias. Reflete o paradoxo do kappa (Feinstein \& Cicchetti, 1990) sob prevalência desbalanceada, não discordância real - ver CVI e AC1 de Gwet (Tabelas 1--2).
}
\end{table}
```

---

## 5. Referências (texto, formato APA 7)

Lista consolidada, copia direto pra lista de referências do artigo (as
entradas de código-fonte estão assinadas por Guilherme Lacerda de Avila,
autor dos scripts):

```
Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543–549. https://doi.org/10.1016/0895-4356(90)90158-L

Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378–382. https://doi.org/10.1037/h0031619

Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. British Journal of Mathematical and Statistical Psychology, 61(1), 29–48. https://doi.org/10.1348/000711006X126600

Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77–89. https://doi.org/10.1080/19312450709336664

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. Computing in Science & Engineering, 9(3), 90–95. https://doi.org/10.1109/MCSE.2007.55

Krippendorff, K. (2019). Content analysis: An introduction to its methodology (4th ed.). Sage.

Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159–174.

Lynn, M. R. (1986). Determination and quantification of content validity. Nursing Research, 35(6), 382–385.

Polit, D. F., & Beck, C. T. (2006). The content validity index: Are you sure you know what's being reported? Critique and recommendations. Research in Nursing & Health, 29(5), 489–497. https://doi.org/10.1002/nur.20147

Polit, D. F., Beck, C. T., & Owen, S. V. (2007). Is the CVI an acceptable indicator of content validity? Appraisal and recommendations. Research in Nursing & Health, 30(4), 459–467. https://doi.org/10.1002/nur.20199

Python Software Foundation. (2026). Python (Versão 3.11) [Linguagem de programação]. https://www.python.org

Seabold, S., & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with Python. Proceedings of the 9th Python in Science Conference, 57–61. https://www.statsmodels.org

openpyxl developers. (2024). openpyxl (Versão 3.1) [Biblioteca de software]. https://openpyxl.readthedocs.io/

Ávila, G. L. de. (2026). Script de cálculo do AC1 de Gwet isolado para o EPMR e o RPMS [Código-fonte não publicado]. estatistica/ac1_epmr.py; estatistica/ac1_rpms.py.

Ávila, G. L. de. (2026). Script de cálculo do Kappa de Fleiss para o EPMR e o RPMS [Código-fonte não publicado]. estatistica/fleiss_kappa_epmr.py; estatistica/fleiss_kappa_rpms.py.

Ávila, G. L. de. (2026). Script de cálculo do CVI e do AC1 de Gwet para o EPMR e o RPMS [Código-fonte não publicado]. estatistica/cvi_ac1_epmr.py; estatistica/cvi_ac1_rpms.py.

Ávila, G. L. de. (2026). Script de cálculo do Alpha de Krippendorff para o EPMR e o RPMS [Código-fonte não publicado]. estatistica/krippendorff_alpha_epmr.py; estatistica/krippendorff_alpha_rpms.py.
```

Se o artigo pedir ABNT em vez de APA, me avisa que eu converto o formato das referências.

---

## 6. Porcentagem de concordância entre traduções (tradução e retrotradução)

Pedido da orientadora (18/08/2026): pra tradução e retrotradução, uma
avaliação **simples de porcentagem de concordância** entre as versões
traduzidas - diferente dos coeficientes das seções 1-4, que medem
concordância entre juízes avaliando itens (Sim/Não). Aqui a medida é o
quão parecido é o **texto** entre versões traduzidas diferentes do mesmo
item (não afetada pela regra "Sim + sugestão = Não" de 21/08/2026, que só
vale pra avaliação de itens). Calculada de dois jeitos: **% exata**
(texto idêntico após normalizar - rígido) e **% de similaridade** (via
`difflib.SequenceMatcher`, mais tolerante a reformulação sem mudar o
sentido - mais realista pra tradução livre). Ver `EXPLICACAO.md`, seção
13, pra justificativa completa do método e limitações (nenhuma das duas
métricas avalia SENTIDO, só texto literal).

### 6.1 Texto redigido (Resultados)

**Tradução (3 versões: leiga, especialista, equipe):**

> A concordância entre as três versões traduzidas do RPMS (tradução
> leiga, tradução especialista e versão consolidada pela equipe) foi
> avaliada em 28 elementos (título, instrução, cinco opções de resposta
> da escala e 21 itens), comparando o texto par a par. As três versões
> foram idênticas em 46,4% dos elementos; a similaridade textual média
> (SequenceMatcher) foi de 94,3% considerando os três pares de
> comparação. A concordância exata entre a tradução leiga e a tradução
> especialista (99,1% de similaridade média) foi superior à concordância
> de cada uma dessas com a versão final da equipe (91,6% e 92,3%,
> respectivamente), refletindo o processo de síntese e revisão da
> equipe sobre as duas traduções iniciais.

**Retrotradução (2 retradutores × original em inglês):**

> A retrotradução do RPMS foi conduzida por dois retradutores
> independentes, e a versão de cada um foi comparada ao texto original
> em inglês da escala. A concordância exata foi baixa em ambos os casos
> (6,7%), como esperado em tarefas de tradução livre; a similaridade
> textual média foi de 69,6% (Retradutor 1) e 66,4% (Retradutor 2). A
> concordância entre as duas retraduções (sem envolver o original) foi
> maior - 83,8% de similaridade média -, consistente com o fato de que
> ambos partiram do mesmo texto em português, enquanto reconstruir
> literalmente um original em inglês nunca visto é uma tarefa mais
> difícil por natureza. Divergências pontuais nos itens de menor
> similaridade foram revisadas qualitativamente pela equipe antes da
> finalização da escala.

### 6.2 Tabela (Markdown)

**Tabela 5.** *Porcentagem de concordância entre versões traduzidas do RPMS - tradução e retrotradução.*

| Comparação | Elementos (N) | % idêntico (exata) | Similaridade média |
|---|---|---|---|
| Tradução: leiga × especialista | 28 | 75,0% | 99,1% |
| Tradução: leiga × equipe | 28 | 46,4% | 91,6% |
| Tradução: especialista × equipe | 28 | 60,7% | 92,3% |
| Tradução: as 3 versões idênticas | 28 | 46,4% | — |
| Retrotradução: Retradutor 1 × original | 30 | 6,7% | 69,6% |
| Retrotradução: Retradutor 2 × original | 30 | 6,7% | 66,4% |
| Retrotradução: Retradutor 1 × Retradutor 2 | 30 | 26,7% | 83,8% |

*Nota.* "% idêntico" = texto idêntico após normalizar (minúsculas, espaços, numeração do item removida). "Similaridade" = percentual calculado com `difflib.SequenceMatcher` (Python), mede semelhança textual mesmo quando o texto não é idêntico. N=28 na tradução (título+instrução+5 opções de resposta+21 itens); N=30 na retrotradução (mesmos 28 + 2 variantes extras testadas nos itens 8 e 10). ⚠ Um item (item 16) está com numeração duplicada na planilha-fonte de retrotradução (rotulado "15" por engano) - conferir manualmente antes de citar esse item específico no artigo (ver `EXPLICACAO.md`, seção 13.3).

### 6.3 Tabela (LaTeX)

```latex
\usepackage{booktabs} % no preâmbulo, se ainda não tiver

\begin{table}[h]
\centering
\caption{Porcentagem de concordância entre versões traduzidas do RPMS - tradução e retrotradução.}
\label{tab:concordancia-traducao}
\begin{tabular}{lccc}
\toprule
Comparação & Elementos (N) & \% idêntico (exata) & Similaridade média \\
\midrule
Tradução: leiga × especialista & 28 & 75,0\% & 99,1\% \\
Tradução: leiga × equipe & 28 & 46,4\% & 91,6\% \\
Tradução: especialista × equipe & 28 & 60,7\% & 92,3\% \\
Tradução: as 3 versões idênticas & 28 & 46,4\% & --- \\
Retrotradução: Retradutor 1 × original$^{a}$ & 30 & 6,7\% & 69,6\% \\
Retrotradução: Retradutor 2 × original$^{a}$ & 30 & 6,7\% & 66,4\% \\
Retrotradução: Retradutor 1 × Retradutor 2 & 30 & 26,7\% & 83,8\% \\
\bottomrule
\end{tabular}

\vspace{4pt}
{\footnotesize
\textit{Nota.} \% idêntico = texto idêntico após normalização; Similaridade = percentual via \texttt{difflib.SequenceMatcher} (Python). N=28 na tradução, N=30 na retrotradução (inclui 2 variantes extras testadas nos itens 8 e 10.
$^{a}$ Um item (item 16) está com numeração duplicada na planilha-fonte, conferir manualmente antes de citar no artigo.
}
\end{table}
```

### 6.4 Referências adicionais

```
Python Software Foundation. (2026). difflib. Helpers for computing deltas [Documentação da biblioteca padrão]. https://docs.python.org/3/library/difflib.html

Ávila, G. L. de. (2026). Script de cálculo de porcentagem de concordância entre traduções e retrotradução do RPMS [Código-fonte não publicado]. estatistica/concordancia_traducao.py; estatistica/concordancia_retrotraducao.py.
```
