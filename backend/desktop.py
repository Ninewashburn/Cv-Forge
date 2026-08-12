"""Point d'entrée de l'application de bureau CVForge (exe portable, V1.5).

Démarre le serveur FastAPI local et affiche l'interface. L'exe est **gelé en
mode fenêtré** (``console=False``) : aucune console noire ne s'ouvre. Deux modes,
choisis automatiquement :

- **Fenêtre native** (pywebview / WebView2) si disponible : une vraie fenêtre
  d'application. Fermer la fenêtre arrête proprement le serveur. C'est le confort
  facon ADWCleaner.
- **Repli navigateur** (toujours fiable) si pywebview n'est pas installé ou si la
  fenêtre ne peut pas s'ouvrir (WebView2 absent) : on ouvre le navigateur par
  défaut, et une petite boite de dialogue sert de bouton d'arrêt (il n'y a pas de
  console en mode fenêtré).

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

# Constantes MessageBox (user32) : OK simple, icone info, icone erreur.
_MB_OK_INFO = 0x40
_MB_OK_ERROR = 0x10


def _ensure_std_streams() -> None:
    """En mode fenêtré, PyInstaller peut laisser ``sys.stdout`` / ``stderr`` à
    ``None`` : uvicorn ecrirait alors dans le vide et planterait. On garantit des
    flux ecrivables (poubelle) au besoin, sans jamais ouvrir de console."""
    for name in ("stdout", "stderr"):
        if getattr(sys, name, None) is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))


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
    """Attend que l'API réponde (évite la page blanche d'une UI ouverte avant que
    le serveur soit prêt). ~20 s max. Retourne False si le serveur ne répond
    jamais."""
    health = f"{url}/api/health"
    for _ in range(attempts):
        try:
            with urllib.request.urlopen(health, timeout=1):  # noqa: S310 - localhost
                return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.2)
    return False


def _message_box(text: str, title: str = "CVForge", style: int = _MB_OK_INFO) -> None:
    """Boite de dialogue Windows - notre canal d'affichage quand il n'y a pas de
    console. Silencieux hors Windows ou si l'appel échoue."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(0, text, title, style)
    except Exception:  # noqa: BLE001 - un dialogue raté ne doit jamais faire planter l'app
        pass


def _try_import_webview():
    """pywebview si présent ET non désactivé, sinon None (repli navigateur)."""
    if os.environ.get("CVFORGE_NO_WINDOW") == "1":
        return None
    try:
        import webview  # type: ignore

        return webview
    except Exception:  # noqa: BLE001 - absence = repli navigateur, jamais une erreur
        return None


class _ThreadedServer:
    """Uvicorn dans un thread démon, pour laisser le thread principal à la GUI /
    au dialogue d'arrêt. Les gestionnaires de signaux d'uvicorn ne s'installent
    que sur le thread principal : on les neutralise (l'arrêt passe par ``stop()``)."""

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


def _serve_with_ui(app: object, url: str, port: int) -> None:
    """Serveur en tâche de fond, puis fenêtre native si possible, sinon repli
    navigateur. L'app reste utilisable dans tous les cas."""
    server = _ThreadedServer(app, port)
    server.start()
    _wait_until_ready(url)

    try:
        webview = _try_import_webview()
        if webview is not None:
            try:
                webview.create_window("CVForge", url, width=1180, height=820, min_size=(900, 640))
                webview.start()  # bloque jusqu'à la fermeture de la fenêtre
                return
            except Exception as exc:  # noqa: BLE001 - on se rabat sur le navigateur, jamais fatal
                print(
                    f"\nFenêtre native indisponible ({exc}) - ouverture du navigateur.",
                    file=sys.stderr,
                )
                # On garde le même serveur (déjà prêt) pour le repli ci-dessous.

        # Repli navigateur : pas de console en mode fenêtré, une boite fait le stop.
        webbrowser.open(url)
        if sys.platform == "win32":
            _message_box(
                "CVForge est ouvert dans ton navigateur.\n\n"
                "Garde cette fenetre ouverte tant que tu utilises CVForge.\n"
                "Clique sur OK (ou ferme cette fenetre) pour arreter CVForge.",
                "CVForge",
                _MB_OK_INFO,
            )
        else:
            while server.is_running():
                time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()


def main() -> None:
    _ensure_std_streams()
    port = _pick_port()
    url = f"http://{HOST}:{port}"

    print("=" * 58)
    print("  CVForge - candidater par la preuve (local-first)")
    print(f"  Interface : {url}")
    print("  Tes données restent sur cette machine. Rien n'est envoyé.")
    print("=" * 58)

    # On passe l'objet app (pas une chaîne d'import) : indispensable en mode
    # gelé, où uvicorn ne peut pas ré-importer par nom de module.
    from app.main import app

    # CVFORGE_NO_BROWSER=1 : ni fenêtre ni navigateur (serveur seul, tests).
    # Serveur bloquant sur le thread principal, comme un uvicorn classique.
    if os.environ.get("CVFORGE_NO_BROWSER") == "1":
        import uvicorn

        uvicorn.run(app, host=HOST, port=port, log_level="warning")
        return

    _serve_with_ui(app, url, port)


if __name__ == "__main__":
    try:
        _ensure_std_streams()
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 - dernier filet : montrer l'erreur, ne pas fermer sec
        message = f"CVForge n'a pas pu démarrer :\n\n{exc}"
        print(message, file=sys.stderr)
        if sys.platform == "win32":
            _message_box(message, "CVForge - erreur", _MB_OK_ERROR)
        else:
            try:
                input("Appuie sur Entrée pour fermer...")
            except EOFError:
                pass
        raise
