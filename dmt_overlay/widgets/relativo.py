from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import nome_curto, numero_carro
from ..calculos.relativo import calcular_relativo
from .base import CENTRO, DIR, WidgetOverlay, selo_classe, texto

ALTURA_LINHA = 22


class Relativo(WidgetOverlay):
    nome = "relativo"
    titulo = "Relativo"
    largura = 300
    posicao_padrao = (40, 640)
    opcoes_padrao = {"carros_cada_lado": 3}

    def tamanho_base(self) -> QSize:
        linhas = self.config["carros_cada_lado"] * 2 + 1
        return QSize(self.largura, 8 + linhas * ALTURA_LINHA)

    def preparar(self, quadro):
        linhas = calcular_relativo(quadro.estado, self.config["carros_cada_lado"])
        return tuple(
            (
                l.carro.posicao,
                l.carro.classe,
                numero_carro(l.carro.equipe),
                l.carro.piloto,
                round(l.tempo, 1),
                l.voltas_diferenca,
                l.carro.nos_boxes,
                l.carro.jogador,
            )
            for l in linhas
        )

    def desenhar(self, p: QPainter, dados) -> None:
        y = 4.0
        for pos, classe, numero, piloto, tempo, voltas, boxes, jogador in dados:
            linha = QRectF(4, y, self.largura - 8, ALTURA_LINHA - 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tema.FUNDO_DESTAQUE if jogador else tema.FUNDO_LINHA)
            p.drawRoundedRect(linha, 3, 3)
            if jogador:
                p.setBrush(tema.DESTAQUE)
                p.drawRoundedRect(QRectF(4, y, 3, ALTURA_LINHA - 2), 1.5, 1.5)
            if voltas > 0:
                cor_nome = tema.VOLTA_A_FRENTE
            elif voltas < 0:
                cor_nome = tema.VOLTA_ATRAS
            else:
                cor_nome = tema.TEXTO
            meio = y + (ALTURA_LINHA - 2) / 2
            texto(p, QRectF(10, y, 24, ALTURA_LINHA - 2), str(pos), tema.TEXTO_SECUNDARIO, 8.5, True, DIR)
            selo_classe(p, QRectF(40, meio - 7, 28, 14), classe)
            texto(p, QRectF(72, y, 30, ALTURA_LINHA - 2), numero, tema.TEXTO_APAGADO, 8, True)
            texto(p, QRectF(102, y, 118, ALTURA_LINHA - 2), nome_curto(piloto, 16), cor_nome, 9, jogador)
            if boxes:
                caixa = QRectF(222, meio - 6, 22, 12)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(tema.TRILHO)
                p.drawRoundedRect(caixa, 3, 3)
                texto(p, caixa, "BOX", tema.TEXTO_SECUNDARIO, 6, True, CENTRO)
            valor = "" if jogador else f"{tempo:+.1f}"
            texto(p, QRectF(244, y, 48, ALTURA_LINHA - 2), valor, tema.TEXTO, 9, False, DIR)
            y += ALTURA_LINHA
