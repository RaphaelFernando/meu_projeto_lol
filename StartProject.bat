@echo off
title Iniciando Projeto League of Legends
echo ========================================
echo    Projeto: meu_projeto_lol
echo ========================================

IF NOT EXIST ".venv\" (
    echo Criando ambiente virtual...
    python -m venv .venv
)

echo Ativando ambiente virtual...
call .venv\Scripts\activate

echo Instalando dependencias...
python -m pip install -r requirements.txt

echo Iniciando Streamlit...
python -m streamlit run main.py

pause
