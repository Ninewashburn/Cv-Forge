# CVForge - spec PyInstaller (exe portable, V1.5).
#
# Produit un exécutable --onefile double-cliquable : Python + FastAPI + build
# Angular + scripts Alembic, dans un seul binaire. Lancé depuis backend/ :
#     pyinstaller cvforge.spec
# Résultat : backend/dist/CVForge.exe
#
# Données : jamais dans l'exe. Résolues au runtime par resolve_data_dir()
# (~/.cvforge/ par défaut, ./data/ si un marqueur cvforge.portable est posé à
# côté de l'exe). Le binaire est en lecture seule ; il ne stocke rien.

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules

BACKEND = Path(SPECPATH)  # noqa: F821 - SPECPATH injecté par PyInstaller
FRONTEND_BUILD = BACKEND.parent / "frontend" / "dist" / "cvforge" / "browser"

if not (FRONTEND_BUILD / "index.html").is_file():
    raise SystemExit(
        f"Build Angular introuvable : {FRONTEND_BUILD}\n"
        "Lance d'abord `npm run build` dans frontend/ (ou build_portable.py)."
    )

# Ressources embarquées, extraites dans sys._MEIPASS au lancement.
datas = [
    (str(FRONTEND_BUILD), "static"),
    (str(BACKEND / "alembic"), "alembic"),
    (str(BACKEND / "alembic.ini"), "."),
]
binaries = []
hiddenimports = ["multipart"]

# uvicorn et alembic importent leurs implémentations dynamiquement (boucles,
# protocoles, scripts de migration) : PyInstaller ne les voit pas sans aide.
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("alembic")

# anthropic (niveau clé API) est importé paresseusement, à l'appel seulement.
# fpdf2 embarque ses métriques de polices. collect_all récupère code + données.
for package in ("anthropic", "fpdf"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

# pywebview (fenêtre native, optionnel) : présent au build => on l'embarque avec
# ses backends de plateforme ; absent => l'exe se rabattra sur le navigateur.
# Jamais bloquant pour le build.
try:
    wv_datas, wv_binaries, wv_hidden = collect_all("webview")
    datas += wv_datas
    binaries += wv_binaries
    hiddenimports += wv_hidden
except Exception as exc:  # noqa: BLE001 - pywebview absent : repli navigateur au runtime
    print(f"[cvforge.spec] pywebview non embarque ({exc}) - l'exe utilisera le navigateur.")

a = Analysis(  # noqa: F821
    ["desktop.py"],
    pathex=[str(BACKEND)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest", "ruff"],
    noarchive=False,
)
pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="CVForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # ROADMAP : pas d'UPX (faux positifs antivirus)
    runtime_tmpdir=None,
    console=True,  # console visible en beta : logs et erreurs lisibles
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
