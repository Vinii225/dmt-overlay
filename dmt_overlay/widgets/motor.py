from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter

from .. import tema
from .base import CENTRO, DIR, WidgetOverlay, rotulo, texto


def nome_marcha(marcha: int) -> str:
    if marcha < 0:
        return "R"
    if marcha == 0:
        return "N"
    return str(marcha)


class Motor(WidgetOverlay):
    nome = "motor"
    titulo = "Marcha e RPM"
    largura = 250
    altura = 64
    posicao_padrao = (835, 900)
    opcoes_padrao = {"unidade_velocidade": "kmh", "luz_troca": 0.94}

    def preparar(self, quadro):
        j = quadro.estado.jogador
        fator = 3.6 if self.config["unidade_velocidade"] == "kmh" else 2.23694
        no_limite = j.rpm_max > 0 and j.rpm / j.rpm_max >= self.config["luz_troca"]
        piscar = no_limite and int(quadro.instante * 8) % 2 == 0
        return (j.marcha, round(j.rpm, -1), j.rpm_max, round(j.velocidade * fator), j.limitador, piscar)

    def desenhar(self, p: QPainter, dados) -> None:
        marcha, rpm, rpm_max, velocidade, limitador, piscar = dados
        fracao = rpm / rpm_max if rpm_max > 0 else 0.0
        troca = self.config["luz_troca"]
        segmentos = 20
        largura_seg = (self.largura - 16 - (segmentos - 1) * 2) / segmentos
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(segmentos):
            limiar = (i + 1) / segmentos
            aceso = fracao >= limiar * troca
            if limiar > 0.85:
                cor = tema.CRITICO
            elif limiar > 0.65:
                cor = tema.ALERTA
            else:
                cor = tema.BOM
            if fracao >= troca:
                cor = tema.CRITICO if piscar else tema.TRILHO
                aceso = True
            p.setBrush(cor if aceso else tema.TRILHO)
            p.drawRoundedRect(QRectF(8 + i * (largura_seg + 2), 7, largura_seg, 7), 2, 2)

        cor_marcha = tema.CRITICO if fracao >= troca and piscar else tema.TEXTO
        texto(p, QRectF(8, 18, 50, 42), nome_marcha(marcha), cor_marcha, 27, True, CENTRO)
        texto(p, QRectF(66, 20, 96, 26), f"{velocidade}", tema.TEXTO, 16, True)
        rotulo(p, QRectF(66, 44, 96, 12), "km/h" if self.config["unidade_velocidade"] == "kmh" else "mph")
        texto(p, QRectF(150, 20, 92, 26), f"{rpm:,.0f}".replace(",", "."), tema.TEXTO_SECUNDARIO, 11, False, DIR)
        rotulo(p, QRectF(150, 44, 92, 12), "rpm", DIR)
        if limitador:
            caixa = QRectF(100, 46, 50, 13)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tema.ALERTA)
            p.drawRoundedRect(caixa, 3, 3)
            texto(p, caixa, "PIT", tema.FUNDO.darker(300), 7, True, CENTRO)
