"""Modo narrador: escolhe o carro em foco quando quem usa o app está assistindo, sem carro."""

from __future__ import annotations

from ..telemetria.modelos import Carro, Estado
from .formatacao import numero_carro

MODOS = (("briga", "Briga mais apertada"), ("lider", "Líder"), ("numero", "Carro pelo número"))
# Na briga automática, só troca de foco se a nova briga for bem mais apertada e depois de um tempo mínimo,
# para o HUD não ficar pulando de carro em carro.
VANTAGEM_TROCA = 0.4
TEMPO_MINIMO = 8.0


def brigas(carros: list[Carro]) -> list[tuple[float, Carro]]:
    """(intervalo, carro de trás) para cada par vizinho da mesma classe na mesma volta."""
    por_classe: dict[str, list[Carro]] = {}
    for c in sorted(carros, key=lambda c: c.posicao):
        if not c.nos_boxes:
            por_classe.setdefault(c.classe, []).append(c)
    pares = []
    for lista in por_classe.values():
        for frente, tras in zip(lista, lista[1:], strict=False):
            if tras.voltas_lider == frente.voltas_lider:
                intervalo = tras.tempo_lider - frente.tempo_lider
                if intervalo > 0:
                    pares.append((intervalo, tras))
    return sorted(pares, key=lambda par: par[0])


class Foco:
    def __init__(self) -> None:
        self.atual: int | None = None
        self._desde = 0.0

    def escolher(self, estado: Estado, modo: str, numero: str = "") -> int | None:
        carros = estado.carros
        if not carros:
            return None
        agora = estado.sessao.tempo_decorrido
        if modo == "numero" and numero.strip():
            alvo = next((c for c in carros if numero_carro(c.equipe) == numero.strip().lstrip("#")), None)
            if alvo is not None:
                return self._fixar(alvo.id, agora)
        if modo == "lider":
            return self._fixar(min(carros, key=lambda c: c.posicao).id, agora)

        pares = brigas(carros)
        if not pares:
            atual_existe = any(c.id == self.atual for c in carros)
            return self.atual if atual_existe else self._fixar(min(carros, key=lambda c: c.posicao).id, agora)
        melhor_intervalo, melhor = pares[0]
        atual = next(((i, c) for i, c in pares if c.id == self.atual), None)
        if atual is not None:
            segurou_pouco = agora - self._desde < TEMPO_MINIMO and agora >= self._desde
            if segurou_pouco or atual[0] <= melhor_intervalo + VANTAGEM_TROCA:
                return self.atual
        return self._fixar(melhor.id, agora)

    def _fixar(self, id_: int, agora: float) -> int:
        if id_ != self.atual:
            self.atual = id_
            self._desde = agora
        return id_


def aplicar_foco(estado: Estado, id_: int | None) -> None:
    """Marca o carro em foco como o "jogador", para widgets e HUD girarem em volta dele."""
    if id_ is None:
        return
    for c in estado.carros:
        c.jogador = c.id == id_
