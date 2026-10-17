
import streamlit as st
import pandas as pd

from analisador.api import buscar_corrida
from analisador.analise import montar_tabela, calcular_ranking_equipes
from analisador.relatorios import gerar_relatorio


# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Race Data Analyzer",
    page_icon="🏎️",
    layout="wide"
)


# ESTILO E CABEÇALHO
st.title("🏎️ Race Data Analyzer")
st.caption("Dashboard de análise de corridas de Fórmula 1")
st.divider()


# SELEÇÃO DA CORRIDA
st.sidebar.header("Configurações da corrida")

ano = st.sidebar.selectbox(
    "Temporada",
    options=list(range(2026, 1949, -1)),
    index=2
)

etapa = st.sidebar.number_input(
    "Número da etapa",
    min_value=1,
    max_value=30,
    value=16,
    step=1
)

buscar = st.sidebar.button(
    "🔎 Analisar corrida",
    type="primary",
    use_container_width=True
)


# BUSCA E EXIBIÇÃO DOS DADOS
if "corrida_selecionada" not in st.session_state:
    st.session_state.corrida_selecionada = None

if buscar:
    try:
        with st.spinner("Consultando os dados da Fórmula 1..."):
            corrida = buscar_corrida(ano, etapa)

            if corrida is None:
                st.session_state.corrida_selecionada = None
                st.error("Corrida não encontrada para esse ano e etapa.")
            else:
                tabela = montar_tabela(corrida)

                if tabela.empty:
                    st.session_state.corrida_selecionada = None
                    st.warning("Não há resultados disponíveis para essa corrida.")
                else:
                    ranking = calcular_ranking_equipes(tabela)
                    relatorio = gerar_relatorio(
                        tabela, ranking, corrida, ano, etapa
                    )

                    st.session_state.corrida_selecionada = {
                        "corrida": corrida,
                        "tabela": tabela,
                        "ranking": ranking,
                        "relatorio": relatorio,
                        "ano": ano,
                        "etapa": etapa
                    }

    except Exception as erro:
        st.error(f"Não foi possível carregar a corrida: {erro}")


dados = st.session_state.corrida_selecionada


if dados is None:
    st.info(
        "👈 Escolha a temporada e a etapa na barra lateral "
        "e clique em **Analisar corrida**."
    )

    st.subheader("O que você pode analisar?")
    col1, col2, col3 = st.columns(3)

    col1.metric("🏁", "Resultados", "Classificação dos pilotos")
    col2.metric("🏆", "Equipes", "Pontuação por construtor")
    col3.metric("📊", "Estatísticas", "Gráficos e comparações")

else:
    corrida = dados["corrida"]
    tabela = dados["tabela"]
    ranking = dados["ranking"]
    relatorio = dados["relatorio"]
    ano_atual = dados["ano"]
    etapa_atual = dados["etapa"]

    st.header(corrida["raceName"])
    st.write(
        f"**Circuito:** {corrida['Circuit']['circuitName']}  \n"
        f"**Data:** {corrida['date']}  \n"
        f"**Temporada:** {ano_atual} · **Etapa:** {etapa_atual}"
    )

    # INDICADORES PRINCIPAIS
    vencedores = tabela[tabela["Chegada"] == 1]

    if not vencedores.empty:
        vencedor = vencedores.iloc[0]
        nome_vencedor = vencedor["Nome"]
        equipe_vencedora = vencedor["Equipe"]
    else:
        nome_vencedor = "Não identificado"
        equipe_vencedora = "Não identificada"

    equipe_lider = (
        ranking.iloc[0]["Equipe"] if not ranking.empty else "Indisponível"
    )
    pontos_lider = (
        ranking.iloc[0]["Pontos"] if not ranking.empty else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏆 Vencedor", nome_vencedor)
    col2.metric("🏎️ Equipe vencedora", equipe_vencedora)
    col3.metric("👥 Pilotos com resultados", len(tabela))
    col4.metric("📈 Equipe líder em pontos", equipe_lider)

    st.caption(f"Pontuação da equipe líder nesta corrida: {pontos_lider:g} pontos")

    st.divider()

    # ABAS DO DASHBOARD
    aba_resultados, aba_graficos, aba_equipes, aba_relatorio = st.tabs(
        ["🏁 Pilotos", "📊 Gráficos", "🏆 Equipes", "📄 Relatório"]
    )

    with aba_resultados:
        st.subheader("Classificação dos pilotos")

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True
        )

        csv_pilotos = tabela.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar resultados dos pilotos (CSV)",
            data=csv_pilotos,
            file_name=f"f1_{ano_atual}_etapa_{etapa_atual}.csv",
            mime="text/csv"
        )

    with aba_graficos:
        st.subheader("Pontos por piloto")

        pontos_pilotos = tabela.sort_values("Pontos", ascending=True)
        st.bar_chart(
            pontos_pilotos,
            x="Piloto",
            y="Pontos",
            horizontal=True
        )

        st.subheader("Posições ganhas ou perdidas")

        posicoes = tabela.dropna(
            subset=["Posições ganhas"]
        ).sort_values("Posições ganhas", ascending=True)

        if not posicoes.empty:
            st.bar_chart(
                posicoes,
                x="Piloto",
                y="Posições ganhas",
                horizontal=True
            )
        else:
            st.info("Não há dados suficientes sobre posições.")

        st.caption(
            "A variação de posições é calculada pela diferença "
            "entre a posição de largada e a de chegada; não representa "
            "o número exato de ultrapassagens."
        )

        st.subheader("Largada versus chegada")

        comparacao = tabela.dropna(
            subset=["Largada", "Chegada"]
        ).copy()

        if not comparacao.empty:
            comparacao = comparacao.set_index("Piloto")[
                ["Largada", "Chegada"]
            ]
            st.bar_chart(comparacao)
        else:
            st.info("Não há dados suficientes para essa comparação.")

        st.subheader("Voltas mais rápidas")

        tempos = tabela.dropna(
            subset=["Tempo (s)"]
        ).sort_values("Tempo (s)")

        if not tempos.empty:
            st.bar_chart(
                tempos,
                x="Piloto",
                y="Tempo (s)"
            )
            st.caption(
                "Tempo em segundos. A disponibilidade depende dos dados "
                "fornecidos pela API."
            )
        else:
            st.info("Não há tempos de volta rápida disponíveis.")

    with aba_equipes:
        st.subheader("Ranking das equipes")

        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Pontos por equipe")

        ranking_grafico = ranking.sort_values(
            "Pontos", ascending=True
        )

        st.bar_chart(
            ranking_grafico,
            x="Equipe",
            y="Pontos",
            horizontal=True
        )

        csv_equipes = ranking.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar ranking das equipes (CSV)",
            data=csv_equipes,
            file_name=f"equipes_{ano_atual}_etapa_{etapa_atual}.csv",
            mime="text/csv"
        )

    with aba_relatorio:
        st.subheader("Relatório da corrida")
        st.text(relatorio)

        st.download_button(
            "⬇️ Baixar relatório (TXT)",
            data=relatorio.encode("utf-8"),
            file_name=f"relatorio_{ano_atual}_etapa_{etapa_atual}.txt",
            mime="text/plain"
        )


st.divider()
st.caption("Race Data Analyzer 6.0 · Dados fornecidos pela API Jolpica F1")
