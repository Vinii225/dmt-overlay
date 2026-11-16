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
    largura = 340
    altura = 76
    posicao_padrao = (790, 960)
    ativo_padrao = False
    opcoes_padrao = {"janela": 5.0, "giro": 540, "luz_troca": 0.94, "unidade_velocidade": "kmh"}
    descricao = "Volante girando com a marcha no centro, anel de RPM e o gráfico do acelerador e freio nos últimos segundos."
    opcoes = {
        "janela": Opcao("Tempo no gráfico", "Quantos segundos de acelerador e freio aparecem.", 2, 10, 1, " s"),
        "giro": Opcao("Giro do volante", "Use o mesmo do carro no jogo para o desenho bater.", 180, 1080, 10, "°"),
        "luz_troca": Opcao("Luz de troca", "Porcentagem do RPM máximo em que o anel pisca.", 80, 99, 1, "%", fator=100),
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
            round(j.acelerador, 2),
            round(j.freio, 2),
            round(j.velocidade * fator),
            pontos,
        )

    def desenhar(self, p: QPainter, dados) -> None:
        angulo, marcha, fracao, piscar, acel, freio, velocidade, pontos = dados
        self._desenhar_volante(p, QPointF(40, self.altura / 2), angulo, marcha, fracao, piscar)
        self._desenhar_grafico(p, QRectF(84, 9, 196, self.altura - 18), pontos)
        topo, base = 9.0, self.altura - 9.0
        barra(p, QRectF(288, topo, 8, base - topo), acel, tema.ACELERADOR, vertical=True, raio=2)
        barra(p, QRectF(300, topo, 8, base - topo), freio, tema.FREIO, vertical=True, raio=2)
        texto(p, QRectF(308, 14, 30, 26), str(velocidade), tema.TEXTO, 12, True, CENTRO)
        rotulo(p, QRectF(308, 40, 30, 12), "km/h" if self.config["unidade_velocidade"] == "kmh" else "mph", CENTRO)

    def _desenhar_volante(self, p: QPainter, centro: QPointF, angulo: float, marcha: int, fracao: float, piscar: bool) -> None:
        raio_anel = 32.0
        caixa_anel = QRectF(centro.x() - raio_anel, centro.y() - raio_anel, raio_anel * 2, raio_anel * 2)
        # Anel de RPM: 270° abrindo embaixo, enche no sentido horário.
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(tema.TRILHO, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(caixa_anel, 225 * 16, -270 * 16)
        if fracao > 0:
            troca = self.config["luz_troca"]
            cor = (tema.CRITICO if piscar else tema.TRILHO) if fracao >= troca else cor_rpm(fracao, troca)
            p.setPen(QPen(cor, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(caixa_anel, 225 * 16, round(-270 * 16 * min(1.0, fracao / troca)))

        p.save()
        p.translate(centro)
        p.rotate(angulo)
        r = 24.0
        p.setPen(QPen(tema.TEXTO_SECUNDARIO, 4))
        p.drawEllipse(QPointF(0, 0), r, r)
        p.setPen(QPen(tema.TEXTO_SECUNDARIO, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        for x1, y1, x2, y2 in ((-r, 2, -10, 4), (r, 2, 10, 4), (0, 12, 0, r)):
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        # Marca de centro no topo do aro, para ver o quanto o volante girou.
        p.setPen(QPen(tema.DESTAQUE, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(0, -r - 1), QPointF(0, -r + 3))
        # Miolo sólido para a marcha não brigar com os raios.
        p.setPen(QPen(tema.TEXTO_SECUNDARIO, 2))
        p.setBrush(tema.FUNDO_FIM)
        p.drawEllipse(QPointF(0, 0), 12, 12)
        p.restore()

        cor_marcha = tema.CRITICO if piscar else tema.TEXTO
        texto(p, QRectF(centro.x() - 12, centro.y() - 12, 24, 22), nome_marcha(marcha), cor_marcha, 15, True, CENTRO)

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
