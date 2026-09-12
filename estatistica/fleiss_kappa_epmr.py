# fleiss_kappa_epmr.py
# Autor: Guilherme Lacerda de Avila
#
# Script pra calcular o Kappa de Fleiss do EPMR. A ideia e ver se os 4
# juizes especialistas concordam entre si quando avaliam cada um dos 21
# itens da escala (cada item e respondido com Sim ou Nao).
#
# Kappa de Fleiss = uma conta que mede o quanto os avaliadores concordam
# entre si, mas descontando a concordancia que ia rolar so por sorte
# (tipo, se todo mundo chutar aleatorio ainda ia ter uma concordancia
# minima só por acaso, o kappa tira isso da conta). Formula original e
# do Fleiss (1971), aqui uso a lib statsmodels que ja tem isso pronto.
#
# Como rodar (o projeto usa uv pra gerenciar as dependencias):
#   uv run estatistica/fleiss_kappa_epmr.py
#
# Se quiser usar outro arquivo excel (tipo uma versao corrigida da
# planilha), da pra passar o caminho dele na hora de rodar:
#   uv run estatistica/fleiss_kappa_epmr.py "caminho/outro_arquivo.xlsx"
# Se nao passar nada ele usa o arquivo padrao que ja vem no projeto.
#
# REGRA DE INTERPRETACAO "Sim + sugestao" (revisada em 11/09/2026, apos
# auditoria celula a celula das planilhas): discordancia e o "Nao" marcado
# na coluna binaria (coluna C). Uma ressalva escrita na coluna D so e
# reclassificada como discordancia quando aponta defeito no item como
# escrito, e nao sugestao de aprimoramento de um item ja julgado coerente.
# Os itens reclassificados ficam listados explicitamente na constante
# ITENS_COM_RESSALVA_RECLASSIFICADA, abaixo, um por instrumento.
#
# A versao anterior deste script reclassificava QUALQUER celula preenchida
# na coluna D, o que divergiu do numero apresentado no poster e do que a
# orientadora de fato aplicou (um unico caso, o item 6 do RPMS).
# Ver EXPLICACAO.md, secao 16.

import csv
import math
import sys
import textwrap
from datetime import datetime
from pathlib import Path

import matplotlib
import openpyxl
from statsmodels.stats.inter_rater import fleiss_kappa

matplotlib.use("Agg")  # backend sem tela, so pra salvar arquivo de imagem direto
import matplotlib.pyplot as plt  # noqa: E402 (precisa vir depois do matplotlib.use)

# linha onde comecam as respostas dos itens (contei abrindo o excel na mao)
LINHA_COMECO = 6
LINHA_FIM = 26  # da 21 itens no total (26 - 6 + 1)
COLUNA_RESPOSTA = 3  # coluna C
COLUNA_JUSTIFICATIVA = 4  # coluna D

# Itens cuja ressalva foi reclassificada como discordancia (ver cabecalho).
# No painel de juizes especialistas: NENHUM. As observacoes registradas nos
# itens 4, 5, 8, 10 e 17 acompanham itens marcados como coerentes e propoem
# aprimoramento de redacao ou acrescimo de conteudo, nao apontam defeito no
# item como escrito. As reprovacoes deste painel sao os "Nao" da coluna C
# (itens 13 e 15 pelo Juiz 1; itens 20 e 21 pelo Juiz 4).
ITENS_COM_RESSALVA_RECLASSIFICADA = frozenset()

# pasta onde esse .py ta salvo - uso isso pra montar os outros caminhos,
# assim o script funciona nao importa de onde a gente chama o "uv run"
PASTA_DO_SCRIPT = Path(__file__).resolve().parent

# o excel padrao fica uma pasta acima (direto na raiz do projeto)
ARQUIVO_PADRAO = PASTA_DO_SCRIPT.parent / "dados" / "avaliacao_epmr.csv"# pasta onde os relatorios gerados vao parar (dentro da propria pasta do
# script, pra nao ficar espalhado por ai)
PASTA_RESULTADOS = PASTA_DO_SCRIPT / "resultados"


