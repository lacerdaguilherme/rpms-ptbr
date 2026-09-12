# gerar_texto_resultados.py
# Autor: Guilherme Lacerda de Avila
#
# Monta o texto da secao de Resultados do artigo, com as tabelas em
# Markdown e em LaTeX, preenchido com os numeros que os scripts de
# calculo produziram nessa mesma execucao.
#
# POR QUE ESSE SCRIPT EXISTE
#
# O risco de escrever numero na mao num artigo e o numero envelhecer:
# alguem corrige um dado bruto, roda os scripts de novo, e o texto fica
# apontando pro valor antigo sem ninguem perceber. Aqui o texto e as
# tabelas sao montados a partir do calculo, entao eles nao tem como
# divergir do que os scripts produzem.
#
# O texto e um MODELO, com a redacao fixa e so os numeros variaveis. Ele
# nao escreve interpretacao nova nem conclusao: isso e trabalho de quem
# assina o artigo. Use como ponto de partida, confira, e reescreva com as
# suas palavras antes de colar no manuscrito.
#
# As funcoes de calculo sao importadas dos proprios scripts de
# coeficiente, de proposito: assim e impossivel esse arquivo usar uma
# formula diferente da que os scripts usam.
#
# Como rodar:
#   uv run estatistica/gerar_texto_resultados.py
#
# Sai em estatistica/resultados/texto_resultados_<data>.md

import sys
import warnings
from datetime import datetime
from pathlib import Path

from statsmodels.stats.inter_rater import fleiss_kappa

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA_DO_SCRIPT))

import ac1_epmr  # noqa: E402
import ac1_rpms  # noqa: E402
import cvi_ac1_epmr  # noqa: E402
import cvi_ac1_rpms  # noqa: E402
import fleiss_kappa_epmr  # noqa: E402
import fleiss_kappa_rpms  # noqa: E402
import krippendorff_alpha_epmr  # noqa: E402
import krippendorff_alpha_rpms  # noqa: E402

PASTA_RESULTADOS = PASTA_DO_SCRIPT / "resultados"


def num(valor, casas=3):
    # numero no formato brasileiro, com virgula decimal
    if valor is None:
        return "—"
    texto = f"{valor:.{casas}f}"
    return texto.replace(".", ",").replace("-", "−")


def coletar(modulo_ac1, modulo_cvi, modulo_kappa, modulo_alpha):
    respostas = modulo_ac1.carregar_arquivo(modulo_ac1.ARQUIVO_PADRAO)
    numero_de_juizes = len(respostas)
    matriz = modulo_ac1.montar_matriz(respostas)

    valor_ac1, pa, pe = modulo_ac1.calcular_ac1(matriz, numero_de_juizes)

    i_cvi = modulo_cvi.calcular_icvi_por_item(matriz, numero_de_juizes)
    s_cvi_ave = modulo_cvi.calcular_scvi_ave(i_cvi)
    s_cvi_ua = modulo_cvi.calcular_scvi_ua(i_cvi)

    respostas_kappa = modulo_kappa.carregar_arquivo(modulo_kappa.ARQUIVO_PADRAO)
    matriz_kappa, itens_sem_variacao = modulo_kappa.montar_matriz_e_achar_empates(respostas_kappa)

    # o aviso de divisao por zero aqui nao e erro: acontece quando todos os
    # juizes respondem igual em tudo. Mesmo tratamento do fleiss_kappa_*.py
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        valor_kappa = float(fleiss_kappa(matriz_kappa, method="fleiss"))

    coincidencia = modulo_alpha.montar_matriz_de_coincidencia(matriz)
    valor_alpha, _do, _de, n_pares = modulo_alpha.calcular_alpha(coincidencia)

    itens_abaixo = [i + 1 for i, valor in enumerate(i_cvi) if valor < 1.0]

    return {
        "itens": len(matriz),
        "juizes": numero_de_juizes,
        "ac1": valor_ac1,
        "pa": pa,
        "pe": pe,
        "interpretacao": modulo_ac1.interpretar_forca_concordancia(valor_ac1),
        "s_cvi_ave": s_cvi_ave,
        "s_cvi_ua": s_cvi_ua,
        "itens_abaixo": itens_abaixo,
        "kappa": valor_kappa,
        "alpha": valor_alpha,
        "n_pares": n_pares,
        "itens_unanimes": len(itens_sem_variacao),
    }


