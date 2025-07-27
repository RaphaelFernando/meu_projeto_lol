import os
from datetime import datetime

def gerar_observacoes(medias):
    """
    Gera observações e dicas com base nas estatísticas médias do jogador.
    """
    observacoes = []

    if medias["media_deaths"] > 8:
        observacoes.append("⚠️ Alta média de mortes. Considere jogar de forma mais segura.")

    if medias["media_kda"] >= 3:
        observacoes.append("✅ Excelente KDA! Mostra bom equilíbrio entre agressividade e sobrevivência.")
    elif medias["media_kda"] < 1.5:
        observacoes.append("⚠️ KDA baixo. Pode indicar mortes em excesso ou poucas participações em abates.")

    if medias["winrate"] >= 60:
        observacoes.append("🏆 Boa taxa de vitórias! Mantenha o ritmo.")
    elif medias["winrate"] < 40:
        observacoes.append("🔄 Winrate abaixo do ideal. Reavalie estratégias ou funções utilizadas.")

    if medias["media_assists"] >= 8:
        observacoes.append("🤝 Alta média de assistências. Boa participação em equipe!")

    if medias["tempo_medio"] > 35:
        observacoes.append("⌛ Partidas muito longas. Considere estratégias para fechar o jogo mais cedo.")

    if "campeao_mais_usado" in medias:
        observacoes.append(f"💡 Campeão mais utilizado: {medias['campeao_mais_usado']}. Pode ser sua especialidade.")

    return observacoes


def gerar_relatorio(nome_jogador, estatisticas, observacoes=None, caminho="relatorios"):
    """
    Gera um relatório de desempenho em formato .txt com base nas estatísticas e observações.
    """

    # Garante que o diretório "relatorios" exista
    os.makedirs(caminho, exist_ok=True)

    # Nome do arquivo com timestamp
    nome_arquivo = f"{nome_jogador.replace('#', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho_completo = os.path.join(caminho, nome_arquivo)

    # Conteúdo do relatório
    conteudo = [
        "Relatório de Desempenho - League of Legends",
        f"Jogador: {nome_jogador}",
        f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "",
        "Resumo das 5 últimas partidas:",
        f"- Campeão mais usado: {estatisticas.get('campeao_mais_usado', 'N/A')}",
        f"- Winrate: {estatisticas.get('winrate', 0.0)}%",
        f"- Média de Kills: {estatisticas.get('media_kills', 0)}",
        f"- Média de Deaths: {estatisticas.get('media_deaths', 0)}",
        f"- Média de Assists: {estatisticas.get('media_assists', 0)}",
        f"- KDA médio: {estatisticas.get('media_kda', 0)}",
        f"- Tempo médio de jogo: {estatisticas.get('tempo_medio', 0)} minutos"
    ]

    if observacoes:
        conteudo.append("")
        conteudo.append("Observações e Recomendações:")
        for obs in observacoes:
            conteudo.append(f"- {obs}")

    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write("\n".join(conteudo))

    print(f"\nRelatório salvo em: {caminho_completo}")
