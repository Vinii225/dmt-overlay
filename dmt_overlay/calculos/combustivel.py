from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass

from ..telemetria.modelos import Estado


@dataclass(slots=True)
class ResumoCombustivel:
    atual: float = 0.0
    tanque: float = 0.0
    media: float = 0.0
    ultima: float = 0.0
    voltas_restantes: float = 0.0
    voltas_para_fim: float = 0.0
    necessario: float = 0.0
    energia: float = 0.0
    energia_media: float = 0.0
    energia_voltas: float = 0.0
    usa_energia: bool = False

    @property
    def para_reabastecer(self) -> float:
        return max(0.0, self.necessario - self.atual)


class CalculadoraCombustivel:
    def __init__(self, amostras: int = 5) -> None:
        self._consumos: deque[float] = deque(maxlen=amostras)
        self._energias: deque[float] = deque(maxlen=amostras)
        self._volta = -1
        self._inicio_combustivel = 0.0
        self._inicio_energia = 0.0
        self._ultimo_combustivel = 0.0
        self._volta_suja = True
        self._ultima = 0.0

    def reiniciar(self) -> None:
        self._consumos.clear()
        self._energias.clear()
        self._volta = -1

    def atualizar(self, estado: Estado) -> ResumoCombustivel:
        j = estado.jogador
        carro = estado.carro_jogador
        if j.combustivel > self._ultimo_combustivel + 0.3:
            self._inicio_combustivel = j.combustivel
            self._inicio_energia = j.energia_virtual
            self._volta_suja = True
        if carro is not None and carro.nos_boxes:
            self._volta_suja = True
        self._ultimo_combustivel = j.combustivel

        if j.volta != self._volta:
            if self._volta >= 0 and j.volta == self._volta + 1 and not self._volta_suja:
                gasto = self._inicio_combustivel - j.combustivel
                if 0 < gasto < max(j.tanque, 1) * 0.5:
                    self._consumos.append(gasto)
                    self._ultima = gasto
                gasto_energia = self._inicio_energia - j.energia_virtual
                if 0 < gasto_energia < 0.5:
                    self._energias.append(gasto_energia)
            self._volta_suja = self._volta < 0 or j.volta < self._volta
            self._volta = j.volta
            self._inicio_combustivel = j.combustivel
            self._inicio_energia = j.energia_virtual

        media = sum(self._consumos) / len(self._consumos) if self._consumos else 0.0
        energia_media = sum(self._energias) / len(self._energias) if self._energias else 0.0
        para_fim = voltas_para_fim(estado)
        return ResumoCombustivel(
            atual=j.combustivel,
            tanque=j.tanque,
            media=media,
            ultima=self._ultima,
            voltas_restantes=j.combustivel / media if media > 0 else 0.0,
            voltas_para_fim=para_fim,
            necessario=para_fim * media,
            energia=j.energia_virtual,
            energia_media=energia_media,
            energia_voltas=j.energia_virtual / energia_media if energia_media > 0 else 0.0,
            usa_energia=j.energia_virtual > 0,
        )


def voltas_para_fim(estado: Estado) -> float:
    s = estado.sessao
    carro = estado.carro_jogador
    if carro is None or s.tamanho_pista <= 0:
        return 0.0
    fracao = carro.distancia_volta / s.tamanho_pista
    if s.por_voltas:
        return max(0.0, s.voltas_max - carro.voltas - fracao)
    if s.tempo_final <= 0:
        return 0.0
    ritmo = carro.ultima_volta if carro.ultima_volta > 0 else carro.tempo_estimado
    if ritmo <= 0:
        return 0.0
    return math.ceil(fracao + s.tempo_restante / ritmo) - fracao
