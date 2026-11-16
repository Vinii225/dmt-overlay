import json
from urllib.error import HTTPError
from urllib.request import urlopen

import pytest
from conftest import carro, estado

from dmt_overlay.hud import ServidorHUD, Voltas, montar_dados, sobrenome
from dmt_overlay.telemetria.modelos import Estado

OPCOES = {"linhas": 18, "classes": "todas", "briga": True, "gaps": True}


def corrida():
    return estado([
        carro(1, 1, 10, 0.0, classe="Hypercar", piloto="Brendon Hartley", equipe="Toyota #8", tempo_lider=0.0),
        carro(2, 2, 10, 0.0, classe="LMP2", tempo_lider=20.0),
        carro(3, 3, 10, 0.0, classe="Hypercar", tempo_lider=1.5, equipe="Ferrari AF Corse #50"),
        carro(4, 4, 10, 0.0, classe="Hypercar", jogador=True, tempo_lider=1.9, piloto="Vinícius Ares", equipe="DMT #10"),
    ], tempo_final=3600.0, tempo_decorrido=600.0, pista="Spa")


def test_sobrenome():
    assert sobrenome("Brendon Hartley") == "HARTLEY"
    assert sobrenome("") == ""


def test_desconectado_esconde_o_hud():
    assert montar_dados(Estado(), OPCOES)["ativo"] is False


def test_torre_por_classe_com_foco():
    dados = montar_dados(corrida(), OPCOES)
    assert dados["sessao"]["relogio"] == "50:00"
    hy, p2 = dados["classes"]
    assert hy["nome"] == "HYPERCAR" and p2["nome"] == "LMP2"
    assert [c["pos"] for c in hy["carros"]] == [1, 2, 3]
    assert hy["carros"][0]["piloto"] == "HARTLEY" and hy["carros"][0]["gap"] == "LÍDER"
    assert hy["carros"][0]["numero"] == "8" and hy["carros"][0]["equipe"] == "Toyota"
    assert hy["carros"][2]["foco"]


def test_so_classe_do_foco():
    dados = montar_dados(corrida(), {**OPCOES, "classes": "foco"})
    assert [c["nome"] for c in dados["classes"]] == ["HYPERCAR"]


def test_briga_com_carro_da_frente_na_classe():
    voltas = Voltas()
    e = corrida()
    for volta, (frente, foco) in enumerate([(100.0, 100.5), (101.0, 100.2)], start=9):
        for c in e.carros:
            c.voltas = volta
            c.ultima_volta = {3: frente, 4: foco}.get(c.id, 0.0)
        voltas.atualizar(e.carros)
    briga = montar_dados(e, OPCOES, voltas)["briga"]
    assert briga["frente"]["id"] == 3 and briga["foco"]["id"] == 4
    assert briga["gap"] == "0.400"
    assert [v["volta"] for v in briga["voltas"]] == [10, 9]
    assert briga["voltas"][0]["dif"] == "-0.800"


def test_lider_da_classe_nao_tem_briga():
    e = corrida()
    for c in e.carros:
        c.jogador = c.id == 1
    assert montar_dados(e, OPCOES)["briga"] is None


def test_servidor_serve_pagina_dados_e_fontes():
    hud = ServidorHUD()
    assert hud.iniciar(0, False)
    base = f"http://127.0.0.1:{hud.porta}"
    try:
        assert b"HUD" in urlopen(base + "/").read()
        hud.atualizar(corrida(), OPCOES)
        assert json.loads(urlopen(base + "/dados").read())["ativo"] is True
        assert urlopen(base + "/fontes/BarlowCondensed-Medium.ttf").status == 200
        for caminho in ("/fontes/../hud.py", "/nada"):
            with pytest.raises(HTTPError):
                urlopen(base + caminho)
    finally:
        hud.parar()
    assert not hud.rodando


def test_porta_ocupada_vira_erro_legivel():
    primeiro = ServidorHUD()
    assert primeiro.iniciar(0, False)
    segundo = ServidorHUD()
    try:
        assert not segundo.iniciar(primeiro.porta, False)
        assert "indisponível" in segundo.erro
    finally:
        primeiro.parar()
