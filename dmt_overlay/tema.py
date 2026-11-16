from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QBrush, QColor, QFont, QFontDatabase, QGuiApplication, QLinearGradient

# Cada tema troca as cores e a fonte; os widgets leem tema.X na hora de desenhar,
# então aplicar() muda tudo ao vivo.
TEMAS: dict[str, dict] = {
    "padrao": {
        "nome": "Padrão",
        "FUNDO": QColor(20, 20, 22, 215),
        "FUNDO_FIM": QColor(20, 20, 22, 215),
        "FUNDO_LINHA": QColor(255, 255, 255, 10),
        "FUNDO_DESTAQUE": QColor(255, 255, 255, 28),
        "BORDA": QColor(255, 255, 255, 26),
        "LARGURA_BORDA": 1.0,
        "TEXTO": QColor("#f0efec"),
        "TEXTO_SECUNDARIO": QColor("#c3c2b7"),
        "TEXTO_APAGADO": QColor("#898781"),
        "TEXTO_POSICAO": QColor("#c3c2b7"),
        "TRILHO": QColor("#2c2c2a"),
        "DESTAQUE": QColor("#2fbf71"),
        "RAIO": 6,
        "FAMILIAS": ["Segoe UI", "Inter", "Noto Sans", "sans-serif"],
        "ESCALA_FONTE": 1.0,
        "ITALICO": False,
        "MAIUSCULAS": False,
        "FAIXA_CABECALHO": False,
    },
    # Visual de transmissão de endurance: azul-marinho, borda azul, fonte condensada e sobrenomes em caixa alta.
    "transmissao": {
        "nome": "Transmissão",
        "FUNDO": QColor(30, 27, 84, 236),
        "FUNDO_FIM": QColor(15, 13, 48, 236),
        "FUNDO_LINHA": QColor(255, 255, 255, 14),
        "FUNDO_DESTAQUE": QColor(64, 150, 255, 70),
        "BORDA": QColor(52, 152, 255, 220),
        "LARGURA_BORDA": 1.6,
        "TEXTO": QColor("#ffffff"),
        "TEXTO_SECUNDARIO": QColor("#cfd2f5"),
        "TEXTO_APAGADO": QColor("#8d91c9"),
        "TEXTO_POSICAO": QColor("#ffffff"),
        "TRILHO": QColor("#2a2770"),
        "DESTAQUE": QColor("#3fb4ff"),
        "RAIO": 7,
        "FAMILIAS": ["Barlow Condensed", "Segoe UI", "sans-serif"],
        "ESCALA_FONTE": 1.22,
        "ITALICO": True,
        "MAIUSCULAS": True,
        "FAIXA_CABECALHO": True,
    },
}

FUNDO = FUNDO_FIM = FUNDO_LINHA = FUNDO_DESTAQUE = BORDA = QColor()
TEXTO = TEXTO_SECUNDARIO = TEXTO_APAGADO = TEXTO_POSICAO = TRILHO = DESTAQUE = QColor()
LARGURA_BORDA = 1.0
RAIO = 6
FAMILIAS: list[str] = []
ESCALA_FONTE = 1.0
ITALICO = MAIUSCULAS = FAIXA_CABECALHO = False
atual = "padrao"

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


def aplicar(nome: str) -> None:
    global atual
    atual = nome if nome in TEMAS else "padrao"
    globals().update({k: v for k, v in TEMAS[atual].items() if k.isupper()})
    _carregar_fontes()
    fonte.cache_clear()


def pincel_fundo(altura: float) -> QBrush:
    if FUNDO == FUNDO_FIM:
        return QBrush(FUNDO)
    gradiente = QLinearGradient(0, 0, 0, altura)
    gradiente.setColorAt(0, FUNDO)
    gradiente.setColorAt(1, FUNDO_FIM)
    return QBrush(gradiente)


def nome_piloto(nome: str, limite: int = 16) -> str:
    """Nome como o tema mostra: "B. Hartley" no padrão, "HARTLEY" na transmissão."""
    from .calculos.formatacao import nome_curto

    if not MAIUSCULAS:
        return nome_curto(nome, limite)
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
    f = QFont()
    f.setFamilies(FAMILIAS)
    f.setPixelSize(max(1, round(tamanho * ESCALA_FONTE * 4 / 3)))
    if ITALICO:
        f.setWeight(QFont.Weight.Bold if negrito else QFont.Weight.Medium)
        f.setItalic(negrito)
    else:
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


aplicar("padrao")
