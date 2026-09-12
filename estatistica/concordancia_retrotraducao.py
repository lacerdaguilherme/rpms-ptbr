# concordancia_retrotraducao.py
# Autor: Guilherme Lacerda de Avila
#
# Script pra calcular a PORCENTAGEM DE CONCORDÂNCIA entre a retrotradução
# e o original em inglês do RPMS - pedido da orientadora (18/08/2026).
#
# Ver concordancia_traducao.py pra explicação completa do que é
# "concordância exata" e "similaridade" (mesmo conceito, mesma fórmula -
# aqui só muda a fonte dos dados e o que está sendo comparado).
#
# ATENÇÃO - retrotradução é um teste DIFERENTE do de tradução direta: a
# ideia é pegar a versão final em português, mandar pra alguém que nunca
# viu o inglês original traduzir DE VOLTA pro inglês, e comparar esse
# "inglês reconstruído" com o inglês original de verdade. Quanto mais
# parecido, mais evidência de que a tradução em português preservou o
# significado original. Por ser tradução livre de um texto pra outro
# idioma, NÃO é esperado bater palavra por palavra - divergência de
# texto aqui é normal, o que importa é preservar o sentido (e comparar
# sentido é coisa que só um humano lendo os dois textos consegue
# realmente avaliar - o percentual de similaridade aqui é só um indício
# textual, não substitui a revisão humana das divergências).
#
# Fontes dos dados (dois arquivos diferentes):
#   1) "Versão Corrigida dos Tradutores.xlsx", aba "RPMS - Tradução e
#      Comparações" - de onde tiramos o INGLÊS ORIGINAL de verdade
#      (coluna A pro título/instrução/opções de resposta; coluna B pros
#      21 itens, que tem uma coluna extra "Original - Inglês" só pra
#      eles).
#   2) "Retrotradução.xlsx", abas cujo nome começa com "Retradução 1" e
#      "Retradução 2" (o nome completo da aba tem, depois disso, o nome
#      de cada retradutor - dado pessoal que este script não reproduz;
#      a busca por prefixo abaixo dispensa saber esse nome) - de onde
#      tiramos o inglês RECONSTRUÍDO por cada um dos dois retradutores
#      (coluna B de cada aba).
#
# Detalhe chato dos dados: nas abas de retrotradução, os itens 8 e 10
# aparecem SUBDIVIDIDOS em duas variantes cada (8.a/8.b e 10.a/10.b) -
# parece que a equipe testou duas redações diferentes desses itens na
# retrotradução. O script trata "8.a" e "8.b" como retraduções
# independentes do mesmo item original 8 (mesma coisa pro item 10),
# então na tabela por elemento aparecem 23 linhas no total (21 itens + as
# 2 variantes extras), não 21.
#
# Como rodar:
#   uv run estatistica/concordancia_retrotraducao.py

import re
import sys
import textwrap
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

import matplotlib
import openpyxl

matplotlib.use("Agg")  # backend sem tela, so pra salvar arquivo de imagem direto
import matplotlib.pyplot as plt  # noqa: E402 (precisa vir depois do matplotlib.use)

ARQUIVO_ORIGINAL = "Versão Corrigida dos Tradutores.xlsx"
ABA_ORIGINAL = "RPMS - Tradução e Comparações"
LINHA_TITULO = 2
LINHA_INSTRUCAO = 3
LINHA_ESCALA_INICIO = 4
LINHA_ESCALA_FIM = 8
LINHA_ITENS_INICIO = 9
LINHA_ITENS_FIM = 29
COLUNA_ORIGINAL_ESCALA = 1  # A - titulo/instrucao/opcoes de resposta em ingles
COLUNA_ORIGINAL_ITENS = 2  # B - "Original - Ingles" so pros 21 itens
COLUNA_NUMERO_ITEM = 1  # A - numero do item (1.0, 2.0, ...), so nas linhas de item

