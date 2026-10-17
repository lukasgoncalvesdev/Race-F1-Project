"""Funções para criar os gráficos da análise."""

import matplotlib.pyplot as plt


def mostrar_graficos(tabela, ranking, corrida, ano):
    """Exibe os gráficos de pontos, posições, largada/chegada e voltas rápidas."""
    # Gráfico 1: pontos por piloto
    dados = tabela.sort_values("Pontos")
    plt.figure(figsize=(11, 6))
    plt.barh(dados["Piloto"], dados["Pontos"])
    plt.title(f"Pontos por piloto - {corrida['raceName']} {ano}")
    plt.xlabel("Pontos")
    plt.ylabel("Piloto")
    plt.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Gráfico 2: posições ganhas ou perdidas
    dados = tabela.dropna(subset=["Posições ganhas"]).sort_values("Posições ganhas")
    if not dados.empty:
        plt.figure(figsize=(11, 6))
        plt.bar(dados["Piloto"], dados["Posições ganhas"])
        plt.axhline(y=0, linewidth=1)
        plt.title(f"Variação de posições - {corrida['raceName']} {ano}")
        plt.xlabel("Piloto")
        plt.ylabel("Posições (+ ganhou / - perdeu)")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Gráfico 3: largada versus chegada
    dados = tabela.dropna(subset=["Largada", "Chegada"]).copy()
    if not dados.empty:
        dados = dados.sort_values("Chegada")
        x = range(len(dados))
        largura = 0.4
        plt.figure(figsize=(12, 6))
        plt.bar([i - largura / 2 for i in x], dados["Largada"], largura, label="Largada")
        plt.bar([i + largura / 2 for i in x], dados["Chegada"], largura, label="Chegada")
        plt.title(f"Largada x chegada - {corrida['raceName']} {ano}")
        plt.xlabel("Piloto")
        plt.ylabel("Posição")
        plt.xticks(list(x), dados["Piloto"], rotation=45)
        plt.gca().invert_yaxis()
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Gráfico 4: pontos por equipe
    if not ranking.empty:
        dados = ranking.sort_values("Pontos")
        plt.figure(figsize=(11, 6))
        plt.barh(dados["Equipe"], dados["Pontos"])
        plt.title(f"Pontos por equipe - {corrida['raceName']} {ano}")
        plt.xlabel("Pontos")
        plt.ylabel("Equipe")
        plt.grid(axis="x", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.show()

    # Gráfico 5: tempos de volta mais rápida disponíveis na API
    dados = tabela.dropna(subset=["Tempo (s)"]).sort_values("Tempo (s)")
    if not dados.empty:
        plt.figure(figsize=(11, 6))
        plt.bar(dados["Piloto"], dados["Tempo (s)"])
        plt.title(f"Voltas mais rápidas - {corrida['raceName']} {ano}")
        plt.xlabel("Piloto")
        plt.ylabel("Tempo (segundos)")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("Não há tempos de volta rápida para comparar.")
