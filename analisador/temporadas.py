
"""Funções para comparar o desempenho de um piloto entre temporadas."""

import pandas as pd


def resumir_temporada(resultados, piloto):
    """Calcula estatísticas de um piloto em uma temporada."""

    if resultados.empty:
        return {
            "Piloto": piloto,
            "Corridas": 0,
            "Pontos": 0.0,
            "Vitórias": 0,
            "Pódios": 0,
            "Média de pontos": 0.0,
        }

    dados = resultados[resultados["Piloto"] == piloto].copy()

    if dados.empty:
        return {
            "Piloto": piloto,
            "Corridas": 0,
            "Pontos": 0.0,
            "Vitórias": 0,
            "Pódios": 0,
            "Média de pontos": 0.0,
        }

    corridas = dados["Corrida"].nunique()
    pontos = dados["Pontos"].sum()

    return {
        "Piloto": piloto,
        "Corridas": corridas,
        "Pontos": round(float(pontos), 2),
        "Vitórias": int(dados["Vitórias"].sum()),
        "Pódios": int(dados["Pódios"].sum()),
        "Média de pontos": round(float(pontos) / corridas, 2)
        if corridas else 0.0,
    }


def comparar_temporadas(
    resultados_a,
    resultados_b,
    piloto,
    ano_a,
    ano_b,
):
    """Compara as estatísticas de um piloto em dois campeonatos."""

    resumo_a = resumir_temporada(resultados_a, piloto)
    resumo_b = resumir_temporada(resultados_b, piloto)

    indicadores = [
        "Corridas",
        "Pontos",
        "Vitórias",
        "Pódios",
        "Média de pontos",
    ]

    comparacao = pd.DataFrame({
        str(ano_a): [resumo_a[item] for item in indicadores],
        str(ano_b): [resumo_b[item] for item in indicadores],
    }, index=indicadores)

    comparacao.index.name = "Indicador"

    return comparacao