ARQUIVO_RETROTRADUCAO = "Retrotradução.xlsx"
# Prefixos, não nomes completos: a aba real tem, depois do prefixo, o
# nome do retradutor (dado pessoal, não reproduzido aqui). A busca por
# prefixo em _achar_aba() localiza a aba certa sem precisar desse nome,
# e tolera o espaço sobrando no início do nome de uma das abas.
ABAS_RETROTRADUCAO = {
    "Retradução 1": "Retradução 1",
    "Retradução 2": "Retradução 2",
}


def _achar_aba(livro, prefixo):
    """Acha, em `livro`, a aba cujo nome (ignorando espaços nas pontas)
    começa com `prefixo`. Lança erro claro se não achar nenhuma ou achar
    mais de uma, em vez de deixar o KeyError genérico do openpyxl.
    """
    candidatas = [nome for nome in livro.sheetnames if nome.strip().startswith(prefixo)]
    if not candidatas:
        raise KeyError(f"nenhuma aba começando com {prefixo!r}; abas disponíveis: {livro.sheetnames}")
    if len(candidatas) > 1:
        raise KeyError(f"mais de uma aba começando com {prefixo!r}: {candidatas}")
    return livro[candidatas[0]]
COLUNA_RETROTRADUCAO = 2  # B - "Retradução para o Inglês"

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
PASTA_PROJETO = PASTA_DO_SCRIPT.parent
PASTA_RESULTADOS = PASTA_DO_SCRIPT / "resultados"


