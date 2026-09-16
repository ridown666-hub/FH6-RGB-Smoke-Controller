@echo off
setlocal
title FH6 RGB Smoke - Build portatil
cd /d "%~dp0"
echo.
echo  FH6 RGB SMOKE CONTROLLER - BUILD PORTATIL
echo  ==========================================
echo  Cria um unico EXE com Python, Pillow e todos os recursos incluidos.
echo  Este script nao instala dependencias nem usa a rede.
echo.
where py >nul 2>nul || (echo Python nao encontrado. Instala Python 3.11 ou superior.& pause & exit /b 1)
py -c "import PIL" >nul 2>nul || (echo Pillow nao encontrado. Executa: py -m pip install --user -r requirements.txt& pause & exit /b 1)
py -c "import PyInstaller" >nul 2>nul || (echo PyInstaller nao encontrado. Executa: py -m pip install --user pyinstaller& pause & exit /b 1)

rem --onefile junta os recursos locais no EXE; nao ha downloads nem comandos elevados.
py -m PyInstaller --noconfirm --clean --onefile --noconsole --name "FH6_RGB_Smoke_Controller_v5_11_1_Portable" --icon "assets\app_icon.ico" --add-data "assets;assets" --add-data "translations.json;." app.py
if errorlevel 1 (echo Falha ao criar o EXE portatil.& pause & exit /b 1)
echo.
echo BUILD CONCLUIDO:
echo dist\FH6_RGB_Smoke_Controller_v5_11_1_Portable.exe
echo.
echo O EXE inclui os recursos e pode ser copiado sozinho para outro PC.
echo Nota: sem assinatura Authenticode, o SmartScreen ainda pode mostrar um aviso.
pause
endlocal
