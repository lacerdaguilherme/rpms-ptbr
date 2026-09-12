# krippendorff_alpha_rpms.py
# Autor: Guilherme Lacerda de Avila
#
# Mesma ideia do krippendorff_alpha_epmr.py, so que pro RPMS (escala
# respondida pelos juizes NAO especialistas, os proprios refugiados que
# avaliaram os itens).
#
# ATENCAO - mesmo cuidado do fleiss_kappa_rpms.py e do cvi_ac1_rpms.py:
# as planilhas desse arquivo excel tem o NOME DE VERDADE dos juizes escrito
# no nome da aba (tipo "Juiz 1 (Fulano de Tal)") e mais pra baixo na planilha
# (da linha 28 em diante) tem ate nome completo, idade, pais de origem e
# outras informacoes desses juizes.
#
# Isso e dado sensivel e NAO PODE aparecer em lugar nenhum do resultado desse
# script. Por isso, aqui eu:
# 1) so leio da linha 6 ate linha 26 de cada planilha (nunca mais que isso)
# 2) NUNCA uso o nome real da aba/planilha em nada que e impresso ou salvo em
#    arquivo - cada juiz vira so "Juiz 1", "Juiz 2", "Juiz 3" e "Juiz 4"
#
# Ver krippendorff_alpha_epmr.py pra explicacao completa do que e o Alpha de
# Krippendorff e por que ele foi calculado (mesmo texto, nao repetido aqui).
#
# Como rodar:
#   uv run estatistica/krippendorff_alpha_rpms.py
#   uv run estatistica/krippendorff_alpha_rpms.py "caminho/outro_arquivo.xlsx"
#
# REGRA DE INTERPRETACAO "Sim + sugestao" (revisada em 11/09/2026, apos
# auditoria celula a celula das planilhas): discordancia e o "Nao" marcado
# na coluna binaria (coluna C). Uma ressalva escrita na coluna D so e
# reclassificada como discordancia quando aponta defeito no item como
# escrito, e nao sugestao de aprimoramento de um item ja julgado coerente.
# Os itens reclassificados ficam listados explicitamente na constante
# ITENS_COM_RESSALVA_RECLASSIFICADA, abaixo.
#
# Neste painel ha exatamente um caso, o item 6 (Juiz 4).
# Ver EXPLICACAO.md, secao 16.

import csv
import math
import sys
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib
import openpyxl

matplotlib.use("Agg")  # backend sem tela, so pra salvar arquivo de imagem direto
import matplotlib.pyplot as plt  # noqa: E402 (precisa vir depois do matplotlib.use)

LINHA_COMECO = 6
LINHA_FIM = 26
COLUNA_RESPOSTA = 3
COLUNA_JUSTIFICATIVA = 4  # coluna D

# Itens cuja ressalva foi reclassificada como discordancia (ver cabecalho).
# Unico caso do estudo inteiro: item 6 (Juiz 4). A ressalva aponta falha de
# COMPREENSAO do enunciado pela propria populacao-alvo ("deslocamento" nao e
# entendivel pela maioria dos estrangeiros), ou seja, um defeito no item como
# escrito, diferente das sugestoes de aprimoramento registradas em itens
# aprovados no painel de especialistas, que nao sao reclassificadas.
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset({6})

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
ARQUIVO_PADRAO = PASTA_DO_SCRIPT.parent / "dados" / "avaliacao_rpms.csv"
PASTA_RESULTADOS = PASTA_DO_SCRIPT / "resultados"


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


def ler_respostas_de_um_juiz(planilha):
    # so leio linha 6 ate 26 mesmo, de proposito - o resto da planilha tem
    # informacao pessoal do juiz e eu nem quero chegar perto disso
    respostas = []
    for linha in range(LINHA_COMECO, LINHA_FIM + 1):
        valor_da_celula = planilha.cell(row=linha, column=COLUNA_RESPOSTA).value
        resposta = normalizar_resposta(valor_da_celula)

        numero_do_item = linha - LINHA_COMECO + 1
        valor_da_justificativa = planilha.cell(row=linha, column=COLUNA_JUSTIFICATIVA).value
        tem_ressalva = valor_da_justificativa is not None and str(valor_da_justificativa).strip() != ""
        if resposta == "Sim" and tem_ressalva and numero_do_item in ITENS_COM_RESSALVA_RECLASSIFICADA:
            # ressalva reclassificada como discordancia (ver regra no cabecalho)
            resposta = "Não"

        respostas.append(resposta)
    return respostas


