# Codebook: Dados Brutos (EPMR e RPMS)

Autor: Guilherme Lacerda de Avila

Dicionário de dados para `dados/avaliacao_epmr.csv` e
`dados/avaliacao_rpms.csv`. Descreve o que cada arquivo, coluna e valor
significa, para permitir reuso e reanálise independente dos dados (boas
práticas de open science; FAIR: dado sem documentação não é realmente
reutilizável).

## O que esses dados são (e o que não são)

Os dois arquivos contêm o julgamento de **validade de conteúdo** de um
painel de 4 juízes sobre os 21 itens da *Refugee Post-Migration Stress
Scale* (RPMS), adaptada para o português/contexto brasileiro. Cada juiz
respondeu **Sim** (item adequado/aprovado) ou **Não** (item
inadequado/reprovado) para cada um dos 21 itens.

- `dados/avaliacao_epmr.csv` → painel de **juízes especialistas** (EPMR)
- `dados/avaliacao_rpms.csv` → painel de **juízes não especialistas**, os
  próprios refugiados que avaliaram os itens (RPMS)

**Isso não são respostas de participantes à escala em si** (não é o
RPMS sendo aplicado para medir estresse pós-migratório em alguém), é a
etapa de **validação de conteúdo** do instrumento, anterior à aplicação.

## Estrutura do arquivo (CSV)

Uma linha por resposta, ou seja, uma linha para cada combinação de item e
juiz. São 84 linhas por arquivo (21 itens × 4 juízes), mais o cabeçalho.
Exemplo, com uma resposta sem ressalva e uma com:

```csv
item,juiz,resposta,tem_ressalva,ressalva
1,1,Sim,0,
17,1,Sim,1,"Talvez trocar ""status social"" por ""condições sociais"""
```

| Coluna | Tipo | Significado |
|---|---|---|
| `item` | inteiro, 1 a 21 | Número do item da escala (ver tabela de itens abaixo) |
| `juiz` | inteiro, 1 a 4 | Identificador sequencial do avaliador |
| `resposta` | `Sim` ou `Não` | O que o juiz marcou na coluna binária da planilha, sem nenhuma alteração |
| `tem_ressalva` | 0 ou 1 | `1` se o juiz escreveu algo no campo de justificativa |
| `ressalva` | texto livre | O que ele escreveu, quando escreveu. Vazio caso contrário |

O campo `resposta` é sempre a marcação literal da planilha. **Nenhuma
reclassificação foi aplicada ao dado publicado**: os arquivos trazem o
registro cru, e a regra de codificação é aplicada em tempo de execução
pelos scripts. Isso é deliberado, para que qualquer pessoa possa aplicar
uma regra diferente e ver o efeito.

## A regra de codificação das ressalvas

Em nove respostas do painel de especialistas e uma do painel da
população-alvo o juiz escreveu algo no campo de justificativa. Essas
anotações não são todas da mesma natureza, e recebem tratamento
diferente no cálculo:

- **Sugestão de aprimoramento de um item aprovado**, do tipo "talvez
  trocar 'status social' por 'condições sociais'" ou "Obs: falar sobre
  sotaque". O juiz não contesta o item, propõe melhorá-lo. Conta como
  concordância, porque foi isso que ele respondeu. Ocorre nos itens 4, 5,
  8, 10 e 17 do EPMR, junto de respostas "Sim", e nos itens 13, 15, 20 e
  21, junto de respostas "Não", onde apenas detalham a reprovação.
- **Ressalva que aponta falha no item como está redigido.** Ocorre uma
  única vez em todo o estudo, no **item 6 do RPMS**, em que a juíza 4
  registrou que a palavra "deslocamento" não é compreendida pela maioria
  dos estrangeiros. Conta como discordância, porque o item não cumpriu
  sua função com aquela respondente, ainda que a marcação na coluna
  binária tenha sido "Sim".

A decisão está declarada na constante `ITENS_COM_RESSALVA_RECLASSIFICADA`,
no topo de cada script de cálculo: vazia nos scripts do EPMR, igual a
`{6}` nos scripts do RPMS. Para reproduzir a análise sob outra regra,
basta alterar essa constante e rodar de novo. A justificativa completa da
escolha está em `EXPLICACAO.md`, seção 16, e o efeito de cada
configuração está tabelado no `README.md`.

