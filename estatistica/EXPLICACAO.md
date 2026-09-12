# Como funcionam os scripts de concordância entre juízes

> **DECISÃO CONFIRMADA PELA ORIENTADORA (18/08/2026, refinada em
> 21/08/2026):** o coeficiente reportado no corpo do artigo pros juízes é
> o **AC1 de Gwet**, isolado (`ac1_epmr.py` / `ac1_rpms.py`, seção 15) ou
> junto do CVI como detalhamento (`cvi_ac1_epmr.py` / `cvi_ac1_rpms.py`).
> Kappa de Fleiss e Alpha de Krippendorff continuam calculados e
> documentados aqui - servem pra justificar a escolha do AC1 (seção 9:
> paradoxo do kappa) - mas não vão pro corpo principal do artigo. Em
> 21/08/2026 a orientadora também fixou a regra "Sim + sugestão = Não"
> (seção 14), que muda os dados de entrada de todos os scripts. Detalhes
> em `RESULTADOS_PARA_ARTIGO.md`, seção 0.

Este documento explica, **linha por linha**, os dez scripts da pasta `estatistica/`:

- `fleiss_kappa_epmr.py` → calcula o Kappa de Fleiss do **EPMR** (4 juízes especialistas)
- `fleiss_kappa_rpms.py` → calcula o Kappa de Fleiss do **RPMS** (4 juízes não especialistas)
- `cvi_ac1_epmr.py` → calcula **CVI** e **AC1 de Gwet** do EPMR (alternativas ao Kappa, seção 9)
- `cvi_ac1_rpms.py` → calcula **CVI** e **AC1 de Gwet** do RPMS
- `krippendorff_alpha_epmr.py` → calcula o **Alpha de Krippendorff** do EPMR (seção 11)
- `krippendorff_alpha_rpms.py` → calcula o **Alpha de Krippendorff** do RPMS
- `ac1_epmr.py` → calcula **só o AC1 de Gwet** do EPMR, sem CVI junto (seção 15) - o que vai no artigo
- `ac1_rpms.py` → calcula **só o AC1 de Gwet** do RPMS, sem CVI junto
- `concordancia_traducao.py` → calcula **% de concordância entre versões traduzidas** do RPMS (seção 13)
- `concordancia_retrotraducao.py` → calcula **% de concordância na retrotradução** do RPMS (seção 13)

Os dois scripts de Kappa fazem basicamente a mesma coisa e têm quase o mesmo código. A diferença principal é que o script do RPMS tem uma camada extra de cuidado com privacidade (explicado na seção 6). Por isso, este guia explica o `fleiss_kappa_epmr.py` bloco por bloco (seção 3), e depois só destaca **o que muda** no `fleiss_kappa_rpms.py` (seção 6).

Os quatro scripts seguintes (CVI/AC1 e Alpha de Krippendorff) seguem exatamente esse mesmo padrão (mesma leitura de planilha, mesma proteção de privacidade no RPMS), as seções 9 e 11 explicam **por que** cada um existe, e as seções 10 e 12 detalham só o que é **novo** em cada um, sem repetir o que já foi explicado nas seções 3-6.

---

## Comandos rápidos

Rodar todos os 10 scripts (cada um imprime na tela e salva `.txt` + `.png` + `.html` em `estatistica/resultados/`, com o mesmo timestamp nos três arquivos):

```bash
uv run estatistica/fleiss_kappa_epmr.py
uv run estatistica/fleiss_kappa_rpms.py
uv run estatistica/cvi_ac1_epmr.py
uv run estatistica/cvi_ac1_rpms.py
uv run estatistica/krippendorff_alpha_epmr.py
uv run estatistica/krippendorff_alpha_rpms.py
uv run estatistica/ac1_epmr.py
uv run estatistica/ac1_rpms.py
uv run estatistica/concordancia_traducao.py
uv run estatistica/concordancia_retrotraducao.py
```

Rodando os 10 de uma vez só, em sequência:

```bash
for s in fleiss_kappa_epmr fleiss_kappa_rpms cvi_ac1_epmr cvi_ac1_rpms krippendorff_alpha_epmr krippendorff_alpha_rpms ac1_epmr ac1_rpms concordancia_traducao concordancia_retrotraducao; do
  uv run estatistica/$s.py
done
```

Pra usar outro arquivo Excel (ex.: uma versão corrigida da planilha), passa o caminho como argumento nos 8 scripts de juízes (kappa/CVI-AC1/alpha/AC1 isolado):

```bash
uv run estatistica/fleiss_kappa_epmr.py "caminho/outro_arquivo.xlsx"
```

(os dois scripts de tradução/retrotradução não aceitam esse argumento - eles sempre leem os arquivos fixos `Versão Corrigida dos Tradutores.xlsx` e `Retrotradução.xlsx` da raiz do projeto, ver seção 13)

Detalhes de cada saída (o que é `.txt`/`.png`/`.html`, onde ficam, como funcionam por dentro) estão nas seções 7, 9-10, 11-12 e 13 abaixo.

---

## 1. O que é o Kappa de Fleiss (resumo pra apresentação)

O EPMR e o RPMS são duas escalas com 21 itens cada. Cada item é avaliado como **Sim** (o item está adequado) ou **Não** (o item precisa de ajuste) por 4 juízes diferentes.

A pergunta que o Kappa de Fleiss responde é: **os juízes concordam entre si mais do que seria esperado só por acaso?**

- Se todos os juízes chutassem aleatoriamente, ainda apareceria uma concordância "de graça" só por coincidência.
- O Kappa de Fleiss calcula a concordância **real** e subtrai essa concordância "de graça" (chamada de concordância esperada ao acaso, ou *Pe*).
- O resultado varia, na prática, de valores negativos até 1:
  - **1** = concordância perfeita
  - **0** = a concordância observada é exatamente igual à esperada por acaso (ou seja, os juízes não estão concordando mais do que o acaso explicaria)
  - **negativo** = os juízes concordam **menos** do que o acaso explicaria
  - **NaN (indefinido)** = não dá pra calcular, porque não existe nenhuma variação nas respostas (todo mundo respondeu a mesma coisa o tempo todo), explicado com mais detalhe na seção 5.

A escala de interpretação usada nos scripts é a clássica de **Landis & Koch (1977)**, comum nas aulas de metodologia:

| Valor do Kappa | Interpretação |
|---|---|
| < 0 | pior que o acaso |
| 0,00 a 0,20 | leve |
| 0,20 a 0,40 | razoável |
| 0,40 a 0,60 | moderada |
| 0,60 a 0,80 | substancial |
| 0,80 a 1,00 | quase perfeita |

---

## 2. Estrutura de pastas

```
IC/
├── Avaliação EPMR Juízes Especialistas.xlsx          ← dado de entrada
├── Avaliação RPMS - Juízes Não Especialistas.xlsx    ← dado de entrada
└── estatistica/
    ├── fleiss_kappa_epmr.py
    ├── fleiss_kappa_rpms.py
    ├── cvi_ac1_epmr.py
    ├── cvi_ac1_rpms.py
    ├── krippendorff_alpha_epmr.py
    ├── krippendorff_alpha_rpms.py
    ├── ac1_epmr.py                (seção 15 - só AC1, sem CVI)
    ├── ac1_rpms.py
    ├── EXPLICACAO.md              (este arquivo)
    └── resultados/                ← criado automaticamente ao rodar
        ├── fleiss_kappa_epmr_<data>.txt
        ├── dados_brutos_epmr_<data>.csv
        ├── fleiss_kappa_rpms_<data>.txt
        ├── dados_brutos_rpms_<data>.csv
        ├── cvi_ac1_epmr_<data>.txt
        ├── cvi_ac1_rpms_<data>.txt
        ├── krippendorff_alpha_epmr_<data>.txt
        ├── krippendorff_alpha_rpms_<data>.txt
        ├── ac1_epmr_<data>.txt
        └── ac1_rpms_<data>.txt
```

Cada Excel tem 4 abas (uma por juiz). Em cada aba, os 21 itens ficam nas **linhas 6 a 26**, e a resposta (Sim/Não) fica sempre na **coluna C**.

---

## 3. `fleiss_kappa_epmr.py`, explicação linha por linha

### Cabeçalho (linhas 1-19)

```python
# fleiss_kappa_epmr.py
#
# Script pra calcular o Kappa de Fleiss do EPMR...
```

É só um comentário explicando o que o arquivo faz e como rodar. Python ignora tudo que começa com `#`, isso é só documentação pra quem for ler o código depois (inclusive você, na apresentação).

### Imports (linhas 21-27)

```python
import math
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
from statsmodels.stats.inter_rater import fleiss_kappa
```

Cada `import` traz uma ferramenta pronta pra usar no resto do script:

| Import | Pra que serve aqui |
|---|---|
| `math` | só usamos a função `math.isnan()`, que checa se um número é "Not a Number" (indefinido) |
| `sys` | pra ler o que a pessoa digitou na linha de comando (`sys.argv`) e pra parar o script com `sys.exit()` |
| `datetime` | pra colocar data e hora no nome dos arquivos de resultado |
| `Path` | representa um caminho de arquivo/pasta de um jeito que funciona em qualquer sistema operacional (Windows, Linux, Mac) |
| `openpyxl` | biblioteca que sabe abrir e ler arquivos `.xlsx` do Excel |
| `fleiss_kappa` | a função pronta (da biblioteca `statsmodels`) que faz a conta do Kappa de Fleiss de verdade, é a fórmula matemática em si |

### Constantes (linhas 29-43)

Constante = uma variável que a gente define uma vez lá no topo e não muda mais durante a execução. Deixar esses valores no topo (em vez de "espalhados" pelo código) facilita mudar depois se precisar.

```python
LINHA_COMECO = 6
LINHA_FIM = 26      # dá 21 itens no total (26 - 6 + 1)
COLUNA_RESPOSTA = 3  # coluna C
```

Isso descreve **onde**, dentro do Excel, estão as respostas: da linha 6 até a linha 26 (21 linhas = 21 itens), sempre na coluna número 3 (A=1, B=2, **C=3**).

```python
PASTA_DO_SCRIPT = Path(__file__).resolve().parent
```

`__file__` é uma variável mágica do Python que sempre contém o caminho do próprio arquivo `.py` que está rodando. `.resolve()` transforma isso num caminho completo (sem `..` nem atalhos), e `.parent` pega a pasta que contém o arquivo, ou seja, a pasta `estatistica/`. Isso é importante porque **garante que o script sempre sabe onde ele mesmo está**, não importa de qual pasta você chamou o comando `uv run`.

