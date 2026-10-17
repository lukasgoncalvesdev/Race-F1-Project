
import streamlit as st
import pandas as pd

from analisador.api import buscar_corrida
from analisador.analise import montar_tabela, calcular_ranking_equipes
from analisador.relatorios import gerar_relatorio
from analisador.comparacao import (
    buscar_resultados_temporada,
    comparar_pilotos,
    comparar_companheiros,
)
from analisador.evolucao import calcular_evolucao


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Race Data Analyzer",
    page_icon="🏎️",
    layout="wide",
)


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🏎️ Race Data Analyzer")
st.caption("Dashboard de análise de corridas de Fórmula 1")
st.divider()


# ============================================================
# BARRA LATERAL — CORRIDA
# ============================================================

st.sidebar.header("Configurações da corrida")

ano = st.sidebar.selectbox(
    "Temporada",
    options=list(range(2026, 1949, -1)),
    index=2,
)

etapa = st.sidebar.number_input(
    "Número da etapa",
    min_value=1,
    max_value=30,
    value=16,
    step=1,
)

buscar = st.sidebar.button(
    "🔎 Analisar corrida",
    type="primary",
    use_container_width=True,
)


# ============================================================
# BUSCA DA CORRIDA SELECIONADA
# ============================================================

if "corrida_selecionada" not in st.session_state:
    st.session_state.corrida_selecionada = None


if buscar:
    try:
        with st.spinner("Consultando os dados da Fórmula 1..."):
            corrida = buscar_corrida(ano, etapa)

            if corrida is None:
                st.session_state.corrida_selecionada = None
                st.error(
                    "Corrida não encontrada para esse ano e etapa."
                )
            else:
                tabela = montar_tabela(corrida)

                if tabela.empty:
                    st.session_state.corrida_selecionada = None
                    st.warning(
                        "Não há resultados disponíveis para essa corrida."
                    )
                else:
                    ranking = calcular_ranking_equipes(tabela)

                    relatorio = gerar_relatorio(
                        tabela,
                        ranking,
                        corrida,
                        ano,
                        etapa,
                    )

                    st.session_state.corrida_selecionada = {
                        "corrida": corrida,
                        "tabela": tabela,
                        "ranking": ranking,
                        "relatorio": relatorio,
                        "ano": ano,
                        "etapa": etapa,
                    }

    except Exception as erro:
        st.error(f"Não foi possível carregar a corrida: {erro}")


dados = st.session_state.corrida_selecionada


# ============================================================
# TELA INICIAL
# ============================================================

if dados is None:
    st.info(
        "👈 Escolha a temporada e a etapa na barra lateral "
        "e clique em **Analisar corrida**."
    )

    st.subheader("O que você pode analisar?")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🏁 Resultados",
        "Pilotos",
        "Classificação da corrida",
    )

    col2.metric(
        "🏆 Equipes",
        "Construtores",
        "Pontuação por equipe",
    )

    col3.metric(
        "📊 Estatísticas",
        "Gráficos",
        "Dados e comparações",
    )

    st.divider()
    st.subheader("⚔️ Duelo de Pilotos")
    st.write(
        "Carregue uma corrida para acessar as abas de análise, "
        "incluindo o duelo e a evolução dos pilotos."
    )