def normalizar_texto(texto):
    # ver concordancia_traducao.py pra explicacao completa dessa funcao
    if texto is None:
        return ""

    texto = str(texto).replace("\xa0", " ").strip().lower()
    texto = re.sub(r"^\d+\s*\.?\s*[a-z]?\s*\.?\s*", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def calcular_similaridade(texto_a, texto_b):
    return SequenceMatcher(None, texto_a, texto_b).ratio() * 100


def extrair_chave_do_item(texto):
    """
    Pega o numero (e a letra a/b, se tiver) do comeco do texto de um
    item, tipo "8.a Preocupacao..." -> "8a", "21. Sentir-me..." -> "21".
    Isso serve pra saber com qual item ORIGINAL (que nao tem variante
    a/b) cada linha de retrotraducao deve ser comparada.
    """
    if texto is None:
        return None

    correspondencia = re.match(r"^\s*(\d+)\s*\.?\s*([ab])?", str(texto))
    if not correspondencia:
        return None

    numero = correspondencia.group(1)
    sufixo = correspondencia.group(2) or ""

    return numero + sufixo


def numero_base(chave):
    # tira a letra a/b do final da chave, pra achar o item original
    # correspondente (que nao tem variante) - "8a" -> "8", "21" -> "21"
    return re.sub(r"[ab]$", "", chave)


def carregar_original_ingles(caminho_projeto):
    """
    Monta um dicionario com o texto original em ingles de cada elemento:
    chaves fixas ("titulo", "instrucao", "escala_1".."escala_5") pro
    cabecalho da escala, e chaves numericas ("1", "2", ..., "21") pros
    itens.
    """
    caminho_excel = caminho_projeto / ARQUIVO_ORIGINAL
    livro = openpyxl.load_workbook(caminho_excel, data_only=True)
    planilha = livro[ABA_ORIGINAL]

    original = {}

    original["titulo"] = planilha.cell(row=LINHA_TITULO, column=COLUNA_ORIGINAL_ESCALA).value
    original["instrucao"] = planilha.cell(row=LINHA_INSTRUCAO, column=COLUNA_ORIGINAL_ESCALA).value

    for linha in range(LINHA_ESCALA_INICIO, LINHA_ESCALA_FIM + 1):
        indice = linha - LINHA_ESCALA_INICIO + 1
        original["escala_" + str(indice)] = planilha.cell(row=linha, column=COLUNA_ORIGINAL_ESCALA).value

    for linha in range(LINHA_ITENS_INICIO, LINHA_ITENS_FIM + 1):
        numero_cel = planilha.cell(row=linha, column=COLUNA_NUMERO_ITEM).value
        texto_original = planilha.cell(row=linha, column=COLUNA_ORIGINAL_ITENS).value
        if numero_cel is None:
            continue
        chave = str(int(round(float(numero_cel))))
        original[chave] = texto_original

    return original


def carregar_retrotraducoes(caminho_projeto):
    """
    Monta, pra cada retradutor, uma lista de elementos com rotulo,
    chave (pra casar com o dicionario do original) e o texto
    retraduzido.
    """
    caminho_excel = caminho_projeto / ARQUIVO_RETROTRADUCAO
    livro = openpyxl.load_workbook(caminho_excel, data_only=True)

    retrotraducoes = {}

    for nome_curto, prefixo_aba in ABAS_RETROTRADUCAO.items():
        planilha = _achar_aba(livro, prefixo_aba)
        elementos = []

        elementos.append(
            {"rotulo": "Título da escala", "chave": "titulo", "texto": planilha.cell(row=LINHA_TITULO, column=COLUNA_RETROTRADUCAO).value}
        )
        elementos.append(
            {"rotulo": "Instrução", "chave": "instrucao", "texto": planilha.cell(row=LINHA_INSTRUCAO, column=COLUNA_RETROTRADUCAO).value}
        )
        for linha in range(LINHA_ESCALA_INICIO, LINHA_ESCALA_FIM + 1):
            indice = linha - LINHA_ESCALA_INICIO + 1
            elementos.append(
                {
                    "rotulo": "Opção de resposta " + str(indice),
                    "chave": "escala_" + str(indice),
                    "texto": planilha.cell(row=linha, column=COLUNA_RETROTRADUCAO).value,
                }
            )

        # os itens nao tem linha fixa aqui porque 8 e 10 tem variantes
        # a/b que empurram as linhas seguintes pra baixo - por isso leio
        # a coluna A (que tem o rotulo em portugues, tipo "8.a ...") pra
        # descobrir a chave de cada linha, em vez de usar a posicao
        chaves_ja_vistas = set()
        linha = LINHA_ITENS_INICIO
        while True:
            rotulo_em_portugues = planilha.cell(row=linha, column=1).value
            if rotulo_em_portugues is None:
                break
            chave = extrair_chave_do_item(rotulo_em_portugues)
            if chave is None:
                break

            rotulo_final = "Item " + chave
            if chave in chaves_ja_vistas:
                # a planilha fonte repete um numero de item (bug de
                # digitacao dela, nao nosso) - normalmente e o item
                # seguinte mal-numerado. Sinalizo isso explicitamente em
                # vez de comparar contra o item errado silenciosamente
                rotulo_final += (
                    " ⚠ NUMERAÇÃO DUPLICADA NA PLANILHA FONTE (conferir manualmente "
                    "qual item é esse de verdade antes de usar esse número no artigo)"
                )
            chaves_ja_vistas.add(chave)

            elementos.append(
                {
                    "rotulo": rotulo_final,
                    "chave": chave,
                    "texto": planilha.cell(row=linha, column=COLUNA_RETROTRADUCAO).value,
                }
            )
            linha += 1

        retrotraducoes[nome_curto] = elementos

    return retrotraducoes


def calcular_comparacoes(original, retrotraducoes):
    """
    Compara cada retraducao com o original em ingles, e as duas
    retraducoes entre si (nos elementos que existem nas duas).
    """
    nomes = list(retrotraducoes.keys())  # ["Retradução 1", "Retradução 2"]

    resultados_vs_original = {nome: [] for nome in nomes}
    for nome in nomes:
        for elemento in retrotraducoes[nome]:
            chave_no_original = numero_base(elemento["chave"]) if elemento["chave"][-1:].isalpha() else elemento["chave"]
            texto_original = original.get(chave_no_original)

            texto_retro_norm = normalizar_texto(elemento["texto"])
            texto_original_norm = normalizar_texto(texto_original)

            resultados_vs_original[nome].append(
                {
                    "rotulo": elemento["rotulo"],
                    "exato": texto_retro_norm == texto_original_norm,
                    "similaridade": calcular_similaridade(texto_retro_norm, texto_original_norm),
                }
            )

    # retraducao 1 vs retraducao 2, casando pela chave (so nos elementos
    # que aparecem nas duas listas)
    elementos_1 = {e["chave"]: e["texto"] for e in retrotraducoes[nomes[0]]}
    elementos_2 = {e["chave"]: e["texto"] for e in retrotraducoes[nomes[1]]}
    chaves_em_comum = [e["chave"] for e in retrotraducoes[nomes[0]] if e["chave"] in elementos_2]

    resultado_entre_retraducoes = []
    for chave in chaves_em_comum:
        texto_1_norm = normalizar_texto(elementos_1[chave])
        texto_2_norm = normalizar_texto(elementos_2[chave])
        resultado_entre_retraducoes.append(
            {
                "rotulo": "Item " + chave if chave not in ("titulo", "instrucao") else chave,
                "chave": chave,
                "exato": texto_1_norm == texto_2_norm,
                "similaridade": calcular_similaridade(texto_1_norm, texto_2_norm),
            }
        )

    return resultados_vs_original, resultado_entre_retraducoes


def calcular_agregados(lista_de_resultados):
    total = len(lista_de_resultados)
    return {
        "total": total,
        "pct_exato": 100 * sum(r["exato"] for r in lista_de_resultados) / total,
        "sim_media": sum(r["similaridade"] for r in lista_de_resultados) / total,
    }


def montar_texto_do_relatorio(resultados_vs_original, resultado_entre_retraducoes, agregados_vs_original, agregado_entre_retraducoes):
    linhas = []
    linhas.append("=" * 70)
    linhas.append("RESULTADO - CONCORDÂNCIA NA RETROTRADUÇÃO - RPMS")
    linhas.append("=" * 70)
    linhas.append("Comparando: inglês original x retradução de cada retradutor")
    linhas.append("")

    for nome, resultados in resultados_vs_original.items():
        linhas.append("--- " + nome + " × Original (por elemento) ---")
        for r in resultados:
            linhas.append(
                "  "
                + r["rotulo"]
                + ": "
                + ("idêntico" if r["exato"] else "diferente")
                + " (similaridade " + str(round(r["similaridade"], 1)) + "%)"
            )
        linhas.append("")

    linhas.append("--- Retradução 1 × Retradução 2 (por elemento) ---")
    for r in resultado_entre_retraducoes:
        linhas.append(
            "  "
            + r["rotulo"]
            + ": "
            + ("idêntico" if r["exato"] else "diferente")
            + " (similaridade " + str(round(r["similaridade"], 1)) + "%)"
        )
    linhas.append("")

    linhas.append("--- Resumo geral ---")
    for nome, agregado in agregados_vs_original.items():
        linhas.append(
            nome
            + " × Original: "
            + str(agregado["total"])
            + " elementos, "
            + str(round(agregado["pct_exato"], 1))
            + "% idênticos, similaridade média "
            + str(round(agregado["sim_media"], 1))
            + "%"
        )
    linhas.append(
        "Retradução 1 × Retradução 2: "
        + str(agregado_entre_retraducoes["total"])
        + " elementos, "
        + str(round(agregado_entre_retraducoes["pct_exato"], 1))
        + "% idênticos, similaridade média "
        + str(round(agregado_entre_retraducoes["sim_media"], 1))
        + "%"
    )
    linhas.append("")
    linhas.append(
        "IMPORTANTE: retrotradução é tradução livre - divergência de texto é esperada e normal. "
        "O % idêntico costuma ser baixo mesmo quando o SENTIDO foi preservado; use a similaridade "
        "como indício, mas a avaliação final de fidelidade de sentido precisa de leitura humana "
        "dos itens com menor similaridade (ver relatório completo acima, por elemento)."
    )
    linhas.append("=" * 70)

    return "\n".join(linhas)


def montar_resumo_para_figura(agregados_vs_original, agregado_entre_retraducoes):
    nomes = list(agregados_vs_original.keys())

    colunas = [
        "Comparação",
        "Elementos (N)",
        "% idêntico",
        "Similaridade média",
    ]

    linhas_valores = []
    for nome in nomes:
        agregado = agregados_vs_original[nome]
        linhas_valores.append(
            [
                nome + " × Original",
                str(agregado["total"]),
                str(round(agregado["pct_exato"], 1)) + "%",
                str(round(agregado["sim_media"], 1)) + "%",
            ]
        )
    linhas_valores.append(
        [
            "Retradução 1 × Retradução 2",
            str(agregado_entre_retraducoes["total"]),
            str(round(agregado_entre_retraducoes["pct_exato"], 1)) + "%",
            str(round(agregado_entre_retraducoes["sim_media"], 1)) + "%",
        ]
    )

    titulo = "Concordância na retrotradução: RPMS (retraduções × inglês original)"

    notas = [
        "Nota. \"% idêntico\" = texto idêntico após normalizar (rígido). \"Similaridade\" = "
        "percentual via difflib.SequenceMatcher - mais informativo aqui, já que retrotradução é "
        "tradução livre e divergência textual é esperada mesmo quando o sentido está correto.",
        "Itens 8 e 10 aparecem com duas variantes testadas (a/b) na planilha de retrotradução, por "
        "isso o N de elementos é 23, não 21.",
    ]

    return {"titulo": titulo, "colunas": colunas, "linhas_valores": linhas_valores, "notas": notas}


def salvar_relatorio_em_arquivo(texto_relatorio, agora):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    nome_do_arquivo = "concordancia_retrotraducao_" + agora + ".txt"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    caminho_completo.write_text(texto_relatorio, encoding="utf-8")

    return caminho_completo


def salvar_imagem_relatorio(resumo, agora):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "serif"

    titulo = resumo["titulo"]
    colunas = resumo["colunas"]
    linhas_valores = resumo["linhas_valores"]
    notas = resumo["notas"]

    linhas_notas = []
    for nota in notas:
        linhas_notas.extend(textwrap.wrap(nota, width=110))
    texto_notas = "\n".join(linhas_notas)

    altura_titulo = 0.5
    altura_tabela = 0.55 + 0.42 * len(linhas_valores)
    altura_notas = 0.15 + 0.24 * max(len(linhas_notas), 1)
    altura_total = altura_titulo + altura_tabela + altura_notas

    fig = plt.figure(figsize=(9.5, altura_total))
    fig.patch.set_facecolor("white")

    fig.text(
        0.03,
        1 - (0.32 / altura_total),
        titulo,
        fontsize=11,
        style="italic",
        ha="left",
        va="top",
        wrap=True,
    )

    topo_tabela = 1 - (altura_titulo / altura_total)
    altura_tabela_frac = altura_tabela / altura_total
    ax = fig.add_axes([0.03, topo_tabela - altura_tabela_frac, 0.94, altura_tabela_frac])
    ax.axis("off")

    tabela = ax.table(cellText=linhas_valores, colLabels=colunas, cellLoc="center", loc="center")
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.auto_set_column_width(col=list(range(len(colunas))))
    tabela.scale(1, 2.0)

    numero_de_linhas_de_dados = len(linhas_valores)
    for (linha, _coluna), celula in tabela.get_celld().items():
        celula.set_edgecolor("black")
        if linha == 0:
            celula.set_text_props(weight="bold")
            celula.visible_edges = "BT"
            celula.set_linewidth(1.1)
        elif linha == numero_de_linhas_de_dados:
            celula.visible_edges = "B"
            celula.set_linewidth(1.1)
        else:
            celula.visible_edges = ""

    y_notas = topo_tabela - altura_tabela_frac - (0.05 / altura_total)
    fig.text(0.03, y_notas, texto_notas, fontsize=8, ha="left", va="top")

    nome_do_arquivo = "concordancia_retrotraducao_" + agora + ".png"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    fig.savefig(caminho_completo, dpi=200, facecolor="white")
    plt.close(fig)

    return caminho_completo


def salvar_html_relatorio(resumo, nome_da_imagem, agora):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    titulo = resumo["titulo"]
    colunas = resumo["colunas"]
    linhas_valores = resumo["linhas_valores"]
    notas = resumo["notas"]

    celulas_cabecalho = "".join("<th>" + c + "</th>" for c in colunas)
    linhas_html = "".join(
        "<tr>" + "".join("<td>" + v + "</td>" for v in linha) + "</tr>" for linha in linhas_valores
    )
    paragrafos_notas = "".join("<p>" + n + "</p>" for n in notas)

    html = (
        "<!doctype html>\n"
        '<html lang="pt-BR">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        "<title>" + titulo + "</title>\n"
        "<style>\n"
        "  body { margin: 0; padding: 24px; background: #ffffff;\n"
        '    font-family: "Times New Roman", Times, Georgia, serif; color: #000000; }\n'
        "  .titulo-tabela { font-size: 14px; margin-bottom: 14px; font-style: italic; }\n"
        "  table { width: 100%; border-collapse: collapse; font-size: 13px; }\n"
        "  thead tr { border-top: 1.6px solid #000; }\n"
        "  th, td { padding: 7px 10px; text-align: center; }\n"
        "  thead th { border-bottom: 1px solid #000; font-weight: bold; }\n"
        "  tbody tr:last-child td { border-bottom: 1.6px solid #000; }\n"
        "  .nota { font-size: 11.5px; margin-top: 12px; line-height: 1.5; }\n"
        "  .nota p { margin: 4px 0; }\n"
        "  .imagem-recente { margin-top: 28px; }\n"
        "  .imagem-recente p { font-size: 11px; font-style: italic; margin-bottom: 6px; }\n"
        "  .imagem-recente img { max-width: 100%; border: 1px solid #ccc; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        '  <div class="titulo-tabela">' + titulo + "</div>\n"
        "  <table>\n"
        "    <thead><tr>" + celulas_cabecalho + "</tr></thead>\n"
        "    <tbody>" + linhas_html + "</tbody>\n"
        "  </table>\n"
        '  <div class="nota">' + paragrafos_notas + "</div>\n"
        '  <div class="imagem-recente">\n'
        "    <p>Imagem gerada nesta execução (" + agora + "):</p>\n"
        '    <img src="' + nome_da_imagem + '" alt="' + titulo + '">\n'
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )

    nome_do_arquivo = "concordancia_retrotraducao_" + agora + ".html"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo
    caminho_completo.write_text(html, encoding="utf-8")

    return caminho_completo


def main():
    caminho_projeto = PASTA_PROJETO

    if not (caminho_projeto / ARQUIVO_ORIGINAL).exists():
        print("Não achei o arquivo: " + str(caminho_projeto / ARQUIVO_ORIGINAL))
        sys.exit(1)
    if not (caminho_projeto / ARQUIVO_RETROTRADUCAO).exists():
        print("Não achei o arquivo: " + str(caminho_projeto / ARQUIVO_RETROTRADUCAO))
        sys.exit(1)

    original = carregar_original_ingles(caminho_projeto)
    retrotraducoes = carregar_retrotraducoes(caminho_projeto)

    resultados_vs_original, resultado_entre_retraducoes = calcular_comparacoes(original, retrotraducoes)

    agregados_vs_original = {
        nome: calcular_agregados(resultados) for nome, resultados in resultados_vs_original.items()
    }
    agregado_entre_retraducoes = calcular_agregados(resultado_entre_retraducoes)

    texto_relatorio = montar_texto_do_relatorio(
        resultados_vs_original, resultado_entre_retraducoes, agregados_vs_original, agregado_entre_retraducoes
    )
    print(texto_relatorio)

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_salvo = salvar_relatorio_em_arquivo(texto_relatorio, agora)
    print("\nRelatório salvo em: " + str(caminho_salvo))

    resumo = montar_resumo_para_figura(agregados_vs_original, agregado_entre_retraducoes)

    caminho_imagem = salvar_imagem_relatorio(resumo, agora)
    print("Imagem (tabela-resumo pronta pro artigo) salva em: " + str(caminho_imagem))

    caminho_html = salvar_html_relatorio(resumo, caminho_imagem.name, agora)
    print("Página HTML (com a imagem mais recente) salva em: " + str(caminho_html))


if __name__ == "__main__":
    main()