```python
ARQUIVO_PADRAO = PASTA_DO_SCRIPT.parent / "Avaliação EPMR Juízes Especialistas.xlsx"
```

`PASTA_DO_SCRIPT.parent` sobe um nível (de `estatistica/` pra raiz do projeto), e o `/` aqui **não é divisão**, é um jeito do `Path` "colar" um nome de arquivo/pasta no final do caminho. Então essa linha monta o caminho completo até o Excel padrão.

```python
PASTA_RESULTADOS = PASTA_DO_SCRIPT / "resultados"
```

Mesma lógica: monta o caminho da pasta `estatistica/resultados/`, onde tudo que o script gerar vai ser salvo.

### Função `normalizar_resposta` (linhas 46-67)

```python
def normalizar_resposta(valor):
    if valor is None:
        raise ValueError("achei uma celula vazia onde devia ter Sim ou Nao")

    texto = str(valor).strip().lower()

    if texto == "sim":
        return "Sim"
    elif texto == "não" or texto == "nao":
        return "Não"
    else:
        raise ValueError("valor estranho na planilha, não é Sim nem Não: " + repr(valor))
```

**Por que essa função existe:** ao abrir as 4 planilhas do EPMR, percebi que a aba do Juiz 4 escreve as respostas em **maiúsculo** (`SIM`, `NÃO`), enquanto as outras 3 escrevem `Sim`/`Não` normal. Se o script não arrumar isso, ele ia tratar `"Sim"` e `"SIM"` como duas categorias diferentes, e a conta do Kappa ficaria errada.

Linha por linha:

- `if valor is None:` → se a célula do Excel estiver vazia, `valor` chega como `None`. Isso é um erro (não devia acontecer), então a função para tudo com `raise ValueError(...)`, uma mensagem de erro que aparece no terminal se isso acontecer.
- `texto = str(valor).strip().lower()` → transforma o valor em texto (`str`), tira espaços em branco do início/fim (`.strip()`) e deixa tudo minúsculo (`.lower()`). Assim, `"Sim"`, `" sim "`, `"SIM"` viram todos `"sim"`.
- `if texto == "sim": return "Sim"` → se depois de normalizar deu `"sim"`, devolve sempre a mesma forma padronizada: `"Sim"` (com S maiúsculo, jeito bonito).
- `elif texto == "não" or texto == "nao":` → mesma ideia pro "não", cobrindo tanto com acento quanto sem (por segurança, caso alguém digite sem o "~").
- `else: raise ValueError(...)` → se não bateu com nenhum dos dois casos, é porque tem algo errado na planilha (erro de digitação, célula com outro texto). Em vez de o script continuar e dar um resultado errado sem avisar, ele **para e avisa**.

### Função `ler_respostas_de_um_juiz` (linhas 70-76)

```python
def ler_respostas_de_um_juiz(planilha):
    respostas = []
    for linha in range(LINHA_COMECO, LINHA_FIM + 1):
        valor_da_celula = planilha.cell(row=linha, column=COLUNA_RESPOSTA).value
        respostas.append(normalizar_resposta(valor_da_celula))
    return respostas
```

Recebe uma aba do Excel já aberta (`planilha`) e devolve uma lista com as 21 respostas normalizadas.

- `respostas = []` → começa uma lista vazia, que vai ser preenchida.
- `for linha in range(LINHA_COMECO, LINHA_FIM + 1):` → repete uma vez pra cada linha de 6 até 26 (o `+ 1` é necessário porque o `range()` do Python **não inclui** o último número; sem o `+1` ele pararia na linha 25).
- `planilha.cell(row=linha, column=COLUNA_RESPOSTA).value` → pega o valor da célula naquela linha, coluna 3 (C). É a leitura de fato da célula do Excel.
- `respostas.append(normalizar_resposta(valor_da_celula))` → joga o valor lido pra dentro da função de normalização, e guarda o resultado (já padronizado) na lista.
- `return respostas` → devolve a lista com as 21 respostas desse juiz.

### Função `carregar_arquivo` (linhas 79-87)

```python
def carregar_arquivo(caminho_excel):
    livro = openpyxl.load_workbook(caminho_excel, data_only=True)

    respostas_por_juiz = []
    for nome_da_planilha in livro.sheetnames:
        planilha = livro[nome_da_planilha]
        respostas_por_juiz.append(ler_respostas_de_um_juiz(planilha))

    return respostas_por_juiz
```

- `openpyxl.load_workbook(caminho_excel, data_only=True)` → abre o arquivo Excel inteiro. O `data_only=True` é importante: se alguma célula tivesse uma fórmula (tipo `=SE(...)`), esse parâmetro faz o `openpyxl` ler o **resultado já calculado** da fórmula, e não o texto da fórmula em si.
- `livro.sheetnames` → é a lista com o nome de todas as abas do arquivo, na ordem que elas aparecem (ex.: `["Juiz 1 (Lygia)", "Juiz 2 (Renata)", ...]`).
- `for nome_da_planilha in livro.sheetnames:` → repete uma vez pra cada aba.
- `planilha = livro[nome_da_planilha]` → abre aquela aba específica.
- `respostas_por_juiz.append(ler_respostas_de_um_juiz(planilha))` → lê as 21 respostas dessa aba (usando a função anterior) e adiciona na lista principal.
- No final, `respostas_por_juiz` é uma **lista de listas**: uma lista por juiz, cada uma com 21 respostas. Por exemplo: `[["Sim", "Sim", ...], ["Sim", "Não", ...], ...]`.

### Função `montar_matriz_e_achar_empates` (linhas 90-120)

Essa é a função mais importante, é onde os dados brutos viram a **matriz** que a fórmula do Kappa de Fleiss espera (uma linha por item, com a contagem de quantos juízes disseram Sim e quantos disseram Não).

```python
numero_de_itens = len(respostas_por_juiz[0])
numero_de_juizes = len(respostas_por_juiz)
```

`len()` conta quantos elementos tem numa lista. `respostas_por_juiz[0]` é a lista do primeiro juiz (21 respostas), então `numero_de_itens` vira 21. `respostas_por_juiz` tem uma entrada por juiz, então `numero_de_juizes` vira 4.

```python
matriz = []
itens_sem_variacao = []
```

Duas listas vazias que vão ser preenchidas: a matriz final, e a lista de itens onde todo mundo concordou 100%.

```python
for i in range(numero_de_itens):
    qtd_sim = 0
    qtd_nao = 0

    for respostas in respostas_por_juiz:
        if respostas[i] == "Sim":
            qtd_sim += 1
        else:
            qtd_nao += 1
```

Aqui tem um **loop dentro de outro loop**:
- O loop de fora (`for i in range(numero_de_itens)`) passa item por item (i = 0, 1, 2... até 20, lembrando que no Python a contagem começa em 0, por isso o item "1" da planilha é o índice `0` aqui).
- Pra cada item, zera dois contadores (`qtd_sim = 0`, `qtd_nao = 0`).
- O loop de dentro (`for respostas in respostas_por_juiz`) passa juiz por juiz, e olha o que aquele juiz respondeu **naquele item específico** (`respostas[i]`).
- Se foi `"Sim"`, soma 1 em `qtd_sim`; senão (só pode ser `"Não"`, já que a normalização garante isso), soma 1 em `qtd_nao`.
- No final desses dois loops, `qtd_sim` e `qtd_nao` têm quantos juízes (de 0 a 4) responderam cada coisa **naquele item**.

```python
        matriz.append([qtd_sim, qtd_nao])

        if qtd_sim == numero_de_juizes or qtd_nao == numero_de_juizes:
            itens_sem_variacao.append(i + 1)
```

- `matriz.append([qtd_sim, qtd_nao])` → adiciona uma linha na matriz: `[quantos Sim, quantos Não]` daquele item.
- `if qtd_sim == numero_de_juizes or qtd_nao == numero_de_juizes:` → se **todos** os juízes (os 4) responderam Sim, ou se **todos** responderam Não, esse item não tem nenhuma variação, todo mundo concordou. Isso é guardado pra explicar no relatório final.
- `itens_sem_variacao.append(i + 1)` → guarda o número do item (o `+1` é só pra mostrar "item 1" em vez de "item 0" no relatório, ficando igual à numeração da planilha).

```python
return matriz, itens_sem_variacao
```

A função devolve **duas coisas de uma vez** (em Python isso é normal, devolve uma "tupla"). Na hora de chamar essa função, isso é recebido assim: `matriz, itens_sem_variacao = montar_matriz_e_achar_empates(...)`.

**Exemplo concreto** com os dados reais do EPMR, item 13: Juiz 1 respondeu "Não", os outros 3 responderam "Sim" → a linha correspondente na matriz fica `[3, 1]` (3 Sins, 1 Não).

### Função `interpretar_kappa` (linhas 123-138)

```python
def interpretar_kappa(valor_kappa):
    if math.isnan(valor_kappa):
        return "indefinido"
    if valor_kappa < 0:
        return "concordância pior do que o esperado por acaso"
    if valor_kappa < 0.20:
        return "concordância leve"
    ...
```

Uma sequência de `if`s que checa em qual faixa da tabela de Landis & Koch (seção 1) o valor calculado caiu, e devolve o texto correspondente. `math.isnan(valor_kappa)` é a forma correta de checar se um número é "NaN", não dá pra usar `== `, porque, curiosamente, `NaN != NaN` sempre em matemática de ponto flutuante (por isso existe uma função própria pra isso).

### Função `montar_texto_do_relatorio` (linhas 141-180)

Essa função só **monta o texto** que vai ser mostrado na tela e salvo em arquivo. Não faz nenhuma conta nova, só organiza os resultados já calculados em frases legíveis.

```python
linhas_do_texto = []
linhas_do_texto.append("=" * 60)
```

`"=" * 60` repete o caractere `=` 60 vezes, criando uma linha divisória (`============...`). A ideia geral da função é ir empilhando linhas de texto numa lista (`linhas_do_texto`) e, no final, juntar tudo com `"\n".join(...)` (a última linha da função), que gruda as linhas com uma quebra de linha entre elas.

O trecho principal que percorre a matriz:

```python
for i in range(len(matriz)):
    qtd_sim, qtd_nao = matriz[i]
    texto_item = "  item " + str(i + 1) + ": Sim=" + str(qtd_sim) + ", Não=" + str(qtd_nao)
    if (i + 1) in itens_sem_variacao:
        texto_item += "  <- todo mundo respondeu igual"
    linhas_do_texto.append(texto_item)
```

