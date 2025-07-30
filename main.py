import streamlit as st
from api_handler import get_account_by_riot_id, get_last_matches_stats
from processamento import calcular_estatisticas
from exibicao import exibir_partidas, exibir_medias
from graficos import plot_kda_bar, plot_resultados_pizza
from utils import gerar_relatorio, gerar_observacoes

def main():
    st.title("Consulta de Desempenho no League of Legends 🎮")

    with st.form("form_riot_id"):
        game_name = st.text_input("Digite o nome do Riot ID (ex: Mugetsu)")
        tag = st.text_input("Digite a tag do Riot ID (ex: Luar)")
        submitted = st.form_submit_button("Buscar")

    if submitted and game_name and tag:
        conta = get_account_by_riot_id(game_name, tag)

        if not conta:
            st.error("Conta Riot não encontrada.")
            return

        puuid = conta["puuid"]  # Utilizado internamente, mas não exibido

        estatisticas = get_last_matches_stats(puuid)

        if not estatisticas:
            st.warning("Não foi possível obter estatísticas.")
            return

        st.subheader("📊 Estatísticas das últimas partidas")
        exibir_partidas(estatisticas)

        medias = calcular_estatisticas(estatisticas)

        st.subheader("📈 Médias de desempenho")
        exibir_medias(medias)

        st.subheader("📉 Visualização Gráfica")
        plot_kda_bar(estatisticas)
        plot_resultados_pizza(estatisticas)

        observacoes = gerar_observacoes(medias)

        if st.button("📄 Gerar relatório em .txt"):
            gerar_relatorio(f"{game_name}#{tag}", medias, observacoes)
            st.success("Relatório gerado com sucesso!")

if __name__ == "__main__":
    main()