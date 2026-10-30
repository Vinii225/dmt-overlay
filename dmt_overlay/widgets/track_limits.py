from __future__ import annotations

import math

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter

from .. import tema
from .base import DIR, WidgetOverlay, rotulo, texto


class TrackLimits(WidgetOverlay):
    nome = "track_limits"
    titulo = "Track limits"
    largura = 120
    altura = 70
    posicao_padrao = (1095, 140)

    def preparar(self, quadro):
        j = quadro.estado.jogador
        return (round(j.track_limits, 2), quadro.estado.sessao.track_limits_punicao)

    def desenhar(self, p: QPainter, dados) -> None:
        pontos, punicao = dados
        rotulo(p, QRectF(10, 6, 100, 12), "Track limits")
        if punicao <= 0:
            texto(p, QRectF(10, 20, 100, 30), f"{pontos:g}", tema.TEXTO, 16, True)
            return
        fracao = pontos / punicao
        cor = tema.CRITICO if fracao >= 0.75 else tema.ALERTA if fracao >= 0.5 else tema.TEXTO
        texto(p, QRectF(10, 20, 60, 30), f"{pontos:g}", cor, 18, True)
        texto(p, QRectF(60, 20, 50, 30), f"/ {punicao:g}", tema.TEXTO_SECUNDARIO, 10, False, DIR)
        segmentos = max(1, math.ceil(punicao))
        largura = (self.largura - 20 - (segmentos - 1) * 3) / segmentos
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(segmentos):
            preenchido = max(0.0, min(1.0, pontos - i))
            caixa = QRectF(10 + i * (largura + 3), 54, largura, 6)
            p.setBrush(tema.TRILHO)
            p.drawRoundedRect(caixa, 2, 2)
            if preenchido > 0:
                p.setBrush(cor if cor != tema.TEXTO else tema.TEXTO_SECUNDARIO)
                p.drawRoundedRect(QRectF(caixa.left(), caixa.top(), caixa.width() * preenchido, caixa.height()), 2, 2)