- `qtd_sim, qtd_nao = matriz[i]` → "desempacota" a linha da matriz (que é uma lista com 2 números) em duas variáveis separadas de uma vez.
- Monta o texto daquele item concatenando strings com `+` (por isso precisa de `str(...)` em volta dos números, não dá pra somar texto com número direto em Python).
- `if (i + 1) in itens_sem_variacao:` → checa se o número desse item está na lista de itens sem variação (calculada lá na função anterior), e se estiver, adiciona um aviso no final da linha.

No final da função, tem a parte que decide o que escrever sobre o Kappa:

```python
if math.isnan(valor_kappa):
    linhas_do_texto.append("Kappa de Fleiss: NÃO DEU PRA CALCULAR (deu NaN)")
    ...
else:
    linhas_do_texto.append("Kappa de Fleiss: " + str(round(valor_kappa, 4)))
    linhas_do_texto.append("  Interpretação: " + interpretar_kappa(valor_kappa))
```

`round(valor_kappa, 4)` arredonda o número pra 4 casas decimais (ex.: `-0.049999999999999635` vira `-0.05`), só pra ficar mais fácil de ler no relatório.

### Função `salvar_dados_brutos_csv` (linhas 183-216)

Gera o arquivo `.csv` com os dados **originais** (Sim/Não, sem contagem nenhuma) pra você poder importar em outro programa (JASP, R, SPSS) e recalcular o Kappa por fora, como conferência.

```python
cabecalho = ["item"]
for j in range(numero_de_juizes):
    cabecalho.append("Juiz " + str(j + 1))
linhas_csv.append(",".join(cabecalho))
```

Monta a primeira linha do CSV (o cabeçalho): `item,Juiz 1,Juiz 2,Juiz 3,Juiz 4`. `",".join(cabecalho)` pega a lista `["item", "Juiz 1", "Juiz 2", ...]` e gruda tudo separado por vírgula, é assim que um CSV ("comma-separated values", valores separados por vírgula) é escrito.

```python
for i in range(numero_de_itens):
    linha = [str(i + 1)]
    for respostas in respostas_por_juiz:
        linha.append(respostas[i])
    linhas_csv.append(",".join(linha))
```

Pra cada item, monta uma linha: primeiro o número do item, depois a resposta de cada juiz naquele item (`respostas[i]`), e junta tudo com vírgula. O resultado final fica assim:

```
item,Juiz 1,Juiz 2,Juiz 3,Juiz 4
1,Sim,Sim,Sim,Sim
...
13,Não,Sim,Sim,Sim
```

### Função `salvar_relatorio_em_arquivo` (linhas 219-229)

```python
PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
```

Cria a pasta `resultados/` se ela ainda não existir. `parents=True` cria também pastas intermediárias que faltarem, e `exist_ok=True` evita dar erro caso a pasta já exista (sem isso, rodar o script 2 vezes ia quebrar na segunda vez).

```python
agora = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_do_arquivo = "fleiss_kappa_epmr_" + agora + ".txt"
```

`datetime.now()` pega a data/hora atual do computador. `.strftime("%Y%m%d_%H%M%S")` formata isso como texto (ano-mês-dia_hora-minuto-segundo, ex.: `20260807_164144`). Isso é colado no nome do arquivo pra cada execução gerar um arquivo novo, sem apagar o resultado da execução anterior.

```python
caminho_completo.write_text(texto_relatorio, encoding="utf-8")
```

Escreve o texto no arquivo. `encoding="utf-8"` garante que os acentos (ã, é, ç) sejam salvos corretamente.

### Função `main` (linhas 232-273), o "maestro" do script

É a função que **organiza a ordem** em que tudo acontece. Quando você roda `uv run estatistica/fleiss_kappa_epmr.py`, é a `main()` que executa primeiro (por causa das duas últimas linhas do arquivo, explicadas mais abaixo).

```python
if len(sys.argv) > 1:
    caminho_excel = Path(sys.argv[1])
else:
    caminho_excel = ARQUIVO_PADRAO
```

`sys.argv` é a lista de tudo que foi digitado no terminal. `sys.argv[0]` é sempre o nome do próprio script; se a pessoa digitou um caminho de arquivo depois, ele vira `sys.argv[1]`. Então: **se tiver mais de 1 item em `sys.argv`, quer dizer que a pessoa passou um arquivo customizado**, usa ele. Senão, usa o arquivo padrão do projeto.

```python
if not caminho_excel.exists():
    print("Não achei esse arquivo aqui: " + str(caminho_excel))
    sys.exit(1)
```

`.exists()` checa se aquele caminho realmente existe no computador. Se não existir, mostra uma mensagem de erro legível e `sys.exit(1)` **encerra o script imediatamente** (o `1` indica "terminou com erro", por convenção do sistema operacional).

```python
respostas_por_juiz = carregar_arquivo(caminho_excel)
matriz, itens_sem_variacao = montar_matriz_e_achar_empates(respostas_por_juiz)
```

Chama as funções na ordem: primeiro lê o Excel inteiro, depois transforma isso na matriz de contagem.

```python
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    valor_kappa = fleiss_kappa(matriz, method="fleiss")
```

Aqui é onde a conta do Kappa **de verdade** acontece, `fleiss_kappa(matriz, method="fleiss")` é a função pronta da biblioteca `statsmodels`. O resto (`with warnings.catch_warnings()...`) é só pra silenciar um aviso chato (`RuntimeWarning: invalid value encountered in scalar divide`) que o Python mostra quando o cálculo dá uma divisão por zero, isso acontece exatamente no caso de "todo mundo respondeu igual em tudo" (ver seção 5). Não é erro, é só o Python avisando de uma divisão matemática que dá NaN de propósito.

```python
texto_relatorio = montar_texto_do_relatorio(
    matriz, itens_sem_variacao, valor_kappa, len(respostas_por_juiz)
)

print(texto_relatorio)
```

Monta o texto do relatório e imprime na tela.

```python
caminho_salvo = salvar_relatorio_em_arquivo(texto_relatorio)
print("\nRelatório salvo em: " + str(caminho_salvo))

caminho_csv = salvar_dados_brutos_csv(respostas_por_juiz)
print("Dados brutos (pra conferir em outro programa) salvos em: " + str(caminho_csv))
```

Salva o `.txt` e o `.csv` em disco, e avisa na tela onde cada um foi parar.

### Última parte do arquivo

```python
if __name__ == "__main__":
    main()
```

Esse é um "truque" padrão do Python. `__name__` é uma variável especial que vale `"__main__"` **só quando o arquivo é executado diretamente** (tipo `uv run estatistica/fleiss_kappa_epmr.py`). Se esse arquivo fosse importado por outro script (`import fleiss_kappa_epmr`), o `__name__` teria outro valor, e a `main()` **não rodaria sozinha**. Isso é uma boa prática, permite reaproveitar as funções do arquivo em outro lugar sem disparar a execução completa sem querer.

---

## 4. O fluxo completo, resumido

```
main()
 ├─ decide qual arquivo excel usar (padrão ou argumento)
 ├─ confere se o arquivo existe
 ├─ carregar_arquivo()               → abre o excel, lê as 4 abas
 │   └─ ler_respostas_de_um_juiz()   → lê 21 células de uma aba
 │       └─ normalizar_resposta()    → padroniza Sim/Não
 ├─ montar_matriz_e_achar_empates()  → conta Sim/Não por item
 ├─ fleiss_kappa()                   → calcula o Kappa (biblioteca pronta)
 ├─ montar_texto_do_relatorio()      → escreve o relatório em texto
 ├─ salvar_relatorio_em_arquivo()    → salva o .txt
 └─ salvar_dados_brutos_csv()        → salva o .csv
```

---

## 5. Por que o Kappa do RPMS dava "NaN" (situação histórica, antes de 21/08/2026)

> **Atualização (21/08/2026):** depois da regra "Sim + sugestão = Não" (ver
> seção 14), o item 6 do RPMS passou a ter um "Não", então o RPMS deixou de
> ter 100% "Sim" em tudo - o Kappa do RPMS hoje dá um valor real
> (κ = −0,012), não mais `NaN`. A explicação matemática abaixo continua
> válida e didaticamente útil (é exatamente o mecanismo que causava o
> `NaN` antes da regra nova), só não reflete mais o estado atual dos
> dados.

Antes da regra "Sim + sugestão = Não" (seção 14), rodando o script do RPMS os 4 juízes respondiam **"Sim" em todos os 21 itens, sem exceção**. Não existia nenhum "Não" em lugar nenhum da planilha.

Matematicamente, o Kappa de Fleiss é calculado como:

```
Kappa = (concordância observada − concordância esperada ao acaso) / (1 − concordância esperada ao acaso)
```

Quando **só existe uma categoria de resposta** (só "Sim"), a concordância esperada ao acaso é **igual a 1** (100%), porque, se só existe uma opção possível, "escolher ao acaso" também sempre dá nessa mesma opção. Isso faz o denominador da fórmula (`1 − 1 = 0`) virar zero, e **dividir por zero é indefinido**, daí o resultado ser `NaN` ("Not a Number").

**Isso não é um bug do script.** É a fórmula do Kappa se comportando exatamente como devia quando não sobra nenhuma discordância pra medir. O script detecta esse caso (compara se `qtd_sim` ou `qtd_nao` bate com o total de juízes em cada item) e explica isso no relatório, em vez de simplesmente mostrar `nan` sem contexto.

**Ponto pra levar pra apresentação:** isso significa que, com os dados atuais, não é possível calcular um Kappa de Fleiss válido pro RPMS, só dá pra reportar que houve 100% de concordância bruta entre os 4 juízes em todos os itens, mas sem uma medida de "concordância além do acaso" (porque não tem variação suficiente nos dados pra essa medida fazer sentido).

---

## 6. O que muda no `fleiss_kappa_rpms.py` (anonimização)

A lógica de cálculo é **idêntica** à do EPMR (mesmas funções `normalizar_resposta`, `montar_matriz_e_achar_empates`, `interpretar_kappa`, etc). A diferença está em como os juízes são identificados.

**O problema:** no arquivo Excel do RPMS, o nome de cada aba tem o nome real do juiz, por exemplo `"Juiz 3 (Angelo)"`. Além disso, a partir da linha 28 de cada aba tem um bloco com nome completo, idade, país de origem e outras informações pessoais desses juízes. Isso é dado sensível e não pode aparecer em nenhum lugar do relatório ou do CSV gerado.

