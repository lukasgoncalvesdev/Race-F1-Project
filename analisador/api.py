"""Funções para consultar os dados da Fórmula 1."""

import requests

URL_BASE = "https://api.jolpi.ca/ergast/f1"
CABECALHOS = {"User-Agent": "RaceDataAnalyzer/5.0"}


def buscar_corrida(ano, etapa):
    """Busca os resultados de uma corrida pelo ano e número da etapa."""
    url = f"{URL_BASE}/{ano}/{etapa}/results/?limit=100"

    resposta = requests.get(url, headers=CABECALHOS, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()
    corridas = dados["MRData"]["RaceTable"]["Races"]

    if not corridas:
        return None

    return corridas[0]
