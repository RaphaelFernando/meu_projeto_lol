import os
import tempfile
import unittest
from unittest.mock import patch

from riot.exceptions import RiotAuthenticationError
from riot.riot_config import load_dotenv, validate_api_key


class RiotConfigTest(unittest.TestCase):
    def test_load_dotenv_carrega_variaveis_para_o_ambiente(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dotenv_path = os.path.join(tmpdir, ".env")
            with open(dotenv_path, "w", encoding="utf-8") as arquivo:
                arquivo.write("RIOT_API_KEY=valor_de_teste\n")

            with patch.dict(os.environ, {}, clear=True):
                load_dotenv(dotenv_path)
                self.assertEqual(os.environ["RIOT_API_KEY"], "valor_de_teste")

    def test_validate_api_key_exige_variavel_de_ambiente(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RiotAuthenticationError):
                validate_api_key()

    def test_validate_api_key_retorna_valor_do_ambiente(self):
        with patch.dict(os.environ, {"RIOT_API_KEY": "valor_de_teste"}, clear=True):
            self.assertEqual(validate_api_key(), "valor_de_teste")


if __name__ == "__main__":
    unittest.main()
