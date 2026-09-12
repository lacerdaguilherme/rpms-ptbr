# cvi_ac1_rpms.py
# Autor: Guilherme Lacerda de Avila
#
# Mesma ideia do cvi_ac1_epmr.py, so que pro RPMS (escala respondida pelos
# juizes NAO especialistas, os proprios refugiados que avaliaram os itens).
#
# ATENCAO - isso aqui e importante, nao pode esquecer (mesmo cuidado do
# fleiss_kappa_rpms.py):
# as planilhas desse arquivo excel tem o NOME DE VERDADE dos juizes escrito
# no nome da aba (tipo "Juiz 1 (Fulano de Tal)") e mais pra baixo na planilha
# (da linha 28 em diante) tem ate nome completo, idade, pais de origem e
# outras informacoes desses juizes.
#
# Isso e dado sensivel e NAO PODE aparecer em lugar nenhum do resultado desse
# script. Por isso, aqui eu:
# 1) so leio da linha 6 ate linha 26 de cada planilha (nunca mais que isso,
#    o resto eu nem toco)
# 2) NUNCA uso o nome real da aba/planilha em nada que e impresso ou salvo em
#    arquivo - cada juiz vira so "Juiz 1", "Juiz 2", "Juiz 3" e "Juiz 4", na
#    ordem que a aba aparece dentro do excel
#
# Por que esse script existe (mesmo motivo do cvi_ac1_epmr.py): o Kappa de
# Fleiss do RPMS deu NaN, porque os 4 juizes responderam "Sim" em todos os 21
# itens (nenhuma variacao nos dados). O CVI nao tem esse problema - com
# concordancia total em tudo, ele simplesmente da o resultado maximo (1.00),
# que e a leitura estatistica correta pra esse caso. O AC1 de Gwet ja nao da
# pra calcular aqui pelo mesmo motivo do kappa (sem nenhuma variacao na
# prevalencia, a formula do AC1 tambem cai numa divisao por zero) - o script
# detecta isso e avisa no relatorio em vez de travar.
#
# Como rodar:
#   uv run estatistica/cvi_ac1_rpms.py
#   uv run estatistica/cvi_ac1_rpms.py "caminho/outro_arquivo.xlsx"
#
# REGRA DE INTERPRETACAO "Sim + sugestao" (revisada em 11/09/2026, apos
# auditoria celula a celula das planilhas): discordancia e o "Nao" marcado
# na coluna binaria (coluna C). Uma ressalva escrita na coluna D so e
# reclassificada como discordancia quando aponta defeito no item como
# escrito, e nao sugestao de aprimoramento de um item ja julgado coerente.
# Os itens reclassificados ficam listados explicitamente na constante
# ITENS_COM_RESSALVA_RECLASSIFICADA, abaixo.
#
# Neste painel ha exatamente um caso, o item 6 (Juiz 4), que sem essa
# reclassificacao daria 100% "Sim" sem nenhuma variacao (kappa/AC1
# indefinidos). Ver EXPLICACAO.md, secao 16.

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
    # uso o enumerate comecando em 1 so pra numerar os juizes na ordem que
    # aparecem no arquivo. o nome_da_planilha (que tem nome de gente de
    # verdade) so serve pra abrir a aba certa aqui embaixo, ele NAO e
    # guardado em nenhuma variavel usada depois disso
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


def calcular_icvi_por_item(matriz, numero_de_juizes):
    return [qtd_sim / numero_de_juizes for qtd_sim, qtd_nao in matriz]


def calcular_scvi_ave(lista_de_icvi):
    return sum(lista_de_icvi) / len(lista_de_icvi)


def calcular_scvi_ua(lista_de_icvi):
    itens_com_acordo_total = sum(1 for icvi in lista_de_icvi if icvi == 1.0)
    return itens_com_acordo_total / len(lista_de_icvi)


def icvi_minimo_aceitavel(numero_de_juizes):
    # tabela de Lynn (1986) - ver comentario completo no cvi_ac1_epmr.py
    if numero_de_juizes <= 5:
        return 1.00
    elif numero_de_juizes <= 8:
        return 0.83
    else:
        return 0.78