def normalizar_resposta(valor):
    """
    Deixa a resposta sempre igual ("Sim" ou "Nao").

    Reparei que a planilha do juiz 4 escreve tudo em maiusculo (SIM /
    NAO) e as outras planilhas nao. Se nao arrumar isso a conta do kappa
    da errado, porque ele ia contar "Sim" e "SIM" como categorias
    diferentes (e nao sao).
    """
    if valor is None:
        raise ValueError("achei uma celula vazia onde devia ter Sim ou Nao")

    texto = str(valor).strip().lower()

    if texto == "sim":
        return "Sim"
    elif texto == "não" or texto == "nao":
        return "Não"
    else:
        # se cair aqui e pq tem algo esquisito na planilha (typo, celula
        # bagunçada, etc). melhor parar aqui do que continuar sem saber
        raise ValueError("valor estranho na planilha, não é Sim nem Não: " + repr(valor))


def ler_respostas_de_um_juiz(planilha):
    # pega as respostas da coluna C, da linha 6 ate a 26 (os 21 itens)
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
    for nome_da_planilha in livro.sheetnames:
        planilha = livro[nome_da_planilha]
        respostas_por_juiz.append(ler_respostas_de_um_juiz(planilha))

    return respostas_por_juiz


def montar_matriz_e_achar_empates(respostas_por_juiz):
    """
    Monta a matriz que o fleiss_kappa pede: uma linha por item, e em
    cada linha quantos juizes marcaram Sim e quantos marcaram Nao.

    De quebra ja aproveito e vejo quais itens deram "empate total" (todo
    mundo respondeu igual) - isso ajuda a explicar depois se o kappa der
    algum valor estranho tipo NaN.
    """
    numero_de_itens = len(respostas_por_juiz[0])
    numero_de_juizes = len(respostas_por_juiz)

    matriz = []
    itens_sem_variacao = []

    for i in range(numero_de_itens):
        qtd_sim = 0
        qtd_nao = 0

        for respostas in respostas_por_juiz:
            if respostas[i] == "Sim":
                qtd_sim += 1
            else:
                qtd_nao += 1

        matriz.append([qtd_sim, qtd_nao])

        if qtd_sim == numero_de_juizes or qtd_nao == numero_de_juizes:
            itens_sem_variacao.append(i + 1)  # +1 pq o item 1 e o indice 0

    return matriz, itens_sem_variacao


def interpretar_kappa(valor_kappa):
    # escala classica do Landis & Koch (1977), vista em metodologia. e so
    # uma regua pra dizer se o kappa deu "bom" ou nao.
    if math.isnan(valor_kappa):
        return "indefinido"
    if valor_kappa < 0:
        return "concordância pior do que o esperado por acaso"
    if valor_kappa < 0.20:
        return "concordância leve"
    if valor_kappa < 0.40:
        return "concordância razoável"
    if valor_kappa < 0.60:
        return "concordância moderada"
    if valor_kappa < 0.80:
        return "concordância substancial"
    return "concordância quase perfeita"


def montar_texto_do_relatorio(matriz, itens_sem_variacao, valor_kappa, numero_de_juizes):
    linhas_do_texto = []
    linhas_do_texto.append("=" * 60)
    linhas_do_texto.append("RESULTADO - KAPPA DE FLEISS - EPMR (juízes especialistas)")
    linhas_do_texto.append("=" * 60)
    linhas_do_texto.append("Número de juízes: " + str(numero_de_juizes))
    linhas_do_texto.append("Número de itens: " + str(len(matriz)))
    linhas_do_texto.append("")
    linhas_do_texto.append("Contagem por item (quantos Sim, quantos Não):")

    for i in range(len(matriz)):
        qtd_sim, qtd_nao = matriz[i]
        texto_item = "  item " + str(i + 1) + ": Sim=" + str(qtd_sim) + ", Não=" + str(qtd_nao)
        if (i + 1) in itens_sem_variacao:
            texto_item += "  <- todo mundo respondeu igual"
        linhas_do_texto.append(texto_item)

    linhas_do_texto.append("")
    linhas_do_texto.append(
        "Itens onde todo mundo concordou 100%: "
        + str(len(itens_sem_variacao))
        + " de "
        + str(len(matriz))
    )

    linhas_do_texto.append("")
    if math.isnan(valor_kappa):
        linhas_do_texto.append("Kappa de Fleiss: NÃO DEU PRA CALCULAR (deu NaN)")
        linhas_do_texto.append(
            "  Isso acontece quando não tem nenhuma variação nos dados "
            "(todo mundo respondeu igual em tudo)."
        )
    else:
        # arredondei em 4 casas, achei que ficou de bom tamanho pra mostrar
        linhas_do_texto.append("Kappa de Fleiss: " + str(round(valor_kappa, 4)))
        linhas_do_texto.append("  Interpretação: " + interpretar_kappa(valor_kappa))

    linhas_do_texto.append("=" * 60)

    return "\n".join(linhas_do_texto)


