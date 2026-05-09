import pandas as pd
import streamlit as st


def formatar_partidas(estatisticas):
    partidas_formatadas = []

    for partida in estatisticas:
        partidas_formatadas.append({
            "Campeão": partida["champion"],
            "Lane": partida["lane"],
            "Kills": partida["kills"],
            "Deaths": partida["deaths"],
            "Assists": partida["assists"],
            "KDA": round((partida["kills"] + partida["assists"]) / max(partida["deaths"], 1), 2),
            "Duração (min)": partida["duration"],
            "Resultado": "Vitória" if partida["win"] else "Derrota",
            "Modo de Jogo": partida["game_mode"],
        })

    return partidas_formatadas


def exibir_partidas(estatisticas):
    """
    Exibe as partidas em uma tabela interativa no Streamlit.
    """
    df = pd.DataFrame(formatar_partidas(estatisticas))
    st.dataframe(df, use_container_width=True)


def exibir_medias(medias):
    """
    Exibe as estatísticas médias do jogador no Streamlit.
    """
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Média de Kills", medias["media_kills"])
        st.metric("Média de Assists", medias["media_assists"])
        st.metric("KDA Médio", round(medias["media_kda"], 2))

    with col2:
        st.metric("Média de Deaths", medias["media_deaths"])
        st.metric("Duração Média", f"{medias['tempo_medio']} min")

    with col3:
        st.metric("Winrate", f"{medias['winrate']}%")
        st.metric("Vitórias", f"{medias['vitorias']}/{medias.get('total_partidas', 5)}")
        st.metric("Mais Jogado", medias["campeao_mais_usado"])
