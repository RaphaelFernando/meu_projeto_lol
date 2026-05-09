import unittest

from exibicao import formatar_partidas


class FormatarPartidasTest(unittest.TestCase):
    def test_formata_partidas_para_tabela(self):
        resultado = formatar_partidas(
            [
                {
                    "champion": "Ahri",
                    "lane": "MIDDLE",
                    "kills": 6,
                    "deaths": 2,
                    "assists": 10,
                    "duration": 28,
                    "win": True,
                    "game_mode": "CLASSIC",
                },
                {
                    "champion": "Lux",
                    "lane": "BOTTOM",
                    "kills": 3,
                    "deaths": 0,
                    "assists": 7,
                    "duration": 22,
                    "win": False,
                    "game_mode": "ARAM",
                },
            ]
        )

        self.assertEqual(resultado[0]["Campeão"], "Ahri")
        self.assertEqual(resultado[0]["KDA"], 8)
        self.assertEqual(resultado[0]["Resultado"], "Vitória")
        self.assertEqual(resultado[1]["KDA"], 10)
        self.assertEqual(resultado[1]["Resultado"], "Derrota")


if __name__ == "__main__":
    unittest.main()
