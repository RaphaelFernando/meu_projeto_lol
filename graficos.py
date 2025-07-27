import matplotlib.pyplot as plt
import streamlit as st

def plot_kda_bar(partidas):
    kda_values = [(p["kills"] + p["assists"]) / max(p["deaths"], 1) for p in partidas]
    labels = [f"Partida {i+1}" for i in range(len(partidas))]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(labels, kda_values, color='skyblue')
    ax.set_title("KDA por Partida")
    ax.set_ylabel("KDA")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')

    st.pyplot(fig)

def plot_resultados_pizza(partidas):
    vitorias = sum(1 for p in partidas if p["win"])
    derrotas = len(partidas) - vitorias

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.pie(
        [vitorias, derrotas],
        labels=["Vitórias", "Derrotas"],
        autopct="%1.1f%%",
        colors=["green", "red"],
        startangle=90
    )
    ax.axis("equal") 
    ax.set_title("Distribuição de Resultados")

    st.pyplot(fig)
