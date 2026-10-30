from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import __version__
from .config import pasta_config
from .icone import icone

if TYPE_CHECKING:
    from .app import Aplicativo

ESCALAS = (0.8, 0.9, 1.0, 1.1, 1.25, 1.5)
OPACIDADES = (0.6, 0.7, 0.8, 0.9, 1.0)
FONTES = (("lmu", "Le Mans Ultimate"), ("demo", "Demonstração"))


def abrir_pasta(caminho) -> None:
    caminho.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(caminho)
    else:
        subprocess.Popen(["xdg-open", str(caminho)])


class Bandeja(QSystemTrayIcon):
    def __init__(self, aplicativo: Aplicativo) -> None:
        super().__init__(icone())
        self.aplicativo = aplicativo
        self.setToolTip(f"DMT Overlay {__version__}")
        self.menu = QMenu()
        self._montar_menu()
        self.setContextMenu(self.menu)
        self.activated.connect(self._ativado)
        aplicativo.provedor.conexao_mudou.connect(self._conexao)

    def _montar_menu(self) -> None:
        app = self.aplicativo
        geral = app.config.geral
        cabecalho = self.menu.addAction(f"DMT Overlay {__version__}")
        cabecalho.setEnabled(False)
        self.status = self.menu.addAction("Aguardando o jogo…")
        self.status.setEnabled(False)
        self.menu.addSeparator()

        self.acao_travar = self.menu.addAction("Travar posições")
        self.acao_travar.setCheckable(True)
        self.acao_travar.setChecked(geral["travado"])
        self.acao_travar.toggled.connect(app.travar)

        widgets = self.menu.addMenu("Widgets")
        for nome, widget in app.widgets.items():
            acao = widgets.addAction(widget.titulo)
            acao.setCheckable(True)
            acao.setChecked(widget.config["ativo"])
            acao.toggled.connect(lambda ativo, n=nome: app.alternar_widget(n, ativo))

        aparencia = self.menu.addMenu("Aparência")
        self._grupo(aparencia.addMenu("Tamanho"), ESCALAS, geral["escala"], app.definir_escala)
        self._grupo(aparencia.addMenu("Opacidade"), OPACIDADES, geral["opacidade"], app.definir_opacidade)

        ocultar = self.menu.addAction("Esconder fora da pista")
        ocultar.setCheckable(True)
        ocultar.setChecked(geral["ocultar_fora_da_pista"])
        ocultar.toggled.connect(app.definir_ocultar)

        fontes = self.menu.addMenu("Fonte de dados")
        grupo = QActionGroup(fontes)
        for chave, nome in FONTES:
            acao = QAction(nome, grupo, checkable=True, checked=chave == app.provedor.fonte)
            acao.triggered.connect(lambda _=False, c=chave: app.trocar_fonte(c))
            fontes.addAction(acao)

        self.menu.addSeparator()
        self.menu.addAction("Restaurar posições").triggered.connect(app.restaurar_posicoes)
        self.menu.addAction("Abrir pasta de configuração").triggered.connect(lambda: abrir_pasta(pasta_config()))
        self.menu.addSeparator()
        self.menu.addAction("Sair").triggered.connect(QApplication.quit)

    @staticmethod
    def _grupo(menu: QMenu, valores, atual: float, callback) -> None:
        grupo = QActionGroup(menu)
        for valor in valores:
            acao = QAction(f"{valor * 100:.0f}%", grupo, checkable=True, checked=abs(valor - atual) < 1e-6)
            acao.triggered.connect(lambda _=False, v=valor: callback(v))
            menu.addAction(acao)

    def _ativado(self, motivo) -> None:
        if motivo == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.acao_travar.toggle()

    def _conexao(self, conectado: bool) -> None:
        texto = "Conectado ao jogo" if conectado else "Aguardando o jogo…"
        self.status.setText(texto)
        self.setToolTip(f"DMT Overlay {__version__} - {texto}")
