import streamlit as st

from api_handler import (
    PLATFORMS,
    get_latest_match_summary,
    get_ranked_entries_by_puuid,
    get_recent_match_summaries,
    probe_rank_across_platforms,
)
from exibicao import exibir_medias
from processamento import calcular_estatisticas
from riot.exceptions import (
    RiotApiError,
    RiotAuthenticationError,
    RiotForbiddenError,
    RiotNotFoundError,
    RiotRateLimitError,
    RiotServerError,
    RiotTimeoutError,
)


def render_rank_card(col, title, entry):
    """Card de Elo/LP/Winrate para uma fila."""
    with col:
        box = st.container(border=True)
        with box:
            st.markdown(f"**{title}**")
            if not entry:
                st.write("Unranked")
                return

            tier_div = f"{entry['tier'].title()} {entry['rank']}".strip()
            st.markdown(f"**{tier_div}**")
            c1, c2, c3 = st.columns(3)
            c1.metric("LP", entry["lp"])
            c2.metric("Winrate", f"{entry['winrate']}%")
            c3.metric("W-L", f"{entry['wins']}-{entry['losses']}")


def render_latest_match_summary(summary):
    participant = summary.get("participant")
    summoner = summary.get("summoner") or {}
    result = "Vitória" if participant.get("win") else "Derrota"

    st.subheader("Resumo da partida mais recente")
    c1, c2, c3 = st.columns(3)
    c1.metric("Riot ID", summary["riot_id"])
    c2.metric("Summoner Level", summoner.get("summonerLevel", "N/A"))
    c3.metric("Resultado", result)

    c4, c5, c6 = st.columns(3)
    c4.metric("Match ID", summary["match_id"])
    c5.metric("Champion", participant["champion"])
    c6.metric("K/D/A", f"{participant['kills']}/{participant['deaths']}/{participant['assists']}")


def render_recent_matches_table(match_summaries):
    rows = []
    for match in match_summaries:
        duration_seconds = match.get("game_duration") or 0
        rows.append(
            {
                "Resultado": "Vitória" if match["win"] else "Derrota",
                "Champion": match["champion"],
                "K/D/A": f"{match['kills']}/{match['deaths']}/{match['assists']}",
                "Duração": f"{duration_seconds // 60} min",
                "Modo/Fila": f"{match.get('game_mode', '')} / {match.get('queue_id', 'N/A')}",
                "Match ID": match["match_id"],
            }
        )

    st.subheader("Histórico recente")
    st.dataframe(rows, use_container_width=True)


def normalizar_historico_para_estatisticas(match_summaries):
    estatisticas = []
    for match in match_summaries:
        estatisticas.append(
            {
                "champion": match["champion"],
                "kills": match["kills"],
                "deaths": match["deaths"],
                "assists": match["assists"],
                "win": match["win"],
                "duration": (match.get("game_duration") or 0) // 60,
            }
        )
    return estatisticas


def show_riot_error(error):
    if isinstance(error, RiotAuthenticationError):
        st.error("Chave Riot inválida, ausente ou expirada. Verifique RIOT_API_KEY no .env.")
    elif isinstance(error, RiotForbiddenError):
        st.error("Acesso negado pela Riot API. A chave pode estar expirada ou sem permissão.")
    elif isinstance(error, RiotNotFoundError):
        st.error("Riot ID não encontrado. Verifique gameName e tagLine.")
    elif isinstance(error, RiotRateLimitError):
        st.warning("Rate limit da Riot atingido. Aguarde um pouco e tente novamente.")
    elif isinstance(error, RiotTimeoutError):
        st.warning("A Riot API demorou para responder. Tente novamente.")
    elif isinstance(error, RiotServerError):
        st.warning("A Riot API retornou erro temporário. Tente novamente mais tarde.")
    elif isinstance(error, RiotApiError):
        st.error(f"Erro ao consultar Riot API: {error}")
    else:
        st.error("Erro inesperado ao consultar Riot API.")


def main():
    st.title("Consulta de Desempenho no League of Legends")

    with st.form("form_riot_id"):
        game_name = st.text_input("Digite o nome do Riot ID (ex: Mugetsu)")
        tag = st.text_input("Digite a tag do Riot ID (ex: Luar)")
        region_label = st.selectbox(
            "Região preferida (usada como prioridade na detecção do Elo)",
            list(PLATFORMS.keys()),
            index=0,
        )
        submitted = st.form_submit_button("Buscar")

    if not submitted:
        return

    if not game_name or not tag:
        st.warning("Preencha gameName e tagLine antes de buscar.")
        return

    try:
        with st.spinner("Carregando resumo da Riot API..."):
            latest_summary = get_latest_match_summary(game_name, tag, count=10, strict=True)
    except (
        RiotAuthenticationError,
        RiotForbiddenError,
        RiotNotFoundError,
        RiotRateLimitError,
        RiotTimeoutError,
        RiotServerError,
        RiotApiError,
    ) as error:
        show_riot_error(error)
        return

    if not latest_summary:
        st.error("Não foi possível montar o resumo para este Riot ID.")
        return

    if not latest_summary.get("match_ids"):
        st.warning("Nenhuma partida encontrada para este Riot ID.")
        return

    if not latest_summary.get("participant"):
        st.warning("Não encontrei o jogador na partida mais recente retornada pela Riot.")
        return

    puuid = latest_summary["puuid"]
    render_latest_match_summary(latest_summary)

    with st.spinner("Carregando histórico recente..."):
        recent_matches = get_recent_match_summaries(
            game_name,
            tag,
            count=10,
            routing=None,
            platform=latest_summary.get("region"),
        )

    if not recent_matches:
        st.warning("Não foi possível carregar o histórico recente de partidas.")
        return

    failed_count = recent_matches[0].get("failed_count", 0)
    if failed_count:
        st.warning(f"{failed_count} partida(s) não puderam ser carregadas, mas o restante foi exibido.")
    render_recent_matches_table(recent_matches)

    st.subheader("Classificação Ranqueada")
    preferred = latest_summary.get("region") or PLATFORMS[region_label]
    with st.spinner(f"Carregando Elo (prioridade: {preferred})..."):
        entries = get_ranked_entries_by_puuid(puuid, platform=preferred)

    if not entries:
        st.info("Rank indisponível ou jogador sem filas ranqueadas recentes.")

    col1, col2 = st.columns(2)
    render_rank_card(col1, "Solo/Duo", entries.get("RANKED_SOLO_5x5", {}))
    render_rank_card(col2, "Flex", entries.get("RANKED_FLEX_SR", {}))

    with st.expander("Debug do Elo (opcional)"):
        if st.button("Rodar diagnóstico de plataformas"):
            diag = probe_rank_across_platforms(puuid, game_name)
            st.write(diag)

    estatisticas = normalizar_historico_para_estatisticas(recent_matches)
    medias = calcular_estatisticas(estatisticas)
    if not medias:
        st.error("Erro ao calcular estatísticas médias.")
        return

    st.subheader("Médias de desempenho")
    exibir_medias(medias)


if __name__ == "__main__":
    main()
