# verificar_concordancia_traducao.py
# Autor: Guilherme Lacerda de Avila
#
# Script de VERIFICAÇÃO INDEPENDENTE dos números de concordância entre
# versões traduzidas do RPMS reportados no artigo (46,4% de concordância
# exata, similaridade média 94,3% etc.).
#
# Diferença pro concordancia_traducao.py: aquele script lê a planilha
# ORIGINAL com o texto de cada tradução (que não pode ser redistribuída,
# é o instrumento do Malm et al., 2020) e calcula tudo do zero. Este
# script lê só o CSV público derivado (dados/concordancia_traducao_por_item.csv),
# que já vem sem nenhuma coluna de texto - só rótulo do item e o
# resultado numérico da comparação (idêntico/diferente, % de
# similaridade). Ou seja, qualquer pessoa com acesso só ao repositório
# público (Zenodo/GitHub) consegue rodar isso e reproduzir os
# percentuais do artigo, sem precisar da planilha privada.
#
# Como rodar:
#   uv run estatistica/verificar_concordancia_traducao.py

import csv
import sys
from pathlib import Path

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT.parent / "dados" / "concordancia_traducao_por_item.csv"


def texto_para_bool(valor):
    return valor.strip().lower() == "true"


def carregar_csv(caminho_csv):
    with caminho_csv.open(encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        linhas = list(leitor)

    resultados = []
    for linha in linhas:
        resultados.append(
            {
                "rotulo": linha["rotulo"],
                "exato_leiga_especialista": texto_para_bool(linha["exato_leiga_especialista"]),
                "exato_leiga_equipe": texto_para_bool(linha["exato_leiga_equipe"]),
                "exato_especialista_equipe": texto_para_bool(linha["exato_especialista_equipe"]),
                "exato_todos": texto_para_bool(linha["exato_todos"]),
                "sim_leiga_especialista": float(linha["sim_leiga_especialista"]),
                "sim_leiga_equipe": float(linha["sim_leiga_equipe"]),
                "sim_especialista_equipe": float(linha["sim_especialista_equipe"]),
                "sim_media": float(linha["sim_media"]),
            }
        )

    return resultados


def calcular_agregados(resultados):
    total = len(resultados)

    return {
        "total_elementos": total,
        "pct_exato_leiga_especialista": 100 * sum(r["exato_leiga_especialista"] for r in resultados) / total,
        "pct_exato_leiga_equipe": 100 * sum(r["exato_leiga_equipe"] for r in resultados) / total,
        "pct_exato_especialista_equipe": 100 * sum(r["exato_especialista_equipe"] for r in resultados) / total,
        "pct_exato_todos": 100 * sum(r["exato_todos"] for r in resultados) / total,
        "sim_media_leiga_especialista": sum(r["sim_leiga_especialista"] for r in resultados) / total,
        "sim_media_leiga_equipe": sum(r["sim_leiga_equipe"] for r in resultados) / total,
        "sim_media_especialista_equipe": sum(r["sim_especialista_equipe"] for r in resultados) / total,
        "sim_media_geral": sum(r["sim_media"] for r in resultados) / total,
    }


def main():
    if not CAMINHO_CSV.exists():
        print("Não achei o CSV público: " + str(CAMINHO_CSV))
        print("Rode primeiro: uv run estatistica/concordancia_traducao.py (precisa da planilha privada)")
        sys.exit(1)

    resultados = carregar_csv(CAMINHO_CSV)
    agregados = calcular_agregados(resultados)

    print("=" * 70)
    print("VERIFICAÇÃO INDEPENDENTE - CONCORDÂNCIA ENTRE VERSÕES TRADUZIDAS")
    print("=" * 70)
    print("Fonte: " + str(CAMINHO_CSV) + " (dado público, sem texto do instrumento)")
    print("Total de elementos: " + str(agregados["total_elementos"]))
    print()
    print(
        "Concordância EXATA (as 3 versões idênticas): "
        + str(round(agregados["pct_exato_todos"], 1))
        + "% dos elementos  <- compare com o artigo (esperado: 46,4%)"
    )
    print("Concordância EXATA leiga×especialista: " + str(round(agregados["pct_exato_leiga_especialista"], 1)) + "%")
    print("Concordância EXATA leiga×equipe: " + str(round(agregados["pct_exato_leiga_equipe"], 1)) + "%")
    print(
        "Concordância EXATA especialista×equipe: "
        + str(round(agregados["pct_exato_especialista_equipe"], 1))
        + "%"
    )
    print()
    print(
        "Similaridade MÉDIA GERAL (os 3 pares juntos): "
        + str(round(agregados["sim_media_geral"], 1))
        + "%  <- compare com o artigo (esperado: 94,3%)"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