def ler_respostas_do_csv(caminho_csv):
    # O CSV publicado em dados/ tem uma linha por resposta (item x juiz),
    # com a ressalva escrita pelo juiz quando houve. E a mesma informacao
    # da planilha, sem os dados pessoais dos avaliadores. Ver CODEBOOK.md.
    respostas_por_juiz = {}

    with caminho_csv.open(encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            numero_do_item = int(linha["item"])
            numero_do_juiz = int(linha["juiz"])
            resposta = normalizar_resposta(linha["resposta"])
            tem_ressalva = str(linha.get("tem_ressalva", "")).strip() == "1"

            if resposta == "Sim" and tem_ressalva and numero_do_item in ITENS_COM_RESSALVA_RECLASSIFICADA:
                # ressalva reclassificada como discordancia (ver regra no cabecalho)
                resposta = "Não"

            respostas_por_juiz.setdefault(numero_do_juiz, {})[numero_do_item] = resposta

    if not respostas_por_juiz:
        raise ValueError("o CSV está vazio: " + str(caminho_csv))

    # devolve no mesmo formato da leitura do Excel: uma lista por juiz,
    # com as respostas na ordem dos itens
    return [
        [respostas_por_juiz[juiz][item] for item in sorted(respostas_por_juiz[juiz])]
        for juiz in sorted(respostas_por_juiz)
    ]


def carregar_arquivo(caminho_excel):
    if caminho_excel.suffix.lower() == ".csv":
        return ler_respostas_do_csv(caminho_excel)

    livro = openpyxl.load_workbook(caminho_excel, data_only=True)

    respostas_por_juiz = []
    # o nome_da_planilha (que tem nome de gente de verdade) so serve pra
    # abrir a aba certa aqui embaixo, ele NAO e guardado em nenhuma variavel
    # usada depois disso
    for indice, nome_da_planilha in enumerate(livro.sheetnames, start=1):
        planilha = livro[nome_da_planilha]
        respostas_por_juiz.append(ler_respostas_de_um_juiz(planilha))

    return respostas_por_juiz


def montar_matriz(respostas_por_juiz):
    numero_de_itens = len(respostas_por_juiz[0])

    matriz = []
    for i in range(numero_de_itens):
        qtd_sim = 0
        qtd_nao = 0
        for respostas in respostas_por_juiz:
            if respostas[i] == "Sim":
                qtd_sim += 1
            else:
                qtd_nao += 1
        matriz.append([qtd_sim, qtd_nao])

    return matriz


def montar_matriz_de_coincidencia(matriz):
    # ver krippendorff_alpha_epmr.py pra explicação completa
    sim_sim = 0
    nao_nao = 0
    sim_nao = 0

    for qtd_sim, qtd_nao in matriz:
        sim_sim += qtd_sim * (qtd_sim - 1)
        nao_nao += qtd_nao * (qtd_nao - 1)
        sim_nao += qtd_sim * qtd_nao

    nao_sim = sim_nao

    return {
        "sim_sim": sim_sim,
        "sim_nao": sim_nao,
        "nao_sim": nao_sim,
        "nao_nao": nao_nao,
    }


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

    if discordancia_esperada == 0:
        return float("nan"), discordancia_observada, discordancia_esperada, n_total

    alpha = 1 - (discordancia_observada / discordancia_esperada)
    return alpha, discordancia_observada, discordancia_esperada, n_total


def interpretar_alpha(valor):
    if math.isnan(valor):
        return "indefinido"
    if valor >= 0.800:
        return "confiabilidade adequada para conclusões definitivas (critério de Krippendorff)"
    if valor >= 0.667:
        return "confiabilidade suficiente só para conclusões tentativas/exploratórias (critério de Krippendorff)"
    return "confiabilidade insuficiente, abaixo do critério mínimo de Krippendorff"


def montar_texto_do_relatorio(matriz, numero_de_juizes):
    coincidencia = montar_matriz_de_coincidencia(matriz)
    valor_alpha, do, de, n_total = calcular_alpha(coincidencia)

    linhas = []
    linhas.append("=" * 60)
    linhas.append("RESULTADO - ALPHA DE KRIPPENDORFF - RPMS (juízes não especialistas)")
    linhas.append("=" * 60)
    linhas.append(
        "Número de juízes: "
        + str(numero_de_juizes)
        + " (identificados de Juiz 1 até Juiz "
        + str(numero_de_juizes)
        + ")"
    )
    linhas.append("Número de itens: " + str(len(matriz)))
    linhas.append("")

    linhas.append("Matriz de coincidência (soma de todos os pares avaliador-avaliador, todos os itens):")
    linhas.append("              Sim        Não")
    linhas.append(
        "  Sim    " + str(coincidencia["sim_sim"]).rjust(6) + "   " + str(coincidencia["sim_nao"]).rjust(6)
    )
    linhas.append(
        "  Não    " + str(coincidencia["nao_sim"]).rjust(6) + "   " + str(coincidencia["nao_nao"]).rjust(6)
    )
    linhas.append("")
    linhas.append("Total de pares avaliáveis (n..): " + str(n_total))
    linhas.append("Discordância observada (Do): " + str(round(do, 4)))
    linhas.append("Discordância esperada ao acaso (De): " + str(round(de, 4)))
    linhas.append("")

    if math.isnan(valor_alpha):
        linhas.append("Alpha de Krippendorff: NÃO DEU PRA CALCULAR (deu NaN)")
        linhas.append(
            "  Isso acontece quando só existe uma categoria de resposta em todos os "
            "itens (aqui, 100% Sim, sem nenhuma exceção) - não sobra nenhuma "
            "discordância (observada nem esperada) pra fórmula medir, e o cálculo "
            "vira uma divisão por zero. Não é erro do script, é o comportamento "
            "matemático esperado nesse cenário. Nesse caso, reporte o CVI "
            "(estatistica/cvi_ac1_rpms.py), que já mostra I-CVI = S-CVI = 1,00, "
            "como evidência de validade de conteúdo."
        )
    else:
        linhas.append("Alpha de Krippendorff (α): " + str(round(valor_alpha, 4)))
        linhas.append("  Interpretação: " + interpretar_alpha(valor_alpha))

    linhas.append("=" * 60)

    return "\n".join(linhas)


def salvar_relatorio_em_arquivo(texto_relatorio, agora):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    nome_do_arquivo = "krippendorff_alpha_rpms_" + agora + ".txt"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    caminho_completo.write_text(texto_relatorio, encoding="utf-8")

    return caminho_completo


def montar_resumo_para_figura(matriz, numero_de_juizes):
    """
    Monta os dados prontos pra virar figura (PNG) e pagina (HTML) - ver
    krippendorff_alpha_epmr.py pra explicação completa. Mesma lógica
    aqui, só muda o título e os juízes serem identificados como "não
    especialistas".
    """
    coincidencia = montar_matriz_de_coincidencia(matriz)
    valor_alpha, _do, _de, n_total = calcular_alpha(coincidencia)

    texto_alpha = "—" if math.isnan(valor_alpha) else str(round(valor_alpha, 3))
    interpretacao = interpretar_alpha(valor_alpha)
    if not math.isnan(valor_alpha):
        interpretacao = interpretacao[0].upper() + interpretacao[1:]
    else:
        interpretacao = interpretacao.capitalize()

    colunas = ["Itens (N)", "Avaliadores", "n..", "Alpha (α)", "Interpretação"]
    valores = [str(len(matriz)), str(numero_de_juizes), str(n_total), texto_alpha, interpretacao]

    titulo = "Alpha de Krippendorff: RPMS (juízes não especialistas)"

    notas = [
        "Nota. Critério de Krippendorff (1980, 2004, 2019): α >= 0,800 pra conclusões "
        "definitivas; α >= 0,667 só pra conclusões tentativas."
    ]
    if math.isnan(valor_alpha):
        notas.append(
            "Indefinido: 100% de concordância \"Sim\" em todos os itens, sem nenhuma variação "
            "nas respostas pra estimar a discordância esperada ao acaso (ver EXPLICACAO.md, "
            "seção 11). Reporte o CVI (cvi_ac1_rpms.py) como evidência de validade de conteúdo."
        )
    else:
        notas.append(
            "Este valor tende a ficar próximo do Kappa de Fleiss e pode sofrer do mesmo "
            "paradoxo do kappa - ver EXPLICACAO.md, seção 11."
        )

    return {"titulo": titulo, "colunas": colunas, "valores": valores, "notas": notas}


def salvar_imagem_relatorio(resumo, agora):
    """
    Gera uma imagem PNG com uma tabela-resumo do resultado - ver
    fleiss_kappa_epmr.py pra explicação completa de como essa função
    funciona.
    """
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "serif"

    titulo = resumo["titulo"]
    colunas = resumo["colunas"]
    valores = resumo["valores"]
    notas = resumo["notas"]

    linhas_notas = []
    for nota in notas:
        linhas_notas.extend(textwrap.wrap(nota, width=105))
    texto_notas = "\n".join(linhas_notas)

    altura_titulo = 0.5
    altura_tabela = 1.3
    altura_notas = 0.15 + 0.24 * max(len(linhas_notas), 1)
    altura_total = altura_titulo + altura_tabela + altura_notas

    fig = plt.figure(figsize=(10.0, altura_total))
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

    tabela = ax.table(cellText=[valores], colLabels=colunas, cellLoc="center", loc="center")
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)
    tabela.auto_set_column_width(col=list(range(len(colunas))))
    tabela.scale(1, 2.2)

    for (linha, _coluna), celula in tabela.get_celld().items():
        celula.set_edgecolor("black")
        if linha == 0:
            celula.set_text_props(weight="bold")
            celula.visible_edges = "BT"
            celula.set_linewidth(1.1)
        else:
            celula.visible_edges = "B"
            celula.set_linewidth(1.1)

    y_notas = topo_tabela - altura_tabela_frac - (0.05 / altura_total)
    fig.text(0.03, y_notas, texto_notas, fontsize=8, ha="left", va="top")

    nome_do_arquivo = "krippendorff_alpha_rpms_" + agora + ".png"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    fig.savefig(caminho_completo, dpi=200, facecolor="white")
    plt.close(fig)

    return caminho_completo


