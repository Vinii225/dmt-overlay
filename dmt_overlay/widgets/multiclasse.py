from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPolygonF

from .. import tema
from ..calculos.multiclasse import alerta_multiclasse
from .base import DIR, Opcao, WidgetOverlay, barra, rotulo, selo_classe, texto

AZUL = QColor("#2f7cff")


def desenhar_bandeira(p: QPainter, area: QRectF, cor: QColor) -> None:
    """Bandeira tremulando num mastro, do tamanho da área."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(tema.TEXTO_SECUNDARIO)
    p.drawRoundedRect(QRectF(area.left(), area.top(), 2.5, area.height()), 1, 1)
    x, y, w, h = area.left() + 2.5, area.top() + 1, area.width() - 2.5, area.height() * 0.62
    pano = QPainterPath(QPointF(x, y))
    pano.cubicTo(QPointF(x + w * 0.35, y - 3), QPointF(x + w * 0.65, y + 3), QPointF(x + w, y))
    pano.lineTo(QPointF(x + w, y + h))
    pano.cubicTo(QPointF(x + w * 0.65, y + h + 3), QPointF(x + w * 0.35, y + h - 3), QPointF(x, y + h))
    pano.closeSubpath()
    p.fillPath(pano, cor)


def desenhar_seta(p: QPainter, area: QRectF, cor: QColor) -> None:
    """Duas setas para cima: carro mais lento logo à frente."""
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(cor)
    cx, meia = area.center().x(), area.width() / 2
    for topo in (area.top(), area.top() + area.height() * 0.45):
        p.drawPolygon(QPolygonF([
            QPointF(cx, topo), QPointF(cx + meia, topo + meia), QPointF(cx + meia, topo + meia + 4),
            QPointF(cx, topo + 4), QPointF(cx - meia, topo + meia + 4), QPointF(cx - meia, topo + meia),
        ]))


class Multiclasse(WidgetOverlay):
    nome = "multiclasse"
    titulo = "Tráfego multiclasse"
    largura = 260
    altura = 50
    posicao_padrao = (835, 220)
    opcoes_padrao = {"janela_atras": 3.0, "janela_frente": 2.5}
    descricao = "Aparece só quando precisa: bandeira azul ou classe mais lenta à frente, o que estiver mais perto."
    opcoes = {
        "janela_atras": Opcao("Bandeira azul", "Classe mais rápida a menos disso atrás.", 1, 10, 0.5, " s"),
        "janela_frente": Opcao("Tráfego à frente", "Classe mais lenta a menos disso à frente.", 1, 10, 0.5, " s"),
    }

    def preparar(self, quadro):
        alerta = alerta_multiclasse(quadro.estado, self.config["janela_atras"], self.config["janela_frente"])
        linha = alerta.mais_perto
        if linha is None:
            return None
        atras = linha.tempo < 0
        janela = self.config["janela_atras" if atras else "janela_frente"]
        tempo = abs(linha.tempo)
        # Pisca só no último segundo da bandeira azul, para chamar atenção sem cansar.
        piscar = atras and tempo < 1.0 and int(quadro.instante * 4) % 2 == 0
        # Proximidade em centésimos: a barra anda suave enquanto o carro chega.
        perto = round(max(0.0, min(1.0, 1 - tempo / janela)), 2)
        return (atras, linha.carro.classe, linha.carro.piloto, round(tempo, 1), perto, piscar)

    def desenhar(self, p: QPainter, dados) -> None:
        atras, classe, piloto, tempo, perto, piscar = dados
        _, cor_classe = tema.classe(classe)
        if atras:
            fundo = QColor(AZUL)
            fundo.setAlpha(110 if piscar else 55)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(fundo)
            p.drawRoundedRect(QRectF(3, 3, self.largura - 6, self.altura - 6), tema.RAIO - 2, tema.RAIO - 2)
            desenhar_bandeira(p, QRectF(10, 9, 26, 28), AZUL)
        else:
            desenhar_seta(p, QRectF(13, 11, 20, 24), cor_classe)
        rotulo(p, QRectF(44, 5, 150, 12), "Bandeira azul" if atras else "Tráfego à frente")
        selo_classe(p, QRectF(44, 20, 30, 14), classe)
        texto(p, QRectF(80, 18, 110, 18), tema.nome_piloto(piloto, 14), tema.TEXTO, 9, True)
        cor_tempo = tema.CRITICO if atras and tempo < 1.0 else tema.TEXTO
        texto(p, QRectF(186, 5, 66, 32), f"{tempo:.1f}s", cor_tempo, 15, True, DIR)
        barra(p, QRectF(44, self.altura - 10, self.largura - 52, 3), perto, AZUL if atras else cor_classe, raio=1.5)
