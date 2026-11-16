from __future__ import annotations

from collections import deque

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from .. import tema
from .base import CENTRO, Opcao, WidgetOverlay, barra, rotulo, texto
from .motor import nome_marcha

# Pontos guardados por segundo de gráfico; o widget recebe mais quadros que isso.
AMOSTRAS_POR_SEGUNDO = 30
# Com folga: o timer de 30 Hz bate a cada ~33 ms e não pode perder um quadro sim, outro não.
INTERVALO_AMOSTRA = 0.8 / AMOSTRAS_POR_SEGUNDO


def angulo_volante(volante: float, giro: float) -> float:
    """Graus para desenhar o volante: -1..1 do jogo vira metade do giro para cada lado."""
    return max(-1.0, min(1.0, volante)) * giro / 2


def cor_rpm(fracao: float, troca: float) -> QColor:
    if fracao >= troca * 0.97:
        return tema.CRITICO
    if fracao >= troca * 0.85:
        return tema.ALERTA
    return tema.BOM


class Volante(WidgetOverlay):
    nome = "volante"
    titulo = "Volante e inputs"
    largura = 330
    altura = 64
    posicao_padrao = (790, 960)
    ativo_padrao = False
    opcoes_padrao = {"janela": 5.0, "giro": 540, "luz_troca": 0.94, "unidade_velocidade": "kmh"}
    descricao = "Volante de GT3 girando, marcha e velocidade ao lado e o gráfico do acelerador e freio nos últimos segundos."
    opcoes = {
        "janela": Opcao("Tempo no gráfico", "Quantos segundos de acelerador e freio aparecem.", 2, 10, 1, " s"),
        "giro": Opcao("Giro do volante", "Use o mesmo do carro no jogo para o desenho bater.", 180, 1080, 10, "°"),
        "luz_troca": Opcao("Luz de troca", "Porcentagem do RPM máximo em que a marcha pisca.", 80, 99, 1, "%", fator=100),
        "unidade_velocidade": Opcao("Velocidade em", escolhas=(("kmh", "km/h"), ("mph", "mph"))),
    }

    def __init__(self, *args, **kwargs) -> None:
        self._historico: deque[tuple[float, float, float, bool, bool]] = deque()
        super().__init__(*args, **kwargs)

    def reconfigurar(self) -> None:
        self._historico.clear()
        super().reconfigurar()

    def preparar(self, quadro):
        j = quadro.estado.jogador
        agora = quadro.instante
        janela = self.config["janela"]
        if not self._historico or agora - self._historico[-1][0] >= INTERVALO_AMOSTRA or agora < self._historico[-1][0]:
            self._historico.append((agora, j.acelerador, j.freio, j.tc_ativo, j.abs_ativo))
        while self._historico and (agora - self._historico[0][0] > janela or self._historico[0][0] > agora):
            self._historico.popleft()
        # Posição no gráfico de 0 (mais antigo) a 1 (agora), arredondada para não redesenhar à toa.
        pontos = tuple(
            (round(1 - (agora - t) / janela, 3), round(a, 2), round(f, 2), tc, abs_)
            for t, a, f, tc, abs_ in self._historico
        )
        fator = 3.6 if self.config["unidade_velocidade"] == "kmh" else 2.23694
        fracao = j.rpm / j.rpm_max if j.rpm_max > 0 else 0.0
        piscar = fracao >= self.config["luz_troca"] and int(agora * 8) % 2 == 0
        return (
            round(angulo_volante(j.volante, self.config["giro"])),
            j.marcha,
            round(fracao, 3),
            piscar,
            round(j.velocidade * fator),
            pontos,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        angulo, marcha, fracao, piscar, velocidade, pontos = dados
        self._desenhar_volante(p, QPointF(38, self.altura / 2), angulo)
        # Marcha e velocidade à direita do volante, com uma faixa fina de RPM embaixo.
        cor_marcha = tema.CRITICO if piscar else tema.TEXTO
        texto(p, QRectF(74, 4, 56, 30), nome_marcha(marcha), cor_marcha, 20, True, CENTRO)
        texto(p, QRectF(74, 31, 56, 16), str(velocidade), tema.TEXTO_SECUNDARIO, 10, True, CENTRO)
        rotulo(p, QRectF(74, 45, 56, 10), "km/h" if self.config["unidade_velocidade"] == "kmh" else "mph", CENTRO)
        troca = self.config["luz_troca"]
        cor = (tema.CRITICO if piscar else tema.TRILHO) if fracao >= troca else cor_rpm(fracao, troca)
        barra(p, QRectF(78, self.altura - 8, 48, 3), min(1.0, fracao / troca) if fracao < troca else 1.0, cor, raio=1.5)
        self._desenhar_grafico(p, QRectF(138, 8, self.largura - 146, self.altura - 16), pontos)

    def _desenhar_volante(self, p: QPainter, centro: QPointF, angulo: float) -> None:
        """Volante de GT3 em silhueta: pegadas laterais mais altas, tela no meio e botões dos lados."""
        p.save()
        p.translate(centro)
        p.rotate(angulo)
        corpo = QPainterPath()
        corpo.addRoundedRect(QRectF(-27, -15, 12, 30), 5, 5)
        corpo.addRoundedRect(QRectF(15, -15, 12, 30), 5, 5)
        corpo.addRoundedRect(QRectF(-19, -11, 38, 22), 4, 4)
        p.fillPath(corpo.simplified(), tema.TEXTO_SECUNDARIO)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tema.FUNDO_FIM)
        p.drawRoundedRect(QRectF(-9, -6, 18, 10), 2, 2)
        for x in (-13.5, 13.5):
            for y in (-5.0, 1.0, 7.0):
                p.drawEllipse(QPointF(x, y), 1.6, 1.6)
        for x in (-4.0, 0.0, 4.0):
            p.drawEllipse(QPointF(x, 7.5), 1.3, 1.3)
        # Marca de centro no topo, para ver o quanto girou.
        p.setBrush(tema.DESTAQUE)
        p.drawRoundedRect(QRectF(-3, -11, 6, 3), 1, 1)
        p.restore()

    def _desenhar_grafico(self, p: QPainter, area: QRectF, pontos) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tema.FUNDO_LINHA)
        p.drawRoundedRect(area, 3, 3)
        p.setPen(QPen(tema.TRILHO, 1, Qt.PenStyle.DashLine))
        meio = area.top() + area.height() / 2
        p.drawLine(QPointF(area.left() + 2, meio), QPointF(area.right() - 2, meio))
        if len(pontos) < 2:
            return

        def ponto(x: float, valor: float) -> QPointF:
            return QPointF(area.left() + x * area.width(), area.bottom() - 2 - valor * (area.height() - 4))

        # Preenchimento leve embaixo do acelerador, para ler de longe.
        preenchido = QPainterPath(ponto(pontos[0][0], 0))
        for x, a, *_ in pontos:
            preenchido.lineTo(ponto(x, a))
        preenchido.lineTo(ponto(pontos[-1][0], 0))
        cor_fundo = QColor(tema.ACELERADOR)
        cor_fundo.setAlpha(45)
        p.fillPath(preenchido, cor_fundo)

        # Freio e acelerador; o trecho fica amarelo quando o ABS ou o TC está atuando.
        for indice, cor, indice_alerta in ((2, tema.FREIO, 4), (1, tema.ACELERADOR, 3)):
            for anterior, atual in zip(pontos, pontos[1:], strict=False):
                alerta = atual[indice_alerta]
                p.setPen(QPen(tema.ALERTA if alerta else cor, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawLine(ponto(anterior[0], anterior[indice]), ponto(atual[0], atual[indice]))
