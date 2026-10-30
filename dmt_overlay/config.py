from __future__ import annotations

import copy
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

PADRAO_GERAL: dict[str, Any] = {
    "fonte_dados": "lmu",
    "taxa_atualizacao": 30,
    "travado": True,
    "ocultar_fora_da_pista": True,
    "escala": 1.0,
    "opacidade": 1.0,
    "verificar_atualizacoes": True,
}


def pasta_config() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
        return base / "DMT Overlay"
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "dmt-overlay"


def mesclar(padrao: dict, atual: dict) -> dict:
    resultado = copy.deepcopy(padrao)
    for chave, valor in atual.items():
        if isinstance(valor, dict) and isinstance(resultado.get(chave), dict):
            resultado[chave] = mesclar(resultado[chave], valor)
        else:
            resultado[chave] = valor
    return resultado


class Config:
    def __init__(self, caminho: Path | None = None) -> None:
        self.caminho = caminho or pasta_config() / "config.json"
        self.geral: dict[str, Any] = copy.deepcopy(PADRAO_GERAL)
        self.widgets: dict[str, dict[str, Any]] = {}
        self.carregar()

    def carregar(self) -> None:
        if not self.caminho.exists():
            return
        try:
            dados = json.loads(self.caminho.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            log.warning("config inválida, usando padrão: %s", erro)
            backup = self.caminho.with_suffix(".json.bak")
            try:
                self.caminho.replace(backup)
            except OSError:
                pass
            return
        self.geral = mesclar(PADRAO_GERAL, dados.get("geral", {}))
        self.widgets = dados.get("widgets", {})

    def salvar(self) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_suffix(".tmp")
        conteudo = json.dumps({"geral": self.geral, "widgets": self.widgets}, indent=2, ensure_ascii=False)
        temporario.write_text(conteudo, encoding="utf-8")
        temporario.replace(self.caminho)

    def widget(self, nome: str, padrao: dict[str, Any]) -> dict[str, Any]:
        self.widgets[nome] = mesclar(padrao, self.widgets.get(nome, {}))
        return self.widgets[nome]
