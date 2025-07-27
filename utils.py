import os
from datetime import datetime
from fpdf import FPDF

def gerar_relatorio(nome_jogador, estatisticas, observacoes, caminho="relatorios"):
    """
    Gera um relatório de desempenho em formato .txt com base nas estatísticas e observações passadas.
    """
    os.makedirs(caminho, exist_ok=True)

    nome_arquivo = f"{nome_jogador.replace('#', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho_completo = os.path.join(caminho, nome_arquivo)

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
        f"- Tempo médio de jogo: {estatisticas.get('tempo_medio', 0)} minutos",
        "",
        "Análise:",
    ]

    conteudo.extend([f"- {obs}" for obs in observacoes])

    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write("\n".join(conteudo))

    print(f"\nRelatório salvo em: {caminho_completo}")

def gerar_observacoes(medias):
    """
    Gera observações e dicas com base nas estatísticas médias do jogador.
    """
    observacoes = []

    if medias["media_deaths"] > 8:
        observacoes.append(" Alta média de mortes. Considere jogar de forma mais segura.")

    if medias["media_kda"] >= 3:
        observacoes.append(" Excelente KDA! Mostra bom equilíbrio entre agressividade e sobrevivência.")
    elif medias["media_kda"] < 1.5:
        observacoes.append(" KDA baixo. Pode indicar mortes em excesso ou poucas participações em abates.")

    if medias["winrate"] >= 60:
        observacoes.append(" Boa taxa de vitórias! Mantenha o ritmo.")
    elif medias["winrate"] < 40:
        observacoes.append(" Winrate abaixo do ideal. Reavalie estratégias ou funções utilizadas.")

    if medias["media_assists"] >= 8:
        observacoes.append(" Alta média de assistências. Boa participação em equipe!")

    if medias["tempo_medio"] > 35:
        observacoes.append(" Partidas muito longas. Considere estratégias para fechar o jogo mais cedo.")

    if "campeao_mais_usado" in medias:
        observacoes.append(f" Campeão mais utilizado: {medias['campeao_mais_usado']}. Pode ser sua especialidade.")

    return observacoes

def gerar_relatorio_pdf(nome_jogador, estatisticas, observacoes, caminho="relatorios_pdf"):
    """
    Gera um relatório de desempenho em formato PDF com base nas estatísticas e observações passadas.
    """
    os.makedirs(caminho, exist_ok=True)

    nome_arquivo = f"{nome_jogador.replace('#', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_completo = os.path.join(caminho, nome_arquivo)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Relatório de Desempenho - League of Legends", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Jogador: {nome_jogador}", ln=True)
    pdf.cell(200, 10, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Resumo:", ln=True)

    pdf.set_font("Arial", "", 12)
    for chave, valor in estatisticas.items():
        if isinstance(valor, float):
            valor = round(valor, 2)
        pdf.cell(200, 8, f"- {chave.replace('_', ' ').capitalize()}: {valor}", ln=True)

    pdf.ln(8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Análise:", ln=True)
    pdf.set_font("Arial", "", 12)

    for obs in observacoes:
        pdf.multi_cell(0, 8, f"- {obs}")

    pdf.output(caminho_completo)
    print(f" Relatório PDF salvo em: {caminho_completo}")
    return caminho_completo, nome_arquivo
