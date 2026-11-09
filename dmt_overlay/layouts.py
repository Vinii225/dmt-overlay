from __future__ import annotations

from typing import Any

from . import tema

# O que muda de uma classe para outra; as opções de cada widget continuam globais.
CHAVES_LAYOUT = ("ativo", "x", "y")


def chave_classe(nome: str) -> str:
    """Normaliza o nome da classe do jogo ("LMGT3", "GT3 Pro"...) para a mesma chave."""
    return tema.classe(nome)[0] if nome.strip() else ""


def capturar(widgets: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {nome: {c: config[c] for c in CHAVES_LAYOUT} for nome, config in widgets.items()}


def aplicar(layout: dict[str, dict[str, Any]], widgets: dict[str, dict[str, Any]]) -> None:
    for nome, salvo in layout.items():
        if nome in widgets:
            widgets[nome].update({c: salvo[c] for c in CHAVES_LAYOUT if c in salvo})
