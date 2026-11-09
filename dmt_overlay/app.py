from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Callable
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox

from . import __version__
from .atalhos import AtalhosGlobais
from .atualizacao import VerificadorAtualizacao
from .bandeja import Bandeja
from .config import Config, pasta_config, pasta_voltas
from .configuracoes import JanelaConfiguracoes
from .gravador import GravadorVoltas
from .provedor import Provedor, Quadro
from .widgets import WIDGETS
from .widgets.base import WidgetOverlay

log = logging.getLogger("dmt_overlay")


def configurar_log(debug: bool) -> None:
    pasta = pasta_config()
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = RotatingFileHandler(pasta / "dmt-overlay.log", maxBytes=1_000_000, backupCount=2, encoding="utf-8")
    console = logging.StreamHandler()
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[arquivo, console],
    )


class Aplicativo:
    def __init__(self, config: Config, fonte: str) -> None:
        self.config = config
        self.provedor = Provedor(fonte, config.geral["taxa_atualizacao"])
        self.pilotando = False
        self.ocultos = False
        self._ouvintes: list[Callable[[], None]] = []
        self.widgets: dict[str, WidgetOverlay] = {}
        for classe in WIDGETS:
            dados = config.widget(classe.nome, classe.padrao())
            widget = classe(dados, config.geral["escala"])
            widget.setWindowOpacity(config.geral["opacidade"])
            self.widgets[classe.nome] = widget
        self.definir_gravar_voltas(config.geral["gravar_voltas"], salvar=False)
        self.provedor.novo_quadro.connect(self._novo_quadro)
        self.provedor.pilotando_mudou.connect(self._pilotando_mudou)
        self.atalhos = AtalhosGlobais()
        self.atalhos.acionado.connect(self._atalho)
        self._registrar_atalhos()
        self.bandeja = Bandeja(self)
        self.ao_mudar(self.bandeja.sincronizar)
        self.janela_configuracoes: JanelaConfiguracoes | None = None
        self.verificador = VerificadorAtualizacao()
        self.verificador.encontrada.connect(self.bandeja.nova_versao)
        self.travar(config.geral["travado"])
        self.atualizar_visibilidade()

    def iniciar(self) -> None:
        self.provedor.iniciar()
        self.bandeja.show()
        if self.config.geral["verificar_atualizacoes"]:
            self.verificador.verificar()
        log.info("DMT Overlay %s iniciado (fonte: %s)", __version__, self.provedor.fonte)

    def encerrar(self) -> None:
        self.provedor.parar()
        self.atalhos.liberar()
        self.salvar()
        self.bandeja.hide()

    def ao_mudar(self, ouvinte: Callable[[], None]) -> None:
        self._ouvintes.append(ouvinte)

    def notificar(self) -> None:
        for ouvinte in self._ouvintes:
            ouvinte()

    def _registrar_atalhos(self) -> None:
        self.atalhos.liberar()
        for nome, sequencia in self.config.geral["atalhos"].items():
            if sequencia:
                self.atalhos.registrar(nome, sequencia)

    def definir_atalho(self, nome: str, sequencia: str) -> bool:
        """Troca um atalho; devolve False se não deu para registrar (inválido ou em uso)."""
        atalhos = self.config.geral["atalhos"]
        anterior = atalhos.get(nome, "")
        atalhos[nome] = sequencia
        self._registrar_atalhos()
        ok = not sequencia or nome in self.atalhos.registrados or not self.atalhos.suportado
        if not ok:
            atalhos[nome] = anterior
            self._registrar_atalhos()
        self.salvar()
        self.notificar()
        return ok

    def abrir_configuracoes(self, pagina: str = "") -> None:
        if self.janela_configuracoes is None:
            self.janela_configuracoes = JanelaConfiguracoes(self)
        janela = self.janela_configuracoes
        if pagina:
            janela.mostrar_pagina(pagina)
        janela.showNormal()
        janela.raise_()
        janela.activateWindow()

    def salvar(self) -> None:
        try:
            self.config.salvar()
        except OSError:
            log.exception("não foi possível salvar a configuração")

    def _novo_quadro(self, quadro: Quadro) -> None:
        for widget in self.widgets.values():
            if widget.isVisible():
                widget.atualizar(quadro)

    def _pilotando_mudou(self, pilotando: bool) -> None:
        self.pilotando = pilotando
        self.atualizar_visibilidade()

    def atualizar_visibilidade(self) -> None:
        geral = self.config.geral
        mostrar = self.pilotando or not geral["ocultar_fora_da_pista"] or not geral["travado"]
        mostrar = mostrar and not self.ocultos
        for widget in self.widgets.values():
            widget.setVisible(mostrar and widget.config["ativo"])

    def _atalho(self, nome: str) -> None:
        if nome == "mostrar_ocultar":
            self.bandeja.acao_ocultar.toggle()
        elif nome == "travar":
            self.bandeja.acao_travar.toggle()

    def ocultar(self, ocultos: bool) -> None:
        self.ocultos = ocultos
        self.atualizar_visibilidade()
        self.notificar()

    def travar(self, travado: bool) -> None:
        if not travado and self.ocultos:
            # Destravar é para posicionar: não faz sentido continuar escondido.
            self.bandeja.acao_ocultar.setChecked(False)
        self.config.geral["travado"] = travado
        for widget in self.widgets.values():
            widget.travar(travado)
        self.atualizar_visibilidade()
        if travado:
            self.salvar()
        self.notificar()

    def alternar_widget(self, nome: str, ativo: bool) -> None:
        self.widgets[nome].config["ativo"] = ativo
        self.atualizar_visibilidade()
        self.salvar()
        self.notificar()

    def definir_escala(self, escala: float) -> None:
        self.config.geral["escala"] = escala
        for widget in self.widgets.values():
            widget.escala = escala
            widget.ajustar_tamanho()
            widget.update()
        self.salvar()
        self.notificar()

    def definir_opacidade(self, opacidade: float) -> None:
        self.config.geral["opacidade"] = opacidade
        for widget in self.widgets.values():
            widget.setWindowOpacity(opacidade)
        self.salvar()
        self.notificar()

    def definir_ocultar(self, ocultar: bool) -> None:
        self.config.geral["ocultar_fora_da_pista"] = ocultar
        self.atualizar_visibilidade()
        self.salvar()
        self.notificar()

    def definir_verificar_atualizacoes(self, ativo: bool) -> None:
        self.config.geral["verificar_atualizacoes"] = ativo
        self.salvar()
        self.notificar()

    def definir_gravar_voltas(self, ativo: bool, salvar: bool = True) -> None:
        self.config.geral["gravar_voltas"] = ativo
        self.provedor.gravador = GravadorVoltas(pasta_voltas()) if ativo else None
        if salvar:
            self.salvar()
        self.notificar()

    def definir_taxa(self, taxa: int) -> None:
        self.config.geral["taxa_atualizacao"] = taxa
        self.provedor.definir_taxa(taxa)
        self.salvar()
        self.notificar()

    def definir_opcao(self, widget: str, chave: str, valor) -> None:
        alvo = self.widgets[widget]
        alvo.config[chave] = valor
        alvo.reconfigurar()
        self.salvar()

    def restaurar_opcoes(self, widget: str) -> None:
        alvo = self.widgets[widget]
        alvo.config.update(type(alvo).opcoes_padrao)
        alvo.reconfigurar()
        self.salvar()
        self.notificar()

    def trocar_fonte(self, chave: str) -> None:
        self.provedor.trocar_fonte(chave)
        self.config.geral["fonte_dados"] = chave
        self.salvar()
        self.notificar()

    def restaurar_posicoes(self) -> None:
        for widget in self.widgets.values():
            x, y = widget.posicao_padrao
            widget.config["x"], widget.config["y"] = x, y
            widget.move(x, y)
        self.salvar()
        self.notificar()


def main() -> None:
    parser = argparse.ArgumentParser(prog="dmt-overlay", description="Overlays de telemetria para Le Mans Ultimate")
    parser.add_argument("--demo", action="store_true", help="usa dados de demonstração em vez do jogo")
    parser.add_argument("--debug", action="store_true", help="log detalhado")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    configurar_log(args.debug)
    app = QApplication(sys.argv)
    app.setApplicationName("DMT Overlay")
    app.setApplicationVersion(__version__)
    app.setQuitOnLastWindowClosed(False)

    trava = QLockFile(str(pasta_config() / "dmt-overlay.lock"))
    trava.setStaleLockTime(0)
    if not trava.tryLock(100):
        QMessageBox.information(None, "DMT Overlay", "O DMT Overlay já está aberto. Procure o ícone na bandeja do sistema.")
        sys.exit(0)

    config = Config()
    fonte = "demo" if args.demo else config.geral["fonte_dados"]
    aplicativo = Aplicativo(config, fonte)
    app.aboutToQuit.connect(aplicativo.encerrar)
    aplicativo.iniciar()
    sys.exit(app.exec())
