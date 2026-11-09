import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from conftest import carro, estado  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.app import Aplicativo  # noqa: E402
from dmt_overlay.config import Config  # noqa: E402
from dmt_overlay.layouts import chave_classe  # noqa: E402
from dmt_overlay.provedor import Quadro  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def aplicativo(qapp, tmp_path):
    config = Config(tmp_path / "config.json")
    config.geral["layout_por_classe"] = True
    config.geral["ocultar_fora_da_pista"] = False
    app = Aplicativo(config, "demo")
    yield app
    app.encerrar()


def quadro(classe):
    return Quadro(estado([carro(1, 1, 3, 100.0, jogador=True, classe=classe)]))


def test_chave_classe_junta_nomes_parecidos():
    assert chave_classe("LMGT3") == chave_classe("GT3") == "GT3"
    assert chave_classe("Hypercar") == "HY"
    assert chave_classe("  ") == ""


def test_cada_classe_guarda_seu_layout(aplicativo):
    radar = aplicativo.widgets["radar"]
    aplicativo._novo_quadro(quadro("Hypercar"))
    radar.config["x"] = 111
    aplicativo.alternar_widget("pedais", False)

    aplicativo._novo_quadro(quadro("LMGT3"))
    assert aplicativo.nome_classe == "LMGT3"
    radar.config["x"] = 999
    aplicativo.alternar_widget("pedais", True)

    aplicativo._novo_quadro(quadro("Hypercar"))
    assert radar.config["x"] == 111 and radar.x() == 111
    assert not aplicativo.widgets["pedais"].isVisible()

    aplicativo._novo_quadro(quadro("GT3"))
    assert radar.config["x"] == 999
    assert aplicativo.widgets["pedais"].isVisible()


def test_desligado_nao_troca_layout(aplicativo):
    aplicativo.definir_layout_por_classe(False)
    radar = aplicativo.widgets["radar"]
    aplicativo._novo_quadro(quadro("Hypercar"))
    radar.config["x"] = 50
    aplicativo._novo_quadro(quadro("LMP2"))
    assert radar.config["x"] == 50
    assert aplicativo.nome_classe == "LMP2"