def calcular_pa_observada(matriz, numero_de_juizes):
    r = numero_de_juizes
    soma = 0.0
    for qtd_sim, qtd_nao in matriz:
        soma += (qtd_sim * (qtd_sim - 1) + qtd_nao * (qtd_nao - 1)) / (r * (r - 1))
    return soma / len(matriz)


def calcular_prevalencia_media(matriz, numero_de_juizes):
    total_de_sim = sum(qtd_sim for qtd_sim, qtd_nao in matriz)
    total_de_respostas = len(matriz) * numero_de_juizes
    return total_de_sim / total_de_respostas


def calcular_ac1(matriz, numero_de_juizes):
    pa = calcular_pa_observada(matriz, numero_de_juizes)
    pi = calcular_prevalencia_media(matriz, numero_de_juizes)

    pe = 2 * pi * (1 - pi)

    if pe == 1 or pe == 0:
        # pe = 0 acontece quando pi = 0 ou pi = 1 (todo mundo respondeu a
        # MESMA categoria em TODOS os itens, tipo o caso do RPMS aqui - 100%
        # Sim em tudo). Nesse caso 1 - pe = 1, entao o AC1 na verdade nao
        # quebra matematicamente, mas ele so reflete Pa (que ja e 1.0) e nao
        # sobra nenhuma variacao real pra "corrigir por acaso" - reporto
        # como indefinido pq nao ha nenhuma discordancia pra medir, igual o
        # script do kappa faz nesse mesmo cenario
        return float("nan"), pa, pe

    ac1 = (pa - pe) / (1 - pe)
    return ac1, pa, pe


def interpretar_forca_concordancia(valor):
    if math.isnan(valor):
        return "indefinido"
    if valor < 0:
        return "concordância pior do que o esperado por acaso"
    if valor < 0.20:
        return "concordância leve"
    if valor < 0.40:
        return "concordância razoável"
    if valor < 0.60:
        return "concordância moderada"
    if valor < 0.80:
        return "concordância substancial"
    return "concordância quase perfeita"


def montar_texto_do_relatorio(matriz, numero_de_juizes):
    lista_de_icvi = calcular_icvi_por_item(matriz, numero_de_juizes)
    scvi_ave = calcular_scvi_ave(lista_de_icvi)
    scvi_ua = calcular_scvi_ua(lista_de_icvi)
    cutoff = icvi_minimo_aceitavel(numero_de_juizes)

    valor_ac1, pa, pe = calcular_ac1(matriz, numero_de_juizes)

    linhas = []
    linhas.append("=" * 60)
    linhas.append("RESULTADO - CVI e AC1 de Gwet - RPMS (juízes não especialistas)")
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

    linhas.append("--- CVI (Content Validity Index) ---")
    linhas.append(
        "Critério mínimo de aceitação p/ I-CVI com "
        + str(numero_de_juizes)
        + " juízes (Lynn, 1986): "
        + str(cutoff)
    )
    linhas.append("")
    linhas.append("I-CVI por item (proporção de juízes que marcou Sim):")
    for i, icvi in enumerate(lista_de_icvi):
        qtd_sim, qtd_nao = matriz[i]
        texto_item = (
            "  item "
            + str(i + 1)
            + ": I-CVI="
            + str(round(icvi, 3))
            + " (Sim="
            + str(qtd_sim)
            + ", Não="
            + str(qtd_nao)
            + ")"
        )
        if icvi < cutoff:
            texto_item += "  <- abaixo do critério mínimo"
        linhas.append(texto_item)

    linhas.append("")
    linhas.append("S-CVI/Ave (média dos I-CVI de todos os itens): " + str(round(scvi_ave, 4)))
    linhas.append(
        "  Critério de referência (Polit, Beck & Owen, 2007): aceitável se >= 0,90"
    )
    linhas.append(
        "S-CVI/UA (proporção de itens com acordo universal, I-CVI = 1,00): "
        + str(round(scvi_ua, 4))
    )
    linhas.append("  Critério de referência (Polit, Beck & Owen, 2007): aceitável se >= 0,80")

    linhas.append("")
    linhas.append("--- AC1 de Gwet ---")
    linhas.append("Concordância observada (Pa): " + str(round(pa, 4)))
    if math.isnan(valor_ac1):
        linhas.append("Concordância esperada ao acaso pelo AC1 (Pe): " + str(round(pe, 4)))
        linhas.append("AC1 de Gwet: NÃO DEU PRA INTERPRETAR (sem nenhuma discordância nos dados)")
        linhas.append(
            "  Com Pa = 1,00 e nenhuma variação nas respostas, não sobra discordância "
            "nenhuma pra uma estatística de concordância corrigida por acaso medir. "
            "Nesse caso, reporte o CVI (que já mostra I-CVI = S-CVI = 1,00 acima) como "
            "a evidência de validade de conteúdo do RPMS."
        )
    else:
        linhas.append("Concordância esperada ao acaso pelo AC1 (Pe): " + str(round(pe, 4)))
        linhas.append("AC1 de Gwet: " + str(round(valor_ac1, 4)))
        linhas.append("  Interpretação: " + interpretar_forca_concordancia(valor_ac1))

    linhas.append("=" * 60)

    return "\n".join(linhas)


