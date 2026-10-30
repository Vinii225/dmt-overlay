import re
import sys
from pathlib import Path

INSTALACAO = """
## Como instalar

1. Baixe o arquivo `DMT-Overlay-v{versao}-windows.zip` abaixo.
2. Extraia em qualquer pasta (ex.: `Documentos\\DMT Overlay`).
3. Abra `DMT Overlay.exe`. O ícone aparece na bandeja do sistema, ao lado do relógio.
4. No LMU: **Settings → Gameplay → Enable Plugins = ON** e vídeo em **Borderless/Janela sem bordas**.
"""


def secao(versao: str) -> str:
    texto = (Path(__file__).resolve().parents[1] / "CHANGELOG.md").read_text(encoding="utf-8")
    achado = re.search(rf"^## \[{re.escape(versao)}\].*?$(.*?)(?=^## \[|\Z)", texto, re.S | re.M)
    return achado.group(1).strip() if achado else ""


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    versao = sys.argv[1]
    print(secao(versao) + "\n" + INSTALACAO.format(versao=versao))
