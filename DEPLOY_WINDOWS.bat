@echo off
echo.
echo ==========================================
echo    ALsistem NC Portal - Deploy automatico
echo ==========================================
echo.

echo Controllo Node.js...
node --version >nul 2>&1
IF ERRORLEVEL 1 (
  echo ERRORE: Node.js non trovato.
  echo Scaricalo da https://nodejs.org e riesegui questo file.
  pause
  exit
)

echo Installo Railway CLI...
call npm install -g @railway/cli

echo.
echo Login Railway (si apre il browser)...
call railway login

echo.
echo Creo il progetto su Railway...
call railway init --name "alsistem-nc-portal"

echo.
echo Deploy in corso (circa 2 minuti)...
call railway up

echo.
echo Genero link pubblico...
call railway domain

echo.
echo ==========================================
echo  FATTO! Copia il link qui sopra.
echo  Mandalo con lo ZIP ai tuoi sviluppatori.
echo ==========================================
echo.
pause