**A solução, na função `carregar_arquivo`:**

```python
for indice, nome_da_planilha in enumerate(livro.sheetnames, start=1):
    planilha = livro[nome_da_planilha]
    respostas_por_juiz.append(ler_respostas_de_um_juiz(planilha))
```

`enumerate(livro.sheetnames, start=1)` percorre a lista de nomes de abas, mas junto com um número que vai contando 1, 2, 3, 4 (o `start=1` é só pra começar em 1 em vez de 0). A variável `nome_da_planilha` (que tem o nome real, tipo `"Juiz 3 (Angelo)"`) é usada **só nessa linha**, para abrir a aba certa (`livro[nome_da_planilha]`), e depois disso ela nunca mais é usada em nenhuma outra parte do script. O `indice` (1, 2, 3, 4) é o único número que sobrevive e vira `"Juiz 1"`, `"Juiz 2"` etc. nos relatórios e no CSV.

Duas garantias que valem pra esse script inteiro:

1. **Nunca lê além da linha 26**, as constantes `LINHA_COMECO`/`LINHA_FIM` limitam a leitura estritamente ao intervalo dos itens, então o bloco de dados pessoais (linha 28 em diante) nunca chega a ser lido pelo Python.
2. **Nunca imprime ou salva o nome real da aba**, em nenhuma das funções (`montar_texto_do_relatorio`, `salvar_dados_brutos_csv`) o `nome_da_planilha` é usado; elas só recebem `respostas_por_juiz`, que já é uma lista "anônima" (sem nenhum nome junto, só as respostas na ordem 1-2-3-4).

Se um dia você (ou outra pessoa) for mexer nesse script, é importante manter essas duas garantias.

---

## 7. Como rodar (roteiro pra demonstração ao vivo)

```bash
# Kappa de Fleiss
uv run estatistica/fleiss_kappa_epmr.py
uv run estatistica/fleiss_kappa_rpms.py

# CVI + AC1 de Gwet (seção 9-10)
uv run estatistica/cvi_ac1_epmr.py
uv run estatistica/cvi_ac1_rpms.py

# Alpha de Krippendorff (seção 11-12)
uv run estatistica/krippendorff_alpha_epmr.py
uv run estatistica/krippendorff_alpha_rpms.py

# AC1 de Gwet isolado, sem CVI junto (seção 15) - o único que vai no artigo
uv run estatistica/ac1_epmr.py
uv run estatistica/ac1_rpms.py

# rodar apontando pra outro arquivo excel (ex.: uma versão corrigida) -
# funciona nos 8 scripts, passando o caminho como argumento
uv run estatistica/fleiss_kappa_epmr.py "caminho/outro_arquivo.xlsx"
```

Ao rodar `fleiss_kappa_epmr.py` ou `fleiss_kappa_rpms.py`, o script:
1. imprime o relatório completo na tela (contagem por item, itens com concordância total, valor do Kappa e interpretação);
2. salva uma cópia do relatório em `estatistica/resultados/<nome>_<data-hora>.txt`;
3. salva os dados brutos (Sim/Não por item e por juiz) em `estatistica/resultados/dados_brutos_<nome>_<data-hora>.csv`, prontos pra importar no JASP, R ou SPSS como conferência.

Ao rodar `cvi_ac1_epmr.py` ou `cvi_ac1_rpms.py`, o script:
1. imprime o relatório completo na tela (I-CVI por item, S-CVI/Ave, S-CVI/UA, e o AC1 de Gwet com sua interpretação);
2. salva uma cópia do relatório em `estatistica/resultados/cvi_ac1_<nome>_<data-hora>.txt`.

Ao rodar `krippendorff_alpha_epmr.py` ou `krippendorff_alpha_rpms.py`, o script:
1. imprime o relatório completo na tela (matriz de coincidência, discordância observada e esperada, e o Alpha com sua interpretação);
2. salva uma cópia do relatório em `estatistica/resultados/krippendorff_alpha_<nome>_<data-hora>.txt`.

Ao rodar `ac1_epmr.py` ou `ac1_rpms.py`, o script:
1. imprime o relatório completo na tela (contagem por item e o AC1 de Gwet com sua interpretação, sem CVI junto);
2. salva uma cópia do relatório em `estatistica/resultados/ac1_<nome>_<data-hora>.txt`.

(esses seis scripts não geram CSV novo - usam os mesmos dados brutos já exportados pelos scripts de Kappa, seção 3.)

Cada execução gera arquivos novos (com data/hora no nome), então dá pra rodar quantas vezes quiser sem perder o histórico de execuções anteriores.

---

## 8. Perguntas que podem surgir na apresentação

**"Por que usar Python e não fazer direto no Excel/SPSS?"**
Porque o cálculo do Kappa de Fleiss precisa de uma matriz de contagem organizada de um jeito específico, e fazer isso manualmente pra 21 itens × 4 juízes é repetitivo e sujeito a erro de digitação. O script automatiza a leitura da planilha, a contagem e o cálculo, sempre do mesmo jeito.

**"Como eu sei que o cálculo está certo?"**
O script exporta o CSV com os dados brutos (seção 7, item 3) exatamente pra permitir essa conferência: importar os mesmos dados originais numa outra ferramenta (JASP, R, SPSS) e comparar se o Kappa calculado lá bate com o do script.

**"Por que precisou 'esconder' os nomes dos juízes do RPMS?"**
Porque as abas dessa planilha específica têm o nome real dos juízes no próprio nome da aba, e mais informações pessoais nas linhas abaixo dos itens. O script foi construído pra nunca ler nem exibir essas informações, os juízes aparecem só como "Juiz 1" a "Juiz 4", na ordem em que as abas aparecem no arquivo.

**"Por que o Kappa do RPMS dava indefinido (NaN)?"**
Situação histórica, antes de 21/08/2026 (ver seção 5 e seção 14): nos dados de então, todos os 4 juízes tinham respondido "Sim" para os 21 itens, sem nenhuma exceção. Sem nenhuma variação nas respostas, a fórmula do Kappa de Fleiss caía numa divisão por zero matemática, não era erro do script, era assim que a fórmula se comportava quando não sobrava discordância nenhuma pra medir. Depois da regra "Sim + sugestão = Não" (seção 14), o item 6 do RPMS passou a ter um "Não" e o Kappa do RPMS hoje dá um valor real: κ = −0,012.

**"Por que o Kappa do EPMR deu negativo (-0,050) se 17 dos 21 itens tiveram concordância total?"**
Isso é o **paradoxo do kappa** (seção 9), quando a prevalência das respostas é muito desbalanceada (quase tudo "Sim"), a fórmula do Kappa de Fleiss pode dar baixa ou negativa mesmo com concordância bruta alta. Não indica juízes ruins nem erro de cálculo. Por isso foram criados os scripts `cvi_ac1_epmr.py`/`cvi_ac1_rpms.py` (e, depois, `ac1_epmr.py`/`ac1_rpms.py`), que calculam CVI e AC1 de Gwet, medidas que não sofrem desse problema.

**"Então qual número eu reporto no artigo, o Kappa ou o CVI/AC1?"**
Decisão da orientadora (18/08/2026, ver `RESULTADOS_PARA_ARTIGO.md` seção 0): só o **AC1 de Gwet** vai no corpo do artigo, isolado (`ac1_epmr.py`/`ac1_rpms.py`, seção 15) ou junto do CVI como detalhamento (`cvi_ac1_epmr.py`/`cvi_ac1_rpms.py`, seção 9-10). O Kappa de Fleiss e o Alpha de Krippendorff ficam só como documentação técnica, citando o paradoxo do kappa (Feinstein & Cicchetti, 1990) como justificativa de por que não são a medida principal reportada.

**"E o Alpha de Krippendorff, também dá pra usar como medida principal?"**
Não é recomendado como medida principal aqui - ele sofre do mesmo paradoxo do kappa que o Kappa de Fleiss (seção 11), porque também corrige a concordância pela variância das categorias marginais. Com os nossos dados ele dá α ≈ -0,046 no EPMR (bem próximo do Kappa de Fleiss, -0,050) e α ≈ -0,008 no RPMS (também próximo do Kappa, -0,012) - os mesmos resultados problemáticos, não uma solução pro paradoxo. O valor dele serve como **evidência complementar de robustez**: mostra que o resultado baixo do Kappa não foi um acaso de uma fórmula específica, e sim um padrão consistente em toda a família de estatísticas "tipo kappa" (variância-based) diante da nossa prevalência desbalanceada - o que reforça, por exclusão, que o AC1 é a medida certa a reportar como principal.

**"Por que 'Sim + sugestão' virou 'Não'? Isso não é reprovar quem só quis melhorar a redação?"**
Decisão da orientadora (21/08/2026, ver seção 14): aprovar um item com ressalva não é a mesma coisa que concordar que ele está plenamente coerente. Se o juiz sentiu necessidade de sugerir mudança na redação, o item, do jeito que está, não passou no teste sem reserva - então conta como "Não" pra fins de cálculo de concordância, mesmo que a caixinha marcada tenha sido "Sim". A sugestão em si continua registrada na planilha, só a contagem estatística que muda.

---

## 9. Por que criamos `cvi_ac1_epmr.py` e `cvi_ac1_rpms.py` (o paradoxo do kappa)

Depois de rodar o `fleiss_kappa_epmr.py`, o resultado foi **Kappa = -0,050** ("pior que o acaso"), mesmo com **17 dos 21 itens** tendo concordância total entre os 4 juízes (ver seção 1). Isso parece contraditório à primeira vista, mas é um fenômeno conhecido e documentado na literatura de estatística, chamado **paradoxo do kappa** (Feinstein & Cicchetti, 1990).

> **Nota sobre os números:** os valores desta seção já refletem a regra
> "Sim + sugestão = Não" (decisão da orientadora, 21/08/2026 - ver seção
> 14). Antes dessa regra, o Kappa do EPMR era -0,05 com 17 itens de
> concordância total; a lógica matemática explicada abaixo (o paradoxo do
> kappa) é a mesma nos dois casos, só os números mudaram porque os dados
> de entrada mudaram.

