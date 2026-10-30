from conftest import carro, estado

from dmt_overlay.calculos.combustivel import CalculadoraCombustivel, voltas_para_fim


def quadro(volta, combustivel, distancia=100.0):
    e = estado([carro(1, 1, volta, distancia, jogador=True)], tempo_final=3600.0, tempo_decorrido=1800.0)
    e.jogador.volta = volta
    e.jogador.combustivel = combustivel
    e.jogador.tanque = 100.0
    return e


def test_media_ignora_primeira_volta_e_reabastecimento():
    calc = CalculadoraCombustivel()
    calc.atualizar(quadro(1, 90))
    calc.atualizar(quadro(2, 87))
    calc.atualizar(quadro(3, 84))
    resumo = calc.atualizar(quadro(4, 81))
    assert resumo.media == 3.0
    assert round(resumo.voltas_restantes) == 27
    calc.atualizar(quadro(4, 100))
    resumo = calc.atualizar(quadro(5, 97))
    assert resumo.media == 3.0


def test_voltas_para_fim_por_tempo():
    e = quadro(5, 50, distancia=0.0)
    assert voltas_para_fim(e) == 9
