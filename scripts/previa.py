import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dmt_overlay.calculos.combustivel import CalculadoraCombustivel  # noqa: E402
from dmt_overlay.calculos.multiclasse import alerta_multiclasse  # noqa: E402
from dmt_overlay.config import Config  # noqa: E402
from dmt_overlay.provedor import Quadro  # noqa: E402
from dmt_overlay.telemetria.demo import FonteDemo  # noqa: E402
from dmt_overlay.widgets import WIDGETS  # noqa: E402

LAYOUT = {
    "classificacao": (20, 20),
    "relativo": (380, 20),
    "sessao": (700, 20),
    "delta": (700, 80),
    "motor": (700, 170),
    "eletronica": (700, 252),
    "pedais": (970, 80),
    "pneus": (1120, 80),
    "combustivel": (1120, 250),
    "track_limits": (970, 250),
    "multiclasse": (380, 200),
}


def main() -> None:
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/previa.png")
    escala = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    _app = QApplication([])
    fonte = FonteDemo()
    for _ in range(4000):
        if not alerta_multiclasse(fonte.ler(), 3.0, 2.5).vazio:
            break
        fonte._inicio -= 1.0
    calc = CalculadoraCombustivel()
    for volta in range(3):
        estado = fonte.ler()
        estado.jogador.volta = volta
        estado.jogador.combustivel = 90 - volta * 3.1
        calc.atualizar(estado)
    estado = fonte.ler()
    estado.jogador.volta = 3
    estado.jogador.combustivel = 90 - 3 * 3.1
    quadro = Quadro(estado, calc.atualizar(estado), 0.0)

    config = Config(Path(tempfile.mkdtemp()) / "config.json")
    largura, altura = round(1370 * escala), round(400 * escala)
    tela = QPixmap(largura, altura)
    p = QPainter(tela)
    gradiente = QLinearGradient(0, 0, largura, altura)
    gradiente.setColorAt(0, QColor("#4a5a6a"))
    gradiente.setColorAt(1, QColor("#7d8a74"))
    p.fillRect(tela.rect(), gradiente)
    for classe in WIDGETS:
        widget = classe(config.widget(classe.nome, classe.padrao()), escala)
        widget.atualizar(quadro)
        x, y = LAYOUT[classe.nome]
        imagem = widget.grab()
        p.drawPixmap(QPoint(round(x * escala), round(y * escala)), imagem)
    p.end()
    destino.parent.mkdir(parents=True, exist_ok=True)
    tela.save(str(destino))
    print(destino)


if __name__ == "__main__":
    main()