**Por que isso acontece:** o Kappa de Fleiss calcula a concordância esperada ao acaso (*Pe*) a partir da soma dos quadrados das proporções de cada categoria de resposta. Quando uma categoria domina muito (no nosso caso, "Sim" aparece em ~93% de todas as respostas), essa *Pe* fica artificialmente alta, perto de 1. Como o Kappa é `(Pa - Pe) / (1 - Pe)`, um *Pe* alto empurra o resultado final pra baixo (ou até negativo), **mesmo que a concordância observada (*Pa*) também esteja alta**. Ou seja: o Kappa está penalizando o desbalanceamento das respostas, não a falta de concordância real entre os juízes.

Isso é agravado por dois fatores presentes nos nossos dados:
1. **Prevalência desbalanceada**, a maioria dos itens é considerada adequada ("Sim") pelos juízes, o que é o resultado *esperado e desejável* numa avaliação de validade de conteúdo bem-sucedida, não um problema.
2. **Amostra pequena**, 4 juízes e 21 itens é um painel pequeno; qualquer estatística do tipo kappa fica estatisticamente instável nesse tamanho, ainda mais quando poucas discordâncias (aqui, 4 itens com 3-1 no EPMR) concentram todo o "sinal" que o kappa usa pra calcular.

**A solução: duas medidas alternativas, calculadas nos novos scripts:**

1. **CVI (Content Validity Index)**. Polit & Beck (2006); Lynn (1986). É o método padrão da literatura de psicometria especificamente pra esse desenho de estudo (painel de juízes avaliando validade de conteúdo item a item, com resposta binária Sim/Não). Não usa nenhuma correção por "acaso" baseada em prevalência, só mede a proporção de juízes que concordou, item por item e na escala como um todo. Não sofre do paradoxo do kappa.
2. **AC1 de Gwet (2008)**, uma estatística "tipo kappa" (também corrigida por concordância ao acaso), mas com uma fórmula de *Pe* diferente, que **foi desenhada especificamente pra não sofrer do paradoxo do kappa** sob prevalência alta. Serve como complemento ao CVI pra quem quer reportar uma medida "corrigida por acaso" mesmo assim.

Rodando os dois scripts novos com os mesmos dados: o EPMR passou a ter **AC1 = 0,895** ("concordância quase perfeita") e **S-CVI/Ave = 0,952**, números que refletem bem melhor o que os dados realmente mostram (concordância alta) do que o Kappa de Fleiss de -0,050.

---

## 10. `cvi_ac1_epmr.py` / `cvi_ac1_rpms.py`, explicação linha por linha (só o que é novo)

Os dois scripts reaproveitam, **sem nenhuma mudança de lógica**, as seguintes partes já explicadas nas seções 3 e 6:

- `normalizar_resposta()`, padroniza Sim/Não (seção 3)
- `ler_respostas_de_um_juiz()`, lê as 21 células da coluna C (seção 3)
- `carregar_arquivo()`, abre o Excel e lê as 4 abas, incluindo a proteção de privacidade do RPMS via `enumerate(livro.sheetnames, start=1)` (seção 6)
- `montar_matriz()`, é a mesma ideia de `montar_matriz_e_achar_empates()` (seção 3), só que sem a parte de rastrear itens sem variação (essa parte não é usada aqui)
- `salvar_relatorio_em_arquivo()`, mesma lógica de salvar `.txt` com data/hora no nome (seção 3)

O que muda são as funções que calculam o **CVI** e o **AC1**, e a função que monta o texto do relatório final.

### `calcular_icvi_por_item` e `calcular_scvi_ave` / `calcular_scvi_ua`

```python
def calcular_icvi_por_item(matriz, numero_de_juizes):
    return [qtd_sim / numero_de_juizes for qtd_sim, qtd_nao in matriz]
```

Pra cada item da matriz (`[qtd_sim, qtd_nao]`), o I-CVI é simplesmente `qtd_sim / numero_de_juizes`, a fração de juízes que marcou "Sim" naquele item. Isso é feito com uma **list comprehension** (a forma compacta `[expressão for item in lista]` de escrever um loop que constrói uma lista nova), rodando uma vez pra cada linha da matriz.

```python
def calcular_scvi_ave(lista_de_icvi):
    return sum(lista_de_icvi) / len(lista_de_icvi)


def calcular_scvi_ua(lista_de_icvi):
    itens_com_acordo_total = sum(1 for icvi in lista_de_icvi if icvi == 1.0)
    return itens_com_acordo_total / len(lista_de_icvi)
```

- `calcular_scvi_ave` é só a **média aritmética** de todos os I-CVI, soma tudo e divide pela quantidade de itens.
- `calcular_scvi_ua` conta quantos itens tiveram I-CVI **exatamente igual a 1,00** (ou seja, os 4 juízes concordaram 100% naquele item) e divide pelo total de itens. `sum(1 for icvi in lista_de_icvi if icvi == 1.0)` é um jeito compacto de "contar quantos elementos satisfazem uma condição": cada vez que a condição é verdadeira, soma-se 1 ao total.

### `icvi_minimo_aceitavel`

```python
def icvi_minimo_aceitavel(numero_de_juizes):
    if numero_de_juizes <= 5:
        return 1.00
    elif numero_de_juizes <= 8:
        return 0.83
    else:
        return 0.78
```

Essa função implementa a **tabela de Lynn (1986)**: quanto menor o painel de juízes, mais alto precisa ser o I-CVI pra ser estatisticamente aceitável (com poucos juízes, uma única discordância já derruba bastante a chance de a concordância não ter sido por acaso). Com os nossos 4 juízes, o critério mínimo é **1,00**, ou seja, qualquer item com pelo menos um "Não" já fica marcado como abaixo do critério no relatório (é o que acontece com os itens 13, 15, 20 e 21 do EPMR).

### `calcular_pa_observada` e `calcular_prevalencia_media`

```python
def calcular_pa_observada(matriz, numero_de_juizes):
    r = numero_de_juizes
    soma = 0.0
    for qtd_sim, qtd_nao in matriz:
        soma += (qtd_sim * (qtd_sim - 1) + qtd_nao * (qtd_nao - 1)) / (r * (r - 1))
    return soma / len(matriz)
```

Essa é a mesma conta de "concordância observada média" (*Pa*) que a fórmula do Kappa de Fleiss já faz internamente (dentro da função pronta `fleiss_kappa()` da biblioteca `statsmodels`), só que aqui ela é escrita na mão, porque o AC1 também precisa desse mesmo número. Pra cada item, `qtd_sim * (qtd_sim - 1) + qtd_nao * (qtd_nao - 1)` conta quantos **pares de juízes concordantes** existem naquele item (fórmula clássica de contagem de pares), dividido pelo total de pares possíveis (`r * (r - 1)`, sem contar um juiz consigo mesmo). No final, tira a média entre todos os itens.

```python
def calcular_prevalencia_media(matriz, numero_de_juizes):
    total_de_sim = sum(qtd_sim for qtd_sim, qtd_nao in matriz)
    total_de_respostas = len(matriz) * numero_de_juizes
    return total_de_sim / total_de_respostas
```

Aqui está a **diferença central** entre o Kappa de Fleiss e o AC1 (seção 9): em vez de usar a soma dos quadrados das proporções por categoria (como o Kappa faz), essa função calcula só a **proporção geral de "Sim"** entre absolutamente todas as respostas dadas (todos os itens, todos os juízes juntos), soma total de "Sim" dividido pelo total de respostas possíveis (`número de itens × número de juízes`).

### `calcular_ac1`

```python
def calcular_ac1(matriz, numero_de_juizes):
    pa = calcular_pa_observada(matriz, numero_de_juizes)
    pi = calcular_prevalencia_media(matriz, numero_de_juizes)

    pe = 2 * pi * (1 - pi)

    if pe == 1:
        return float("nan"), pa, pe

    ac1 = (pa - pe) / (1 - pe)
    return ac1, pa, pe
```

Aplica a fórmula de Gwet (2008) pra 2 categorias: `Pe = 2 * pi * (1 - pi)`. Repare que essa fórmula é bem diferente da usada no Kappa de Fleiss, ela cresce mais devagar quando a prevalência é desbalanceada, e é isso que evita o paradoxo do kappa. Depois, `AC1 = (Pa - Pe) / (1 - Pe)` é exatamente a mesma estrutura de fórmula do Kappa (concordância observada menos esperada, dividido pelo máximo possível de concordância "extra"), só que com esse *Pe* diferente. A checagem `if pe == 1` é só uma proteção matemática (na prática, `2 * pi * (1 - pi)` nunca chega a 1, então esse caso não ocorre com dados reais).

No script do RPMS, tem uma checagem extra (`if pe == 1 or pe == 0`) porque, com 100% de "Sim" em tudo, `pi = 1` e `pe = 2 * 1 * (1 - 1) = 0`. Matematicamente isso não quebra a divisão (`1 - 0 = 1`), mas o resultado do AC1 nesse caso só refletiria `Pa` (que já é 1,00) sem sobrar nenhuma discordância real pra "corrigir por acaso", por isso o script trata esse caso como indefinido e recomenda reportar o CVI em vez disso (seção 9).

### Mudanças em `montar_texto_do_relatorio`

A função monta o relatório final juntando as três partes calculadas: a lista de I-CVI por item (com aviso `<- abaixo do critério mínimo` nos itens que não bateram o corte de `icvi_minimo_aceitavel`), o S-CVI/Ave e S-CVI/UA (cada um com seu critério de referência de Polit, Beck & Owen, 2007, impresso junto no relatório), e por fim o AC1 com sua interpretação (reaproveitando a mesma escala de Landis & Koch já usada pro Kappa, seção 1, a literatura usa essa mesma régua também pro AC1).

---

## 11. Por que criamos `krippendorff_alpha_epmr.py` e `krippendorff_alpha_rpms.py`

**O que é o Alpha de Krippendorff:** é um coeficiente de confiabilidade entre avaliadores criado por Klaus Krippendorff (1980; edições revisadas em 2004 e 2019), considerado na literatura de metodologia o mais **geral** entre todas as medidas de concordância. Diferente do Kappa de Fleiss (que só funciona com dados completos, sem nenhuma avaliação faltando) e do AC1 de Gwet, o Alpha de Krippendorff:

- funciona com **qualquer número de avaliadores** por item (não precisa ser sempre o mesmo número);
- aceita **dado faltante** (um juiz que não avaliou determinado item) sem precisar descartar nada nem imputar valor;
- serve pra **qualquer nível de mensuração** (nominal - o nosso caso, Sim/Não -, ordinal, intervalar ou razão), bastando trocar a função de distância entre categorias.

