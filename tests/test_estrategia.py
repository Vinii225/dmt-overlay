from conftest import carro, estado

from dmt_overlay.calculos.combustivel import ResumoCombustivel
from dmt_overlay.calculos.estrategia import CalculadoraEstrategia, planejar


def resumo(atual=30.0, media=3.0, para_fim=20.0, energia=0.0, energia_media=0.0):
    return ResumoCombustivel(
        atual=atual,
        tanque=100.0,
        media=media,
        voltas_restantes=atual / media,
        voltas_para_fim=para_fim,
        energia=energia,
        energia_media=energia_media,
        energia_voltas=energia / energia_media if energia_media else 0.0,
        usa_energia=energia > 0,
    )


def test_sem_parada_quando_combustivel_basta():
    plano = planejar(10, resumo(atual=90.0, para_fim=20.0))
    assert plano.valido and plano.paradas == 0


def test_uma_parada_com_janela():
    plano = planejar(10, resumo(atual=30.0, para_fim=40.0))
    assert plano.paradas == 1
    assert plano.janela_fim == 20
    assert plano.janela_inicio == 17
    assert round(plano.abastecer_litros) == 90


def test_energia_virtual_limita():
    plano = planejar(0, resumo(atual=90.0, para_fim=20.0, energia=0.5, energia_media=0.05))
    assert plano.janela_fim == 10
    assert plano.paradas == 1
    assert plano.abastecer_energia > 0


def test_sem_dados_nao_planeja():
    assert not planejar(0, ResumoCombustivel()).valido


def test_stint_reinicia_ao_sair_do_box():
    calc = CalculadoraEstrategia()
    box = estado([carro(1, 1, 5, 0, jogador=True, nos_boxes=True)], tempo_decorrido=100.0)
    calc.atualizar(box, resumo())
    pista = estado([carro(1, 1, 8, 0, jogador=True)], tempo_decorrido=400.0)
    r = calc.atualizar(pista, resumo())
    assert r.tempo_stint == 300.0
    assert r.voltas_stint == 3
