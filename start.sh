#!/usr/bin/env bash
# CVForge — lancement en un double-clic (macOS / Linux).
set -e
cd "$(dirname "$0")/backend"

if [ ! -x ".venv/bin/python" ]; then
    echo "[CVForge] Première installation : environnement Python…"
    python3 -m venv .venv
    .venv/bin/python -m pip install -q -e .
fi

if [ ! -f "../frontend/dist/cvforge/browser/index.html" ]; then
    if [ -d "../frontend/node_modules" ]; then
        echo "[CVForge] Construction de l'interface…"
        (cd ../frontend && npm run build)
    else
        echo "[CVForge] Interface absente. Pour l'obtenir : cd frontend && npm install && npm run build"
        echo "[CVForge] Démarrage en mode API seule (http://localhost:8000/docs)."
    fi
fi

echo "[CVForge] Démarrage sur http://localhost:8000 (Ctrl+C pour arrêter)"
( sleep 2; xdg-open http://localhost:8000 2>/dev/null || open http://localhost:8000 2>/dev/null || true ) &
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
