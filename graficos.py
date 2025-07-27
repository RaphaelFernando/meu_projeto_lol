import matplotlib.pyplot as plt
import streamlit as st

def plot_kda_bar(partidas):
    partidas_labels = [f"P{i+1}" for i in range(len(partidas))]
    kda_values = [
        round((p['kills'] + p['assists']) / max(1, p['deaths']), 2)
        for p in partidas
    ]

    fig, ax = plt.subplots(figsize=(4, 4))  # Ajuste o tamanho aqui
    ax.bar(partidas_labels, kda_values, color='skyblue')
    ax.set_title("KDA por Partida")
    ax.set_ylabel("KDA")
    ax.set_ylim(0, max(kda_values) + 1)

    st.pyplot(fig)



def plot_resultados_pizza(partidas):
    vitorias = sum(1 for p in partidas if p["win"])
    derrotas = len(partidas) - vitorias

    fig, ax = plt.subplots(figsize=(4, 4))  # <-- ajuste aqui também
    ax.pie([vitorias, derrotas], labels=["Vitórias", "Derrotas"], autopct="%1.1f%%", colors=["green", "red"])
    ax.set_title("Distribuição de Resultados")

    st.pyplot(fig)