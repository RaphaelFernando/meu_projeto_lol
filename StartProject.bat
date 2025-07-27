@echo off
title Iniciando Projeto League of Legends
echo ========================================
echo    Projeto: meu_projeto_lol
echo ========================================

:: Ativar o ambiente virtual
IF NOT EXIST "venv\" (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate

:: Instalar dependências
echo Instalando dependências (streamlit, requests, dotenv, matplotlib)...
pip install -r requirements.txt

:: Executar a aplicação Streamlit
echo Iniciando Streamlit...
python -m streamlit run streamlit_app.py

pause