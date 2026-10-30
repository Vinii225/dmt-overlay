from __future__ import annotations

from dataclasses import dataclass

from ..telemetria.modelos import Carro, Estado


@dataclass(slots=True)
class LinhaRelativo:
    carro: Carro
    distancia: float
    tempo: float
    voltas_diferenca: int


def calcular_relativo(estado: Estado, quantidade: int = 3) -> list[LinhaRelativo]:
    jogador = estado.carro_jogador
    pista = estado.sessao.tamanho_pista
    if jogador is None or pista <= 0:
        return []
    ritmo = jogador.tempo_estimado or jogador.melhor_volta or 200.0
    metade = pista / 2
    total_jogador = jogador.voltas + jogador.distancia_volta / pista
    linhas = []
    for carro in estado.carros:
        if carro.jogador:
            linhas.append(LinhaRelativo(carro, 0.0, 0.0, 0))
            continue
        if carro.finalizado > 1:
            continue
        d = carro.distancia_volta - jogador.distancia_volta
        if d > metade:
            d -= pista
        elif d < -metade:
            d += pista
        total = carro.voltas + carro.distancia_volta / pista
        voltas = round(total - total_jogador - d / pista)
        linhas.append(LinhaRelativo(carro, d, d / pista * ritmo, voltas))
    linhas.sort(key=lambda l: l.distancia, reverse=True)
    centro = next(i for i, l in enumerate(linhas) if l.carro.jogador)
    inicio = max(0, centro - quantidade)
    return linhas[inicio : centro + quantidade + 1]
