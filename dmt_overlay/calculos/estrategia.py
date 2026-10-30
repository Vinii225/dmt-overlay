from __future__ import annotations

import math
from dataclasses import dataclass

from ..telemetria.modelos import Estado
from .combustivel import ResumoCombustivel


@dataclass(slots=True)
class ResumoEstrategia:
    tempo_stint: float = 0.0
    voltas_stint: int = 0
    volta_atual: int = 0
    janela_inicio: int = 0
    janela_fim: int = 0
    paradas: int = 0
    abastecer_litros: float = 0.0
    abastecer_energia: float = 0.0
    valido: bool = False


def voltas_por_tanque(c: ResumoCombustivel) -> float:
    candidatos = []
    if c.media > 0 and c.tanque > 0:
        candidatos.append(c.tanque / c.media)
    if c.usa_energia and c.energia_media > 0:
        candidatos.append(1.0 / c.energia_media)
    return min(candidatos) if candidatos else 0.0


def voltas_possiveis(c: ResumoCombustivel) -> float:
    candidatos = []
    if c.media > 0:
        candidatos.append(c.voltas_restantes)
    if c.usa_energia and c.energia_media > 0:
        candidatos.append(c.energia_voltas)
    return min(candidatos) if candidatos else 0.0


def planejar(volta: int, c: ResumoCombustivel) -> ResumoEstrategia:
    possiveis = voltas_possiveis(c)
    por_tanque = voltas_por_tanque(c)
    para_fim = c.voltas_para_fim
    if possiveis <= 0 or por_tanque <= 0 or para_fim <= 0:
        return ResumoEstrategia(volta_atual=volta)
    faltando = max(0.0, para_fim - possiveis)
    paradas = math.ceil(faltando / por_tanque - 1e-6) if faltando > 0 else 0
    janela_fim = volta + max(0, math.floor(possiveis))
    janela_inicio = volta + max(0, math.ceil(para_fim - por_tanque * paradas)) if paradas else janela_fim
    janela_inicio = min(janela_inicio, janela_fim)
    litros = 0.0
    energia = 0.0
    if paradas:
        ate_fim_depois = min(para_fim - (janela_inicio - volta), por_tanque)
        litros = min(c.tanque, ate_fim_depois * c.media) - max(0.0, c.atual - (janela_inicio - volta) * c.media)
        if c.usa_energia and c.energia_media > 0:
            energia = min(1.0, ate_fim_depois * c.energia_media) - max(0.0, c.energia - (janela_inicio - volta) * c.energia_media)
    return ResumoEstrategia(
        volta_atual=volta,
        janela_inicio=janela_inicio,
        janela_fim=janela_fim,
        paradas=paradas,
        abastecer_litros=max(0.0, litros),
        abastecer_energia=max(0.0, energia),
        valido=True,
    )


class CalculadoraEstrategia:
    def __init__(self) -> None:
        self.reiniciar()

    def reiniciar(self) -> None:
        self._inicio_tempo = -1.0
        self._inicio_volta = 0

    def atualizar(self, estado: Estado, combustivel: ResumoCombustivel) -> ResumoEstrategia:
        carro = estado.carro_jogador
        agora = estado.sessao.tempo_decorrido
        if carro is None:
            return ResumoEstrategia()
        if carro.nos_boxes or self._inicio_tempo < 0 or agora < self._inicio_tempo:
            self._inicio_tempo = agora
            self._inicio_volta = carro.voltas
        resumo = planejar(carro.voltas, combustivel)
        resumo.tempo_stint = max(0.0, agora - self._inicio_tempo)
        resumo.voltas_stint = max(0, carro.voltas - self._inicio_volta)
        return resumo
