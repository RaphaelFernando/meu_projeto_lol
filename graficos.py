import matplotlib.pyplot as plt

def plot_kda_bar(estatisticas):
    partidas = [f"P{i+1}" for i in range(len(estatisticas))]
    kills = [p["kills"] for p in estatisticas]
    deaths = [p["deaths"] for p in estatisticas]
    assists = [p["assists"] for p in estatisticas]

    x = range(len(partidas))
    plt.figure(figsize=(10, 6))
    plt.bar(x, kills, width=0.2, label="Kills", align='center')
    plt.bar([i + 0.2 for i in x], deaths, width=0.2, label="Deaths")
    plt.bar([i + 0.4 for i in x], assists, width=0.2, label="Assists")

    plt.xticks([i + 0.2 for i in x], partidas)
    plt.ylabel("Quantidade")
    plt.title("Desempenho por Partida")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_resultados_pizza(estatisticas):
    vitorias = sum(1 for p in estatisticas if p["win"])
    derrotas = len(estatisticas) - vitorias

    plt.figure(figsize=(6, 6))
    plt.pie([vitorias, derrotas], labels=["Vitórias", "Derrotas"],
            autopct="%1.1f%%", colors=["#4CAF50", "#F44336"], startangle=90)
    plt.title("Resultado das Últimas Partidas")
    plt.show()