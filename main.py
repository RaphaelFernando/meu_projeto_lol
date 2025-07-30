import streamlit as st
from api_handler import get_account_by_riot_id, get_last_matches_stats
from processamento import calcular_estatisticas
from exibicao import exibir_partidas, exibir_medias
from graficos import plot_kda_bar, plot_resultados_pizza
from utils import gerar_relatorio, gerar_observacoes

def main():
    st.title("Consulta de Desempenho no League of Legends")

    with st.form("form_riot_id"):
        game_name = st.text_input("Digite o nome do Riot ID (ex: Mugetsu)")
        tag = st.text_input("Digite a tag do Riot ID (ex: Luar)")
        submitted = st.form_submit_button("Buscar")

    if submitted and game_name and tag:
        conta = get_account_by_riot_id(game_name, tag)

        if not conta:
            st.error("Conta Riot não encontrada.")
            return

        puuid = conta["puuid"]  # Oculto para o usuário, usado internamente

        estatisticas = get_last_matches_stats(puuid)

        if not estatisticas:
            st.warning("Não foi possível obter estatísticas.")
            return

        # Calcula as médias primeiro
        medias = calcular_estatisticas(estatisticas)

        # Exibe as médias antes do histórico
        st.subheader("Médias de desempenho")
        exibir_medias(medias)

        st.subheader("Estatísticas das últimas partidas")
        exibir_partidas(estatisticas)

        st.subheader("Visualização Gráfica")
        plot_kda_bar(estatisticas)
        plot_resultados_pizza(estatisticas)

        observacoes = gerar_observacoes(medias)

        # Opcional: salvar relatório
        gerar_relatorio(f"{game_name}#{tag}", medias, observacoes)

if __name__ == "__main__":
    main()