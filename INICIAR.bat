@echo off
setlocal
title FH6 RGB Smoke Controller
cd /d "%~dp0"

rem Arranque local e offline. Este ficheiro nao instala pacotes nem descarrega
rem nada: apenas abre a interface a partir da pasta que foi extraida.
where py >nul 2>nul
if errorlevel 1 (
    echo Python 3.11 ou superior nao foi encontrado.
    echo Instala Python a partir do site oficial e volta a executar este ficheiro.
    pause
    exit /b 1
)

py -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo A dependencia Pillow nao esta instalada.
    echo Abre requirements.txt e executa manualmente:
    echo     py -m pip install --user -r requirements.txt
    pause
    exit /b 1
)

py app.py
if errorlevel 1 (
    echo.
    echo A aplicacao terminou com um erro. Nenhum ficheiro foi descarregado.
    pause
    exit /b 1
)
endlocal