def resposta_para_numero(resposta):
    # jasp/r/spss geralmente preferem numero a texto pra essas contas,
    # entao aqui eu transformo Sim em 1 e Nao em 0
    if resposta == "Sim":
        return "1"
    else:
        return "0"


def salvar_dados_brutos_csv(respostas_por_juiz):
    """
    Salva os dados originais (item x juiz, sem nenhuma conta feita
    ainda) num CSV, ja convertendo Sim -> 1 e Não -> 0. Isso serve pra
    quem quiser conferir a conta em outro programa (JASP, R, SPSS etc) -
    ai da pra comparar se bate com o que esse script calculou.
    """
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    numero_de_itens = len(respostas_por_juiz[0])
    numero_de_juizes = len(respostas_por_juiz)

    linhas_csv = []

    # linha do cabecalho: item, Juiz 1, Juiz 2, Juiz 3, Juiz 4
    cabecalho = ["item"]
    for j in range(numero_de_juizes):
        cabecalho.append("Juiz " + str(j + 1))
    linhas_csv.append(",".join(cabecalho))

    # uma linha por item, com a resposta de cada juiz naquele item
    # (ja em numero: 1 = Sim, 0 = Não)
    for i in range(numero_de_itens):
        linha = [str(i + 1)]
        for respostas in respostas_por_juiz:
            linha.append(resposta_para_numero(respostas[i]))
        linhas_csv.append(",".join(linha))

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_do_arquivo = "dados_brutos_epmr_" + agora + ".csv"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    caminho_completo.write_text("\n".join(linhas_csv), encoding="utf-8")

    return caminho_completo


def salvar_relatorio_em_arquivo(texto_relatorio, agora):
    # cria a pasta resultados se ela ainda nao existir
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    nome_do_arquivo = "fleiss_kappa_epmr_" + agora + ".txt"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    caminho_completo.write_text(texto_relatorio, encoding="utf-8")

    return caminho_completo


def montar_resumo_para_figura(matriz, valor_kappa, numero_de_juizes):
    """
    Monta os dados prontos pra virar figura (PNG) e pagina (HTML): titulo,
    nomes das colunas, os valores de uma unica linha de resultado, e as
    notas de rodape. Fica numa funcao separada pra nao duplicar essa
    logica entre salvar_imagem_relatorio() e salvar_html_relatorio() - as
    duas usam exatamente os mesmos dados, so mudam no jeito de desenhar.
    """
    if math.isnan(valor_kappa):
        texto_kappa = "—"
        interpretacao = "Indefinido"
    else:
        texto_kappa = str(round(valor_kappa, 3))
        interpretacao = interpretar_kappa(valor_kappa)

    colunas = ["Itens (N)", "Avaliadores", "Kappa de Fleiss (κ)", "Interpretação"]
    valores = [str(len(matriz)), str(numero_de_juizes), texto_kappa, interpretacao]

    titulo = "Concordância entre avaliadores: Kappa de Fleiss (EPMR, juízes especialistas)"

    notas = ["Nota. Interpretação qualitativa segundo a escala de Landis e Koch (1977)."]
    if math.isnan(valor_kappa):
        notas.append(
            "O coeficiente não pôde ser calculado: sem variação suficiente nas respostas "
            "(ver EXPLICACAO.md, seção 5)."
        )
    else:
        notas.append(
            "Este valor pode sofrer do paradoxo do kappa sob prevalência de respostas "
            "desbalanceada - ver CVI/AC1 (cvi_ac1_epmr.py) e EXPLICACAO.md, seção 9."
        )

    return {"titulo": titulo, "colunas": colunas, "valores": valores, "notas": notas}


