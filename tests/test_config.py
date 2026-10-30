import json

from dmt_overlay.config import Config, mesclar


def test_mesclar_preserva_padroes_novos():
    assert mesclar({"a": 1, "b": {"c": 2, "d": 3}}, {"b": {"c": 9}}) == {"a": 1, "b": {"c": 9, "d": 3}}


def test_salvar_e_carregar(tmp_path):
    caminho = tmp_path / "config.json"
    config = Config(caminho)
    config.widget("relativo", {"ativo": True, "x": 1, "y": 2})["x"] = 50
    config.geral["escala"] = 1.25
    config.salvar()
    nova = Config(caminho)
    assert nova.geral["escala"] == 1.25
    assert nova.widget("relativo", {"ativo": True, "x": 1, "y": 2, "novo": 7}) == {"ativo": True, "x": 50, "y": 2, "novo": 7}


def test_config_corrompida_vira_backup(tmp_path):
    caminho = tmp_path / "config.json"
    caminho.write_text("{ quebrado", encoding="utf-8")
    config = Config(caminho)
    assert config.geral["travado"] is True
    assert (tmp_path / "config.json.bak").exists()
    json.dumps(config.geral)
