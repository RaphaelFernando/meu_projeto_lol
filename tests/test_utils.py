import os
import tempfile
import unittest

from utils import gerar_observacoes, gerar_relatorio


class UtilsTest(unittest.TestCase):
    def test_gerar_observacoes_para_metricas_relevantes(self):
        observacoes = gerar_observacoes(
            {
                "media_deaths": 9,
                "media_kda": 1.2,
                "winrate": 35,
                "media_assists": 10,
                "tempo_medio": 40,
                "campeao_mais_usado": "Ahri",
            }
        )

        self.assertTrue(any("Alta média de mortes" in obs for obs in observacoes))
        self.assertTrue(any("KDA baixo" in obs for obs in observacoes))
        self.assertTrue(any("Winrate abaixo" in obs for obs in observacoes))
        self.assertTrue(any("Ahri" in obs for obs in observacoes))

    def test_gerar_relatorio_cria_arquivo_txt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            caminho = gerar_relatorio(
                "Jogador#BR1",
                {
                    "campeao_mais_usado": "Ahri",
                    "winrate": 66.7,
                    "media_kills": 5,
                    "media_deaths": 2,
                    "media_assists": 7.5,
                    "media_kda": 6.2,
                    "tempo_medio": 28,
                },
                ["Boa taxa de vitórias!"],
                caminho=tmpdir,
            )

            self.assertTrue(os.path.exists(caminho))
            with open(caminho, encoding="utf-8") as arquivo:
                conteudo = arquivo.read()

        self.assertIn("Jogador: Jogador#BR1", conteudo)
        self.assertIn("Campeão mais usado: Ahri", conteudo)
        self.assertIn("Boa taxa de vitórias!", conteudo)


if __name__ == "__main__":
    unittest.main()
