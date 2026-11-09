import csv

from conftest import carro, estado

from dmt_overlay.gravador import COLUNAS, GravadorVoltas, RegistroVoltas, formatar, nome_arquivo
from dmt_overlay.telemetria.modelos import Jogador, Pneu


def quadro(et, volta, inicio, combustivel, restante=0.9, invalida=False, boxes=False, voltas=0):
    e = estado([carro(1, 3, voltas, 500.0, jogador=True, nos_boxes=boxes)], tempo_decorrido=et, pista="Le Mans")
    pneu = Pneu(temp_superficie=(80.0, 90.0, 100.0), pressao=170.0, restante=restante)
    e.jogador = Jogador(
        volta=volta, inicio_volta=inicio, combustivel=combustivel, tanque=100.0, volta_invalidada=invalida,
        energia_virtual=0.6, pneus=(pneu, pneu, pneu, pneu), composto_dianteiro="Medium", composto_traseiro="Medium",
    )
    return e


def rodar(registro, quadros):
    linhas = []
    for q in quadros:
        linhas += registro.atualizar(q)
    return linhas


def test_volta_parcial_e_ignorada_e_volta_completa_vira_linha():
    registro = RegistroVoltas()
    linhas = rodar(registro, [
        quadro(50, 0, 0, 50.0),
        quadro(100, 1, 100, 47.0, voltas=1),
        quadro(200, 1, 100, 45.5, restante=0.89, voltas=1),
        quadro(300, 2, 300, 44.0, restante=0.88, voltas=1),
        quadro(300.5, 2, 300, 44.0, restante=0.88, voltas=2),
    ])
    assert linhas == []
    [linha] = rodar(registro, [quadro(301.5, 2, 300, 43.9, voltas=2)])
    assert linha["tempo"] == "3:20.000"
    assert linha["tempo_s"] == 200.0
    assert linha["valida"] == "sim"
    assert linha["volta"] == 2
    assert linha["stint"] == 1 and linha["volta_no_stint"] == 1
    assert linha["combustivel_gasto"] == 3.0
    assert linha["desgaste_de"] == 2.0
    assert linha["temp_de"] == 90.0
    assert linha["posicao"] == 3


def test_volta_invalidada_e_box():
    registro = RegistroVoltas()
    rodar(registro, [quadro(0, 0, 0, 50.0), quadro(100, 1, 100, 47.0)])
    linhas = rodar(registro, [
        quadro(150, 1, 100, 46.0, invalida=True),
        quadro(190, 1, 100, 45.0, boxes=True),
        quadro(300, 2, 300, 44.0),
        quadro(302, 2, 300, 44.0),
    ])
    assert linhas[0]["valida"] == "não"
    assert linhas[0]["box"] == "sim"


def test_servico_abre_stint_novo_e_esconde_consumo():
    registro = RegistroVoltas()
    rodar(registro, [quadro(0, 0, 0, 50.0), quadro(100, 1, 100, 47.0), quadro(300, 2, 300, 44.0), quadro(302, 2, 300, 44.0)])
    linhas = rodar(registro, [
        quadro(350, 2, 300, 95.0, restante=1.0, boxes=True),
        quadro(500, 3, 500, 92.0, restante=0.99),
        quadro(502, 3, 500, 92.0, restante=0.99),
    ])
    [linha] = linhas
    assert linha["stint"] == 2 and linha["volta_no_stint"] == 1
    assert linha["combustivel_gasto"] == ""
    assert linha["desgaste_de"] == ""
    assert registro.stint == 2


def test_passar_pelo_box_sem_servico_nao_abre_stint():
    registro = RegistroVoltas()
    rodar(registro, [quadro(0, 0, 0, 50.0), quadro(100, 1, 100, 47.0), quadro(150, 1, 100, 46.0, boxes=True)])
    assert registro.stint == 1


def test_formatar_usa_virgula_decimal():
    assert formatar(3.25) == "3,25"
    assert formatar(7) == "7"
    assert formatar("") == ""


def test_gravador_escreve_csv(tmp_path):
    gravador = GravadorVoltas(tmp_path)
    for q in [quadro(0, 0, 0, 50.0), quadro(100, 1, 100, 47.0), quadro(300, 2, 300, 44.0), quadro(302, 2, 300, 44.0)]:
        gravador.atualizar(q)
    [arquivo] = tmp_path.glob("*.csv")
    assert arquivo.name.endswith("_Le-Mans_Corrida.csv")
    texto = arquivo.read_text(encoding="utf-8-sig")
    linhas = list(csv.reader(texto.splitlines(), delimiter=";"))
    assert tuple(linhas[0]) == COLUNAS
    assert len(linhas) == 2
    assert linhas[1][COLUNAS.index("combustivel_gasto")] == "3,0"


def test_nome_arquivo_limpa_pista():
    from datetime import datetime

    e = quadro(0, 0, 0, 50.0)
    e.sessao.pista = "Circuit de la Sarthe / 24h"
    assert nome_arquivo(e, datetime(2026, 11, 9, 15, 30)) == "2026-11-09_1530_Circuit-de-la-Sarthe-24h_Corrida.csv"
