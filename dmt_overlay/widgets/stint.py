from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import duracao
from .base import DIR, WidgetOverlay, rotulo, texto


class Stint(WidgetOverlay):
    nome = "stint"
    titulo = "Stint e estratégia"
    largura = 230
    altura = 104
    posicao_padrao = (1640, 470)

    def preparar(self, quadro):
        e = quadro.estrategia
        return (
            int(e.tempo_stint),
            e.voltas_stint,
            e.volta_atual,
            e.janela_inicio,
            e.janela_fim,
            e.paradas,
            round(e.abastecer_litros),
            round(e.abastecer_energia * 100),
            e.valido,
            quadro.combustivel.usa_energia,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        tempo, voltas, atual, inicio, fim, paradas, litros, energia, valido, usa_energia = dados
        rotulo(p, QRectF(10, 6, 100, 12), "Stint")
        texto(p, QRectF(10, 18, 110, 24), duracao(tempo), tema.TEXTO, 14, True)
        rotulo(p, QRectF(120, 6, 100, 12), "Voltas", DIR)
        texto(p, QRectF(120, 18, 100, 24), str(voltas), tema.TEXTO, 14, True, DIR)

        p.setPen(tema.BORDA)
        p.drawLine(10, 47, self.largura - 10, 47)

        rotulo(p, QRectF(10, 52, 120, 12), "Janela de box")
        if not valido:
            texto(p, QRectF(10, 64, 210, 18), "Calculando após 2 voltas…", tema.TEXTO_APAGADO, 8.5)
            return
        if paradas == 0:
            texto(p, QRectF(10, 64, 210, 18), "Sem parada até o fim", tema.BOM, 9.5, True)
            return
        if fim <= atual:
            janela, cor = "Parar agora", tema.CRITICO
        elif inicio <= atual:
            janela, cor = f"Aberta até V{fim}", tema.ALERTA if fim - atual <= 2 else tema.BOM
        else:
            janela, cor = f"V{inicio} – V{fim}", tema.TEXTO
        texto(p, QRectF(10, 64, 140, 18), janela, cor, 10, True)
        rotulo(p, QRectF(150, 52, 70, 12), "Paradas", DIR)
        texto(p, QRectF(150, 64, 70, 18), str(paradas), tema.TEXTO, 10, True, DIR)
        rotulo(p, QRectF(10, 84, 60, 14), "Abastecer")
        valor = f"+{litros} L" + (f"  ·  VE +{energia}%" if usa_energia and energia > 0 else "")
        texto(p, QRectF(70, 84, 150, 14), valor, tema.TEXTO_SECUNDARIO, 8.5, False, DIR)
