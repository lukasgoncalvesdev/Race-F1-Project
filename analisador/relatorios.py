"""Geração e gravação de relatórios e arquivos CSV."""

from pathlib import Path
import pandas as pd

PASTA_RESULTADOS = Path("resultados")


def gerar_relatorio(tabela, ranking, corrida, ano, etapa):
    """Gera um relatório textual com o resumo da corrida."""
    vencedor = tabela[tabela["Chegada"] == 1]
    dados_posicoes = tabela.dropna(subset=["Posições ganhas"])

    if not vencedor.empty:
        nome_vencedor = vencedor.iloc[0]["Nome"]
        equipe_vencedor = vencedor.iloc[0]["Equipe"]
        pontos_vencedor = vencedor.iloc[0]["Pontos"]
    else:
        nome_vencedor = "Não identificado nos dados"
        equipe_vencedor = "Não identificada"
        pontos_vencedor = 0

    if not dados_posicoes.empty:
        maior_avanco = dados_posicoes.loc[dados_posicoes["Posições ganhas"].idxmax()]
        maior_queda = dados_posicoes.loc[dados_posicoes["Posições ganhas"].idxmin()]
        texto_avanco = f"{maior_avanco['Nome']}: {maior_avanco['Posições ganhas']:+.0f} posições"
        texto_queda = f"{maior_queda['Nome']}: {maior_queda['Posições ganhas']:+.0f} posições"
    else:
        texto_avanco = "Dados insuficientes"
        texto_queda = "Dados insuficientes"

    if not ranking.empty:
        melhor_equipe = ranking.iloc[0]["Equipe"]
        pontos_equipe = ranking.iloc[0]["Pontos"]
    else:
        melhor_equipe = "Não identificada"
        pontos_equipe = 0

    linhas = [
        "=" * 55,
        "RACE DATA ANALYZER 5.0",
        "RELATÓRIO DE ANÁLISE DA CORRIDA",
        "=" * 55,
        "",
        f"Grande Prêmio: {corrida['raceName']}",
        f"Temporada: {ano}",
        f"Etapa: {etapa}",
        f"Data: {corrida['date']}",
        f"Circuito: {corrida['Circuit']['circuitName']}",
        "",
        "-" * 55,
        "RESUMO DA CORRIDA",
        "-" * 55,
        f"Pilotos com resultados: {len(tabela)}",
        f"Vencedor: {nome_vencedor}",
        f"Equipe do vencedor: {equipe_vencedor}",
        f"Pontos do vencedor: {pontos_vencedor:g}",
        "",
        f"Maior avanço no grid: {texto_avanco}",
        f"Maior queda no grid: {texto_queda}",
        "",
        "-" * 55,
        "RANKING DE EQUIPES",
        "-" * 55,
    ]

    for _, equipe in ranking.iterrows():
        linhas.append(
            f"{equipe['Equipe']}: {equipe['Pontos']:g} pontos "
            f"({equipe['Pilotos']} pilotos)"
        )

    linhas.extend([
        "",
        f"Equipe com mais pontos: {melhor_equipe}",
        f"Pontos da equipe líder: {pontos_equipe:g}",
        "",
        "-" * 55,
        "CLASSIFICAÇÃO DOS PILOTOS",
        "-" * 55,
    ])

    for _, piloto in tabela.iterrows():
        chegada = (
            f"{int(piloto['Chegada'])}º"
            if pd.notna(piloto["Chegada"])
            else piloto["Situação"]
        )
        linhas.append(
            f"{chegada:>12} | {piloto['Piloto']:<5} | "
            f"{piloto['Nome']:<25} | {piloto['Pontos']:g} pontos"
        )

    linhas.extend([
        "",
        "Observação: posições ganhas são calculadas pela",
        "diferença entre largada e chegada. Isso não equivale",
        "ao número exato de ultrapassagens na pista.",
        "",
        "Dados obtidos pela API Jolpica F1.",
        "=" * 55,
    ])

    return "\n".join(linhas)


def salvar_arquivos(tabela, ranking, relatorio, ano, etapa):
    """Salva classificação, ranking de equipes e relatório de texto."""
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    prefixo = PASTA_RESULTADOS / f"f1_{ano}_etapa_{etapa}"
    arquivo_csv = prefixo.with_suffix(".csv")
    arquivo_equipes = PASTA_RESULTADOS / f"equipes_{ano}_etapa_{etapa}.csv"
    arquivo_txt = PASTA_RESULTADOS / f"relatorio_{ano}_etapa_{etapa}.txt"

    tabela.to_csv(arquivo_csv, index=False, encoding="utf-8-sig")
    ranking.to_csv(arquivo_equipes, index=False, encoding="utf-8-sig")
    arquivo_txt.write_text(relatorio, encoding="utf-8")

    print("\nARQUIVOS SALVOS")
    print(f"Classificação: {arquivo_csv.resolve()}")
    print(f"Ranking de equipes: {arquivo_equipes.resolve()}")
    print(f"Relatório: {arquivo_txt.resolve()}")
