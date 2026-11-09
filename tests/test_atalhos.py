import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from dmt_overlay.app import Aplicativo  # noqa: E402
from dmt_overlay.atalhos import AtalhosGlobais, interpretar  # noqa: E402
from dmt_overlay.config import Config  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize(
    ("sequencia", "esperado"),
    [
        ("Ctrl+Shift+H", (0x0006, ord("H"), "Ctrl+Shift+H")),
        ("shift + ctrl + l", (0x0006, ord("L"), "Ctrl+Shift+L")),
        ("Alt+F9", (0x0001, 0x78, "Alt+F9")),
        ("Ctrl+Alt+5", (0x0003, ord("5"), "Ctrl+Alt+5")),
        ("Ctrl+pgdown", (0x0002, 0x22, "Ctrl+PgDown")),
    ],
)
def test_interpretar(sequencia, esperado):
    assert interpretar(sequencia) == esperado


@pytest.mark.parametrize("sequencia", ["", "H", "Ctrl", "Ctrl+Ctrl+H", "Hyper+H", "Ctrl+F25", "Ctrl+Ç", "Ctrl+Shift+HH"])
def test_interpretar_rejeita_invalidos(sequencia):
    assert interpretar(sequencia) is None


def test_atalho_invalido_nao_registra(qapp):
    atalhos = AtalhosGlobais()
    assert not atalhos.registrar("travar", "Ctrl+Nada")
    assert "travar" not in atalhos.registrados
    atalhos.liberar()


def test_atalhos_escondem_e_destravar_mostra(qapp, tmp_path):
    config = Config(tmp_path / "config.json")
    config.geral["ocultar_fora_da_pista"] = False
    aplicativo = Aplicativo(config, "demo")
    ativos = [w for w in aplicativo.widgets.values() if w.config["ativo"]]
    assert all(w.isVisible() for w in ativos)

    aplicativo._atalho("mostrar_ocultar")
    assert not any(w.isVisible() for w in ativos)
    assert aplicativo.bandeja.acao_ocultar.isChecked()

    aplicativo._atalho("travar")
    assert not config.geral["travado"]
    assert not aplicativo.ocultos
    assert all(w.isVisible() for w in ativos)
    aplicativo.encerrar()
