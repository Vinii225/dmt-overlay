from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter

from .. import tema
from .base import CENTRO, WidgetOverlay, barra, rotulo, texto


class Pedais(WidgetOverlay):
    nome = "pedais"
    titulo = "Pedais"
    largura = 132
    altura = 128
    posicao_padrao = (1180, 880)
    opcoes_padrao = {"mostrar_embreagem": True, "mostrar_volante": True}

    def preparar(self, quadro):
        j = quadro.estado.jogador
        return (
            round(j.acelerador, 2),
            round(j.freio, 2),
            round(j.embreagem, 2),
            round(j.volante, 2),
            j.abs_ativo,
            j.tc_ativo,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        acel, freio, embr, volante, abs_ativo, tc_ativo = dados
        colunas = [("ACL", acel, tema.ACELERADOR, tc_ativo, "TC"), ("FRE", freio, tema.FREIO, abs_ativo, "ABS")]
        if self.config["mostrar_embreagem"]:
            colunas.append(("EMB", embr, tema.EMBREAGEM, False, ""))
        topo, base = 22.0, 96.0
        if not self.config["mostrar_volante"]:
            base = 112.0
        largura_col = (self.largura - 16) / len(colunas)
        for i, (nome, valor, cor, alerta, sigla) in enumerate(colunas):
            x = 8 + i * largura_col
            centro = QRectF(x, 4, largura_col, 16)
            if alerta:
                texto(p, centro, sigla, tema.ALERTA, 7.5, True, CENTRO)
            else:
                texto(p, centro, f"{valor * 100:.0f}", tema.TEXTO_SECUNDARIO, 7.5, True, CENTRO)
            trilho = QRectF(x + largura_col / 2 - 7, topo, 14, base - topo)
            barra(p, trilho, valor, tema.ALERTA if alerta else cor, vertical=True, raio=3)
            rotulo(p, QRectF(x, base + 1, largura_col, 12), nome, CENTRO)
        if self.config["mostrar_volante"]:
            trilho = QRectF(10, 116, self.largura - 20, 4)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tema.TRILHO)
            p.drawRoundedRect(trilho, 2, 2)
            meio = trilho.center().x()
            deslocamento = max(-1.0, min(1.0, volante)) * trilho.width() / 2
            p.setBrush(tema.TEXTO_SECUNDARIO)
            p.drawRoundedRect(QRectF(min(meio, meio + deslocamento), trilho.top(), max(2.0, abs(deslocamento)), 4), 2, 2)
            p.setBrush(tema.TEXTO)
            p.drawRect(QRectF(meio - 0.75, trilho.top() - 2, 1.5, 8))
