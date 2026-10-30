import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from dmt_overlay import __version__  # noqa: E402

NOME = "DMT Overlay"
SEPARADOR = ";" if sys.platform == "win32" else ":"
EXCLUIR = (
    "tkinter", "unittest", "pydoc", "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick",
    "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtDBus", "PySide6.QtOpenGL", "PySide6.QtPdf",
)

PODAR = ("translations", "plugins/networkinformation", "plugins/tls", "plugins/generic", "plugins/iconengines")
FORMATOS_IMAGEM = ("qico",)


def podar(pasta: Path) -> None:
    base = pasta / "_internal" / "PySide6"
    raiz_qt = base / "Qt" if (base / "Qt").exists() else base
    for relativo in PODAR:
        shutil.rmtree(raiz_qt / relativo, ignore_errors=True)
    formatos = raiz_qt / "plugins" / "imageformats"
    if formatos.exists():
        for arquivo in formatos.iterdir():
            if not any(nome in arquivo.name for nome in FORMATOS_IMAGEM):
                arquivo.unlink()
    for arquivo in pasta.rglob("*Qt6Network*"):
        arquivo.unlink()
    for arquivo in pasta.rglob("*Qt6Pdf*"):
        arquivo.unlink()


def main() -> None:
    dist = RAIZ / "dist"
    shutil.rmtree(dist, ignore_errors=True)
    argumentos = [
        str(RAIZ / "run.py"),
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", NOME,
        "--icon", str(RAIZ / "dmt_overlay" / "recursos" / "icone.ico"),
        "--add-data", f"{RAIZ / 'dmt_overlay' / 'recursos'}{SEPARADOR}dmt_overlay/recursos",
        "--distpath", str(dist),
        "--workpath", str(RAIZ / "build"),
        "--specpath", str(RAIZ / "build"),
    ]
    for modulo in EXCLUIR:
        argumentos += ["--exclude-module", modulo]
    PyInstaller.__main__.run(argumentos)
    podar(dist / NOME)
    for arquivo in ("README.md", "LICENSE"):
        shutil.copy(RAIZ / arquivo, dist / NOME)
    plataforma = "windows" if sys.platform == "win32" else sys.platform
    pacote = shutil.make_archive(str(dist / f"DMT-Overlay-v{__version__}-{plataforma}"), "zip", dist, NOME)
    print(pacote)


if __name__ == "__main__":
    main()