def lista_por_extenso(numeros):
    # ja sai com a preposicao contraida ("no item 6", "nos itens 13, 15 e 20"),
    # pra frase montada nao virar "em o item 6"
    if not numeros:
        return "nenhum item"
    if len(numeros) == 1:
        return "no item " + str(numeros[0])
    return "nos itens " + ", ".join(str(n) for n in numeros[:-1]) + " e " + str(numeros[-1])


def montar_texto(epmr, rpms, agora):
    p = []
    p.append("# Resultados: texto e tabelas gerados a partir do cálculo")
    p.append("")
    p.append("Autor: Guilherme Lacerda de Avila")
    p.append("")
    p.append(
        "Gerado automaticamente por `gerar_texto_resultados.py` em "
        + agora
        + ". Os números vêm dos scripts de cálculo, não foram digitados à mão."
    )
    p.append("")
    p.append("---")
    p.append("")

    p.append("## Texto redigido (seção de Resultados)")
    p.append("")
    p.append("**Painel de juízes especialistas:**")
    p.append("")
    p.append(
        "> A concordância entre os "
        + str(epmr["juizes"])
        + " juízes especialistas na avaliação dos "
        + str(epmr["itens"])
        + " itens foi analisada por meio do coeficiente AC1 de Gwet (Gwet, 2008), "
        "estatística corrigida pela concordância esperada ao acaso que, diferentemente "
        "do Kappa de Fleiss, não incorre no paradoxo do kappa (Feinstein & Cicchetti, 1990) "
        "sob prevalência de respostas desbalanceada. Obteve-se AC1 = "
        + num(epmr["ac1"])
        + " (concordância observada Pa = "
        + num(epmr["pa"])
        + "; concordância esperada ao acaso Pe = "
        + num(epmr["pe"])
        + "), classificado como "
        + epmr["interpretacao"]
        + " (Landis & Koch, 1977). Em nível de escala, o Índice de Validade de Conteúdo "
        "resultou em S-CVI/Ave = "
        + num(epmr["s_cvi_ave"])
        + " e S-CVI/UA = "
        + num(epmr["s_cvi_ua"])
        + ". O I-CVI ficou abaixo do critério mínimo "
        + lista_por_extenso(epmr["itens_abaixo"])
        + "."
    )
    p.append("")
    p.append("**Painel da população-alvo:**")
    p.append("")
    p.append(
        "> Para o painel da população-alvo, os "
        + str(rpms["juizes"])
        + " avaliadores apresentaram AC1 = "
        + num(rpms["ac1"])
        + " (Pa = "
        + num(rpms["pa"])
        + "; Pe = "
        + num(rpms["pe"])
        + "), classificado como "
        + rpms["interpretacao"]
        + " (Landis & Koch, 1977). Em nível de escala, obteve-se S-CVI/Ave = "
        + num(rpms["s_cvi_ave"])
        + " e S-CVI/UA = "
        + num(rpms["s_cvi_ua"])
        + ", com I-CVI abaixo do critério mínimo "
        + lista_por_extenso(rpms["itens_abaixo"])
        + "."
    )
    p.append("")

    p.append("## Tabela 1 (Markdown)")
    p.append("")
    p.append(
        "**Tabela 1.** *Concordância entre avaliadores segundo o coeficiente AC1 de Gwet.*"
    )
    p.append("")
    p.append("| Painel | Itens (N) | Avaliadores | Pa | Pe | AC1 | S-CVI/Ave | S-CVI/UA | Interpretação |")
    p.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")
    for rotulo, d in [("Juízes especialistas", epmr), ("Juízes da população-alvo", rpms)]:
        p.append(
            "| "
            + rotulo
            + " | "
            + str(d["itens"])
            + " | "
            + str(d["juizes"])
            + " | "
            + num(d["pa"])
            + " | "
            + num(d["pe"])
            + " | "
            + num(d["ac1"])
            + " | "
            + num(d["s_cvi_ave"])
            + " | "
            + num(d["s_cvi_ua"])
            + " | "
            + d["interpretacao"].capitalize()
            + " |"
        )
    p.append("")
    p.append("Fonte: elaborado pelos autores.")
    p.append("")

    p.append("## Tabela 1 (LaTeX)")
    p.append("")
    p.append("```latex")
    p.append("\\begin{table}[h]")
    p.append("\\centering")
    p.append(
        "\\caption{Concordância entre avaliadores segundo o coeficiente AC1 de Gwet.}"
    )
    p.append("\\begin{tabular}{lcccccc}")
    p.append("\\toprule")
    p.append(
        "Painel & Itens & Avaliadores & $P_a$ & $P_e$ & AC1 & Interpretação \\\\"
    )
    p.append("\\midrule")
    for rotulo, d in [("Juízes especialistas", epmr), ("Juízes da população-alvo", rpms)]:
        p.append(
            rotulo
            + " & "
            + str(d["itens"])
            + " & "
            + str(d["juizes"])
            + " & $"
            + num(d["pa"]).replace(",", "{,}").replace("−", "-")
            + "$ & $"
            + num(d["pe"]).replace(",", "{,}").replace("−", "-")
            + "$ & $"
            + num(d["ac1"]).replace(",", "{,}").replace("−", "-")
            + "$ & "
            + d["interpretacao"].capitalize()
            + " \\\\"
        )
    p.append("\\bottomrule")
    p.append("\\end{tabular}")
    p.append("\\end{table}")
    p.append("```")
    p.append("")

    p.append("## Coeficientes que não vão para o corpo do artigo")
    p.append("")
    p.append(
        "Kappa de Fleiss e Alpha de Krippendorff foram calculados como verificação de "
        "robustez e documentam por que o AC1 foi escolhido. Ver `EXPLICACAO.md`, seções 9 e 11."
    )
    p.append("")
    p.append("| Painel | Itens unânimes | Kappa de Fleiss | Alpha de Krippendorff | Pares (n..) |")
    p.append("| :--- | :---: | :---: | :---: | :---: |")
    for rotulo, d in [("Juízes especialistas", epmr), ("Juízes da população-alvo", rpms)]:
        p.append(
            "| "
            + rotulo
            + " | "
            + str(d["itens_unanimes"])
            + " de "
            + str(d["itens"])
            + " | "
            + num(d["kappa"])
            + " | "
            + num(d["alpha"])
            + " | "
            + str(d["n_pares"])
            + " |"
        )
    p.append("")
    p.append(
        "Os dois coeficientes deram negativo nos dois painéis apesar da concordância bruta "
        "alta, que é o comportamento esperado sob prevalência de respostas desbalanceada."
    )
    p.append("")

    return "\n".join(p)


def main():
    epmr = coletar(ac1_epmr, cvi_ac1_epmr, fleiss_kappa_epmr, krippendorff_alpha_epmr)
    rpms = coletar(ac1_rpms, cvi_ac1_rpms, fleiss_kappa_rpms, krippendorff_alpha_rpms)

    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    texto = montar_texto(epmr, rpms, agora)

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_RESULTADOS / ("texto_resultados_" + agora + ".md")
    caminho.write_text(texto, encoding="utf-8")

    print(texto)
    print()
    print("Salvo em: " + str(caminho))


if __name__ == "__main__":
    main()
