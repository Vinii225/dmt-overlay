import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.calculos.combustivel import CalculadoraCombustivel  # noqa: E402
from dmt_overlay.provedor import Quadro  # noqa: E402
from dmt_overlay.telemetria.demo import FonteDemo  # noqa: E402
from dmt_overlay.telemetria.modelos import Estado  # noqa: E402
from dmt_overlay.widgets import WIDGETS  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize("classe", WIDGETS, ids=lambda c: c.nome)
def test_widget_desenha_com_e_sem_dados(app, classe):
    estado = FonteDemo().ler()
    for quadro in (Quadro(estado, CalculadoraCombustivel().atualizar(estado), 1.0), Quadro(Estado())):
        widget = classe(classe.padrao(), 1.0)
        widget.atualizar(quadro)
        assert not widget.grab().isNull()
