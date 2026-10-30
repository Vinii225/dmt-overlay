from conftest import carro, estado

from dmt_overlay.calculos.multiclasse import alerta_multiclasse, nivel_classe


def test_nivel_classe():
    assert nivel_classe("Hypercar") < nivel_classe("LMP2") < nivel_classe("LMGT3")


def test_hypercar_chegando_em_gt3():
    carros = [
        carro(1, 1, 10, 4900, classe="Hypercar"),
        carro(2, 2, 10, 5000, jogador=True, classe="LMGT3"),
        carro(3, 3, 10, 4000, classe="Hypercar"),
    ]
    alerta = alerta_multiclasse(estado(carros))
    assert alerta.chegando.carro.id == 1
    assert alerta.a_frente is None


def test_gt3_a_frente_de_hypercar():
    carros = [carro(1, 1, 10, 5100, classe="LMGT3"), carro(2, 2, 10, 5000, jogador=True, classe="Hypercar")]
    alerta = alerta_multiclasse(estado(carros))
    assert alerta.a_frente.carro.id == 1
    assert alerta.chegando is None


def test_mesma_classe_nao_alerta():
    carros = [carro(1, 1, 10, 4950), carro(2, 2, 10, 5000, jogador=True)]
    assert alerta_multiclasse(estado(carros)).vazio