Por essa reputação de robustez e generalidade, o Alpha de Krippendorff é frequentemente pedido por revisores de artigos científicos como uma segunda medida de confiabilidade, complementar ao Kappa - é por isso que foi adicionado aqui.

**O que os nossos dados não têm variação nenhuma pra usar essas vantagens:** como as planilhas do EPMR e do RPMS têm os 4 juízes avaliando os 21 itens sem nenhum dado faltando, boa parte da flexibilidade do Alpha (lidar com avaliadores desiguais, dado ausente) não é usada aqui - o cálculo cai na versão mais simples da fórmula, baseada numa **matriz de coincidência** (ver seção 12).

**O ponto mais importante pra interpretar o resultado:** o Alpha de Krippendorff (nominal) também corrige a concordância observada pela concordância esperada ao acaso usando a **variância das proporções marginais das categorias** - matematicamente parecido com o que o Kappa de Fleiss faz (a fórmula do Alpha, pra dado nominal sem valor faltando, converge assintoticamente pro Kappa de Fleiss). Isso quer dizer que o Alpha **sofre do mesmo paradoxo do kappa** (seção 9) que o Kappa de Fleiss sofre, pelo mesmo motivo: prevalência de respostas desbalanceada.

Rodando os scripts com os dados reais, isso se confirma:
- **EPMR:** Alpha = **-0,046**, praticamente igual ao Kappa de Fleiss (-0,050), não ao AC1 (0,895) nem ao CVI (0,952).
- **RPMS:** Alpha = **-0,008**, praticamente igual ao Kappa de Fleiss (-0,012), apesar da concordância bruta muito alta entre os avaliadores.

**Por que reportar mesmo assim, se dá o mesmo problema do Kappa:** justamente para reforçar o argumento a favor do CVI/AC1. O Alpha de Krippendorff confirma, com uma fórmula matematicamente diferente do Kappa de Fleiss (baseada em matriz de coincidência, não em proporções por item), que o resultado baixo/indefinido **não é uma peculiaridade de uma fórmula específica** - é um padrão robusto em toda a família de estatísticas corrigidas por variância das marginais, diante da nossa prevalência desbalanceada. Isso torna a escolha do CVI e do AC1 como medidas principais mais defensável no artigo, porque mostra que a alternativa não foi "trocar de fórmula até achar um número bonito", e sim reconhecer uma limitação conhecida e documentada de toda essa família de coeficientes.

---

## 12. `krippendorff_alpha_epmr.py` / `krippendorff_alpha_rpms.py`, explicação linha por linha (só o que é novo)

Os dois scripts reaproveitam, sem nenhuma mudança de lógica, as mesmas funções `normalizar_resposta()`, `ler_respostas_de_um_juiz()`, `carregar_arquivo()` (com a mesma proteção de privacidade no RPMS, seção 6), `montar_matriz()` e `salvar_relatorio_em_arquivo()` já explicadas nas seções 3, 6 e 10. O que é novo são as funções que calculam o Alpha propriamente dito.

### `montar_matriz_de_coincidencia`

```python
def montar_matriz_de_coincidencia(matriz):
    sim_sim = 0
    nao_nao = 0
    sim_nao = 0

    for qtd_sim, qtd_nao in matriz:
        sim_sim += qtd_sim * (qtd_sim - 1)
        nao_nao += qtd_nao * (qtd_nao - 1)
        sim_nao += qtd_sim * qtd_nao

    nao_sim = sim_nao

    return {"sim_sim": sim_sim, "sim_nao": sim_nao, "nao_sim": nao_sim, "nao_nao": nao_nao}
```

Essa é a função central do Alpha de Krippendorff (método padrão de Hayes & Krippendorff, 2007, pra dado nominal sem valor faltando). A ideia: pra cada item, olhar **todos os pares ordenados** de respostas de juízes diferentes (com 4 juízes, isso dá `4 × 3 = 12` pares por item, já que cada juiz é pareado com cada um dos outros 3, nas duas ordens - nunca um juiz consigo mesmo).

- `qtd_sim * (qtd_sim - 1)` conta quantos desses pares são "Sim" com "Sim" (fórmula clássica de contagem de pares ordenados dentro de um grupo de tamanho `qtd_sim`).
- `qtd_nao * (qtd_nao - 1)` conta os pares "Não" com "Não", do mesmo jeito.
- `qtd_sim * qtd_nao` conta os pares onde um juiz disse "Sim" e o outro disse "Não" **numa ordem específica** (ex.: primeiro Sim, depois Não). Como a contagem na ordem contrária (primeiro Não, depois Sim) dá exatamente o mesmo número (`nao_sim = sim_nao`), a função só calcula uma vez e reaproveita.

Isso é somado item por item, e no final vira uma matriz 2×2 (a "matriz de coincidência"), onde cada caixinha representa quantos pares de respostas, somando **todos os itens juntos**, caíram em cada combinação de categorias.

**Exemplo concreto com o EPMR:** dos 17 itens com concordância total (4 Sim, 0 Não), cada um contribui `4 × 3 = 12` pares Sim-Sim. Dos 4 itens com 3 Sim/1 Não (itens 13, 15, 20 e 21), cada um contribui `3 × 2 = 6` pares Sim-Sim, `1 × 0 = 0` pares Não-Não, e `3 × 1 = 3` pares Sim-Não (mais 3 pares Não-Sim). Somando tudo: `sim_sim = 17×12 + 4×6 = 228`, `nao_nao = 0`, `sim_nao = nao_sim = 4×3 = 12`. O total de pares fecha em `228 + 0 + 12 + 12 = 252`, que é exatamente o `n..` que o relatório mostra.

### `calcular_alpha`

```python
def calcular_alpha(coincidencia):
    sim_sim = coincidencia["sim_sim"]
    sim_nao = coincidencia["sim_nao"]
    nao_sim = coincidencia["nao_sim"]
    nao_nao = coincidencia["nao_nao"]

    n_total = sim_sim + sim_nao + nao_sim + nao_nao

    n_sim = sim_sim + sim_nao
    n_nao = nao_nao + nao_sim

    discordancia_observada = (sim_nao + nao_sim) / n_total
    discordancia_esperada = (n_total**2 - (n_sim**2 + n_nao**2)) / (n_total * (n_total - 1))
```

- `n_total` (o `n..` da literatura do Alpha) é a soma de toda a matriz de coincidência - o total de pares avaliáveis. Com 21 itens e 4 juízes, isso sempre dá `21 × 4 × 3 = 252` (número de itens × pares por item).
- `n_sim` e `n_nao` são os totais marginais: quantas vezes a categoria "Sim" (ou "Não") apareceu em algum lado de algum par, somando linha e coluna correspondente da matriz.
- `discordancia_observada` (*Do*) é a fração dos pares que caiu **fora da diagonal** da matriz (Sim-Não ou Não-Sim) - ou seja, pares onde os dois avaliadores realmente discordaram. Quanto mais próximo de 0, melhor (menos discordância).
- `discordancia_esperada` (*De*) usa só os totais marginais (`n_sim`, `n_nao`) pra estimar quanta discordância "aconteceria por acaso" - é essa fórmula, baseada na variância das proporções marginais, que torna o Alpha parecido com o Kappa de Fleiss e sujeito ao mesmo paradoxo (seção 11).

```python
    if discordancia_esperada == 0:
        return float("nan"), discordancia_observada, discordancia_esperada, n_total

    alpha = 1 - (discordancia_observada / discordancia_esperada)
    return alpha, discordancia_observada, discordancia_esperada, n_total
```

`discordancia_esperada == 0` só acontece quando **só existe uma categoria** em todos os pares (por exemplo, o RPMS: só "Sim" em tudo) - nesse caso `n_nao = 0`, e a fórmula de *De* dá zero. Sem isso, a divisão `Do / De` quebraria com um `ZeroDivisionError` em vez de gerar um `NaN` controlado, então a função verifica isso antes e devolve `nan` de propósito (mesma estratégia usada no Kappa de Fleiss, seção 5).

Quando *De* não é zero, `alpha = 1 - (Do / De)` é a fórmula final do Alpha de Krippendorff: **1 menos a razão entre a discordância observada e a esperada ao acaso**. Repare que é estruturalmente parecida com o Kappa (`(Pa - Pe) / (1 - Pe)`), só que expressa em termos de discordância em vez de concordância - por isso os dois valores costumam ficar próximos um do outro nos mesmos dados.

### `interpretar_alpha`

```python
def interpretar_alpha(valor):
    if math.isnan(valor):
        return "indefinido"
    if valor >= 0.800:
        return "confiabilidade adequada para conclusões definitivas (critério de Krippendorff)"
    if valor >= 0.667:
        return "confiabilidade suficiente só para conclusões tentativas/exploratórias (critério de Krippendorff)"
    return "confiabilidade insuficiente, abaixo do critério mínimo de Krippendorff"
```

Diferente da escala de Landis & Koch (1977) usada nos outros scripts, essa função usa o **critério do próprio Krippendorff** (1980, 2004, 2019) - mais rigoroso e específico da literatura de análise de conteúdo: `α ≥ 0,800` pra confiar no resultado com segurança, `α ≥ 0,667` só pra conclusões tentativas/exploratórias, e abaixo disso a confiabilidade é considerada insuficiente pra qualquer conclusão.

---

## 13. `concordancia_traducao.py` e `concordancia_retrotraducao.py` - por que existem e como funcionam

### 13.1 Por que esse método (pedido da orientadora, 18/08/2026)

Esses dois scripts calculam uma coisa **fundamentalmente diferente** dos
outros seis: Kappa/CVI-AC1/Alpha medem concordância entre **juízes
avaliando itens** (cada avaliação é um "Sim" ou "Não" categórico).
Tradução e retrotradução não têm avaliação categórica nenhuma - o que
existe são **várias versões de texto livre** do mesmo item (traduzido
por pessoas diferentes), e o que a orientadora pediu foi uma "avaliação
simples da porcentagem de concordância entre as traduções". Ou seja: uma
medida de o quanto o TEXTO se parece entre as versões, não uma medida de
concordância categórica.

Não existe um coeficiente psicométrico padrão-ouro pra "porcentagem de
concordância entre textos livres" (diferente do Kappa/CVI/AC1/Alpha, que
são métodos publicados e citáveis) - por isso os scripts calculam duas
medidas complementares, as duas bem estabelecidas e fáceis de explicar
num artigo:

