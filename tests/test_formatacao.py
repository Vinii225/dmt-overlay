from dmt_overlay.calculos.formatacao import duracao, intervalo, nome_curto, numero_carro, tempo_volta


def test_tempo_volta():
    assert tempo_volta(208.456) == "3:28.456"
    assert tempo_volta(0) == "-:--.---"


def test_duracao():
    assert duracao(3725) == "1:02:05"
    assert duracao(65) == "01:05"


def test_intervalo():
    assert intervalo(1.23, 0) == "+1.2"
    assert intervalo(75.0, 0) == "+1:15.0"
    assert intervalo(10.0, 2) == "+2V"


def test_nome_curto():
    assert nome_curto("Vinicius Ares") == "Vinicius Ares"
    assert nome_curto("Vinicius Ares Damata Silva") == "V. Ares Damata …"


def test_numero_carro():
    assert numero_carro("DMT Damata Racing #12") == "12"
    assert numero_carro("Equipe sem numero") == ""
