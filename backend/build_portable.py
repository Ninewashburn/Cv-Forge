"""Construit l'exe portable CVForge (V1.5) en une commande.

    python build_portable.py

Étapes : (1) construit l'interface Angular si le build manque, (2) installe
PyInstaller au besoin, (3) gèle l'application. Résultat : backend/dist/CVForge.exe

Le binaire ne stocke aucune donnée : au lancement, resolve_data_dir() choisit
~/.cvforge/ par défaut, ou ./data/ si un fichier `cvforge.portable` est posé à
côté de l'exe (mode clé USB).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
FRONTEND = BACKEND.parent / "frontend"
FRONTEND_BUILD = FRONTEND / "dist" / "cvforge" / "browser"


def _run(cmd: list[str], cwd: Path) -> None:
    print(f"\n> {' '.join(cmd)}  (dans {cwd})")
    subprocess.run(cmd, cwd=cwd, check=True)


def _ensure_frontend_build() -> None:
    if (FRONTEND_BUILD / "index.html").is_file():
        print(f"Build Angular présent : {FRONTEND_BUILD}")
        return
    if not (FRONTEND / "node_modules").is_dir():
        raise SystemExit(
            "Build Angular absent et node_modules manquant.\n"
            f"Lance d'abord : cd {FRONTEND} && npm install && npm run build"
        )
    npm = shutil.which("npm") or "npm"
    _run([npm, "run", "build"], cwd=FRONTEND)


def _ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        _run([sys.executable, "-m", "pip", "install", "pyinstaller>=6,<7"], cwd=BACKEND)


def _ensure_pywebview() -> None:
    """Fenêtre native de l'exe. Optionnel : si l'install échoue (pas de réseau,
    plateforme non gérée), on continue - l'exe se rabattra sur le navigateur."""
    try:
        import webview  # noqa: F401
        return
    except ImportError:
        pass
    try:
        _run([sys.executable, "-m", "pip", "install", "pywebview>=5,<6"], cwd=BACKEND)
    except subprocess.CalledProcessError:
        print("Note : pywebview non installe - l'exe s'ouvrira dans le navigateur.")


def main() -> None:
    _ensure_frontend_build()
    _ensure_pyinstaller()
    _ensure_pywebview()
    _run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "cvforge.spec"],
        cwd=BACKEND,
    )
    exe = BACKEND / "dist" / "CVForge.exe"
    print("\n" + "=" * 58)
    if exe.is_file():
        print(f"OK - exe portable : {exe}")
        print("Mode clé USB : pose un fichier vide `cvforge.portable` à côté")
        print("de l'exe, et les données iront dans ./data/ (au lieu de ~/.cvforge/).")
    else:
        print("PyInstaller a fini mais l'exe est introuvable - voir les logs ci-dessus.")
    print("=" * 58)


if __name__ == "__main__":
    main()