1. **% de concordância EXATA** - depois de normalizar (removendo
   diferenças triviais como maiúscula/minúscula, espaço extra e a
   numeração do item), a versão A é *exatamente igual* à versão B?
   Sim/Não por elemento, contado em porcentagem no final. É rígido -
   qualquer troca de uma única palavra já conta como "diferente" - mas é
   exatamente o que "porcentagem de concordância" quer dizer no sentido
   mais literal.
2. **% de similaridade textual** - usando `difflib.SequenceMatcher` (que
   já vem pronto no Python, não precisa instalar nada), calcula um
   percentual de 0 a 100% de o quanto duas strings se parecem, mesmo
   quando não são idênticas. É mais informativo pra tradução livre, onde
   reformular com outras palavras (sem mudar o sentido) é normal e
   esperado, não é "erro" de tradução.

**Isso serve bem pro nosso caso de uso?** Serve como indício textual
rápido e reprodutível, mas com uma limitação importante que o script
deixa explícita no relatório: nem `% exata` nem `% de similaridade`
avaliam SENTIDO - só avaliam o texto literal. Duas traduções podem usar
palavras completamente diferentes e ainda assim preservar o significado
perfeitamente (e isso é o esperado numa boa tradução, não um problema) -
nesse caso a % de concordância dá baixa mesmo a tradução estando
correta. Por isso, principalmente pra retrotradução (onde divergência
textual é ainda mais esperada, por ser uma segunda tradução livre em
cima da primeira), o script recomenda usar a % como indício de quais
itens merecem uma segunda leitura humana, não como veredito automático de
qualidade da tradução.

### 13.2 `concordancia_traducao.py` - fonte dos dados e o que compara

Fonte: `Versão Corrigida dos Tradutores.xlsx` (a versão mais recente do
processo de tradução, já com as 3 versões reconciliadas lado a lado),
aba "RPMS - Tradução e Comparações":

- coluna C = tradução inicial, leiga
- coluna D = tradução especialista
- coluna E = versão final da equipe (geralmente construída em cima de C
  e D, não é uma tradução independente - por isso C×D é a comparação
  "mais pura" entre dois tradutores de verdade; C×E e D×E mostram o
  quanto a versão final se afastou de cada tradução inicial)

Compara 28 elementos (título, instrução, 5 opções de resposta da escala,
e os 21 itens) nos 3 pares possíveis, item a item, e agrega em
porcentagens gerais. `normalizar_texto()` tira espaço invisível (`\xa0`,
que apareceu em alguns itens da planilha), padroniza maiúscula/minúscula
e remove a numeração do item do início do texto (ex.: "6. " ou "8.a ")
antes de comparar - assim a comparação foca no conteúdo da tradução, não
em formatação.

**Resultado (rodado em 18/08/2026):** 46,4% dos 28 elementos têm as 3
versões idênticas; similaridade média geral de 94,3%. Os itens que mais
divergem entre as versões (Item 19, Item 12, Item 4) valem uma segunda
leitura da equipe pra confirmar se a divergência é só estilo ou muda o
sentido.

### 13.3 `concordancia_retrotraducao.py` - fonte dos dados e o detalhe chato dos itens 8/10

Duas fontes:

- **Inglês original de verdade**: `Versão Corrigida dos Tradutores.xlsx`,
  mesma aba - coluna A pro título/instrução/opções de resposta, coluna B
  (rotulada "Original - Inglês") pros 21 itens.