def salvar_html_relatorio(resumo, nome_da_imagem, agora):
    """
    Gera uma pagina HTML com a mesma tabela-resumo - ver
    fleiss_kappa_epmr.py pra explicação completa. Referencia a imagem
    PNG gerada nessa mesma execução (mesmo "agora"), nunca uma antiga.
    """
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    titulo = resumo["titulo"]
    colunas = resumo["colunas"]
    valores = resumo["valores"]
    notas = resumo["notas"]

    celulas_cabecalho = "".join("<th>" + c + "</th>" for c in colunas)
    celulas_dados = "".join("<td>" + v + "</td>" for v in valores)
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
        "    <tbody><tr>" + celulas_dados + "</tr></tbody>\n"
        "  </table>\n"
        '  <div class="nota">' + paragrafos_notas + "</div>\n"
        '  <div class="imagem-recente">\n'
        "    <p>Imagem gerada nesta execução (" + agora + "):</p>\n"
        '    <img src="' + nome_da_imagem + '" alt="' + titulo + '">\n'
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )

    nome_do_arquivo = "krippendorff_alpha_rpms_" + agora + ".html"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo
    caminho_completo.write_text(html, encoding="utf-8")

    return caminho_completo


def main():
    if len(sys.argv) > 1:
        caminho_excel = Path(sys.argv[1])
    else:
        caminho_excel = ARQUIVO_PADRAO

    if not caminho_excel.exists():
        print("Não achei esse arquivo aqui: " + str(caminho_excel))
        sys.exit(1)

    respostas_por_juiz = carregar_arquivo(caminho_excel)
    matriz = montar_matriz(respostas_por_juiz)

    texto_relatorio = montar_texto_do_relatorio(matriz, len(respostas_por_juiz))

    print(texto_relatorio)

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_salvo = salvar_relatorio_em_arquivo(texto_relatorio, agora)
    print("\nRelatório salvo em: " + str(caminho_salvo))

    resumo = montar_resumo_para_figura(matriz, len(respostas_por_juiz))

    caminho_imagem = salvar_imagem_relatorio(resumo, agora)
    print("Imagem (tabela-resumo pronta pro artigo) salva em: " + str(caminho_imagem))

    caminho_html = salvar_html_relatorio(resumo, caminho_imagem.name, agora)
    print("Página HTML (com a imagem mais recente) salva em: " + str(caminho_html))


if __name__ == "__main__":
    main()
