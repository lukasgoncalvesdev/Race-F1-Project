
"""Funções para comparar pilotos de uma temporada de F1."""

import requests
import pandas as pd

from analisador.api import URL_BASE, CABECALHOS


def buscar_resultados_temporada(ano):
    """Busca os resultados disponíveis de todas as corridas de uma temporada."""
    url = f"{URL_BASE}/{ano}/results/"

    resposta = requests.get(
        url,
        headers=CABECALHOS,
        params={"limit": 1000},
        timeout=30,
    )
    resposta.raise_for_status()

    dados = resposta.json()
    corridas = dados["MRData"]["RaceTable"]["Races"]

    resultados = []

    for corrida in corridas:
        for resultado in corrida.get("Results", []):
            piloto = resultado["Driver"]
            equipe = resultado["Constructor"]

            resultados.append({
                "Corrida": corrida["raceName"],
                "Data": corrida["date"],
                "Piloto": (
                    f'{piloto["givenName"]} {piloto["familyName"]}'
                ),
                "Código": piloto.get("code", piloto["driverId"]),
                "Equipe": equipe["name"],
                "Posição": int(resultado["position"]),
                "Pontos": float(resultado["points"]),
                "Vitórias": int(resultado["position"]) == 1,
                "Pódios": int(resultado["position"]) <= 3,
            })

    return pd.DataFrame(resultados)


def comparar_pilotos(resultados, piloto_a, piloto_b):
    """Gera estatísticas e comparação direta entre dois pilotos."""
    if resultados.empty:
        return pd.DataFrame()

    dados = resultados[
        resultados["Piloto"].isin([piloto_a, piloto_b])
    ].copy()

    if dados.empty:
        return pd.DataFrame()

    resumo = dados.groupby("Piloto").agg(
        Corridas=("Corrida", "nunique"),
        Pontos=("Pontos", "sum"),
        Vitórias=("Vitórias", "sum"),
        Pódios=("Pódios", "sum"),
    )

    resumo["Média de pontos"] = (
        resumo["Pontos"] / resumo["Corridas"]
    ).round(2)

    return resumo.reindex([piloto_a, piloto_b]).fillna(0)


def comparar_companheiros(resultados, piloto_a, piloto_b):
    """Conta em quantas corridas cada piloto terminou à frente do outro."""
    if resultados.empty:
        return {"Piloto A": 0, "Piloto B": 0, "Empates": 0}

    dados = resultados[
        resultados["Piloto"].isin([piloto_a, piloto_b])
    ]

    confronto = dados.pivot_table(
        index="Corrida",
        columns="Piloto",
        values="Posição",
        aggfunc="min",
    )

    if piloto_a not in confronto.columns or piloto_b not in confronto.columns:
        return {"Piloto A": 0, "Piloto B": 0, "Empates": 0}

    confronto = confronto.dropna(subset=[piloto_a, piloto_b])

    return {
        "Piloto A": int(
            (confronto[piloto_a] < confronto[piloto_b]).sum()
        ),
        "Piloto B": int(
            (confronto[piloto_b] < confronto[piloto_a]).sum()
        ),
        "Empates": int(
            (confronto[piloto_a] == confronto[piloto_b]).sum()
        ),
    }
