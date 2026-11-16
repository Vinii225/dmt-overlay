from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QBrush, QColor, QFont, QFontDatabase, QGuiApplication, QLinearGradient

# Visual de transmissão de endurance: azul-marinho, borda azul, fonte condensada e sobrenomes em caixa alta.
FUNDO = QColor(30, 27, 84, 236)
FUNDO_FIM = QColor(15, 13, 48, 236)
FUNDO_LINHA = QColor(255, 255, 255, 14)
FUNDO_DESTAQUE = QColor(64, 150, 255, 70)
BORDA = QColor(52, 152, 255, 220)
LARGURA_BORDA = 1.6
TEXTO = QColor("#ffffff")
TEXTO_SECUNDARIO = QColor("#cfd2f5")
TEXTO_APAGADO = QColor("#8d91c9")
TEXTO_POSICAO = QColor("#ffffff")
TRILHO = QColor("#2a2770")
DESTAQUE = QColor("#3fb4ff")
RAIO = 7
FAMILIAS = ["Barlow Condensed", "Segoe UI", "sans-serif"]
ESCALA_FONTE = 1.22

NEUTRO = QColor("#5c5c58")

BOM = QColor("#0ca30c")
ALERTA = QColor("#fab219")
SERIO = QColor("#ec835a")
CRITICO = QColor("#d03b3b")

ACELERADOR = QColor("#0ca30c")
FREIO = QColor("#d03b3b")
EMBREAGEM = QColor("#3987e5")

FRIO = QColor("#3987e5")
QUENTE = QColor("#e66767")

VOLTA_A_FRENTE = QColor("#e66767")
VOLTA_ATRAS = QColor("#5598e7")

CLASSES = {
    "hypercar": ("HY", QColor("#e66767")),
    "lmp2": ("P2", QColor("#3987e5")),
    "lmgt3": ("GT3", QColor("#199e70")),
    "gt3": ("GT3", QColor("#199e70")),
    "gte": ("GTE", QColor("#c98500")),
    "lmp3": ("P3", QColor("#9085e9")),
}

MARGEM = 8
PASTA_FONTES = Path(__file__).parent / "recursos" / "fontes"
_fontes_carregadas = False


def _carregar_fontes() -> None:
    global _fontes_carregadas
    if _fontes_carregadas or QGuiApplication.instance() is None:
        return
    for arquivo in sorted(PASTA_FONTES.glob("*.ttf")):
        QFontDatabase.addApplicationFont(str(arquivo))
    _fontes_carregadas = True


def pincel_fundo(altura: float) -> QBrush:
    gradiente = QLinearGradient(0, 0, 0, altura)
    gradiente.setColorAt(0, FUNDO)
    gradiente.setColorAt(1, FUNDO_FIM)
    return QBrush(gradiente)


def nome_piloto(nome: str, limite: int = 16) -> str:
    """Sobrenome em caixa alta, como na TV: "HARTLEY"."""
    from .calculos.formatacao import nome_curto

    sobrenome = nome.split()[-1] if nome.split() else nome
    return nome_curto(sobrenome.upper(), limite)


def classe(nome: str) -> tuple[str, QColor]:
    chave = nome.lower().replace(" ", "").replace("-", "")
    for prefixo, valor in CLASSES.items():
        if chave.startswith(prefixo) or prefixo in chave:
            return valor
    return (nome[:3].upper() or "?", NEUTRO)


@lru_cache(maxsize=64)
def fonte(tamanho: float, negrito: bool = False) -> QFont:
    _carregar_fontes()
    f = QFont()
    f.setFamilies(FAMILIAS)
    f.setPixelSize(max(1, round(tamanho * ESCALA_FONTE * 4 / 3)))
    f.setWeight(QFont.Weight.Bold if negrito else QFont.Weight.Medium)
    f.setItalic(negrito)
    f.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f


def mistura(a: QColor, b: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        round(a.red() + (b.red() - a.red()) * t),
        round(a.green() + (b.green() - a.green()) * t),
        round(a.blue() + (b.blue() - a.blue()) * t),
    )


def cor_temperatura(valor: float, ideal: float, faixa: float = 15.0) -> QColor:
    if valor <= -100:
        return NEUTRO
    desvio = (valor - ideal) / faixa
    if abs(desvio) < 0.33:
        return NEUTRO
    if desvio < 0:
        return mistura(NEUTRO, FRIO, (-desvio - 0.33) / 0.67)
    return mistura(NEUTRO, QUENTE, (desvio - 0.33) / 0.67)