# ============================================================
# DASHBOARD DA CORRIDA
# ============================================================

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

    # --------------------------------------------------------
    # INDICADORES PRINCIPAIS
    # --------------------------------------------------------

    vencedores = tabela[tabela["Chegada"] == 1]

    if not vencedores.empty:
        vencedor = vencedores.iloc[0]
        nome_vencedor = vencedor["Nome"]
        equipe_vencedora = vencedor["Equipe"]
    else:
        nome_vencedor = "Não identificado"
        equipe_vencedora = "Não identificada"

    equipe_lider = (
        ranking.iloc[0]["Equipe"]
        if not ranking.empty
        else "Indisponível"
    )

    pontos_lider = (
        ranking.iloc[0]["Pontos"]
        if not ranking.empty
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🏁 Vencedor", nome_vencedor)
    col2.metric("🏎️ Equipe vencedora", equipe_vencedora)
    col3.metric("👥 Pilotos com resultados", len(tabela))
    col4.metric("📈 Equipe líder em pontos", equipe_lider)

    st.caption(
        f"Pontuação da equipe líder nesta corrida: "
        f"{pontos_lider:g} pontos"
    )

    st.divider()

    # --------------------------------------------------------
    # ABAS DO DASHBOARD
    # --------------------------------------------------------

    (
        aba_resultados,
        aba_graficos,
        aba_equipes,
        aba_relatorio,
        aba_duelo,
        aba_evolucao,
    ) = st.tabs(
        [
            "🏁 Pilotos",
            "📊 Gráficos",
            "🏆 Equipes",
            "📄 Relatório",
            "⚔️ Duelo de Pilotos",
            "📈 Evolução dos Pilotos",
        ]
    )

    # ========================================================
    # ABA 1 — RESULTADOS
    # ========================================================

    with aba_resultados:
        st.subheader("Classificação dos pilotos")

        st.dataframe(
            tabela,
            use_container_width=True,
            hide_index=True,
        )

        csv_pilotos = tabela.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar resultados dos pilotos (CSV)",
            data=csv_pilotos,
            file_name=f"f1_{ano_atual}_etapa_{etapa_atual}.csv",
            mime="text/csv",
        )

    # ========================================================
    # ABA 2 — GRÁFICOS
    # ========================================================

    with aba_graficos:
        st.subheader("Pontos por piloto")

        pontos_pilotos = tabela.sort_values(
            "Pontos",
            ascending=True,
        )

        st.bar_chart(
            pontos_pilotos,
            x="Piloto",
            y="Pontos",
            horizontal=True,
        )

        st.subheader("Posições ganhas ou perdidas")

        posicoes = tabela.dropna(
            subset=["Posições ganhas"]
        ).sort_values(
            "Posições ganhas",
            ascending=True,
        )

        if not posicoes.empty:
            st.bar_chart(
                posicoes,
                x="Piloto",
                y="Posições ganhas",
                horizontal=True,
            )
        else:
            st.info(
                "Não há dados suficientes sobre posições."
            )

        st.caption(
            "A variação de posições é calculada pela diferença "
            "entre a posição de largada e a de chegada; não "
            "representa o número exato de ultrapassagens."
        )

        st.subheader("Largada versus chegada")

        comparacao_largada = tabela.dropna(
            subset=["Largada", "Chegada"]
        ).copy()

        if not comparacao_largada.empty:
            comparacao_largada = comparacao_largada.set_index(
                "Piloto"
            )[["Largada", "Chegada"]]

            st.bar_chart(comparacao_largada)
        else:
            st.info(
                "Não há dados suficientes para essa comparação."
            )

        st.subheader("Voltas mais rápidas")

        tempos = tabela.dropna(
            subset=["Tempo (s)"]
        ).sort_values("Tempo (s)")

        if not tempos.empty:
            st.bar_chart(
                tempos,
                x="Piloto",
                y="Tempo (s)",
            )

            st.caption(
                "Tempo em segundos. A disponibilidade depende "
                "dos dados fornecidos pela API."
            )
        else:
            st.info(
                "Não há tempos de volta rápida disponíveis."
            )

    # ========================================================
    # ABA 3 — EQUIPES
    # ========================================================

    with aba_equipes:
        st.subheader("Ranking das equipes")

        st.dataframe(
            ranking,
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Pontos por equipe")

        ranking_grafico = ranking.sort_values(
            "Pontos",
            ascending=True,
        )

        st.bar_chart(
            ranking_grafico,
            x="Equipe",
            y="Pontos",
            horizontal=True,
        )

        csv_equipes = ranking.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar ranking das equipes (CSV)",
            data=csv_equipes,
            file_name=f"equipes_{ano_atual}_etapa_{etapa_atual}.csv",
            mime="text/csv",
        )

    # ========================================================
    # ABA 4 — RELATÓRIO
    # ========================================================

    with aba_relatorio:
        st.subheader("Relatório da corrida")

        st.text(relatorio)

        st.download_button(
            "⬇️ Baixar relatório (TXT)",
            data=relatorio.encode("utf-8"),
            file_name=f"relatorio_{ano_atual}_etapa_{etapa_atual}.txt",
            mime="text/plain",
        )

    # ========================================================
    # ABA 5 — DUELO DE PILOTOS
    # ========================================================

    with aba_duelo:
        st.subheader("⚔️ Duelo de Pilotos")

        st.write(
            "Compare pontos, vitórias, pódios e resultados "
            "de dois pilotos em uma temporada completa."
        )

        temporada_duelo = st.selectbox(
            "Temporada do duelo",
            options=list(range(2025, 1949, -1)),
            index=0,
            key="temporada_duelo",
        )

        try:
            with st.spinner(
                f"Buscando resultados de {temporada_duelo}..."
            ):
                resultados_temporada = buscar_resultados_temporada(
                    temporada_duelo
                )

            if resultados_temporada.empty:
                st.warning(
                    "Não há resultados disponíveis para essa temporada."
                )
            else:
                pilotos = sorted(
                    resultados_temporada["Piloto"]
                    .dropna()
                    .unique()
                )

                if len(pilotos) < 2:
                    st.warning(
                        "Não há pilotos suficientes para comparar."
                    )
                else:
                    col_a, col_b = st.columns(2)

                    with col_a:
                        piloto_a = st.selectbox(
                            "Primeiro piloto",
                            pilotos,
                            index=0,
                            key="piloto_duelo_a",
                        )

                    with col_b:
                        indice_b = min(1, len(pilotos) - 1)

                        piloto_b = st.selectbox(
                            "Segundo piloto",
                            pilotos,
                            index=indice_b,
                            key="piloto_duelo_b",
                        )

                    if piloto_a == piloto_b:
                        st.warning(
                            "Escolha dois pilotos diferentes."
                        )
                    else:
                        resumo = comparar_pilotos(
                            resultados_temporada,
                            piloto_a,
                            piloto_b,
                        )

                        if resumo.empty:
                            st.warning(
                                "Não foi possível calcular a comparação."
                            )
                        else:
                            st.subheader(
                                "Estatísticas da temporada"
                            )

                            col1, col2 = st.columns(2)

                            with col1:
                                st.markdown(f"### {piloto_a}")

                                st.metric(
                                    "Pontos",
                                    f"{resumo.loc[piloto_a, 'Pontos']:g}",
                                )

                                st.metric(
                                    "Vitórias",
                                    int(
                                        resumo.loc[
                                            piloto_a, "Vitórias"
                                        ]
                                    ),
                                )

                                st.metric(
                                    "Pódios",
                                    int(
                                        resumo.loc[
                                            piloto_a, "Pódios"
                                        ]
                                    ),
                                )

                            with col2:
                                st.markdown(f"### {piloto_b}")

                                st.metric(
                                    "Pontos",
                                    f"{resumo.loc[piloto_b, 'Pontos']:g}",
                                )

                                st.metric(
                                    "Vitórias",
                                    int(
                                        resumo.loc[
                                            piloto_b, "Vitórias"
                                        ]
                                    ),
                                )

                                st.metric(
                                    "Pódios",
                                    int(
                                        resumo.loc[
                                            piloto_b, "Pódios"
                                        ]
                                    ),
                                )

                            st.subheader("Comparação de pontos")

                            grafico = resumo[
                                ["Pontos"]
                            ].sort_values("Pontos")

                            st.bar_chart(
                                grafico,
                                horizontal=True,
                            )

                            st.subheader("Confronto direto")

                            confronto = comparar_companheiros(
                                resultados_temporada,
                                piloto_a,
                                piloto_b,
                            )

                            c1, c2, c3 = st.columns(3)

                            c1.metric(
                                f"Vitórias de {piloto_a}",
                                confronto["Piloto A"],
                            )

                            c2.metric(
                                f"Vitórias de {piloto_b}",
                                confronto["Piloto B"],
                            )

                            c3.metric(
                                "Empates",
                                confronto["Empates"],
                            )

                            st.caption(
                                "O confronto considera apenas corridas "
                                "em que ambos têm posição registrada. "
                                "Ele compara posições finais, não "
                                "classificações de sábado."
                            )

                            st.dataframe(
                                resumo,
                                use_container_width=True,
                            )

                            st.download_button(
                                "⬇️ Baixar comparação (CSV)",
                                data=resumo.to_csv().encode(
                                    "utf-8-sig"
                                ),
                                file_name=(
                                    f"duelo_f1_{temporada_duelo}.csv"
                                ),
                                mime="text/csv",
                            )

        except Exception as erro:
            st.error(
                f"Não foi possível carregar a comparação: {erro}"
            )

    # ========================================================
    # ABA 6 — EVOLUÇÃO DOS PILOTOS
    # ========================================================

    with aba_evolucao:
        st.subheader("📈 Evolução dos Pilotos")

        st.write(
            "Acompanhe a pontuação acumulada dos pilotos "
            "corrida após corrida durante uma temporada."
        )

        temporada_evolucao = st.selectbox(
            "Temporada da evolução",
            options=list(range(2025, 1949, -1)),
            index=0,
            key="temporada_evolucao",
        )

        try:
            with st.spinner(
                f"Calculando a evolução da temporada "
                f"{temporada_evolucao}..."
            ):
                resultados_evolucao = buscar_resultados_temporada(
                    temporada_evolucao
                )

                evolucao = calcular_evolucao(
                    resultados_evolucao
                )

            if evolucao.empty:
                st.warning(
                    "Não há dados disponíveis para essa temporada."
                )
            else:
                pilotos_disponiveis = sorted(
                    evolucao["Piloto"].unique()
                )

                pilotos_selecionados = st.multiselect(
                    "Selecione os pilotos que deseja acompanhar",
                    options=pilotos_disponiveis,
                    default=pilotos_disponiveis[:5],
                    key="pilotos_evolucao",
                )

                if not pilotos_selecionados:
                    st.info("Selecione pelo menos um piloto.")
                else:
                    dados_grafico = evolucao[
                        evolucao["Piloto"].isin(
                            pilotos_selecionados
                        )
                    ]

                    grafico_evolucao = dados_grafico.pivot(
                        index="Número da corrida",
                        columns="Piloto",
                        values="Pontos acumulados",
                    )

                    nomes_corridas = (
                        evolucao[
                            ["Número da corrida", "Corrida"]
                        ]
                        .drop_duplicates()
                        .sort_values("Número da corrida")
                        .set_index("Número da corrida")["Corrida"]
                    )

                    grafico_evolucao.index = [
                        nomes_corridas.loc[numero]
                        for numero in grafico_evolucao.index
                    ]

                    st.line_chart(
                        grafico_evolucao,
                        x_label="Corrida",
                        y_label="Pontos acumulados",
                    )

                    st.subheader("Classificação acumulada")

                    ultima_corrida = evolucao[
                        "Número da corrida"
                    ].max()

                    classificacao = evolucao[
                        evolucao["Número da corrida"]
                        == ultima_corrida
                    ][
                        ["Piloto", "Pontos acumulados"]
                    ].copy()

                    classificacao = classificacao.sort_values(
                        "Pontos acumulados",
                        ascending=False,
                    ).reset_index(drop=True)

                    classificacao.index = (
                        classificacao.index + 1
                    )
                    classificacao.index.name = "Posição"

                    st.dataframe(
                        classificacao,
                        use_container_width=True,
                    )

                    st.download_button(
                        "⬇️ Baixar evolução completa (CSV)",
                        data=evolucao.to_csv(
                            index=False
                        ).encode("utf-8-sig"),
                        file_name=(
                            f"evolucao_f1_{temporada_evolucao}.csv"
                        ),
                        mime="text/csv",
                    )

        except Exception as erro:
            st.error(
                f"Não foi possível calcular a evolução: {erro}"
            )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()
st.caption(
    "Race Data Analyzer 9.0 · Dados fornecidos pela API Jolpica F1"
)
