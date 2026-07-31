"""Point d'entrée de l'application de bureau CVForge (exe portable, V1.5).

Démarre le serveur FastAPI local et ouvre le navigateur sur l'interface. C'est
l'entrée gelée par PyInstaller ; en développement on continue d'utiliser
``uvicorn app.main:app --reload``.

Local-first jusqu'au bout : on n'écoute que sur 127.0.0.1 (jamais exposé au
réseau), et rien ne sort de la machine (sauf l'appel LLM que l'utilisateur
déclenche lui-même avec sa propre clé).
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

HOST = "127.0.0.1"
PREFERRED_PORT = 8000


def _pick_port() -> int:
    """Port 8000 s'il est libre, sinon un port choisi par le système. Comme
    l'interface parle à l'API en même-origine (``/api``), n'importe quel port
    convient - on ne dépend pas d'un numéro fixe."""
    for candidate in (PREFERRED_PORT, 0):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                probe.bind((HOST, candidate))
                return probe.getsockname()[1]
        except OSError:
            continue
    return PREFERRED_PORT


def _open_browser_when_ready(url: str) -> None:
    """Attend que l'API réponde puis ouvre le navigateur - évite la page
    blanche d'un navigateur ouvert avant que le serveur soit prêt."""
    health = f"{url}/api/health"
    for _ in range(100):  # ~20 s max
        try:
            with urllib.request.urlopen(health, timeout=1):  # noqa: S310 - localhost
                break
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    webbrowser.open(url)


def main() -> None:
    import uvicorn

    port = _pick_port()
    url = f"http://{HOST}:{port}"

    print("=" * 58)
    print("  CVForge - candidater par la preuve (local-first)")
    print(f"  Interface : {url}")
    print("  Tes données restent sur cette machine. Rien n'est envoyé.")
    print("  Ferme cette fenêtre pour arrêter CVForge.")
    print("=" * 58)

    # CVFORGE_NO_BROWSER=1 : ne pas ouvrir le navigateur (usage serveur, tests).
    if os.environ.get("CVFORGE_NO_BROWSER") != "1":
        threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()

    # On passe l'objet app (pas une chaîne d'import) : indispensable en mode
    # gelé, où uvicorn ne peut pas ré-importer par nom de module.
    from app.main import app

    uvicorn.run(app, host=HOST, port=port, log_level="warning")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 - dernier filet : montrer l'erreur, ne pas fermer sec
        print(f"\nCVForge n'a pas pu démarrer : {exc}", file=sys.stderr)
        input("Appuie sur Entrée pour fermer...")
        raise