def salvar_relatorio_em_arquivo(texto_relatorio, agora):
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    nome_do_arquivo = "cvi_ac1_rpms_" + agora + ".txt"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    caminho_completo.write_text(texto_relatorio, encoding="utf-8")

    return caminho_completo


def montar_resumo_para_figura(matriz, numero_de_juizes):
    """
    Monta os dados prontos pra virar figura (PNG) e pagina (HTML) - ver
    cvi_ac1_epmr.py pra explicação completa. Mesma lógica aqui, só muda
    o título e os juízes serem identificados como "não especialistas".
    """
    lista_de_icvi = calcular_icvi_por_item(matriz, numero_de_juizes)
    scvi_ave = calcular_scvi_ave(lista_de_icvi)
    scvi_ua = calcular_scvi_ua(lista_de_icvi)
    valor_ac1, _pa, _pe = calcular_ac1(matriz, numero_de_juizes)

    texto_ac1 = "—" if math.isnan(valor_ac1) else str(round(valor_ac1, 3))
    interpretacao = interpretar_forca_concordancia(valor_ac1)

    colunas = ["Itens (N)", "Avaliadores", "S-CVI/Ave", "S-CVI/UA", "AC1 de Gwet", "Interpretação (AC1)"]
    valores = [
        str(len(matriz)),
        str(numero_de_juizes),
        str(round(scvi_ave, 3)),
        str(round(scvi_ua, 3)),
        texto_ac1,
        interpretacao.capitalize(),
    ]

    titulo = "CVI e AC1 de Gwet: RPMS (juízes não especialistas)"

    notas = [
        "Nota. S-CVI/Ave e S-CVI/UA: critério de aceitação >= 0,90 e >= 0,80, respectivamente "
        "(Polit, Beck & Owen, 2007)."
    ]
    if math.isnan(valor_ac1):
        notas.append(
            "AC1 indefinido: com 100% de concordância \"Sim\" em todos os itens, não sobra "
            "discordância nos dados pra uma estatística corrigida por acaso medir (ver "
            "EXPLICACAO.md, seção 9). Use o CVI acima (S-CVI = 1,00) como evidência."
        )
    else:
        notas.append("Interpretação do AC1 segundo a escala de Landis e Koch (1977).")

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
        linhas_notas.extend(textwrap.wrap(nota, width=115))
    texto_notas = "\n".join(linhas_notas)

    altura_titulo = 0.5
    altura_tabela = 1.3
    altura_notas = 0.15 + 0.24 * max(len(linhas_notas), 1)
    altura_total = altura_titulo + altura_tabela + altura_notas

    fig = plt.figure(figsize=(11.0, altura_total))
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
    tabela.set_fontsize(9.5)
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

    nome_do_arquivo = "cvi_ac1_rpms_" + agora + ".png"
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

    nome_do_arquivo = "cvi_ac1_rpms_" + agora + ".html"
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
