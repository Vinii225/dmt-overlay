import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dmt_overlay.icone import ARQUIVO, desenhar_icone  # noqa: E402

app = QApplication([])
ARQUIVO.parent.mkdir(exist_ok=True)
desenhar_icone(256).save(str(ARQUIVO))
desenhar_icone(256).save(str(ARQUIVO.with_suffix(".ico")))
print(ARQUIVO, ARQUIVO.with_suffix(".ico"))
