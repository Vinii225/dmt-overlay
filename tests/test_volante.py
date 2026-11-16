import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.provedor import Quadro  # noqa: E402
from dmt_overlay.telemetria.modelos import Estado, Jogador  # noqa: E402
from dmt_overlay.widgets.volante import Volante, angulo_volante  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def quadro(t, acel=0.0, freio=0.0, volante=0.0):
    jogador = Jogador(acelerador=acel, freio=freio, volante=volante, marcha=3, rpm=7000, rpm_max=8000)
    return Quadro(Estado(jogador=jogador), instante=t)


def test_angulo_do_volante():
    assert angulo_volante(0.0, 540) == 0
    assert angulo_volante(1.0, 540) == 270
    assert angulo_volante(-0.5, 360) == -90
    assert angulo_volante(3.0, 360) == 180


def test_grafico_guarda_so_a_janela(app):
    widget = Volante(Volante.padrao(), 1.0)
    for i in range(300):
        widget.atualizar(quadro(i / 30, acel=1.0))
    pontos = widget._dados[-1]
    assert 140 <= len(pontos) <= 152
    assert pontos[-1][0] == 1.0 and pontos[0][0] >= 0.0
    assert not widget.grab().isNull()


def test_mudar_janela_limpa_o_historico(app):
    widget = Volante(Volante.padrao(), 1.0)
    for i in range(60):
        widget.atualizar(quadro(i / 30))
    widget.config["janela"] = 2.0
    widget.reconfigurar()
    widget.atualizar(quadro(10.0))
    assert len(widget._dados[-1]) == 1
