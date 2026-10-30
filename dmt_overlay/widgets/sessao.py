from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import duracao
from ..telemetria.modelos import NOMES_SESSAO
from .base import DIR, WidgetOverlay, rotulo, texto


class Sessao(WidgetOverlay):
    nome = "sessao"
    titulo = "Sessão"
    largura = 360
    altura = 40
    posicao_padrao = (780, 20)

    def preparar(self, quadro):
        s = quadro.estado.sessao
        carro = quadro.estado.carro_jogador
        if s.por_voltas:
            volta = carro.voltas + 1 if carro else 0
            restante = f"Volta {volta}/{s.voltas_max}"
        else:
            restante = duracao(s.tempo_restante)
        hora = int(s.hora_do_dia // 3600) % 24, int(s.hora_do_dia % 3600 // 60)
        posicao = carro.posicao if carro else 0
        clima = (round(s.temp_ar), round(s.temp_pista), round(s.chuva * 100))
        return (NOMES_SESSAO.get(s.tipo, ""), restante, hora, *clima, posicao)

    def desenhar(self, p: QPainter, dados) -> None:
        nome, restante, (h, m), ar, pista, chuva, posicao = dados
        rotulo(p, QRectF(10, 4, 80, 12), nome)
        texto(p, QRectF(10, 15, 100, 20), restante, tema.TEXTO, 12, True)
        if posicao:
            rotulo(p, QRectF(112, 4, 40, 12), "Pos")
            texto(p, QRectF(112, 15, 40, 20), f"P{posicao}", tema.DESTAQUE, 12, True)
        rotulo(p, QRectF(160, 4, 50, 12), "Hora")
        texto(p, QRectF(160, 15, 50, 20), f"{h:02d}:{m:02d}", tema.TEXTO_SECUNDARIO, 10)
        rotulo(p, QRectF(212, 4, 50, 12), "Ar / Pista")
        texto(p, QRectF(212, 15, 70, 20), f"{ar}° / {pista}°", tema.TEXTO_SECUNDARIO, 10)
        rotulo(p, QRectF(290, 4, 60, 12), "Chuva", DIR)
        cor = tema.FRIO if chuva > 0 else tema.TEXTO_SECUNDARIO
        texto(p, QRectF(290, 15, 60, 20), f"{chuva}%", cor, 10, False, DIR)
