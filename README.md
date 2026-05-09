# Meu Projeto LoL

Aplicacao em Python com Streamlit para consultar dados da Riot API, exibir o historico recente de partidas de League of Legends e resumir metricas de desempenho do jogador.

## Features

- Consulta por Riot ID (`gameName` + `tagLine`)
- Historico recente de partidas
- Estatisticas agregadas de desempenho
- Informacoes ranqueadas
- Integracao com Riot API
- UI em Streamlit
- Testes automatizados

## Stack

- Python
- Streamlit
- Riot API
- requests
- dotenv via arquivo `.env`
- unittest

## Estrutura Do Projeto

- `main.py`: entrypoint oficial da aplicacao Streamlit.
- `streamlit_app.py`: wrapper de compatibilidade para executar `main.main()`.
- `api_handler.py`: fachada de compatibilidade para imports antigos; delega para a camada `riot/`.
- `riot/`: pacote principal de integracao com a Riot API.
- `riot/riot_config.py`: carrega `.env`, le configuracoes e valida `RIOT_API_KEY`.
- `riot/riot_client.py`: cliente HTTP centralizado com `requests.Session`, timeout, retries, logging e tratamento de erros.
- `riot/riot_services.py`: servicos de alto nivel para Account, Match, Summoner, Ranked e historico recente.
- `riot/endpoints.py`: URLs centralizadas da Riot API.
- `riot/rate_limiter.py`: controle local simples de rate limit.
- `riot/exceptions.py`: excecoes tipadas para erros da Riot API.
- `tests/`: testes automatizados com `unittest`.
- `scripts/`: scripts auxiliares, incluindo smoke test real da Riot API.

## Instalacao

Crie a virtualenv:

```powershell
python -m venv .venv
```

Ative a virtualenv:

```powershell
. .\.venv\Scripts\Activate.ps1
```

Instale as dependencias:

```powershell
python -m pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Preencha o `.env` com seus valores locais:

```dotenv
RIOT_API_KEY=
RIOT_REGION=br1
RIOT_ROUTING=americas
```

Nunca commite o arquivo `.env`.

## Execucao

Aplicacao principal:

```powershell
python main.py
```

Interface Streamlit:

```powershell
streamlit run streamlit_app.py
```

Smoke test real da Riot API:

```powershell
python scripts/smoke_test_riot.py
```

## Testes

Execute a suite automatizada:

```powershell
python -m unittest discover -s tests
```

## Arquitetura

Fluxo principal:

```text
UI Streamlit -> api_handler.py -> riot_services.py -> riot_client.py -> Riot API
```

A UI chama a fachada `api_handler.py` para manter compatibilidade. A fachada delega para `riot/riot_services.py`, que concentra as regras de uso da Riot API. As chamadas HTTP passam por `riot/riot_client.py`, onde ficam autenticação, retries, timeout, logging e tratamento de erros.

O historico recente e as medias da tela usam a mesma fonte de dados para evitar chamadas duplicadas e divergencia visual.

## Seguranca

- `.env` esta no `.gitignore`.
- A API key nao deve ser commitada.
- A API key nao e exibida em logs ou na interface.
- O cliente Riot aplica rate limiting local.
- O cliente Riot aplica retries para falhas temporarias e `429`.
- Erros como `401`, `403`, `404`, `429` e `500+` sao tratados com excecoes especificas.

## Screenshots

Adicione screenshots futuras nesta secao.

```markdown
![Dashboard](ScreenShots/home.png)
```

## Roadmap

- Cache local para reduzir chamadas repetidas
- Chamadas async para carregar partidas em paralelo
- Recomendacoes de champion
- Deploy da aplicacao
- Analise de timeline das partidas
