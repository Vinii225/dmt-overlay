from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import tempo_volta
from .base import DIR, WidgetOverlay, rotulo, texto


class Delta(WidgetOverlay):
    nome = "delta"
    titulo = "Delta"
    largura = 250
    altura = 70
    posicao_padrao = (835, 140)
    opcoes_padrao = {"limite": 2.0}

    def preparar(self, quadro):
        e = quadro.estado
        j = e.jogador
        carro = e.carro_jogador
        atual = e.sessao.tempo_decorrido - j.inicio_volta if j.inicio_volta > 0 else 0.0
        melhor = carro.melhor_volta if carro else 0.0
        ultima = carro.ultima_volta if carro else 0.0
        return (round(j.delta_melhor, 2), round(atual, 1), ultima, melhor, j.volta_invalidada)

    def desenhar(self, p: QPainter, dados) -> None:
        delta, atual, ultima, melhor, invalida = dados
        limite = self.config["limite"]
        trilho = QRectF(8, 8, self.largura - 16, 6)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tema.TRILHO)
        p.drawRoundedRect(trilho, 3, 3)
        meio = trilho.center().x()
        fracao = max(-1.0, min(1.0, delta / limite))
        cor = tema.BOM if delta <= 0 else tema.CRITICO
        largura = abs(fracao) * trilho.width() / 2
        if largura > 0.5:
            x = meio - largura if fracao < 0 else meio
            p.setBrush(cor)
            p.drawRoundedRect(QRectF(x, trilho.top(), largura, trilho.height()), 3, 3)
        p.setBrush(tema.TEXTO)
        p.drawRect(QRectF(meio - 1, trilho.top() - 3, 2, trilho.height() + 6))

        cor_texto = tema.BOM if delta < -0.005 else tema.CRITICO if delta > 0.005 else tema.TEXTO
        texto(p, QRectF(8, 18, 110, 30), f"{delta:+.2f}", cor_texto, 18, True)
        cor_atual = tema.CRITICO if invalida else tema.TEXTO
        texto(p, QRectF(118, 18, 124, 30), tempo_volta(atual)[:-2] if atual > 0 else "-:--.-", cor_atual, 13, True, DIR)
        rotulo(p, QRectF(8, 50, 40, 14), "Última")
        texto(p, QRectF(44, 50, 70, 14), tempo_volta(ultima), tema.TEXTO_SECUNDARIO, 8.5)
        rotulo(p, QRectF(128, 50, 50, 14), "Melhor")
        texto(p, QRectF(164, 50, 78, 14), tempo_volta(melhor), tema.TEXTO_SECUNDARIO, 8.5, False, DIR)