- **Retraduções**: `Retrotradução.xlsx`, abas "Retradução 1" e
  "Retradução 2" (nomeadas na planilha original com o nome de cada
  retradutor, omitido aqui) - coluna B de cada uma ("Retradução para o
  Inglês").

Compara: cada retradução contra o inglês original, e as duas retraduções
entre si. Duas coisas exigiram tratamento especial nessa planilha
(bugs/peculiaridades da fonte, não do script):

1. **Itens 8 e 10 aparecem com duas variantes cada** (8.a/8.b e
   10.a/10.b) só nas abas de retrotradução - parece que a equipe testou
   duas redações diferentes pra esses dois itens nesse processo
   especificamente. O script extrai o número do item a partir do texto
   da coluna A de cada linha (`extrair_chave_do_item()`), em vez de usar
   a posição da linha, exatamente pra lidar com essas linhas extras sem
   quebrar - por isso o N de elementos nas tabelas de retrotradução é 30
   (título+instrução+5 opções+21 itens+2 variantes extras), não 28.
2. **Numeração duplicada**: a planilha rotula o item 16 como "15." por
   engano na coluna A (comparar com a coluna B da mesma linha, que o
   próprio retradutor numerou corretamente como "16."). O script detecta
   automaticamente quando uma chave de item já apareceu antes na mesma
   aba e marca a linha com `⚠ NUMERAÇÃO DUPLICADA NA PLANILHA FONTE` no
   relatório, em vez de comparar silenciosamente contra o item errado -
   **essa linha precisa de conferência manual** antes de entrar em
   qualquer número final do artigo.

**Resultado (rodado em 18/08/2026):** Retradução 1 × Original: 6,7%
idêntico, 69,6% de similaridade média. Retradução 2 × Original: 6,7%
idêntico, 66,4% de similaridade média. Retradução 1 × Retradução 2 (as
duas retraduções entre si, sem envolver o original): 26,7% idêntico,
83,8% de similaridade média - mais alto que contra o original, o que faz
sentido: duas pessoas traduzindo do MESMO português têm mais chance de
convergir entre si do que de reconstruir literalmente o inglês original
que nenhuma delas viu.

---

## 14. Regra "Sim + sugestão = Não" (decisão da orientadora, 21/08/2026)

> **Atenção: o escopo desta regra foi corrigido em 11/09/2026.** Esta
> seção descreve a decisão original e a implementação que valeu entre
> 21/08 e 11/09/2026, mantida aqui como registro histórico do processo.
> A regra vigente reclassifica **um único** caso do estudo (o item 6 do
> RPMS), não qualquer justificativa preenchida. Ver **seção 16** para a
> auditoria que motivou a correção e para a regra atual.

### Por que essa regra existe

Em 18/08/2026, a orientadora perguntou por que a Tabela 1 do RPMS mostrava
100% de concordância - será que o script estava arredondando ou ignorando
um "Não" de algum juiz? Conferência célula a célula confirmou: não havia
bug. No item 6 do RPMS, a Juíza 4 tinha marcado **"Sim"** na coluna de
aprovação, mas deixou um comentário à parte sugerindo mudança na redação
("deslocamento" → "transporte"). Ou seja: ela aprovou o item, só que com
ressalva - e a coluna binária Sim/Não da planilha não tem uma terceira
categoria pra "aprovado com ressalva", então o script, até então,
contava isso como "Sim" puro e simples (ver `RESULTADOS_PARA_ARTIGO.md`,
seção 0.1, pra registro completo da dúvida original).

Em 21/08/2026 a orientadora decidiu: esse tipo de sugestão **conta como
"Não"** daqui pra frente. A lógica por trás: se o juiz sentiu necessidade
de sugerir uma mudança de redação, o item, do jeito que estava escrito
quando ele avaliou, não passou no teste de coerência sem reserva nenhuma
- aprovar com ressalva é categoricamente diferente de concordar
plenamente. A sugestão continua registrada na planilha (ninguém apaga
nada); só a contagem estatística de Sim/Não que passa a refletir essa
distinção.

### Quais itens mudaram

Conferindo célula a célula as duas planilhas (coluna C = resposta, coluna
D = justificativa/sugestão) depois da decisão, os itens que têm "Sim" na
coluna C **e** algum texto na coluna D, e por isso viram "Não" pro
cálculo:

**EPMR** (5 itens mudam):
- Juiz 1 / item 4, sugeriu trocar "racista" por "inadequado"/"ruins"
- Juiz 1 / item 17, sugeriu trocar "status social" por "condições sociais"
- Juiz 4 / item 5, comentário sobre sotaque
- Juiz 4 / item 8, comentário sobre acesso a oportunidades de trabalho
- Juiz 4 / item 10, comentário sobre envio de dinheiro ao país de origem

**RPMS** (1 item muda):
- Juiz 4 / item 6, o item que gerou a dúvida original (seção acima)

(itens que já eram "Não" com justificativa, como os itens 13/15/20/21 do
EPMR no Juiz 1/Juiz 4, **não mudam** - a regra só afeta "Sim" com
sugestão; "Não" com justificativa já era "Não".)

### Onde a regra foi implementada

A mesma lógica foi replicada, idêntica, em **todos os 8 scripts de
cálculo** (o padrão de leitura da planilha já era duplicado entre eles
antes dessa mudança - ver seção 2 - então a correção seguiu o mesmo
padrão em vez de introduzir uma dependência compartilhada nova):
`fleiss_kappa_epmr.py`, `fleiss_kappa_rpms.py`,
`krippendorff_alpha_epmr.py`, `krippendorff_alpha_rpms.py`,
`cvi_ac1_epmr.py`, `cvi_ac1_rpms.py`, `ac1_epmr.py`, `ac1_rpms.py`. Em
cada um, a função `ler_respostas_de_um_juiz` passou a ler também a coluna
D (`COLUNA_JUSTIFICATIVA = 4`) e, se a resposta normalizada for "Sim" e
essa célula não estiver vazia, troca a resposta final pra "Não":

```python
def ler_respostas_de_um_juiz(planilha):
    respostas = []
    for linha in range(LINHA_COMECO, LINHA_FIM + 1):
        valor_da_celula = planilha.cell(row=linha, column=COLUNA_RESPOSTA).value
        resposta = normalizar_resposta(valor_da_celula)

        valor_da_justificativa = planilha.cell(row=linha, column=COLUNA_JUSTIFICATIVA).value
        if resposta == "Sim" and valor_da_justificativa is not None and str(valor_da_justificativa).strip() != "":
            resposta = "Não"

        respostas.append(resposta)
    return respostas
```

### Impacto nos resultados

Como a regra muda os dados de entrada, **todos** os coeficientes mudaram
de valor (não só o AC1/CVI do RPMS, que foi o gatilho da dúvida) -
comparação completa em `RESULTADOS_PARA_ARTIGO.md`, seção 0. Resumo:

| Instrumento | Kappa (antes → depois) | Alpha (antes → depois) | AC1 (antes → depois) |
|---|---|---|---|
| EPMR | −0,05 → −0,120 | −0,046 → −0,116 | 0,90 → 0,735 |
| RPMS | indefinido → −0,012 | indefinido → −0,008 | indefinido → 0,976 |

O padrão geral se mantém: Kappa e Alpha continuam baixos/negativos pelo
mesmo motivo de sempre (paradoxo do kappa, seção 9), e o AC1 continua
sendo a medida que melhor reflete a concordância real - só que agora
calculável também no RPMS, porque a regra nova introduziu variação real
nos dados onde antes não havia nenhuma.

---

## 15. `ac1_epmr.py` / `ac1_rpms.py`, explicação linha por linha (só o que é novo)

Pedido explícito da orientadora em 21/08/2026: um produto com **só** o
AC1 de Gwet, sem o CVI ao lado (que já existe combinado em
`cvi_ac1_epmr.py`/`cvi_ac1_rpms.py`, seções 9-10) - já que o AC1 isolado
é o único coeficiente que vai pro corpo do artigo
(`RESULTADOS_PARA_ARTIGO.md`, seção 0).

Esses dois scripts são basicamente `cvi_ac1_epmr.py`/`cvi_ac1_rpms.py`
**menos** as funções de CVI (`calcular_icvi_por_item`,
`calcular_scvi_ave`, `calcular_scvi_ua`, `icvi_minimo_aceitavel`) e menos
as linhas do relatório/figura que mostravam I-CVI/S-CVI. Tudo o mais é
idêntico:

- Mesma leitura de planilha (`normalizar_resposta`,
  `ler_respostas_de_um_juiz`, `carregar_arquivo`), já com a regra "Sim +
  sugestão = Não" da seção 14.
- Mesmas funções de cálculo do AC1: `calcular_pa_observada`,
  `calcular_prevalencia_media`, `calcular_ac1`,
  `interpretar_forca_concordancia` (idênticas às de
  `cvi_ac1_epmr.py`/`cvi_ac1_rpms.py` - ver seção 10 pra explicação linha
  por linha dessas funções, não repetida aqui).
- Mesmo padrão de saída: `.txt` + `.png` + `.html` com timestamp
  compartilhado em `estatistica/resultados/`, prefixados `ac1_epmr_` e
  `ac1_rpms_`.

A única diferença de conteúdo é o relatório e a tabela-resumo terem só
quatro colunas (`Itens (N)`, `Avaliadores`, `AC1 de Gwet`,
`Interpretação`) em vez das seis que `cvi_ac1_*.py` mostra - sem
S-CVI/Ave nem S-CVI/UA. `ac1_rpms.py` mantém a mesma disciplina de
anonimização dos outros scripts do RPMS (seção 6): os juízes aparecem só
como "Juiz 1" a "Juiz 4", nunca com o nome real da aba.

---

## 16. Correção de escopo da regra "Sim + sugestão" (11/09/2026)

### Por que essa correção foi necessária

O pôster apresentado no congresso reporta AC1 = 0,90 para o painel de
juízes especialistas e AC1 = 0,97 para o painel da população-alvo. Os
scripts, depois da implementação da regra descrita na seção 14, passaram
a produzir AC1 = 0,735 e AC1 = 0,976. O segundo bate com o pôster, o
primeiro não. Como os dois números iam para o artigo, a divergência
precisava ser resolvida antes de qualquer publicação ou de subir os
scripts para o repositório público.

A auditoria feita em 11/09/2026 leu as duas planilhas célula a célula e
reconstruiu o cálculo sob cada interpretação possível dos dados brutos.
O resultado está abaixo.

### O que a auditoria encontrou

No painel de **juízes especialistas** (EPMR), a coluna binária (coluna C)
tem quatro "Não" explícitos:

| Item | Juiz | Trecho do comentário |
|---|---|---|
| 13 | Juiz 1 | "Me parece que faz parte do desenvolvimento humano e maturidade [...] Está muito ampla a questão" |
| 15 | Juiz 1 | "É redundante, e óbvio, a não ser que a pessoa não goste de seus familiares" |
| 20 | Juiz 4 | "Questões muito pessoais os refugiados não gostam de dar resposta" |
| 21 | Juiz 4 | "Questões muito pessoais os refugiados não gostam de dar resposta" |

E tem outros cinco itens marcados "Sim" com comentário na coluna D:

| Item | Juiz | Trecho do comentário |
|---|---|---|
| 4 | Juiz 1 | "Talvez trocaria a palavra 'racista' por 'inadequado' ou 'ruins'" |
| 5 | Juiz 4 | "Obs: falar sobre sotaque" |
| 8 | Juiz 4 | "Obs: falar sobre acesso a oportunidades de trabalho de acordo com a formação do refugiado" |
| 10 | Juiz 4 | "...E o envio de dinheiro ao país de origem" |
| 17 | Juiz 1 | "Talvez trocar 'status social' por 'condições sociais'" |

No painel da **população-alvo** (RPMS) não há nenhum "Não" explícito, só
a ressalva do item 6 (Juiz 4): "a palavra deslocamento não é muito
entendível pela maioria dos estrangeiros".

### Os três cenários, calculados

| Cenário | EPMR | RPMS |
|---|---|---|
| A. Nenhuma ressalva vira "Não" (dado bruto puro) | Pa = 0,905; Pe = 0,091; **AC1 = 0,895** | Pa = 1; Pe = 0; **AC1 indefinido** |
| B. Só uma ressalva vira "Não" | Pa = 0,881; Pe = 0,112; AC1 = 0,866 | Pa = 0,976; Pe = 0,024; **AC1 = 0,976** |
| C. Todas as ressalvas viram "Não" (implementação de 21/08) | Pa = 0,786; Pe = 0,191; AC1 = 0,735 | igual ao cenário B (só existe uma) |

O 0,90 do pôster é o **cenário A** do EPMR (0,8953, arredondado). O 0,97
do pôster é o **cenário B** do RPMS (0,9756). Ou seja: o pôster aplicou a
reclassificação em exatamente **um** caso do estudo inteiro, o item 6 do
RPMS, que foi justamente o caso que originou a discussão com a
orientadora em 18/08. Isso confirma o relato dela de que apenas um "Sim"
com sugestão virou "Não".

Repare que no RPMS a reclassificação não era opcional: sem ela o painel
tem unanimidade absoluta, o que zera a variância, faz Pe = 0 e deixa o
AC1 matematicamente indefinido. Não existia número para reportar.

### Por que o cenário A é o correto para o EPMR

A distinção não é conveniência para bater com o pôster, é de conteúdo.
Comparando os textos das duas tabelas acima, as cinco ressalvas do
cenário C são de natureza diferente das quatro reprovações:

- As reprovações **contestam o item**: dizem que ele é redundante, amplo
  demais ou inadequado de perguntar àquela população.
- As cinco ressalvas **propõem melhorar um item que o juiz já aprovou**:
  acrescentar o sotaque, acrescentar o envio de remessas, trocar uma
  palavra por sinônimo mais claro. A linguagem é hedge pura ("talvez
  trocaria", "Obs:", "...e também").

Contar as duas coisas como a mesma coisa faz o coeficiente medir **volume
de comentários** em vez de acordo sobre a adequação dos itens. Um juiz
generoso, que escreve sugestões em muitos itens que aprovou, derrubaria
artificialmente a concordância do painel. Foi exatamente o que aconteceu:
o Juiz 4 do EPMR comentou em três itens aprovados e o Juiz 1 em dois, e
esses cinco comentários sozinhos derrubaram o AC1 de 0,895 para 0,735.

O item 6 do RPMS é o caso oposto: a respondente relata que **não entende
a palavra do enunciado**. Isso é falha do item em cumprir sua função,
não sugestão de aprimoramento, e num painel de população-alvo é
justamente o tipo de achado que a etapa existe para capturar.

### O que mudou no código

Os oito scripts tinham esse bloco dentro de `ler_respostas_de_um_juiz`:

```python
valor_da_justificativa = planilha.cell(row=linha, column=COLUNA_JUSTIFICATIVA).value
if resposta == "Sim" and valor_da_justificativa is not None and str(valor_da_justificativa).strip() != "":
    # aprovou com ressalva - conta como "Nao" (ver regra no cabecalho)
    resposta = "Não"
```

O problema é que a condição dispara em **qualquer** célula preenchida.
A regra ficava implícita no dado, invisível em code review, e mudava
silenciosamente de resultado se alguém digitasse qualquer coisa na
coluna D. Foi substituído por:

```python
numero_do_item = linha - LINHA_COMECO + 1
valor_da_justificativa = planilha.cell(row=linha, column=COLUNA_JUSTIFICATIVA).value
tem_ressalva = valor_da_justificativa is not None and str(valor_da_justificativa).strip() != ""
if resposta == "Sim" and tem_ressalva and numero_do_item in ITENS_COM_RESSALVA_RECLASSIFICADA:
    # ressalva reclassificada como discordancia (ver regra no cabecalho)
    resposta = "Não"
```

E a constante, declarada no topo de cada script junto das outras, com a
justificativa por escrito:

- Nos quatro scripts do EPMR: `ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset()`
- Nos quatro scripts do RPMS: `ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset({6})`

Agora a decisão metodológica está declarada em um lugar só, por
instrumento, e qualquer pessoa que abra o script vê imediatamente quais
itens foram reclassificados e por quê. Se a orientadora quiser rever a
decisão, muda a constante e roda de novo, sem mexer na lógica.

### Impacto nos números

| Coeficiente | Antes (cenário C) | Depois (cenário A/B) |
|---|---|---|
| EPMR, AC1 de Gwet | 0,735 | **0,895** |
| EPMR, S-CVI/Ave | 0,893 | **0,952** |
| EPMR, S-CVI/UA | 0,571 | **0,810** |
| EPMR, Kappa de Fleiss | −0,120 | **−0,050** |
| EPMR, Alpha de Krippendorff | −0,116 | **−0,046** |
| EPMR, itens com I-CVI = 0,75 | 9 itens | **4 itens** (13, 15, 20, 21) |
| RPMS, todos os coeficientes | sem mudança | sem mudança |

Vale notar que o EPMR passou a atender os dois critérios de Polit, Beck e
Owen (2007) para validade de conteúdo em nível de escala (S-CVI/Ave ≥
0,90 e S-CVI/UA ≥ 0,80), o que não acontecia sob o cenário C. O Kappa e
o Alpha continuam negativos nos dois instrumentos, então a conclusão da
seção 9 sobre o paradoxo do kappa permanece válida e o AC1 continua sendo
o coeficiente correto a reportar.
