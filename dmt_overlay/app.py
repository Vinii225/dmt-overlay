from __future__ import annotations

import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler

from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox

from . import __version__
from .atualizacao import VerificadorAtualizacao
from .bandeja import Bandeja
from .config import Config, pasta_config
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
        self.widgets: dict[str, WidgetOverlay] = {}
        for classe in WIDGETS:
            dados = config.widget(classe.nome, classe.padrao())
            widget = classe(dados, config.geral["escala"])
            widget.setWindowOpacity(config.geral["opacidade"])
            self.widgets[classe.nome] = widget
        self.provedor.novo_quadro.connect(self._novo_quadro)
        self.provedor.pilotando_mudou.connect(self._pilotando_mudou)
        self.bandeja = Bandeja(self)
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
        self.salvar()
        self.bandeja.hide()

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
        for widget in self.widgets.values():
            widget.setVisible(mostrar and widget.config["ativo"])

    def travar(self, travado: bool) -> None:
        self.config.geral["travado"] = travado
        for widget in self.widgets.values():
            widget.travar(travado)
        self.atualizar_visibilidade()
        if travado:
            self.salvar()

    def alternar_widget(self, nome: str, ativo: bool) -> None:
        self.widgets[nome].config["ativo"] = ativo
        self.atualizar_visibilidade()
        self.salvar()

    def definir_escala(self, escala: float) -> None:
        self.config.geral["escala"] = escala
        for widget in self.widgets.values():
            widget.escala = escala
            widget.ajustar_tamanho()
            widget.update()
        self.salvar()

    def definir_opacidade(self, opacidade: float) -> None:
        self.config.geral["opacidade"] = opacidade
        for widget in self.widgets.values():
            widget.setWindowOpacity(opacidade)
        self.salvar()

    def definir_ocultar(self, ocultar: bool) -> None:
        self.config.geral["ocultar_fora_da_pista"] = ocultar
        self.atualizar_visibilidade()
        self.salvar()

    def definir_verificar_atualizacoes(self, ativo: bool) -> None:
        self.config.geral["verificar_atualizacoes"] = ativo
        self.salvar()

    def trocar_fonte(self, chave: str) -> None:
        self.provedor.trocar_fonte(chave)
        self.config.geral["fonte_dados"] = chave
        self.salvar()

    def restaurar_posicoes(self) -> None:
        for widget in self.widgets.values():
            x, y = widget.posicao_padrao
            widget.config["x"], widget.config["y"] = x, y
            widget.move(x, y)
        self.salvar()


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
