from __future__ import annotations

import json
import logging
import re
import threading
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, Signal

from . import __version__

log = logging.getLogger(__name__)

URL_RELEASES = "https://api.github.com/repos/Vinii225/dmt-overlay/releases/latest"


def versao_tupla(texto: str) -> tuple[int, ...]:
    achado = re.match(r"v?(\d+)\.(\d+)\.(\d+)(-)?", texto.strip())
    if not achado:
        return (0, 0, 0, 0)
    final = 0 if achado.group(4) else 1
    return (*(int(x) for x in achado.groups()[:3]), final)


def mais_nova(remota: str, local: str = __version__) -> bool:
    return versao_tupla(remota) > versao_tupla(local)


class VerificadorAtualizacao(QObject):
    encontrada = Signal(str, str)

    def verificar(self) -> None:
        threading.Thread(target=self._buscar, name="atualizacao", daemon=True).start()

    def _buscar(self) -> None:
        requisicao = Request(
            URL_RELEASES,
            headers={"Accept": "application/vnd.github+json", "User-Agent": f"dmt-overlay/{__version__}"},
        )
        try:
            with urlopen(requisicao, timeout=5) as resposta:
                dados = json.load(resposta)
        except (OSError, ValueError) as erro:
            log.info("não foi possível verificar atualizações: %s", erro)
            return
        tag = dados.get("tag_name", "")
        if mais_nova(tag):
            log.info("nova versão disponível: %s", tag)
            self.encontrada.emit(tag, dados.get("html_url", ""))
