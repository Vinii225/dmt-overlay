from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, QTimer, Signal

from .calculos.combustivel import CalculadoraCombustivel, ResumoCombustivel
from .calculos.estrategia import CalculadoraEstrategia, ResumoEstrategia
from .telemetria.demo import FonteDemo
from .telemetria.lmu import FonteLMU
from .telemetria.modelos import Estado

log = logging.getLogger(__name__)

FONTES = {"lmu": FonteLMU, "demo": FonteDemo}


@dataclass(slots=True)
class Quadro:
    estado: Estado = field(default_factory=Estado)
    combustivel: ResumoCombustivel = field(default_factory=ResumoCombustivel)
    instante: float = 0.0
    estrategia: ResumoEstrategia = field(default_factory=ResumoEstrategia)


class Provedor(QObject):
    novo_quadro = Signal(object)
    conexao_mudou = Signal(bool)
    pilotando_mudou = Signal(bool)

    def __init__(self, fonte: str = "lmu", taxa: int = 30) -> None:
        super().__init__()
        self._fonte = FONTES.get(fonte, FonteLMU)()
        self._chave_fonte = fonte
        self._combustivel = CalculadoraCombustivel()
        self._estrategia = CalculadoraEstrategia()
        self._conectado = False
        self._pilotando = False
        self._identidade_sessao: tuple | None = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self.definir_taxa(taxa)

    @property
    def fonte(self) -> str:
        return self._chave_fonte

    def definir_taxa(self, taxa: int) -> None:
        self._timer.setInterval(max(5, int(1000 / max(1, taxa))))

    def trocar_fonte(self, chave: str) -> None:
        if chave == self._chave_fonte:
            return
        self._fonte.fechar()
        self._fonte = FONTES[chave]()
        self._chave_fonte = chave
        self._combustivel.reiniciar()
        self._estrategia.reiniciar()
        log.info("fonte de dados: %s", self._fonte.nome)

    def iniciar(self) -> None:
        self._timer.start()

    def parar(self) -> None:
        self._timer.stop()
        self._fonte.fechar()

    def _tick(self) -> None:
        try:
            estado = self._fonte.ler()
        except Exception:
            log.exception("erro ao ler telemetria")
            self._fonte.fechar()
            estado = Estado()
        self._detectar_nova_sessao(estado)
        if estado.pilotando:
            resumo = self._combustivel.atualizar(estado)
            estrategia = self._estrategia.atualizar(estado, resumo)
        else:
            resumo = ResumoCombustivel()
            estrategia = ResumoEstrategia()
        if estado.conectado != self._conectado:
            self._conectado = estado.conectado
            self.conexao_mudou.emit(estado.conectado)
        if estado.pilotando != self._pilotando:
            self._pilotando = estado.pilotando
            self.pilotando_mudou.emit(estado.pilotando)
        self.novo_quadro.emit(Quadro(estado, resumo, time.monotonic(), estrategia))

    def _detectar_nova_sessao(self, estado: Estado) -> None:
        s = estado.sessao
        identidade = (s.pista, s.tipo, s.tempo_final, estado.jogador.id)
        if estado.conectado and identidade != self._identidade_sessao:
            self._identidade_sessao = identidade
            self._combustivel.reiniciar()
            self._estrategia.reiniciar()
