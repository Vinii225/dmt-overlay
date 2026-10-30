from dmt_overlay.atualizacao import mais_nova, versao_tupla


def test_versao_tupla():
    assert versao_tupla("v0.2.0") == (0, 2, 0, 1)
    assert versao_tupla("1.10.3-beta.1") == (1, 10, 3, 0)
    assert versao_tupla("lixo") == (0, 0, 0, 0)


def test_mais_nova():
    assert mais_nova("v0.2.0", "0.1.9")
    assert mais_nova("v0.10.0", "0.9.0")
    assert not mais_nova("v0.1.0", "0.1.0")
    assert not mais_nova("v0.0.9", "0.1.0")
    assert mais_nova("v0.2.0", "0.2.0-beta.1")
    assert not mais_nova("v0.2.0-beta.1", "0.2.0")
