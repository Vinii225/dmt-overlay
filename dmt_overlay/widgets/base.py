from __future__ import annotations

from typing import Any, ClassVar

from PySide6.QtCore import QPoint, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from .. import tema
from ..provedor import Quadro

ESQ = Qt.AlignmentFlag.AlignLeft
DIR = Qt.AlignmentFlag.AlignRight
CENTRO = Qt.AlignmentFlag.AlignHCenter


class WidgetOverlay(QWidget):
    nome: ClassVar[str] = ""
    titulo: ClassVar[str] = ""
    largura: ClassVar[int] = 200
    altura: ClassVar[int] = 60
    posicao_padrao: ClassVar[tuple[int, int]] = (100, 100)
    ativo_padrao: ClassVar[bool] = True
    opcoes_padrao: ClassVar[dict[str, Any]] = {}

    def __init__(self, config: dict[str, Any], escala: float = 1.0) -> None:
        super().__init__(None)
        self.config = config
        self.escala = escala
        self._dados: Any = None
        self._travado = True
        self._arrasto: QPoint | None = None
        self.setWindowTitle(f"DMT Overlay - {self.titulo}")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._aplicar_flags()
        self.ajustar_tamanho()
        self.move(self.config["x"], self.config["y"])

    @classmethod
    def padrao(cls) -> dict[str, Any]:
        x, y = cls.posicao_padrao
        return {"ativo": cls.ativo_padrao, "x": x, "y": y, **cls.opcoes_padrao}

    def tamanho_base(self) -> QSize:
        return QSize(self.largura, self.altura)

    def ajustar_tamanho(self) -> None:
        base = self.tamanho_base()
        self.setFixedSize(round(base.width() * self.escala), round(base.height() * self.escala))

    def _aplicar_flags(self) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.NoDropShadowWindowHint
        )
        if self._travado:
            flags |= Qt.WindowType.WindowTransparentForInput
        visivel = self.isVisible()
        self.setWindowFlags(flags)
        if visivel:
            self.show()

    def travar(self, travado: bool) -> None:
        if travado == self._travado:
            return
        self._travado = travado
        self.setCursor(Qt.CursorShape.ArrowCursor if travado else Qt.CursorShape.SizeAllCursor)
        self._aplicar_flags()
        self.update()

    def preparar(self, quadro: Quadro) -> Any:
        raise NotImplementedError

    def desenhar(self, p: QPainter, dados: Any) -> None:
        raise NotImplementedError

    def atualizar(self, quadro: Quadro) -> None:
        dados = self.preparar(quadro)
        if dados != self._dados:
            self._dados = dados
            self.update()

    def paintEvent(self, _evento) -> None:
        if self._dados is None and self._travado:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.scale(self.escala, self.escala)
        base = self.tamanho_base()
        caixa = QRectF(0.5, 0.5, base.width() - 1, base.height() - 1)
        caminho = QPainterPath()
        caminho.addRoundedRect(caixa, tema.RAIO, tema.RAIO)
        p.fillPath(caminho, tema.FUNDO)
        p.setPen(QPen(tema.DESTAQUE if not self._travado else tema.BORDA, 1.5 if not self._travado else 1))
        p.drawPath(caminho)
        p.setClipPath(caminho)
        if self._dados is not None:
            self.desenhar(p, self._dados)
        if not self._travado:
            p.setClipping(False)
            p.setPen(tema.DESTAQUE)
            p.setFont(tema.fonte(7, True))
            p.drawText(QRectF(0, 0, base.width() - 6, 14), DIR | Qt.AlignmentFlag.AlignVCenter, self.titulo.upper())
        p.end()

    def mousePressEvent(self, evento) -> None:
        if not self._travado and evento.button() == Qt.MouseButton.LeftButton:
            self._arrasto = evento.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, evento) -> None:
        if self._arrasto is not None:
            destino = evento.globalPosition().toPoint() - self._arrasto
            self.move(self._encaixar(destino))

    def mouseReleaseEvent(self, _evento) -> None:
        if self._arrasto is not None:
            self._arrasto = None
            self.config["x"], self.config["y"] = self.x(), self.y()

    def _encaixar(self, ponto: QPoint, distancia: int = 10) -> QPoint:
        tela = QGuiApplication.screenAt(ponto) or QGuiApplication.primaryScreen()
        area = tela.geometry()
        x, y = ponto.x(), ponto.y()
        if abs(x - area.left()) < distancia:
            x = area.left()
        elif abs(x + self.width() - area.right() - 1) < distancia:
            x = area.right() + 1 - self.width()
        if abs(y - area.top()) < distancia:
            y = area.top()
        elif abs(y + self.height() - area.bottom() - 1) < distancia:
            y = area.bottom() + 1 - self.height()
        return QPoint(x, y)


def texto(
    p: QPainter,
    rect: QRectF,
    valor: str,
    cor: QColor = tema.TEXTO,
    tamanho: float = 9,
    negrito: bool = False,
    alinhamento=ESQ,
) -> None:
    p.setPen(cor)
    p.setFont(tema.fonte(tamanho, negrito))
    p.drawText(rect, alinhamento | Qt.AlignmentFlag.AlignVCenter, valor)


def barra(p: QPainter, rect: QRectF, fracao: float, cor: QColor, vertical: bool = False, raio: float = 2) -> None:
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(tema.TRILHO)
    p.drawRoundedRect(rect, raio, raio)
    fracao = max(0.0, min(1.0, fracao))
    if fracao <= 0:
        return
    if vertical:
        h = rect.height() * fracao
        cheio = QRectF(rect.left(), rect.bottom() - h, rect.width(), h)
    else:
        cheio = QRectF(rect.left(), rect.top(), rect.width() * fracao, rect.height())
    p.setBrush(cor)
    p.drawRoundedRect(cheio, raio, raio)


def selo_classe(p: QPainter, rect: QRectF, classe: str) -> None:
    sigla, cor = tema.classe(classe)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(cor)
    p.drawRoundedRect(rect, 3, 3)
    texto(p, rect, sigla, QColor("#ffffff"), 7, True, CENTRO)


def rotulo(p: QPainter, rect: QRectF, valor: str, alinhamento=ESQ) -> None:
    texto(p, rect, valor.upper(), tema.TEXTO_APAGADO, 6.5, True, alinhamento)
