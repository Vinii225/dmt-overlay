from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter

from .. import tema
from ..calculos.formatacao import intervalo, nome_curto, numero_carro, tempo_volta
from .base import DIR, WidgetOverlay, rotulo, selo_classe, texto

ALTURA_LINHA = 21
CABECALHO = 22


def selecionar(carros, total: int, topo: int):
    indice = next((i for i, c in enumerate(carros) if c.jogador), 0)
    if len(carros) <= total:
        return list(range(len(carros)))
    escolhidos = set(range(min(topo, len(carros))))
    restante = total - len(escolhidos)
    inicio = max(topo, min(indice - restante // 2, len(carros) - restante))
    escolhidos.update(range(inicio, inicio + restante))
    return sorted(escolhidos)[:total]


class Classificacao(WidgetOverlay):
    nome = "classificacao"
    titulo = "Classificação"
    largura = 340
    posicao_padrao = (40, 120)
    opcoes_padrao = {"linhas": 10, "lideres": 3, "somente_minha_classe": True}

    def __init__(self, *args, **kwargs) -> None:
        self._quantidade = 0
        super().__init__(*args, **kwargs)

    def tamanho_base(self) -> QSize:
        linhas = self._quantidade or self.config["linhas"]
        return QSize(self.largura, CABECALHO + 6 + linhas * ALTURA_LINHA)

    def atualizar(self, quadro) -> None:
        super().atualizar(quadro)
        quantidade = len(self._dados[2]) if self._dados else 0
        if quantidade and quantidade != self._quantidade:
            self._quantidade = quantidade
            self.ajustar_tamanho()

    def preparar(self, quadro):
        estado = quadro.estado
        jogador = estado.carro_jogador
        carros = estado.carros
        if self.config["somente_minha_classe"] and jogador is not None:
            carros = [c for c in carros if c.classe == jogador.classe]
        if not carros:
            return ("", len(estado.carros), ())
        lider = carros[0]
        linhas = []
        anterior_idx = None
        for idx in selecionar(carros, self.config["linhas"], self.config["lideres"]):
            c = carros[idx]
            salto = anterior_idx is not None and idx != anterior_idx + 1
            anterior_idx = idx
            if c is lider:
                gap = "Líder"
            else:
                voltas = c.voltas_lider - lider.voltas_lider
                gap = intervalo(c.tempo_lider - lider.tempo_lider, voltas)
            numero = numero_carro(c.equipe)
            linhas.append((idx + 1, c.classe, numero, c.piloto, c.ultima_volta, gap, c.nos_boxes, c.jogador, salto))
        classe = jogador.classe if jogador and self.config["somente_minha_classe"] else "Geral"
        return (classe, len(carros), tuple(linhas))

    def desenhar(self, p: QPainter, dados) -> None:
        classe, total, linhas = dados
        texto(p, QRectF(10, 4, 200, 16), classe or "Classificação", tema.TEXTO, 9, True)
        rotulo(p, QRectF(170, 4, 162, 16), f"{total} carros", DIR)
        y = float(CABECALHO + 2)
        for pos, cls, numero, piloto, ultima, gap, boxes, jogador, salto in linhas:
            linha = QRectF(4, y, self.largura - 8, ALTURA_LINHA - 2)
            if salto:
                p.setPen(tema.BORDA)
                p.drawLine(QRectF(12, y - 1, self.largura - 24, 0).topLeft(), QRectF(12, y - 1, self.largura - 24, 0).topRight())
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tema.FUNDO_DESTAQUE if jogador else tema.FUNDO_LINHA)
            p.drawRoundedRect(linha, 3, 3)
            if jogador:
                p.setBrush(tema.DESTAQUE)
                p.drawRoundedRect(QRectF(4, y, 3, ALTURA_LINHA - 2), 1.5, 1.5)
            meio = y + (ALTURA_LINHA - 2) / 2
            altura = ALTURA_LINHA - 2
            texto(p, QRectF(8, y, 22, altura), str(pos), tema.TEXTO_SECUNDARIO, 8.5, True, DIR)
            selo_classe(p, QRectF(36, meio - 7, 28, 14), cls)
            texto(p, QRectF(68, y, 28, altura), numero, tema.TEXTO_APAGADO, 8, True)
            texto(p, QRectF(96, y, 116, altura), nome_curto(piloto, 16), tema.TEXTO, 9, jogador)
            cor_volta = tema.TEXTO_APAGADO if boxes else tema.TEXTO_SECUNDARIO
            texto(p, QRectF(206, y, 64, altura), "BOX" if boxes else tempo_volta(ultima), cor_volta, 8, False, DIR)
            texto(p, QRectF(270, y, 62, altura), gap, tema.TEXTO, 8.5, False, DIR)
            y += ALTURA_LINHA
