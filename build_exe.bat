@echo off
setlocal
title FH6 RGB Smoke - Build opcional
cd /d "%~dp0"
echo.
echo  FH6 RGB SMOKE CONTROLLER - BUILD OPCIONAL
echo  ==========================================
echo  Este script nao instala dependencias nem usa a rede.
echo  O resultado e uma pasta (onedir), nao um executavel auto-extraivel.
echo.
where py >nul 2>nul || (echo Python nao encontrado. Instala Python 3.11 ou superior.& pause & exit /b 1)
py -c "import PIL" >nul 2>nul || (echo Pillow nao encontrado. Executa: py -m pip install --user -r requirements.txt& pause & exit /b 1)
py -c "import PyInstaller" >nul 2>nul || (echo PyInstaller nao encontrado. Executa: py -m pip install --user pyinstaller& pause & exit /b 1)

rem Os DDS, imagens e traducoes sao incluidos localmente; nao ha downloads.
py -m PyInstaller --noconfirm --clean --onedir --noconsole --name "FH6_RGB_Smoke_Controller_v5_11_1" --icon "assets\app_icon.ico" --add-data "assets;assets" --add-data "translations.json;." app.py
if errorlevel 1 (echo Falha ao criar a pasta do programa.& pause & exit /b 1)
echo.
echo BUILD CONCLUIDO: dist\FH6_RGB_Smoke_Controller_v5_11_1\
echo Nota: um EXE sem assinatura digital pode continuar a mostrar um aviso SmartScreen.
pause
endlocal
