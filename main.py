import streamlit as st
from api_handler import (
    get_account_by_riot_id,
    get_last_matches_stats,
    get_encrypted_summoner_id_and_platform_hint,  # << usa matchId para sugerir plataforma
    find_platform_by_summoner_id,
    get_ranked_entries,
    probe_rank_across_platforms,                   # debug opcional
    PLATFORMS,
)
from processamento import calcular_estatisticas
from exibicao import exibir_partidas, exibir_medias
from graficos import plot_kda_bar, plot_resultados_pizza
from utils import gerar_relatorio, gerar_observacoes


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


def main():
    st.title("Consulta de Desempenho no League of Legends")

    with st.form("form_riot_id"):
        game_name = st.text_input("Digite o nome do Riot ID (ex: Mugetsu)")
        tag = st.text_input("Digite a tag do Riot ID (ex: Luar)")
        region_label = st.selectbox(
            "Região preferida (usada como prioridade na detecção do Elo)",
            list(PLATFORMS.keys()),
            index=0
        )
        submitted = st.form_submit_button("Buscar")

    if submitted and game_name and tag:
        with st.spinner("Buscando conta..."):
            conta = get_account_by_riot_id(game_name, tag)

        if not conta:
            st.error("Conta Riot não encontrada. Verifique Riot ID e Tag.")
            return

        puuid = conta["puuid"]  # oculto para o usuário

        # ===== Elo / Rank via match-v5 -> league-v4 =====
        st.subheader("Classificação Ranqueada")
        with st.spinner("Obtendo summonerId e plataforma sugerida pelo último match..."):
            enc_id, platform_hint = get_encrypted_summoner_id_and_platform_hint(puuid)

        entries = {}
        if not enc_id:
            st.warning("Não consegui obter o summonerId a partir das partidas recentes.")
        else:
            preferred = platform_hint or PLATFORMS[region_label]
            with st.spinner(f"Carregando Elo (prioridade: {preferred})..."):
                platform, entries = find_platform_by_summoner_id(enc_id, preferred=preferred)

        col1, col2 = st.columns(2)
        render_rank_card(col1, "Solo/Duo", entries.get("RANKED_SOLO_5x5", {}))
        render_rank_card(col2, "Flex", entries.get("RANKED_FLEX_SR", {}))

        # ===== Painel opcional de debug =====
        with st.expander("Debug do Elo (opcional)"):
            if st.button("Rodar diagnóstico de plataformas"):
                diag = probe_rank_across_platforms(puuid, game_name)
                st.write(diag)

        # ===== Partidas e Estatísticas =====
        with st.spinner("Carregando partidas..."):
            estatisticas = get_last_matches_stats(puuid)

        if not estatisticas:
            st.warning("Não foi possível obter estatísticas de partidas.")
            return

        medias = calcular_estatisticas(estatisticas)
        if not medias:
            st.error("Erro ao calcular estatísticas médias.")
            return

        st.subheader("Médias de desempenho")
        exibir_medias(medias)

        st.subheader("Estatísticas das últimas partidas")
        exibir_partidas(estatisticas)

        st.subheader("Visualização Gráfica")
        plot_kda_bar(estatisticas)
        plot_resultados_pizza(estatisticas)

        observacoes = gerar_observacoes(medias)
        if st.button("Gerar relatório .txt"):
            gerar_relatorio(f"{game_name}#{tag}", medias, observacoes)
            st.success("Relatório gerado com sucesso!")


if __name__ == "__main__":
    main()