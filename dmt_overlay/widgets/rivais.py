from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter

from .. import tema
from ..calculos.formatacao import numero_carro
from .base import CENTRO, DIR, Opcao, WidgetOverlay, barra, rotulo, texto

ALTURA_LINHA = 20
CABECALHO = 18
# Quantos rivais mostrar, pela sigla da classe do jogador (tema.classe).
CHAVES_CLASSE = {"HY": "qtd_hy", "P2": "qtd_p2", "GT3": "qtd_gt3"}


def quantidade(config: dict, classe: str) -> int:
    return int(config[CHAVES_CLASSE.get(tema.classe(classe)[0], "qtd_outras")])


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
    opcoes_padrao = {"qtd_hy": 5, "qtd_p2": 3, "qtd_gt3": 3, "qtd_outras": 3}
    descricao = "Pneu e energia virtual dos líderes da sua classe, para saber quem vai parar antes ou estender o stint."
    opcoes = {
        "qtd_hy": Opcao("Rivais no Hypercar", "Quantos do topo da classe aparecem.", 1, 10, 1),
        "qtd_p2": Opcao("Rivais no LMP2", minimo=1, maximo=10, passo=1),
        "qtd_gt3": Opcao("Rivais no LMGT3", minimo=1, maximo=10, passo=1),
        "qtd_outras": Opcao("Rivais nas outras classes", minimo=1, maximo=10, passo=1),
    }

    def tamanho_base(self) -> QSize:
        linhas = len(self._dados[1]) if self._dados else self.config["qtd_hy"] + 1
        return QSize(self.largura, CABECALHO + 6 + linhas * ALTURA_LINHA)

    def atualizar(self, quadro) -> None:
        anterior = len(self._dados[1]) if self._dados else 0
        super().atualizar(quadro)
        atual = len(self._dados[1]) if self._dados else 0
        if atual and atual != anterior:
            self.ajustar_tamanho()

    def preparar(self, quadro):
        estado = quadro.estado
        jogador = estado.carro_jogador
        if jogador is None:
            return None
        classe = [c for c in sorted(estado.carros, key=lambda c: c.posicao) if c.classe == jogador.classe]
        topo = classe[: quantidade(self.config, jogador.classe)]
        if jogador not in topo:
            topo.append(jogador)
        linhas = tuple(
            (
                classe.index(c) + 1,
                numero_carro(c.equipe),
                c.piloto,
                (c.composto[:1] or "-").upper(),
                round(min(c.pneus_restante), 2) if c.pneus_restante else -1.0,
                round(c.energia, 2),
                c.nos_boxes,
                c.jogador,
            )
            for c in topo
        )
        return (jogador.classe, linhas)

    def desenhar(self, p: QPainter, dados) -> None:
        classe, linhas = dados
        sigla, cor_classe = tema.classe(classe)
        rotulo(p, QRectF(10, 3, 140, 14), f"Rivais · {classe or sigla}")
        rotulo(p, QRectF(168, 3, 60, 14), "Pneu", CENTRO)
        rotulo(p, QRectF(232, 3, 60, 14), "VE", CENTRO)
        y = float(CABECALHO + 2)
        for pos, numero, piloto, composto, pneu, energia, boxes, jogador in linhas:
            linha = QRectF(4, y, self.largura - 8, ALTURA_LINHA - 2)
            altura = ALTURA_LINHA - 2
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(tema.FUNDO_DESTAQUE if jogador else tema.FUNDO_LINHA)
            p.drawRoundedRect(linha, 3, 3)
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
            y += ALTURA_LINHA

    @staticmethod
    def _valor(p: QPainter, area: QRectF, fracao: float) -> None:
        if fracao < 0:
            texto(p, area, "–", tema.TEXTO_APAGADO, 8.5, False, CENTRO)
            return
        barra(p, QRectF(area.left() + 2, area.center().y() - 2, 28, 4), fracao, cor_restante(fracao))
        texto(p, QRectF(area.left() + 32, area.top(), 28, area.height()), f"{fracao * 100:.0f}%", tema.TEXTO, 8, False, DIR)
