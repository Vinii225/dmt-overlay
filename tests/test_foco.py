from conftest import carro, estado

from dmt_overlay.calculos.foco import TEMPO_MINIMO, Foco, aplicar_foco, brigas


def grid(gaps, tempo=0.0):
    """Carros 1..n da mesma classe, com o tempo para o líder acumulando os intervalos."""
    acumulado, carros = 0.0, []
    for i, gap in enumerate([0.0, *gaps], start=1):
        acumulado += gap
        carros.append(carro(i, i, 10, 0.0, tempo_lider=acumulado))
    e = estado(carros, tempo_decorrido=tempo)
    e.pilotando = False
    return e


def test_brigas_ordena_pela_mais_apertada():
    pares = brigas(grid([3.0, 0.4, 1.2]).carros)
    assert [(round(i, 1), c.id) for i, c in pares] == [(0.4, 3), (1.2, 4), (3.0, 2)]


def test_briga_nao_mistura_classes_nem_voltas():
    e = grid([0.3, 0.3])
    e.carros[1].classe = "LMP2"
    e.carros[2].voltas_lider = 1
    assert brigas(e.carros) == []


def test_foco_segura_a_briga_antes_de_trocar():
    foco = Foco()
    assert foco.escolher(grid([0.5, 2.0], tempo=0), "briga") == 2
    # Outra briga ficou mais apertada, mas ainda não deu o tempo mínimo.
    assert foco.escolher(grid([0.9, 0.1], tempo=3), "briga") == 2
    assert foco.escolher(grid([0.9, 0.1], tempo=TEMPO_MINIMO + 1), "briga") == 3


def test_foco_por_numero_e_lider():
    e = grid([1.0, 1.0])
    assert Foco().escolher(e, "numero", "#3") == 3
    assert Foco().escolher(e, "lider") == 1
    aplicar_foco(e, 3)
    assert e.carro_jogador.id == 3
