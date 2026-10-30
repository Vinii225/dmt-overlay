import math

from conftest import carro, estado

from dmt_overlay.calculos.radar import calcular_vizinhos
from dmt_overlay.telemetria.modelos import Posicao

IDENTIDADE = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)


def girar_y(theta):
    c, s = math.cos(theta), math.sin(theta)
    return (c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c)


def cenario(posicoes):
    e = estado([carro(1, 1, 1, 0, jogador=True), carro(2, 2, 1, 0, classe="LMGT3")])
    e.posicoes = posicoes
    return e


def test_carro_a_frente_e_a_direita():
    e = cenario({1: Posicao(0, 0, 0, IDENTIDADE), 2: Posicao(-2.0, 0, -3.0, IDENTIDADE)})
    (v,) = calcular_vizinhos(e)
    assert math.isclose(v.direita, 2.0) and math.isclose(v.frente, 3.0)
    assert math.isclose(v.angulo, 0.0, abs_tol=1e-9)
    assert v.lado_a_lado and v.classe == "LMGT3"


def test_rotacao_do_jogador_nao_muda_posicao_relativa():
    theta = 1.1
    ori = girar_y(theta)
    frente_mundo = (-ori[2], -ori[5], -ori[8])
    direita_mundo = (-ori[0], -ori[3], -ori[6])
    alvo = tuple(5 * f + 1.5 * d for f, d in zip(frente_mundo, direita_mundo, strict=True))
    e = cenario({1: Posicao(0, 0, 0, ori), 2: Posicao(alvo[0], alvo[1], alvo[2], ori)})
    (v,) = calcular_vizinhos(e)
    assert math.isclose(v.frente, 5.0, abs_tol=1e-9) and math.isclose(v.direita, 1.5, abs_tol=1e-9)


def test_fora_do_alcance_e_inverter_lados():
    e = cenario({1: Posicao(0, 0, 0, IDENTIDADE), 2: Posicao(-2.0, 0, -30.0, IDENTIDADE)})
    assert calcular_vizinhos(e) == []
    e.posicoes[2] = Posicao(-2.0, 0, -3.0, IDENTIDADE)
    assert math.isclose(calcular_vizinhos(e, inverter_lados=True)[0].direita, -2.0)
