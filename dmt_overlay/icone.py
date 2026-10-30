from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap

from . import tema

ARQUIVO = Path(__file__).parent / "recursos" / "icone.png"


def desenhar_icone(tamanho: int = 256) -> QPixmap:
    pixmap = QPixmap(tamanho, tamanho)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    s = tamanho / 256
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#141416"))
    p.drawRoundedRect(QRectF(8 * s, 8 * s, 240 * s, 240 * s), 52 * s, 52 * s)
    p.setBrush(tema.DESTAQUE)
    p.drawRoundedRect(QRectF(40 * s, 176 * s, 176 * s, 22 * s), 11 * s, 11 * s)
    fonte = QFont()
    fonte.setFamilies(["Segoe UI", "Inter", "Noto Sans", "sans-serif"])
    fonte.setWeight(QFont.Weight.Black)
    fonte.setPixelSize(round(92 * s))
    fonte.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 92)
    p.setFont(fonte)
    p.setPen(QColor("#f0efec"))
    p.drawText(QRectF(0, 40 * s, tamanho, 120 * s), Qt.AlignmentFlag.AlignCenter, "DMT")
    p.end()
    return pixmap


def icone() -> QIcon:
    if ARQUIVO.exists():
        return QIcon(str(ARQUIVO))
    return QIcon(desenhar_icone())
