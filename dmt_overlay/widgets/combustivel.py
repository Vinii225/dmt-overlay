from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter

from .. import tema
from .base import DIR, WidgetOverlay, barra, rotulo, texto


class Combustivel(WidgetOverlay):
    nome = "combustivel"
    titulo = "Combustível"
    largura = 230
    altura = 118
    posicao_padrao = (1640, 760)
    opcoes_padrao = {"voltas_alerta": 3.0}

    def preparar(self, quadro):
        c = quadro.combustivel
        return (
            round(c.atual, 1),
            c.tanque,
            round(c.media, 2),
            round(c.voltas_restantes, 1),
            round(c.voltas_para_fim, 1),
            round(c.para_reabastecer, 1),
            round(c.energia * 100, 1),
            round(c.energia_voltas, 1),
            c.usa_energia,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        atual, tanque, media, voltas, para_fim, reabastecer, energia, energia_voltas, usa_energia = dados
        limitante = min(voltas, energia_voltas) if usa_energia and energia_voltas > 0 else voltas
        if limitante <= 0:
            cor_voltas = tema.TEXTO
        elif limitante <= self.config["voltas_alerta"]:
            cor_voltas = tema.CRITICO
        elif limitante <= self.config["voltas_alerta"] * 2:
            cor_voltas = tema.ALERTA
        else:
            cor_voltas = tema.TEXTO

        rotulo(p, QRectF(10, 6, 100, 12), "Voltas restantes")
        texto(p, QRectF(10, 18, 100, 34), f"{limitante:.1f}" if limitante > 0 else "--", cor_voltas, 22, True)
        rotulo(p, QRectF(120, 6, 100, 12), "Média / volta", DIR)
        texto(p, QRectF(120, 18, 100, 20), f"{media:.2f} L" if media > 0 else "-- L", tema.TEXTO, 11, True, DIR)
        texto(p, QRectF(120, 36, 100, 16), f"{atual:.1f} / {tanque:.0f} L", tema.TEXTO_SECUNDARIO, 8.5, False, DIR)

        y = 58.0
        rotulo(p, QRectF(10, y, 30, 12), "Comb.")
        barra(p, QRectF(48, y + 4, 172, 5), atual / tanque if tanque > 0 else 0, tema.TEXTO_SECUNDARIO)
        if usa_energia:
            y += 15
            rotulo(p, QRectF(10, y, 30, 12), "VE")
            barra(p, QRectF(48, y + 4, 128, 5), energia / 100, tema.DESTAQUE)
            texto(p, QRectF(176, y, 44, 12), f"{energia:.0f}%", tema.TEXTO_SECUNDARIO, 7.5, False, DIR)

        y = 94.0
        p.setPen(tema.BORDA)
        p.drawLine(10, int(y - 3), self.largura - 10, int(y - 3))
        rotulo(p, QRectF(10, y, 60, 18), "Até o fim")
        texto(p, QRectF(54, y, 50, 18), f"{para_fim:.1f} V" if para_fim > 0 else "--", tema.TEXTO, 8.5)
        rotulo(p, QRectF(106, y, 60, 18), "Abastecer")
        cor = tema.ALERTA if reabastecer > 0 else tema.BOM
        valor = f"+{reabastecer:.1f} L" if reabastecer > 0 else ("OK" if media > 0 and para_fim > 0 else "--")
        texto(p, QRectF(150, y, 70, 18), valor, cor if media > 0 else tema.TEXTO, 9, True, DIR)
