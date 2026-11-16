from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter

from .. import tema
from ..calculos.formatacao import numero_carro
from .base import CENTRO, DIR, Opcao, WidgetOverlay, barra, rotulo, texto

ALTURA_LINHA = 20
CABECALHO = 18
ALTURA_CLASSE = 16


def cor_restante(fracao: float) -> QColor:
    if fracao < 0.3:
        return tema.CRITICO
    if fracao < 0.5:
        return tema.ALERTA
    return tema.BOM


class Rivais(WidgetOverlay):
    nome = "rivais"
    titulo = "Rivais: pneus e VE"
    largura = 300
    posicao_padrao = (1640, 120)
    ativo_padrao = False
    opcoes_padrao = {"qtd_minha": 5, "qtd_outras": 3, "mostrar_outras": True}
    descricao = "Pneu e energia virtual por classe: mais carros da sua classe e o top das outras."
    opcoes = {
        "qtd_minha": Opcao("Carros da sua classe", "Quantos do topo da classe em que você está pilotando.", 1, 10, 1),
        "qtd_outras": Opcao("Carros das outras classes", "Top de cada uma das outras classes.", 1, 10, 1),
        "mostrar_outras": Opcao("Mostrar as outras classes"),
    }

    def tamanho_base(self) -> QSize:
        if self._dados:
            grupos = self._dados
            linhas = sum(len(linhas) for _, linhas in grupos)
            return QSize(self.largura, CABECALHO + 6 + len(grupos) * ALTURA_CLASSE + linhas * ALTURA_LINHA)
        return QSize(self.largura, CABECALHO + 6 + ALTURA_CLASSE + (self.config["qtd_minha"] + 1) * ALTURA_LINHA)

    def atualizar(self, quadro) -> None:
        anterior = self.tamanho_base()
        super().atualizar(quadro)
        if self._dados and self.tamanho_base() != anterior:
            self.ajustar_tamanho()

    def preparar(self, quadro):
        estado = quadro.estado
        jogador = estado.carro_jogador
        if jogador is None:
            return None
        por_classe: dict[str, list] = {}
        for c in sorted(estado.carros, key=lambda c: c.posicao):
            por_classe.setdefault(c.classe, []).append(c)
        # A classe de quem está pilotando vem primeiro e com mais carros; as outras, só o topo.
        ordem = [jogador.classe] + ([k for k in por_classe if k != jogador.classe] if self.config["mostrar_outras"] else [])
        grupos = []
        for nome in ordem:
            carros = por_classe.get(nome, [])
            minha = nome == jogador.classe
            topo = carros[: int(self.config["qtd_minha" if minha else "qtd_outras"])]
            if minha and jogador not in topo:
                topo.append(jogador)
            grupos.append((nome, tuple(
                (
                    carros.index(c) + 1,
                    numero_carro(c.equipe),
                    c.piloto,
                    (c.composto[:1] or "-").upper(),
                    round(min(c.pneus_restante), 2) if c.pneus_restante else -1.0,
                    round(c.energia, 2),
                    c.nos_boxes,
                    c.jogador,
                )
                for c in topo
            )))
        return tuple(grupos)

    def desenhar(self, p: QPainter, grupos) -> None:
        rotulo(p, QRectF(10, 3, 140, 14), "Rivais")
        rotulo(p, QRectF(168, 3, 60, 14), "Pneu", CENTRO)
        rotulo(p, QRectF(232, 3, 60, 14), "VE", CENTRO)
        y = float(CABECALHO + 2)
        for classe, linhas in grupos:
            sigla, cor_classe = tema.classe(classe)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(cor_classe)
            faixa = QRectF(4, y + 1, self.largura - 8, ALTURA_CLASSE - 3)
            p.drawRoundedRect(faixa, 3, 3)
            texto(p, faixa, (classe or sigla).upper(), tema.TEXTO, 7.5, True, CENTRO)
            y += ALTURA_CLASSE
            for pos, numero, piloto, composto, pneu, energia, boxes, jogador in linhas:
                self._linha(p, y, cor_classe, pos, numero, piloto, composto, pneu, energia, boxes, jogador)
                y += ALTURA_LINHA

    def _linha(self, p: QPainter, y: float, cor_classe, pos, numero, piloto, composto, pneu, energia, boxes, jogador) -> None:
        altura = ALTURA_LINHA - 2
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(tema.FUNDO_DESTAQUE if jogador else tema.FUNDO_LINHA)
        p.drawRoundedRect(QRectF(4, y, self.largura - 8, altura), 3, 3)
        if jogador:
            p.setBrush(tema.DESTAQUE)
            p.drawRoundedRect(QRectF(4, y, 3, altura), 1.5, 1.5)
        texto(p, QRectF(8, y, 18, altura), str(pos), tema.TEXTO_POSICAO, 8.5, True, DIR)
        p.setBrush(cor_classe)
        p.drawRoundedRect(QRectF(30, y + 2, 26, altura - 4), 3, 3)
        texto(p, QRectF(30, y + 2, 26, altura - 4), numero or "–", QColor("#ffffff"), 7.5, True, CENTRO)
        texto(p, QRectF(62, y, 92, altura), tema.nome_piloto(piloto, 13), tema.TEXTO, 8.5, jogador)
        texto(p, QRectF(150, y, 16, altura), "BOX" if boxes else composto, tema.TEXTO_APAGADO, 7.5, True, CENTRO)
        self._valor(p, QRectF(168, y, 60, altura), pneu)
        self._valor(p, QRectF(232, y, 60, altura), energia)

    @staticmethod
    def _valor(p: QPainter, area: QRectF, fracao: float) -> None:
        if fracao < 0:
            texto(p, area, "–", tema.TEXTO_APAGADO, 8.5, False, CENTRO)
            return
        barra(p, QRectF(area.left() + 2, area.center().y() - 2, 28, 4), fracao, cor_restante(fracao))
        texto(p, QRectF(area.left() + 32, area.top(), 28, area.height()), f"{fracao * 100:.0f}%", tema.TEXTO, 8, False, DIR)