def salvar_imagem_relatorio(resumo, agora):
    """
    Gera uma imagem PNG com uma tabela-resumo do resultado (mesmo estilo
    academico das tabelas do artigo: fonte serifada, linha em cima e
    embaixo do cabecalho, linha embaixo da linha de dados). E o "produto
    final" gerado automaticamente toda vez que o script roda, pronto pra
    quem quiser colar no artigo - nao precisa de nenhum passo manual
    (nada de abrir navegador ou tirar print).

    Isso NAO substitui uma figura final revisada a mao (com referencias
    completas etc, como as que ficam direto na pasta estatistica/) - e so
    um resumo visual rapido do resultado dessa execucao especifica.
    """
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.family"] = "serif"

    titulo = resumo["titulo"]
    colunas = resumo["colunas"]
    valores = resumo["valores"]
    notas = resumo["notas"]

    linhas_notas = []
    for nota in notas:
        linhas_notas.extend(textwrap.wrap(nota, width=100))
    texto_notas = "\n".join(linhas_notas)

    # alturas fixas em polegadas pra cada parte da figura (titulo, tabela,
    # notas) - calcular assim (em vez de uma fracao fixa da altura total)
    # garante espaco suficiente pras notas mesmo quando elas tem varias
    # linhas, sem cortar texto embaixo da figura
    altura_titulo = 0.5
    altura_tabela = 1.3
    altura_notas = 0.15 + 0.24 * max(len(linhas_notas), 1)
    altura_total = altura_titulo + altura_tabela + altura_notas

    fig = plt.figure(figsize=(9.5, altura_total))
    fig.patch.set_facecolor("white")

    fig.text(
        0.04,
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
    ax = fig.add_axes([0.04, topo_tabela - altura_tabela_frac, 0.92, altura_tabela_frac])
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
    fig.text(0.04, y_notas, texto_notas, fontsize=8, ha="left", va="top")

    nome_do_arquivo = "fleiss_kappa_epmr_" + agora + ".png"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo

    fig.savefig(caminho_completo, dpi=200, facecolor="white")
    plt.close(fig)

    return caminho_completo


def salvar_html_relatorio(resumo, nome_da_imagem, agora):
    """
    Gera uma pagina HTML com a mesma tabela-resumo, no mesmo estilo
    academico usado nas tabelas do artigo (fonte serifada, linhas
    horizontais simples) - pronta pra abrir direto no navegador, sem
    precisar de nenhuma ferramenta externa (nem Playwright, nem print).

    No final da pagina entra a imagem PNG gerada NESSA MESMA execucao
    (salvar_imagem_relatorio, mesmo "agora"), entao a pagina sempre
    aponta pro arquivo mais recente - nunca fica referenciando uma
    imagem antiga de uma execucao anterior.
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

    nome_do_arquivo = "fleiss_kappa_epmr_" + agora + ".html"
    caminho_completo = PASTA_RESULTADOS / nome_do_arquivo
    caminho_completo.write_text(html, encoding="utf-8")

    return caminho_completo


def main():
    # se a pessoa passar o caminho do excel na linha de comando, usa esse.
    # senao usa o arquivo padrao que ja vem no projeto
    if len(sys.argv) > 1:
        caminho_excel = Path(sys.argv[1])
    else:
        caminho_excel = ARQUIVO_PADRAO

    # coloquei essa checagem pq da primeira vez que digitei o nome do
    # arquivo errado o erro que apareceu foi bem feio de entender
    if not caminho_excel.exists():
        print("Não achei esse arquivo aqui: " + str(caminho_excel))
        sys.exit(1)

    respostas_por_juiz = carregar_arquivo(caminho_excel)
    matriz, itens_sem_variacao = montar_matriz_e_achar_empates(respostas_por_juiz)

    # essa parte as vezes solta um aviso chato (RuntimeWarning) quando da
    # empate total em tudo - nao e erro de verdade, e so o python avisando
    # de uma divisao por zero que rola dentro da formula do kappa. por
    # isso eu ignoro esse aviso aqui embaixo.
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        valor_kappa = fleiss_kappa(matriz, method="fleiss")

    texto_relatorio = montar_texto_do_relatorio(
        matriz, itens_sem_variacao, valor_kappa, len(respostas_por_juiz)
    )

    print(texto_relatorio)

    # mesmo timestamp pro .txt e pro .png, assim os dois arquivos dessa
    # execucao ficam facilmente identificaveis como o mesmo par
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_salvo = salvar_relatorio_em_arquivo(texto_relatorio, agora)
    print("\nRelatório salvo em: " + str(caminho_salvo))

    caminho_csv = salvar_dados_brutos_csv(respostas_por_juiz)
    print("Dados brutos (pra conferir em outro programa) salvos em: " + str(caminho_csv))

    resumo = montar_resumo_para_figura(matriz, valor_kappa, len(respostas_por_juiz))

    caminho_imagem = salvar_imagem_relatorio(resumo, agora)
    print("Imagem (tabela-resumo pronta pro artigo) salva em: " + str(caminho_imagem))

    caminho_html = salvar_html_relatorio(resumo, caminho_imagem.name, agora)
    print("Página HTML (com a imagem mais recente) salva em: " + str(caminho_html))


if __name__ == "__main__":
    main()
