from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter

from .. import tema
from .base import CENTRO, DIR, WidgetOverlay, rotulo, texto

POSICOES = ("DE", "DD", "TE", "TD")


class Pneus(WidgetOverlay):
    nome = "pneus"
    titulo = "Pneus"
    largura = 230
    altura = 150
    posicao_padrao = (1640, 590)
    opcoes_padrao = {"unidade_pressao": "kpa", "faixa_temperatura": 15.0, "freio_ideal": 500.0}

    def preparar(self, quadro):
        j = quadro.estado.jogador
        psi = self.config["unidade_pressao"] == "psi"
        pneus = tuple(
            (
                tuple(round(t) for t in pn.temp_superficie),
                pn.temp_ideal or 85.0,
                round(pn.pressao * 0.145038, 1) if psi else round(pn.pressao),
                round(pn.restante * 100),
                round(pn.temp_freio, -1),
                pn.furado,
            )
            for pn in j.pneus
        )
        return (j.composto_dianteiro, j.composto_traseiro, pneus)

    def desenhar(self, p: QPainter, dados) -> None:
        dianteiro, traseiro, pneus = dados
        faixa = self.config["faixa_temperatura"]
        unidade = "psi" if self.config["unidade_pressao"] == "psi" else "kPa"
        composto = dianteiro if dianteiro == traseiro else f"{dianteiro} / {traseiro}"
        texto(p, QRectF(10, 4, 150, 16), composto or "Pneus", tema.TEXTO, 8.5, True)
        rotulo(p, QRectF(150, 4, 70, 16), unidade, DIR)
        largura_bloco = (self.largura - 26) / 2
        for i, (temps, ideal, pressao, restante, freio, furado) in enumerate(pneus):
            coluna, linha = i % 2, i // 2
            x = 10 + coluna * (largura_bloco + 6)
            y = 24 + linha * 62
            largura_faixa = (largura_bloco - 4) / 3
            for k, t in enumerate(temps):
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(tema.CRITICO if furado else tema.cor_temperatura(t, ideal, faixa))
                p.drawRoundedRect(QRectF(x + k * (largura_faixa + 2), y, largura_faixa, 22), 3, 3)
                texto(p, QRectF(x + k * (largura_faixa + 2), y, largura_faixa, 22), str(t), tema.TEXTO, 8, True, CENTRO)
            rotulo(p, QRectF(x, y + 24, 20, 14), POSICOES[i])
            texto(p, QRectF(x + 18, y + 24, largura_bloco - 18, 14), f"{pressao}", tema.TEXTO, 8.5, True, DIR)
            desgaste_cor = tema.CRITICO if restante < 30 else tema.ALERTA if restante < 50 else tema.TEXTO_SECUNDARIO
            texto(p, QRectF(x, y + 38, largura_bloco / 2, 14), f"{restante}%", desgaste_cor, 8)
            cor_freio = tema.cor_temperatura(freio, self.config["freio_ideal"], 250)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(cor_freio)
            p.drawEllipse(QRectF(x + largura_bloco / 2 + 4, y + 42, 6, 6))
            area_freio = QRectF(x + largura_bloco / 2, y + 38, largura_bloco / 2, 14)
            texto(p, area_freio, f"{freio:.0f}°", tema.TEXTO_SECUNDARIO, 8, False, DIR)
