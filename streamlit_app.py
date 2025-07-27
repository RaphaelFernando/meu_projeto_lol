import streamlit as st
from entrada import solicitar_riot_id
from api_handler import get_account_by_riot_id, get_last_matches_stats
from processamento import calcular_estatisticas
from exibicao import exibir_partidas, exibir_medias
from graficos import plot_kda_bar, plot_resultados_pizza
from utils import gerar_relatorio, gerar_observacoes

st.set_page_config(page_title="Analisador de Desempenho - LoL", layout="wide")

st.title(" Analisador de Desempenho - League of Legends")

# Inputs para Riot ID
game_name = st.text_input("Digite o nome do Riot ID (ex: Mugetsu)")
tag = st.text_input("Digite a tag do Riot ID (ex: Luar)")

if st.button("Analisar"):
    if not game_name or not tag:
        st.warning("Preencha todos os campos antes de continuar.")
    else:
        conta = get_account_by_riot_id(game_name, tag)

        if not conta:
            st.error(" Conta não encontrada.")
        else:
            puuid = conta["puuid"]
            estatisticas = get_last_matches_stats(puuid)

            if not estatisticas:
                st.error(" Não foi possível obter estatísticas.")
            else:
                st.subheader(" Estatísticas das Últimas Partidas")
                exibir_partidas(estatisticas)

                medias = calcular_estatisticas(estatisticas)
                st.subheader(" Estatísticas Consolidadas")
                exibir_medias(medias)

                st.subheader(" Gráficos de Desempenho")
                plot_kda_bar(estatisticas)
                plot_resultados_pizza(estatisticas)

                st.subheader(" Análise Automática")
                observacoes = gerar_observacoes(medias)
                for obs in observacoes:
                    st.write(f"- {obs}")

                # Gera o relatório .txt e retorna o caminho
                caminho_completo = gerar_relatorio(f"{game_name}#{tag}", medias, observacoes)

                # Botão de download do relatório .txt
                with open(caminho_completo, "rb") as f:
                    st.download_button(
                        label="📥 Baixar Relatório (.txt)",
                        data=f,
                        file_name=caminho_completo.split("\\")[-1],
                        mime="text/plain"
                    )
