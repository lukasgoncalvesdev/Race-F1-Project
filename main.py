"""Ponto de entrada do Race Data Analyzer 5.0."""

import requests

from analisador.api import buscar_corrida
from analisador.analise import montar_tabela, calcular_ranking_equipes
from analisador.relatorios import gerar_relatorio, salvar_arquivos
from analisador.graficos import mostrar_graficos


def main():
    print("=" * 48)
    print("       RACE DATA ANALYZER 5.0")
    print("       Análise de corridas de Fórmula 1")
    print("=" * 48)

    try:
        ano = int(input("\nDigite o ano da temporada: "))
        etapa = int(input("Digite o número da etapa: "))

        if not 1950 <= ano <= 2100:
            print("Ano inválido.")
            return

        if not 1 <= etapa <= 30:
            print("Número de etapa inválido.")
            return

        print("\nConsultando a API...")
        corrida = buscar_corrida(ano, etapa)

        if corrida is None:
            print("Corrida não encontrada.")
            return

        tabela = montar_tabela(corrida)
        if tabela.empty:
            print("Não há resultados disponíveis.")
            return

        ranking = calcular_ranking_equipes(tabela)
        relatorio = gerar_relatorio(tabela, ranking, corrida, ano, etapa)

        print("\n" + relatorio)
        salvar_arquivos(tabela, ranking, relatorio, ano, etapa)

        print("\nGerando gráficos...")
        mostrar_graficos(tabela, ranking, corrida, ano)
        print("\nAnálise concluída!")

    except ValueError:
        print("Digite números válidos para ano e etapa.")
    except requests.exceptions.RequestException as erro:
        print(f"Erro ao consultar a API: {erro}")
        print("Verifique sua conexão e tente novamente.")
    except (KeyError, IndexError, TypeError) as erro:
        print(f"Erro ao processar os dados: {erro}")


if __name__ == "__main__":
    main()
