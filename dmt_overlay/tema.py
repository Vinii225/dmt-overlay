from __future__ import annotations

from functools import lru_cache

from PySide6.QtGui import QColor, QFont

FUNDO = QColor(20, 20, 22, 215)
FUNDO_LINHA = QColor(255, 255, 255, 10)
FUNDO_DESTAQUE = QColor(255, 255, 255, 28)
BORDA = QColor(255, 255, 255, 26)
TEXTO = QColor("#f0efec")
TEXTO_SECUNDARIO = QColor("#c3c2b7")
TEXTO_APAGADO = QColor("#898781")
TRILHO = QColor("#2c2c2a")
NEUTRO = QColor("#5c5c58")

DESTAQUE = QColor("#2fbf71")

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

RAIO = 6
MARGEM = 8


def classe(nome: str) -> tuple[str, QColor]:
    chave = nome.lower().replace(" ", "").replace("-", "")
    for prefixo, valor in CLASSES.items():
        if chave.startswith(prefixo) or prefixo in chave:
            return valor
    return (nome[:3].upper() or "?", NEUTRO)


@lru_cache(maxsize=64)
def fonte(tamanho: float, negrito: bool = False) -> QFont:
    f = QFont()
    f.setFamilies(["Segoe UI", "Inter", "Noto Sans", "sans-serif"])
    f.setPixelSize(max(1, round(tamanho * 4 / 3)))
    f.setWeight(QFont.Weight.DemiBold if negrito else QFont.Weight.Normal)
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
