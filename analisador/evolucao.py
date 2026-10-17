
"""Funções para analisar a evolução dos pilotos durante uma temporada."""

import pandas as pd


def calcular_evolucao(resultados):
    """Calcula os pontos acumulados de cada piloto corrida por corrida."""

    if resultados.empty:
        return pd.DataFrame()

    dados = resultados.copy()

    # Garante que as corridas sejam ordenadas cronologicamente.
    dados["Data"] = pd.to_datetime(dados["Data"])

    corridas = (
        dados[["Corrida", "Data"]]
        .drop_duplicates()
        .sort_values(["Data", "Corrida"])
        .reset_index(drop=True)
    )

    # Cria uma sequência numérica para identificar cada corrida.
    corridas["Número da corrida"] = range(1, len(corridas) + 1)

    # Soma os pontos caso um piloto tenha mais de um registro na mesma corrida.
    pontos = (
        dados.groupby(["Piloto", "Corrida"], as_index=False)
        ["Pontos"]
        .sum()
    )

    # Associa cada corrida à sua posição cronológica.
    pontos = pontos.merge(
        corridas[["Corrida", "Número da corrida"]],
        on="Corrida",
        how="left",
    )

    pontos = pontos.sort_values(["Piloto", "Número da corrida"])

    # Calcula a soma acumulada dos pontos de cada piloto.
    pontos["Pontos acumulados"] = (
        pontos.groupby("Piloto")["Pontos"].cumsum()
    )

    # Inclui corridas em que o piloto não pontuou.
    todos_pilotos = sorted(dados["Piloto"].unique())

    grade = pd.MultiIndex.from_product(
        [
            todos_pilotos,
            corridas["Corrida"],
        ],
        names=["Piloto", "Corrida"],
    ).to_frame(index=False)

    grade = grade.merge(
        corridas,
        on="Corrida",
        how="left",
    )

    grade = grade.merge(
        pontos[["Piloto", "Corrida", "Pontos"]],
        on=["Piloto", "Corrida"],
        how="left",
    )

    grade["Pontos"] = grade["Pontos"].fillna(0)

    grade = grade.sort_values(["Piloto", "Número da corrida"])

    grade["Pontos acumulados"] = (
        grade.groupby("Piloto")["Pontos"].cumsum()
    )

    return grade
