from __future__ import annotations

from dataclasses import dataclass

from ..telemetria.modelos import Estado
from .relativo import LinhaRelativo, calcular_relativo

ORDEM_CLASSES = (("hypercar", 0), ("lmp2", 1), ("lmp3", 2), ("gte", 3), ("gt3", 3))


def nivel_classe(nome: str) -> int:
    chave = nome.lower().replace(" ", "").replace("-", "")
    for prefixo, nivel in ORDEM_CLASSES:
        if prefixo in chave:
            return nivel
    return 9


@dataclass(slots=True)
class AlertaMulticlasse:
    chegando: LinhaRelativo | None = None
    a_frente: LinhaRelativo | None = None

    @property
    def vazio(self) -> bool:
        return self.chegando is None and self.a_frente is None


def alerta_multiclasse(estado: Estado, janela_atras: float = 3.0, janela_frente: float = 3.0) -> AlertaMulticlasse:
    jogador = estado.carro_jogador
    if jogador is None:
        return AlertaMulticlasse()
    meu_nivel = nivel_classe(jogador.classe)
    linhas = calcular_relativo(estado, len(estado.carros))
    alerta = AlertaMulticlasse()
    for linha in linhas:
        carro = linha.carro
        if carro.jogador or carro.nos_boxes or carro.classe == jogador.classe:
            continue
        nivel = nivel_classe(carro.classe)
        if nivel < meu_nivel and -janela_atras <= linha.tempo < 0:
            if alerta.chegando is None or linha.tempo > alerta.chegando.tempo:
                alerta.chegando = linha
        elif nivel > meu_nivel and 0 < linha.tempo <= janela_frente:
            if alerta.a_frente is None or linha.tempo < alerta.a_frente.tempo:
                alerta.a_frente = linha
    return alerta
