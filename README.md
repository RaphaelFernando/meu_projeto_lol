# Analisador de Partidas - League of Legends

AplicaÃ§Ã£o em Python com Streamlit para consultar dados da API oficial da Riot Games, analisar partidas recentes de League of Legends e exibir metricas de desempenho.

## Arquitetura

- `main.py`: entrypoint oficial da aplicaÃ§Ã£o Streamlit.
- `streamlit_app.py`: wrapper de compatibilidade que chama `main.main()`.
- `api_handler.py`: fachada de compatibilidade para imports antigos.
- `riot/riot_config.py`: carrega `.env`, valida `RIOT_API_KEY` e expÃµe regiÃ£o/roteamento padrÃ£o.
- `riot/riot_client.py`: cliente HTTP centralizado com `requests.Session`, timeout, retries, logging e tratamento de status HTTP.
- `riot/rate_limiter.py`: rate limit local simples para 20 req/s e 100 req/2min.
- `riot/endpoints.py`: URLs centralizadas da Riot API.
- `riot/riot_services.py`: funÃ§Ãµes de alto nÃ­vel para Account, Match, Summoner, Ranked, Mastery, Spectator e Champion Rotation.
- `processamento.py`: cÃ¡lculo de estatÃ­sticas agregadas.
- `exibicao.py`: renderizacao das metricas da interface.
- `utils.py`: observaÃ§Ãµes automÃ¡ticas e geraÃ§Ã£o de relatÃ³rio.
- `scripts/`: scripts exploratÃ³rios e utilitÃ¡rios manuais.
- `tests/`: testes automatizados.

Os mÃ³dulos antigos `riot_config.py`, `riot_client.py`, `match_service.py` e `rank_service.py` permanecem como wrappers de compatibilidade.

## ConfiguraÃ§Ã£o Da Chave Riot

Nunca coloque uma chave real no cÃ³digo, README, testes ou scripts.

Configure a variÃ¡vel de ambiente `RIOT_API_KEY` antes de rodar a aplicaÃ§Ã£o:

```powershell
$env:RIOT_API_KEY="sua-chave-riot"
$env:RIOT_REGION="br1"
$env:RIOT_ROUTING="americas"
```

Como alternativa local, copie `.env.example` para `.env` e preencha os valores:

```powershell
Copy-Item .env.example .env
```

Exemplo de `.env`:

```dotenv
RIOT_API_KEY=
RIOT_REGION=br1
RIOT_ROUTING=americas
```

O arquivo `.env` estÃ¡ no `.gitignore` e nÃ£o deve ser versionado.

## InstalaÃ§Ã£o

Crie e ative a venv:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

Instale as dependÃªncias:

```powershell
python -m pip install -r requirements.txt
```

## ExecuÃ§Ã£o

Rode a entrypoint oficial:

```powershell
python -m streamlit run main.py
```

O arquivo `streamlit_app.py` continua existindo apenas para compatibilidade.

## Testes

Execute a suÃ­te automatizada:

```powershell
python -m unittest discover -s tests
```

Smoke test real da Riot API:

```powershell
python scripts/smoke_test_riot.py
```

Opcionalmente, compile os mÃ³dulos para validar sintaxe/imports:

```powershell
python -m py_compile api_handler.py riot\riot_config.py riot\riot_client.py riot\riot_services.py riot\rate_limiter.py riot\exceptions.py riot\endpoints.py processamento.py exibicao.py utils.py main.py streamlit_app.py entrada.py scripts\compare.py scripts\matchid.py
```

## Troubleshooting

- `RIOT_API_KEY nÃ£o configurada`: defina a variÃ¡vel de ambiente ou crie `.env` a partir de `.env.example`.
- `401` ou `403`: verifique se a chave estÃ¡ ativa e se nÃ£o expirou.
- `404`: o recurso nÃ£o foi encontrado, geralmente por Riot ID, PUUID ou match id incorretos.
- `429`: a Riot limitou as requisiÃ§Ãµes. O cliente aplica retry e tambÃ©m hÃ¡ rate limit local.
- `500+`: falha temporÃ¡ria da Riot API. O cliente tenta novamente antes de retornar erro.

