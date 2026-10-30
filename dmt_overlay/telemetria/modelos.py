from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class TipoSessao(IntEnum):
    TESTE = 0
    TREINO = 1
    CLASSIFICACAO = 2
    WARMUP = 3
    CORRIDA = 4


NOMES_SESSAO = {
    TipoSessao.TESTE: "Teste",
    TipoSessao.TREINO: "Treino",
    TipoSessao.CLASSIFICACAO: "Classificação",
    TipoSessao.WARMUP: "Warmup",
    TipoSessao.CORRIDA: "Corrida",
}


@dataclass(slots=True)
class Pneu:
    temp_superficie: tuple[float, float, float] = (0.0, 0.0, 0.0)
    temp_carcaca: float = 0.0
    temp_ideal: float = 0.0
    pressao: float = 0.0
    restante: float = 1.0
    temp_freio: float = 0.0
    furado: bool = False


@dataclass(slots=True)
class Jogador:
    id: int = -1
    marcha: int = 0
    marchas: int = 0
    rpm: float = 0.0
    rpm_max: float = 0.0
    velocidade: float = 0.0
    acelerador: float = 0.0
    freio: float = 0.0
    embreagem: float = 0.0
    volante: float = 0.0
    combustivel: float = 0.0
    tanque: float = 0.0
    energia_virtual: float = 0.0
    bateria: float = 0.0
    delta_melhor: float = 0.0
    volta: int = 0
    inicio_volta: float = 0.0
    volta_invalidada: bool = False
    limitador: bool = False
    abs_ativo: bool = False
    tc_ativo: bool = False
    tc: int = 0
    tc_max: int = 0
    tc_corte: int = 0
    tc_slip: int = 0
    abs: int = 0
    abs_max: int = 0
    mapa_motor: int = 0
    balanco_freio: float = 0.0
    temp_agua: float = 0.0
    temp_oleo: float = 0.0
    composto_dianteiro: str = ""
    composto_traseiro: str = ""
    pneus: tuple[Pneu, Pneu, Pneu, Pneu] = field(default_factory=lambda: (Pneu(), Pneu(), Pneu(), Pneu()))


@dataclass(slots=True)
class Carro:
    id: int
    piloto: str
    equipe: str
    classe: str
    posicao: int
    voltas: int
    distancia_volta: float
    melhor_volta: float
    ultima_volta: float
    tempo_lider: float
    voltas_lider: int
    tempo_frente: float
    voltas_frente: int
    nos_boxes: bool
    paradas: int
    jogador: bool
    tempo_estimado: float
    finalizado: int = 0


@dataclass(slots=True)
class Sessao:
    tipo: TipoSessao = TipoSessao.TESTE
    pista: str = ""
    tamanho_pista: float = 0.0
    tempo_decorrido: float = 0.0
    tempo_final: float = 0.0
    voltas_max: int = 0
    fase: int = 0
    temp_ar: float = 0.0
    temp_pista: float = 0.0
    chuva: float = 0.0
    umidade_pista: float = 0.0
    hora_do_dia: float = 0.0
    bandeira_amarela: bool = False

    @property
    def tempo_restante(self) -> float:
        if self.tempo_final <= 0:
            return 0.0
        return max(0.0, self.tempo_final - self.tempo_decorrido)

    @property
    def por_voltas(self) -> bool:
        return 0 < self.voltas_max < 100000 and self.tempo_final <= 0


@dataclass(slots=True)
class Estado:
    conectado: bool = False
    pilotando: bool = False
    sessao: Sessao = field(default_factory=Sessao)
    jogador: Jogador = field(default_factory=Jogador)
    carros: list[Carro] = field(default_factory=list)

    @property
    def carro_jogador(self) -> Carro | None:
        for carro in self.carros:
            if carro.jogador:
                return carro
        return None
