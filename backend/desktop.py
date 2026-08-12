"""Point d'entrée de l'application de bureau CVForge (exe portable, V1.5).

Démarre le serveur FastAPI local et affiche l'interface. Deux modes, choisis
automatiquement :

- **Fenêtre native** (pywebview / WebView2) si disponible : une vraie fenêtre
  d'application, sans console visible. Fermer la fenêtre arrête proprement le
  serveur. C'est le confort facon ADWCleaner.
- **Repli navigateur** (comportement historique, toujours fiable) si pywebview
  n'est pas installé ou si la fenêtre ne peut pas s'ouvrir (WebView2 absent) :
  on ouvre le navigateur par défaut et la console sert de bouton d'arrêt.

C'est l'entrée gelée par PyInstaller ; en développement on continue d'utiliser
``uvicorn app.main:app --reload``.

Local-first jusqu'au bout : on n'écoute que sur 127.0.0.1 (jamais exposé au
réseau), et rien ne sort de la machine (sauf l'appel LLM que l'utilisateur
déclenche lui-même avec sa propre clé).

Deux échappatoires par variable d'environnement :
- ``CVFORGE_NO_BROWSER=1`` : ni fenêtre ni navigateur (usage serveur, tests).
- ``CVFORGE_NO_WINDOW=1``  : force le repli navigateur (ignore pywebview).
"""

from __future__ import annotations

import asyncio
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


def _wait_until_ready(url: str, attempts: int = 100) -> bool:
    """Attend que l'API réponde (évite la page blanche d'une UI ouverte avant
    que le serveur soit prêt). ~20 s max. Retourne False si le serveur ne répond
    jamais."""
    health = f"{url}/api/health"
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(health, timeout=1):  # noqa: S310 - localhost
                return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def _open_browser_when_ready(url: str) -> None:
    _wait_until_ready(url)
    webbrowser.open(url)


# --------------------------------------------------------------- fenêtre native


def _try_import_webview():
    """pywebview si présent ET non désactivé, sinon None (repli navigateur)."""
    if os.environ.get("CVFORGE_NO_WINDOW") == "1":
        return None
    try:
        import webview  # type: ignore

        return webview
    except Exception:  # noqa: BLE001 - absence = repli navigateur, jamais une erreur
        return None


def _set_console_visible(visible: bool) -> None:
    """Masque (ou ré-affiche) la console Windows. En mode fenêtre, la console
    n'a plus de rôle : on la cache. Sur un repli, on la laisse (bouton d'arrêt).
    Silencieux hors Windows ou si la console n'existe pas."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 5 if visible else 0)  # SW_SHOW / SW_HIDE
    except Exception:  # noqa: BLE001 - cacher la console ne doit jamais faire planter l'app
        pass


class _ThreadedServer:
    """Uvicorn dans un thread démon, pour laisser le thread principal à la GUI.

    Les gestionnaires de signaux d'uvicorn ne s'installent que sur le thread
    principal : on les neutralise ici (l'arrêt passe par ``stop()``)."""

    def __init__(self, app: object, port: int) -> None:
        import uvicorn

        config = uvicorn.Config(app, host=HOST, port=port, log_level="warning")
        self._server = uvicorn.Server(config)
        self._server.install_signal_handlers = lambda: None  # type: ignore[method-assign]
        self._thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self) -> None:
        asyncio.run(self._server.serve())

    def start(self) -> None:
        self._thread.start()

    def is_running(self) -> bool:
        return self._thread.is_alive()

    def stop(self) -> None:
        self._server.should_exit = True
        self._thread.join(timeout=5)


def _run_windowed(app: object, url: str, port: int, webview) -> None:
    """Serveur en tâche de fond + fenêtre native. Si la fenêtre ne peut pas
    s'ouvrir (WebView2 absent, backend GUI manquant), on rétablit la console et
    on se rabat sur le navigateur - l'app reste utilisable dans tous les cas."""
    server = _ThreadedServer(app, port)
    server.start()
    _wait_until_ready(url)
    try:
        webview.create_window("CVForge", url, width=1180, height=820, min_size=(900, 640))
        _set_console_visible(False)
        webview.start()  # bloque jusqu'à la fermeture de la fenêtre
    except Exception as exc:  # noqa: BLE001 - repli navigateur, jamais fatal
        _set_console_visible(True)
        print(f"\nFenêtre native indisponible ({exc}) - ouverture du navigateur.", file=sys.stderr)
        webbrowser.open(url)
        try:
            while server.is_running():
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
    finally:
        server.stop()


def main() -> None:
    port = _pick_port()
    url = f"http://{HOST}:{port}"

    no_browser = os.environ.get("CVFORGE_NO_BROWSER") == "1"
    webview = None if no_browser else _try_import_webview()

    print("=" * 58)
    print("  CVForge - candidater par la preuve (local-first)")
    print(f"  Interface : {url}")
    print("  Tes données restent sur cette machine. Rien n'est envoyé.")
    if webview is not None:
        print("  Ferme la fenêtre CVForge pour tout arrêter.")
    else:
        print("  Ferme cette fenêtre pour arrêter CVForge.")
    print("=" * 58)

    # On passe l'objet app (pas une chaîne d'import) : indispensable en mode
    # gelé, où uvicorn ne peut pas ré-importer par nom de module.
    from app.main import app

    if webview is not None:
        _run_windowed(app, url, port, webview)
        return

    # Chemins prouvés, inchangés : navigateur (ou rien) + serveur bloquant sur
    # le thread principal (la console ferme l'app).
    if not no_browser:
        threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()

    import uvicorn

    uvicorn.run(app, host=HOST, port=port, log_level="warning")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 - dernier filet : montrer l'erreur, ne pas fermer sec
        _set_console_visible(True)
        print(f"\nCVForge n'a pas pu démarrer : {exc}", file=sys.stderr)
        input("Appuie sur Entrée pour fermer...")
        raise
