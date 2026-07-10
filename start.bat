@echo off
setlocal
rem CVForge — lancement en un double-clic (Windows).
rem Premiere fois : cree l'environnement Python et construit l'interface si possible.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo [CVForge] Premiere installation : environnement Python...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo [CVForge] Python 3.12+ introuvable. Installez-le depuis python.org puis relancez.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install -q -e .
)

if not exist "..\frontend\dist\cvforge\browser\index.html" (
    if exist "..\frontend\node_modules" (
        echo [CVForge] Construction de l'interface...
        pushd "..\frontend"
        call npm run build
        popd
    ) else (
        echo [CVForge] Interface absente. Pour l'obtenir : cd frontend ^&^& npm install ^&^& npm run build
        echo [CVForge] Demarrage en mode API seule ^(http://localhost:8000/docs^).
    )
)

echo [CVForge] Demarrage sur http://localhost:8000 (Ctrl+C pour arreter)
start "" cmd /c "timeout /t 2 >nul & start "" http://localhost:8000"
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
