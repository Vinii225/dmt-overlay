import os

import pytest
from conftest import carro, estado

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.provedor import Quadro  # noqa: E402
from dmt_overlay.widgets.rivais import Rivais  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def misto(minha, eu_pos):
    """8 carros da classe do jogador e 5 de cada uma das outras duas."""
    carros = [
        carro(i, i, 10, 0.0, classe=minha, jogador=i == eu_pos, pneus_restante=(0.9, 0.8, 0.7, 0.6), energia=0.5)
        for i in range(1, 9)
    ]
    outras = [c for c in ("Hypercar", "LMP2", "LMGT3") if c != minha]
    for k, classe in enumerate(outras):
        carros += [carro(100 + 10 * k + i, 9 + 5 * k + i, 10, 0.0, classe=classe) for i in range(5)]
    return estado(carros)


def test_sua_classe_mostra_mais_e_as_outras_top3(app):
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(misto("LMGT3", 7)))
    grupos = widget._dados
    assert [g[0] for g in grupos] == ["LMGT3", "Hypercar", "LMP2"]
    assert [linha[0] for linha in grupos[0][1]] == [1, 2, 3, 4, 5, 7]
    assert grupos[0][1][-1][-1] is True
    assert grupos[0][1][0][4] == 0.6 and grupos[0][1][0][5] == 0.5
    assert all(len(linhas) == 3 for _, linhas in grupos[1:])
    assert widget.height() == widget.tamanho_base().height()
    assert not widget.grab().isNull()


def test_classe_muda_com_o_carro_do_jogador(app):
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(misto("Hypercar", 2)))
    assert widget._dados[0][0] == "Hypercar"
    assert [linha[0] for linha in widget._dados[0][1]] == [1, 2, 3, 4, 5]


def test_so_a_sua_classe(app):
    config = Rivais.padrao()
    config["mostrar_outras"] = False
    widget = Rivais(config, 1.0)
    widget.atualizar(Quadro(misto("LMP2", 1)))
    assert [g[0] for g in widget._dados] == ["LMP2"]


def test_dado_ausente_vira_traco(app):
    e = misto("LMGT3", 1)
    for c in e.carros:
        c.pneus_restante, c.energia = (), -1.0
    widget = Rivais(Rivais.padrao(), 1.0)
    widget.atualizar(Quadro(e))
    assert all(linha[4] == -1.0 and linha[5] == -1.0 for _, linhas in widget._dados for linha in linhas)
    assert not widget.grab().isNull()
