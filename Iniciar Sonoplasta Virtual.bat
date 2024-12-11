@echo off
chcp 65001 > nul
title Sonoplasta Virtual

echo.
echo === Iniciando Sonoplasta Virtual ===
echo.

REM Verifica se o Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado! Por favor, instale o Python 3.
    echo Você pode baixar em: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Instala dependências se necessário
echo Verificando dependências...
pip install -r requirements.txt > nul 2>&1

REM Inicia o servidor
echo Iniciando o programa...
echo.
echo Acesse o programa em: http://localhost:5000
echo.
python run.py

exit /b 0 