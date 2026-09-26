# verificar_concordancia_retrotraducao.py
# Autor: Guilherme Lacerda de Avila
#
# Script de VERIFICAÇÃO INDEPENDENTE dos números de concordância na
# retrotradução do RPMS reportados no artigo (6,7% de concordância exata
# entre cada retradução e o original, 26,7% entre as duas retraduções).
#
# Mesma lógica do verificar_concordancia_traducao.py: lê só o CSV público
# derivado (dados/concordancia_retrotraducao_por_item.csv), sem nenhuma
# coluna de texto do instrumento (o original de Malm et al., 2020, e as
# retrotraduções não são redistribuídas aqui). Reproduz os percentuais
# do artigo a partir só desse dado público.
#
# Como rodar:
#   uv run estatistica/verificar_concordancia_retrotraducao.py

import csv
import sys
from collections import defaultdict
from pathlib import Path

PASTA_DO_SCRIPT = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_DO_SCRIPT.parent / "dados" / "concordancia_retrotraducao_por_item.csv"


def texto_para_bool(valor):
    return valor.strip().lower() == "true"


def carregar_csv(caminho_csv):
    por_comparacao = defaultdict(list)

    with caminho_csv.open(encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            por_comparacao[linha["comparacao"]].append(
                {
                    "rotulo": linha["rotulo"],
                    "exato": texto_para_bool(linha["exato"]),
                    "similaridade": float(linha["similaridade"]),
                }
            )

    return por_comparacao


def calcular_agregados(resultados):
    total = len(resultados)
    return {
        "total": total,
        "pct_exato": 100 * sum(r["exato"] for r in resultados) / total,
        "sim_media": sum(r["similaridade"] for r in resultados) / total,
    }


def main():
    if not CAMINHO_CSV.exists():
        print("Não achei o CSV público: " + str(CAMINHO_CSV))
        print("Rode primeiro: uv run estatistica/concordancia_retrotraducao.py (precisa das planilhas privadas)")
        sys.exit(1)

    por_comparacao = carregar_csv(CAMINHO_CSV)

    print("=" * 70)
    print("VERIFICAÇÃO INDEPENDENTE - CONCORDÂNCIA NA RETROTRADUÇÃO")
    print("=" * 70)
    print("Fonte: " + str(CAMINHO_CSV) + " (dado público, sem texto do instrumento)")
    print()

    esperado = {
        "Retradução 1 × Original": "6,7% idênticos, 69,6% similaridade média",
        "Retradução 2 × Original": "6,7% idênticos, 66,4% similaridade média",
        "Retradução 1 × Retradução 2": "26,7% idênticos, 83,8% similaridade média",
    }

    for nome, resultados in por_comparacao.items():
        agregado = calcular_agregados(resultados)
        print(
            nome
            + ": "
            + str(agregado["total"])
            + " elementos, "
            + str(round(agregado["pct_exato"], 1))
            + "% idênticos, similaridade média "
            + str(round(agregado["sim_media"], 1))
            + "%"
        )
        if nome in esperado:
            print("  <- compare com o artigo (esperado: " + esperado[nome] + ")")

    print("=" * 70)


if __name__ == "__main__":
    main()
