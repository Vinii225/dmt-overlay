import os

import pytest
from conftest import carro, estado

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.provedor import Quadro  # noqa: E402
from dmt_overlay.widgets.rivais import Rivais, quantidade  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def grid(classe, eu_pos):
    carros = [
        carro(i, i, 10, 0.0, classe=classe, jogador=i == eu_pos, pneus_restante=(0.9, 0.8, 0.7, 0.6), energia=0.5)
        for i in range(1, 9)
    ]
    carros.append(carro(99, 9, 10, 0.0, classe="Outra"))
    return estado(carros)


def test_quantidade_por_classe():
    config = Rivais.padrao()
    assert quantidade(config, "Hypercar") == 5
    assert quantidade(config, "LMP2") == 3
    assert quantidade(config, "LMGT3") == 3
    assert quantidade(config, "GTE") == 3


def test_hypercar_mostra_top5_e_o_jogador(app):
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(grid("Hypercar", 7)))
    classe, linhas = widget._dados
    assert [linha[0] for linha in linhas] == [1, 2, 3, 4, 5, 7]
    assert linhas[-1][-1] is True
    assert linhas[0][4] == 0.6 and linhas[0][5] == 0.5
    assert not widget.grab().isNull()


def test_lmp2_top3_sem_repetir_jogador(app):
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(grid("LMP2", 2)))
    assert [linha[0] for linha in widget._dados[1]] == [1, 2, 3]


def test_dado_ausente_vira_traco(app):
    e = grid("LMGT3", 1)
    for c in e.carros:
        c.pneus_restante, c.energia = (), -1.0
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(e))
    assert all(linha[4] == -1.0 and linha[5] == -1.0 for linha in widget._dados[1])
    assert not widget.grab().isNull()
