"""Funções para organizar os resultados e calcular estatísticas."""

import pandas as pd


def converter_tempo(tempo):
    """Converte um tempo no formato MM:SS.mmm para segundos."""
    if not tempo:
        return None

    try:
        minutos, segundos = tempo.split(":")
        return int(minutos) * 60 + float(segundos)
    except (ValueError, AttributeError):
        return None


def montar_tabela(corrida):
    """Organiza os resultados dos pilotos em uma tabela pandas."""
    resultados = []

    for item in corrida["Results"]:
        piloto = item["Driver"]
        equipe = item.get("Constructor", {})
        volta = item.get("FastestLap", {})

        tempo = volta.get("Time", {}).get("time")
        posicao = item.get("position", "")
        grid = item.get("grid", "")

        chegada = int(posicao) if posicao.isdigit() else None
        largada = int(grid) if grid.isdigit() and int(grid) > 0 else None

        if largada is not None and chegada is not None:
            posicoes_ganhas = largada - chegada
        else:
            posicoes_ganhas = None

        resultados.append({
            "Piloto": piloto.get("code") or piloto["driverId"],
            "Nome": piloto["givenName"] + " " + piloto["familyName"],
            "Equipe": equipe.get("name", "Não informada"),
            "Largada": largada,
            "Chegada": chegada,
            "Posições ganhas": posicoes_ganhas,
            "Pontos": float(item.get("points", 0)),
            "Voltas": int(item.get("laps", 0)),
            "Situação": item.get("status", "Indisponível"),
            "Volta mais rápida": tempo or "Indisponível",
            "Tempo (s)": converter_tempo(tempo),
        })

    tabela = pd.DataFrame(resultados)
    if not tabela.empty:
        tabela = tabela.sort_values("Chegada", na_position="last")

    return tabela


def calcular_ranking_equipes(tabela):
    """Soma os pontos dos pilotos de cada equipe na corrida."""
    ranking = (
        tabela.groupby("Equipe", as_index=False)
        .agg(Pontos=("Pontos", "sum"), Pilotos=("Piloto", "count"))
        .sort_values("Pontos", ascending=False)
    )
    return ranking
