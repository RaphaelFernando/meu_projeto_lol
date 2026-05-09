import unittest

from processamento import calcular_estatisticas


class CalcularEstatisticasTest(unittest.TestCase):
    def test_retorna_dicionario_vazio_quando_nao_ha_partidas(self):
        self.assertEqual(calcular_estatisticas([]), {})

    def test_calcula_medias_winrate_kda_e_campeao_mais_usado(self):
        partidas = [
            {
                "kills": 10,
                "deaths": 2,
                "assists": 8,
                "duration": 30,
                "win": True,
                "champion": "Ahri",
            },
            {
                "kills": 4,
                "deaths": 4,
                "assists": 6,
                "duration": 20,
                "win": False,
                "champion": "Ahri",
            },
            {
                "kills": 1,
                "deaths": 0,
                "assists": 9,
                "duration": 25,
                "win": True,
                "champion": "Lux",
            },
        ]

        resultado = calcular_estatisticas(partidas)

        self.assertEqual(resultado["media_kills"], 5)
        self.assertEqual(resultado["media_deaths"], 2)
        self.assertEqual(resultado["media_assists"], 7.67)
        self.assertEqual(resultado["media_kda"], 6.33)
        self.assertEqual(resultado["vitorias"], 2)
        self.assertEqual(resultado["total_partidas"], 3)
        self.assertEqual(resultado["winrate"], 66.7)
        self.assertEqual(resultado["tempo_medio"], 25)
        self.assertEqual(resultado["campeao_mais_usado"], "Ahri")


if __name__ == "__main__":
    unittest.main()
