from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen

from .. import tema
from ..calculos.radar import COMPRIMENTO_CARRO, LARGURA_CARRO, calcular_vizinhos
from .base import WidgetOverlay


class Radar(WidgetOverlay):
    nome = "radar"
    titulo = "Radar"
    largura = 170
    altura = 170
    posicao_padrao = (875, 640)
    opcoes_padrao = {"alcance": 15.0, "inverter_lados": False}

    def preparar(self, quadro):
        vizinhos = calcular_vizinhos(quadro.estado, self.config["alcance"], self.config["inverter_lados"])
        if not vizinhos:
            return None
        return tuple(
            (v.classe, round(v.direita, 1), round(v.frente, 1), round(v.angulo, 2), v.lado_a_lado) for v in vizinhos[:8]
        )

    def desenhar(self, p: QPainter, dados) -> None:
        centro = QPointF(self.largura / 2, self.altura / 2)
        escala = (self.largura / 2 - 10) / self.config["alcance"]
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(tema.TRILHO, 1))
        for metros in (5, 10):
            raio = metros * escala
            p.drawEllipse(centro, raio, raio)
        p.drawLine(QPointF(centro.x(), 8), QPointF(centro.x(), self.altura - 8))

        esquerda = any(lado and d < 0 for _, d, _, _, lado in dados)
        direita = any(lado and d > 0 for _, d, _, _, lado in dados)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tema.ALERTA)
        if esquerda:
            p.drawRoundedRect(QRectF(4, 30, 4, self.altura - 60), 2, 2)
        if direita:
            p.drawRoundedRect(QRectF(self.largura - 8, 30, 4, self.altura - 60), 2, 2)

        largura, comprimento = LARGURA_CARRO * escala, COMPRIMENTO_CARRO * escala
        for classe, d, f, angulo, lado in reversed(dados):
            _, cor = tema.classe(classe)
            p.save()
            p.translate(centro.x() + d * escala, centro.y() - f * escala)
            p.rotate(angulo * 57.29578)
            p.setPen(QPen(tema.FUNDO, 2))
            p.setBrush(tema.ALERTA if lado else cor)
            p.drawRoundedRect(QRectF(-largura / 2, -comprimento / 2, largura, comprimento), 3, 3)
            p.restore()

        p.setPen(QPen(tema.FUNDO, 2))
        p.setBrush(tema.TEXTO)
        p.drawRoundedRect(QRectF(centro.x() - largura / 2, centro.y() - comprimento / 2, largura, comprimento), 3, 3)
