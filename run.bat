@echo off
title Sonoplasta Virtual
echo Iniciando Sonoplasta Virtual...
echo.

REM Verifica se o Python está instalado
python --version > nul 2>&1
if errorlevel 1 (
    echo Python nao encontrado! Por favor, instale o Python 3.7 ou superior.
    echo Voce pode baixar em: https://www.python.org/downloads/
    pause
    exit
)

REM Verifica se a pasta videos existe
if not exist videos (
    echo Criando pasta videos...
    mkdir videos
    echo Por favor, coloque seus videos na pasta 'videos'
    echo.
)

REM Verifica se as dependências estão instaladas
echo Verificando dependencias...
pip install -r requirements.txt > nul 2>&1

REM Inicia o servidor
echo.
echo Servidor iniciado! Acesse: https://localhost:5000
echo Para acessar de outros dispositivos, use o IP da maquina
echo.
echo Pressione Ctrl+C para encerrar o servidor
echo.
python app.py

pause 