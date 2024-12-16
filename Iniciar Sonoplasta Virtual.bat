@echo off
chcp 65001 > nul
title Sonoplasta Virtual

echo.
echo ===== Iniciando Sonoplasta Virtual =====
echo.

REM Verifica se o Python está instalado
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python não encontrado!
    echo Por favor, instale o Python 3.8 ou superior.
    echo Você pode baixar em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verifica se o ambiente virtual existe
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate

REM Verifica cada pasta individualmente
if not exist "app\files" mkdir "app\files"
if not exist "app\files\entrada" mkdir "app\files\entrada"
if not exist "app\files\despedida" mkdir "app\files\despedida"
if not exist "app\files\ofertorio" mkdir "app\files\ofertorio"
if not exist "app\files\adoracao_infantil" mkdir "app\files\adoracao_infantil"

REM Instala/atualiza dependências
echo Verificando dependências...
python -m pip install --upgrade pip > nul
pip install -r requirements.txt > nul
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependências!
    pause
    exit /b 1
)

REM Limpa a tela
cls

echo ===== Sonoplasta Virtual =====
echo.
echo Servidor iniciado com sucesso!
echo.
echo Acesse o programa em: http://localhost:5000
echo.
echo Pressione Ctrl+C para encerrar o servidor
echo.

REM Inicia o servidor Flask
python run.py

REM Desativa o ambiente virtual ao fechar
deactivate

exit /b 0 