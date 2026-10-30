import ctypes

from dmt_overlay.telemetria import lmu
from dmt_overlay.telemetria.modelos import TipoSessao
from dmt_overlay.terceiros.pylmu import lmu_data as ld


def test_offsets_dentro_da_estrutura():
    assert lmu._TAMANHO == ctypes.sizeof(ld.LMUObjectOut)
    assert lmu._OFF_TELE + lmu._MAX_VEICULOS * lmu._TAM_TELE <= lmu._TAMANHO
    assert lmu._OFF_VEICULOS + lmu._MAX_VEICULOS * lmu._TAM_VEICULO <= lmu._TAMANHO


def test_tipo_sessao():
    assert lmu.tipo_sessao(0) is TipoSessao.TESTE
    assert lmu.tipo_sessao(3) is TipoSessao.TREINO
    assert lmu.tipo_sessao(6) is TipoSessao.CLASSIFICACAO
    assert lmu.tipo_sessao(9) is TipoSessao.WARMUP
    assert lmu.tipo_sessao(10) is TipoSessao.CORRIDA


def test_texto_e_numero():
    assert lmu.texto(b"Le Mans  ") == "Le Mans"
    assert lmu.texto("Señor".encode("cp1252")) == "Señor"
    assert lmu.numero(float("nan")) == 0.0


def test_sem_jogo_retorna_desconectado(monkeypatch):
    def falhar():
        raise OSError("sem jogo")

    monkeypatch.setattr(lmu, "abrir_memoria", falhar)
    estado = lmu.FonteLMU().ler()
    assert not estado.conectado and not estado.pilotando


def test_tamanhos_conhecidos_da_api():
    assert ctypes.sizeof(ld.LMUVehicleScoring) == 584
    assert ctypes.sizeof(ld.LMUVehicleTelemetry) == 1888
    assert ctypes.sizeof(ld.LMUObjectOut) == 324820
