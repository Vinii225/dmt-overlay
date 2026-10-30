from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import nome_curto
from ..calculos.multiclasse import alerta_multiclasse
from .base import DIR, WidgetOverlay, rotulo, selo_classe, texto

ALTURA_LINHA = 30


class Multiclasse(WidgetOverlay):
    nome = "multiclasse"
    titulo = "Alerta multiclasse"
    largura = 250
    altura = 8 + ALTURA_LINHA * 2
    posicao_padrao = (835, 220)
    opcoes_padrao = {"janela_atras": 3.0, "janela_frente": 2.5}

    def tamanho_base(self) -> QSize:
        linhas = len(self._dados) if self._dados else 2
        return QSize(self.largura, 8 + ALTURA_LINHA * linhas)

    def atualizar(self, quadro) -> None:
        anterior = len(self._dados) if self._dados else 0
        super().atualizar(quadro)
        atual = len(self._dados) if self._dados else 0
        if atual and atual != anterior:
            self.ajustar_tamanho()

    def preparar(self, quadro):
        alerta = alerta_multiclasse(quadro.estado, self.config["janela_atras"], self.config["janela_frente"])
        if alerta.vazio:
            return None
        linhas = []
        if alerta.chegando:
            c = alerta.chegando
            linhas.append(("Chegando", c.carro.classe, c.carro.piloto, round(abs(c.tempo), 1), True))
        if alerta.a_frente:
            c = alerta.a_frente
            linhas.append(("Tráfego à frente", c.carro.classe, c.carro.piloto, round(c.tempo, 1), False))
        return tuple(linhas)

    def desenhar(self, p: QPainter, dados) -> None:
        y = 4.0
        for titulo, classe, piloto, tempo, atras in dados:
            _, cor_classe = tema.classe(classe)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(cor_classe)
            p.drawRoundedRect(QRectF(4, y, 4, ALTURA_LINHA - 4), 2, 2)
            selo_classe(p, QRectF(14, y + 7, 30, 14), classe)
            rotulo(p, QRectF(52, y + 1, 120, 12), titulo)
            texto(p, QRectF(52, y + 12, 130, 14), nome_curto(piloto, 18), tema.TEXTO_SECUNDARIO, 8)
            urgente = atras and tempo < 1.0
            cor = tema.CRITICO if urgente else tema.ALERTA if atras else tema.TEXTO
            texto(p, QRectF(170, y, 72, ALTURA_LINHA - 4), f"{tempo:.1f}s", cor, 14, True, DIR)
            y += ALTURA_LINHA