## Anonimização dos juízes

`Juiz 1`–`Juiz 4` são identificadores **sequenciais, na ordem em que as
abas aparecem na planilha original**, não correspondem a nomes reais,
idade, país de origem ou qualquer outro dado pessoal. Essa
correspondência (qual juiz é "Juiz 3", por exemplo) só existe na
planilha Excel original, que **não é publicada** por conter dados
pessoais dos avaliadores (nome completo, idade, país de origem —
especialmente sensível no caso do RPMS, cujos avaliadores não
especialistas são refugiados). Ver `EXPLICACAO.md`, seção 6, para os
detalhes de como essa anonimização é aplicada no código.

Não há garantia de que "Juiz 1" no arquivo do EPMR seja a mesma pessoa
que "Juiz 1" no arquivo do RPMS, são dois painéis diferentes.

## Itens da escala (mesmo texto nos dois instrumentos)

| Item | Enunciado |
|---|---|
| 1 | Discriminação por autoridades brasileiras |
| 2 | Discriminação na escola ou no trabalho |
| 3 | Me sinto desrespeitado por causa das minhas origens |
| 4 | Pessoas fazendo comentários racistas sobre mim |
| 5 | Dificuldades na comunicação em português que me incomodam |
| 6 | Dificuldades de compreender como atividades cotidianas no Brasil funcionam (compras, acesso a serviços, deslocamentos, etc.) |
| 7 | Dificuldade de compreender documentos e formulários das autoridades |
| 8 | Preocupação com a situação financeira instável |
| 9 | Frustração por não conseguir me sustentar financeiramente |
| 10 | Preocupação com dívidas |
| 11 | Sinto falta do meu país de origem |
| 12 | Sinto falta da vida social no meu país de origem |
| 13 | Sinto falta de atividades que eu fazia antes de vir para o Brasil |
| 14 | Preocupação com familiares dos quais estou separado |
| 15 | Tristeza por não estar reunido com meus familiares |
| 16 | Sentir-me excluído ou isolado da sociedade brasileira |
| 17 | Frustração devido à perda de status social no Brasil |
| 18 | Frustração por não conseguir exercer minhas competências no Brasil |
| 19 | Conflitos angustiantes na minha família |
| 20 | Sentir-me desrespeitado na minha família |
| 21 | Sentir-me sem importância na minha família |

Enunciado completo apresentado aos juízes: *"Por favor indique com que
frequência você vivencia cada uma das seguintes situações no Brasil."*
seguido de cada item acima, os juízes avaliaram se **esse enunciado**
(clareza, relevância, pertinência ao construto) estava adequado, não a
frequência em si.

## Valores ausentes

Não há valores ausentes nos arquivos publicados, todos os 4 juízes
responderam todos os 21 itens nos dois instrumentos. Se uma reexecução
futura dos scripts (`fleiss_kappa_epmr.py` / `fleiss_kappa_rpms.py`)
encontrar uma célula vazia na planilha original, o script **para com
erro** em vez de gerar uma linha incompleta silenciosamente (ver
`normalizar_resposta()` em `EXPLICACAO.md`, seção 3).

## Como os dados foram gerados

Extraídos programaticamente da planilha Excel original (colunas C,
linhas 6–26 de cada aba/juiz) pelos scripts `fleiss_kappa_epmr.py` e
`fleiss_kappa_rpms.py`, ver código-fonte e `EXPLICACAO.md` (seções 1–6)
para o processo completo, incluindo normalização de texto (`"Sim"`,
`"sim"`, `"SIM"` tratados como equivalentes) e a proteção de privacidade
aplicada na leitura do RPMS.

## Uso pretendido / licença

Estes dados fazem parte de um estudo de Iniciação Científica em
andamento (adaptação transcultural do RPMS). Publicados aqui como
material de apoio para a orientadora e para revisão, **licença de uso
ainda não definida formalmente**; não redistribuir sem confirmar com os
autores.

## Como citar os coeficientes calculados a partir desses dados

Ver `RESULTADOS_PARA_ARTIGO.md` para o texto, tabelas e referências
completas dos coeficientes de confiabilidade (AC1 de Gwet, Kappa de
Fleiss, Alpha de Krippendorff) calculados sobre estes dados brutos.
