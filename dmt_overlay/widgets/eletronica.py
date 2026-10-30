from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter

from .. import tema
from .base import CENTRO, WidgetOverlay, rotulo, texto


class Eletronica(WidgetOverlay):
    nome = "eletronica"
    titulo = "Eletrônica"
    largura = 250
    altura = 40
    posicao_padrao = (835, 1000)

    def preparar(self, quadro):
        j = quadro.estado.jogador
        return (
            round(j.balanco_freio * 100, 1),
            j.tc,
            j.tc_corte,
            j.tc_slip,
            j.abs,
            j.mapa_motor,
            j.tc_ativo,
            j.abs_ativo,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        bb, tc, corte, slip, abs_, mapa, tc_ativo, abs_ativo = dados
        itens = (
            ("BB", f"{bb:.1f}", False),
            ("TC", str(tc), tc_ativo),
            ("Corte", str(corte), False),
            ("Slip", str(slip), False),
            ("ABS", str(abs_), abs_ativo),
            ("Mapa", str(mapa), False),
        )
        largura = (self.largura - 12) / len(itens)
        for i, (nome, valor, ativo) in enumerate(itens):
            x = 6 + i * largura
            rotulo(p, QRectF(x, 4, largura, 12), nome, CENTRO)
            texto(p, QRectF(x, 16, largura, 20), valor, tema.ALERTA if ativo else tema.TEXTO, 11, True, CENTRO)
