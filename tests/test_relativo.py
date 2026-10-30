from conftest import carro, estado

from dmt_overlay.calculos.relativo import calcular_relativo


def test_ordena_por_distancia_na_pista():
    carros = [
        carro(1, 1, 11, 500),
        carro(2, 2, 10, 5200),
        carro(3, 3, 10, 5000, jogador=True),
        carro(4, 4, 9, 4900),
    ]
    linhas = calcular_relativo(estado(carros), 3)
    assert [l.carro.id for l in linhas] == [2, 3, 4, 1]
    assert linhas[0].tempo > 0
    assert linhas[-1].distancia < 0


def test_diferenca_de_voltas():
    carros = [carro(1, 1, 11, 5300), carro(2, 2, 10, 5000, jogador=True), carro(3, 3, 9, 4800)]
    linhas = {l.carro.id: l for l in calcular_relativo(estado(carros), 3)}
    assert linhas[1].voltas_diferenca == 1
    assert linhas[3].voltas_diferenca == -1


def test_sem_jogador():
    assert calcular_relativo(estado([carro(1, 1, 1, 0)])) == []
