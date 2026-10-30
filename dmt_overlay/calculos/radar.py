from __future__ import annotations

import math
from dataclasses import dataclass

from ..telemetria.modelos import Estado

COMPRIMENTO_CARRO = 4.7
LARGURA_CARRO = 2.0


@dataclass(slots=True, frozen=True)
class Vizinho:
    id: int
    classe: str
    direita: float
    frente: float
    angulo: float

    @property
    def lado_a_lado(self) -> bool:
        return abs(self.frente) < COMPRIMENTO_CARRO and abs(self.direita) < LARGURA_CARRO * 2.5


def para_local(ori: tuple[float, ...], dx: float, dy: float, dz: float) -> tuple[float, float]:
    lx = ori[0] * dx + ori[3] * dy + ori[6] * dz
    lz = ori[2] * dx + ori[5] * dy + ori[8] * dz
    return -lx, -lz


def calcular_vizinhos(estado: Estado, alcance: float = 15.0, inverter_lados: bool = False) -> list[Vizinho]:
    carro = estado.carro_jogador
    id_jogador = carro.id if carro else estado.jogador.id
    eu = estado.posicoes.get(id_jogador)
    if eu is None:
        return []
    classes = {c.id: c.classe for c in estado.carros}
    sinal = -1.0 if inverter_lados else 1.0
    vizinhos = []
    for id_, pos in estado.posicoes.items():
        if id_ == id_jogador:
            continue
        dx, dy, dz = pos.x - eu.x, pos.y - eu.y, pos.z - eu.z
        if abs(dx) > alcance * 1.5 or abs(dz) > alcance * 1.5 or abs(dy) > 10:
            continue
        direita, frente = para_local(eu.orientacao, dx, dy, dz)
        if math.hypot(direita, frente) > alcance:
            continue
        o = pos.orientacao
        fd, ff = para_local(eu.orientacao, -o[2], -o[5], -o[8])
        angulo = math.atan2(fd, ff)
        vizinhos.append(Vizinho(id_, classes.get(id_, ""), direita * sinal, frente, angulo * sinal))
    vizinhos.sort(key=lambda v: math.hypot(v.direita, v.frente))
    return vizinhos
