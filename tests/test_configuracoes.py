import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QKeySequence  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QKeySequenceEdit,
    QLabel,
    QSpinBox,
)

from dmt_overlay.app import Aplicativo  # noqa: E402
from dmt_overlay.config import Config  # noqa: E402
from dmt_overlay.widgets import WIDGETS  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def aplicativo(qapp, tmp_path):
    app = Aplicativo(Config(tmp_path / "config.json"), "demo")
    yield app
    app.encerrar()


@pytest.mark.parametrize("classe", WIDGETS, ids=lambda c: c.nome)
def test_toda_opcao_tem_rotulo_e_cabe_na_faixa(classe):
    assert classe.descricao
    assert set(classe.opcoes) == set(classe.opcoes_padrao)
    for chave, opcao in classe.opcoes.items():
        padrao = classe.opcoes_padrao[chave]
        if isinstance(padrao, bool):
            continue
        if opcao.escolhas:
            assert padrao in dict(opcao.escolhas)
        else:
            assert opcao.minimo <= padrao * opcao.fator <= opcao.maximo


def pagina(janela, titulo):
    janela.mostrar_pagina(titulo)
    return janela.paginas.currentWidget().widget()


def test_janela_abre_com_todas_as_paginas(aplicativo):
    aplicativo.abrir_configuracoes()
    janela = aplicativo.janela_configuracoes
    titulos = [janela.navegacao.item(i).text() for i in range(janela.navegacao.count())]
    assert titulos[:3] == ["Geral", "Aparência", "Atalhos"]
    assert all(w.titulo in titulos for w in aplicativo.widgets.values())
    assert not janela.grab().isNull()


def test_opcao_do_widget_aplica_e_salva(aplicativo):
    aplicativo.abrir_configuracoes()
    relativo = aplicativo.widgets["relativo"]
    altura = relativo.height()
    [spin] = pagina(aplicativo.janela_configuracoes, "Relativo").findChildren(QSpinBox)
    spin.setValue(5)
    assert relativo.config["carros_cada_lado"] == 5
    assert relativo.height() > altura
    assert Config(aplicativo.config.caminho).widgets["relativo"]["carros_cada_lado"] == 5


def test_opcao_com_fator_e_escolha(aplicativo):
    aplicativo.abrir_configuracoes()
    motor = pagina(aplicativo.janela_configuracoes, "Marcha e RPM")
    [luz] = motor.findChildren(QDoubleSpinBox)
    assert luz.value() == 94
    luz.setValue(90)
    assert aplicativo.widgets["motor"].config["luz_troca"] == 0.9
    [unidade] = motor.findChildren(QComboBox)
    unidade.setCurrentIndex(unidade.findData("mph"))
    assert aplicativo.widgets["motor"].config["unidade_velocidade"] == "mph"
    aplicativo.restaurar_opcoes("motor")
    assert luz.value() == 94 and unidade.currentData() == "kmh"


def test_bandeja_e_janela_ficam_em_sincronia(aplicativo):
    aplicativo.abrir_configuracoes()
    caixa = pagina(aplicativo.janela_configuracoes, "Pedais").findChildren(QCheckBox)[0]
    caixa.setChecked(False)
    assert not aplicativo.bandeja.acoes_widgets["pedais"].isChecked()
    aplicativo.bandeja.acoes_widgets["pedais"].setChecked(True)
    assert caixa.isChecked()


def test_atalho_sem_modificador_e_recusado(aplicativo):
    aplicativo.abrir_configuracoes()
    pagina_atalhos = pagina(aplicativo.janela_configuracoes, "Atalhos")
    editor = pagina_atalhos.findChildren(QKeySequenceEdit)[1]
    editor.setKeySequence(QKeySequence("H"))
    editor.editingFinished.emit()
    assert aplicativo.config.geral["atalhos"]["travar"] == "Ctrl+Shift+L"
    assert editor.keySequence().toString() == "Ctrl+Shift+L"
    erros = [r.text() for r in pagina_atalhos.findChildren(QLabel) if r.objectName() == "erro"]
    assert any("inválida" in texto for texto in erros)
