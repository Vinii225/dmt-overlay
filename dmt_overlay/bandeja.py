from __future__ import annotations

import os
import subprocess
import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import __version__
from .config import pasta_voltas
from .icone import icone

if TYPE_CHECKING:
    from .app import Aplicativo

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
        self.messageClicked.connect(self._abrir_atualizacao)
        self._url_atualizacao = ""
        aplicativo.provedor.conexao_mudou.connect(self._conexao)

    def _montar_menu(self) -> None:
        app = self.aplicativo
        geral = app.config.geral
        cabecalho = self.menu.addAction(f"DMT Overlay {__version__}")
        cabecalho.setEnabled(False)
        self.status = self.menu.addAction("Aguardando o jogo…")
        self.status.setEnabled(False)
        self.acao_atualizar = self.menu.addAction("")
        self.acao_atualizar.setVisible(False)
        self.acao_atualizar.triggered.connect(self._abrir_atualizacao)
        self.menu.addSeparator()

        # Só o que se usa durante a sessão; o resto fica na janela de configurações.
        self.acao_travar = self.menu.addAction("")
        self.acao_travar.setCheckable(True)
        self.acao_travar.setChecked(geral["travado"])
        self.acao_travar.toggled.connect(app.travar)

        self.acao_ocultar = self.menu.addAction("")
        self.acao_ocultar.setCheckable(True)
        self.acao_ocultar.toggled.connect(app.ocultar)

        widgets = self.menu.addMenu("Widgets")
        self.acoes_widgets: dict[str, QAction] = {}
        for nome, widget in app.widgets.items():
            acao = widgets.addAction(widget.titulo)
            acao.setCheckable(True)
            acao.setChecked(widget.config["ativo"])
            acao.toggled.connect(lambda ativo, n=nome: app.alternar_widget(n, ativo))
            self.acoes_widgets[nome] = acao

        self.menu.addAction("Abrir voltas gravadas").triggered.connect(lambda: abrir_pasta(pasta_voltas()))
        self.menu.addSeparator()
        configuracoes = self.menu.addAction("Configurações…")
        configuracoes.triggered.connect(app.abrir_configuracoes)
        fonte = configuracoes.font()
        fonte.setBold(True)
        configuracoes.setFont(fonte)
        self.menu.addAction("Sair").triggered.connect(QApplication.quit)
        self._textos_atalhos()

    def _textos_atalhos(self) -> None:
        self.acao_travar.setText(self._com_atalho("Travar posições", "travar"))
        self.acao_ocultar.setText(self._com_atalho("Esconder overlays", "mostrar_ocultar"))

    def sincronizar(self) -> None:
        """Reflete no menu o que mudou por fora (janela de configurações, atalhos)."""
        app = self.aplicativo
        marcados = [(self.acao_travar, app.config.geral["travado"]), (self.acao_ocultar, app.ocultos)]
        marcados += [(acao, app.widgets[nome].config["ativo"]) for nome, acao in self.acoes_widgets.items()]
        for acao, valor in marcados:
            if acao.isChecked() != valor:
                acao.blockSignals(True)
                acao.setChecked(valor)
                acao.blockSignals(False)
        self._textos_atalhos()

    def _com_atalho(self, texto: str, nome: str) -> str:
        atalho = self.aplicativo.atalhos.registrados.get(nome)
        return f"{texto}\t{atalho}" if atalho else texto

    def _ativado(self, motivo) -> None:
        if motivo == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.acao_travar.toggle()

    def nova_versao(self, versao: str, url: str) -> None:
        self._url_atualizacao = url
        self.acao_atualizar.setText(f"Baixar nova versão {versao}")
        self.acao_atualizar.setVisible(True)
        self.showMessage("DMT Overlay", f"Nova versão {versao} disponível. Clique para baixar.", self.icon(), 8000)

    def _abrir_atualizacao(self) -> None:
        if self._url_atualizacao:
            QDesktopServices.openUrl(QUrl(self._url_atualizacao))

    def _conexao(self, conectado: bool) -> None:
        texto = "Conectado ao jogo" if conectado else "Aguardando o jogo…"
        self.status.setText(texto)
        self.setToolTip(f"DMT Overlay {__version__} - {texto}")
