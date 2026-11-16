"""HUD para quem transmite: servidor local que o OBS abre como "Fonte de navegador"."""

from __future__ import annotations

import json
import logging
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from . import tema
from .calculos.formatacao import duracao, intervalo, numero_carro, tempo_volta
from .telemetria.modelos import NOMES_SESSAO, Carro, Estado

log = logging.getLogger(__name__)

PASTA = Path(__file__).parent / "recursos"
PAGINA = PASTA / "hud" / "index.html"
TIPOS = {".html": "text/html; charset=utf-8", ".ttf": "font/ttf", ".json": "application/json"}
# O jogo atualiza a 30-60 Hz; para a página, 10 Hz sobra.
INTERVALO_DADOS = 0.1


def sobrenome(nome: str) -> str:
    partes = nome.split()
    return partes[-1].upper() if partes else ""


def _carro(c: Carro, lider: Carro, foco_id: int) -> dict[str, Any]:
    if c is lider:
        gap = "LÍDER"
    else:
        gap = intervalo(c.tempo_lider - lider.tempo_lider, c.voltas_lider - lider.voltas_lider)
    return {
        "id": c.id,
        "numero": numero_carro(c.equipe),
        "piloto": sobrenome(c.piloto),
        "nome": c.piloto,
        "equipe": c.equipe.split("#")[0].strip(),
        "gap": gap,
        "ultima": tempo_volta(c.ultima_volta) if c.ultima_volta > 0 else "",
        "box": c.nos_boxes,
        "foco": c.id == foco_id,
    }


class Voltas:
    """Guarda as últimas voltas de cada carro (o jogo só informa a última)."""

    def __init__(self, guardar: int = 2) -> None:
        self.guardar = guardar
        self._voltas: dict[int, list[tuple[int, float]]] = {}

    def atualizar(self, carros: list[Carro]) -> None:
        for c in carros:
            lista = self._voltas.setdefault(c.id, [])
            if lista and c.voltas < lista[-1][0]:
                lista.clear()  # sessão nova
            if c.ultima_volta > 0 and (not lista or lista[-1][0] != c.voltas):
                lista.append((c.voltas, c.ultima_volta))
                del lista[: -self.guardar]

    def de(self, id_: int) -> list[tuple[int, float]]:
        return self._voltas.get(id_, [])

    def limpar(self) -> None:
        self._voltas.clear()


def montar_dados(estado: Estado, opcoes: dict[str, Any], voltas: Voltas | None = None) -> dict[str, Any]:
    if not estado.conectado or not estado.carros:
        return {"ativo": False, "opcoes": opcoes}
    s = estado.sessao
    foco = estado.carro_jogador or estado.carros[0]
    if s.por_voltas:
        relogio = f"VOLTA {min(foco.voltas + 1, s.voltas_max)}/{s.voltas_max}"
    else:
        relogio = duracao(s.tempo_restante) if s.tempo_final > 0 else duracao(s.tempo_decorrido)

    por_classe: dict[str, list[Carro]] = {}
    for c in sorted(estado.carros, key=lambda c: c.posicao):
        por_classe.setdefault(c.classe, []).append(c)
    if opcoes.get("classes") == "foco":
        por_classe = {foco.classe: por_classe.get(foco.classe, [foco])}
    classes = []
    for nome, carros in por_classe.items():
        sigla, cor = tema.classe(nome)
        lider = carros[0]
        linhas = [dict(_carro(c, lider, foco.id), pos=i + 1) for i, c in enumerate(carros)]
        classes.append({"nome": nome.upper(), "sigla": sigla, "cor": cor.name(), "carros": linhas})

    dados: dict[str, Any] = {
        "ativo": True,
        "opcoes": opcoes,
        "sessao": {
            "tipo": NOMES_SESSAO.get(s.tipo, "").upper(),
            "pista": s.pista.upper(),
            "relogio": relogio,
            "amarela": s.bandeira_amarela,
        },
        "classes": classes,
        "briga": None,
    }
    mesma_classe = por_classe.get(foco.classe) or [c for c in estado.carros if c.classe == foco.classe]
    indice = next((i for i, c in enumerate(mesma_classe) if c.id == foco.id), 0)
    if indice > 0:
        frente = mesma_classe[indice - 1]
        lider = mesma_classe[0]
        gap = (foco.tempo_lider - lider.tempo_lider) - (frente.tempo_lider - lider.tempo_lider)
        historico = []
        if voltas is not None:
            meus, deles = voltas.de(foco.id), dict(voltas.de(frente.id))
            for volta, tempo in reversed(meus):
                if volta in deles:
                    historico.append({"volta": volta, "frente": tempo_volta(deles[volta]), "foco": tempo_volta(tempo),
                                      "dif": f"{tempo - deles[volta]:+.3f}"})
        dados["briga"] = {
            "frente": dict(_carro(frente, lider, foco.id), pos=indice),
            "foco": dict(_carro(foco, lider, foco.id), pos=indice + 1),
            "gap": f"{gap:.3f}" if gap > 0 and foco.voltas_lider == frente.voltas_lider else "",
            "cor": tema.classe(foco.classe)[1].name(),
            "voltas": historico,
        }
    return dados


def ip_local() -> str:
    """IP deste PC na rede local, para quem transmite de outro computador."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 80))  # não envia nada; só escolhe a interface de saída
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


class ServidorHUD:
    def __init__(self) -> None:
        self._servidor: ThreadingHTTPServer | None = None
        self._json = b'{"ativo": false}'
        self._ultimo = 0.0
        self._trava = threading.Lock()
        self.voltas = Voltas()
        self.porta = 0
        self.erro = ""

    @property
    def rodando(self) -> bool:
        return self._servidor is not None

    def iniciar(self, porta: int, rede: bool) -> bool:
        self.parar()
        hud = self

        class Pedido(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                caminho = self.path.split("?")[0]
                if caminho in ("/", "/index.html"):
                    self._enviar(PAGINA.read_bytes(), TIPOS[".html"])
                elif caminho == "/dados":
                    with hud._trava:
                        corpo = hud._json
                    self._enviar(corpo, TIPOS[".json"])
                elif caminho.startswith("/fontes/") and "/" not in caminho[8:] and caminho.endswith(".ttf"):
                    arquivo = PASTA / "fontes" / caminho[8:]
                    if arquivo.is_file():
                        self._enviar(arquivo.read_bytes(), TIPOS[".ttf"], cache=True)
                    else:
                        self.send_error(404)
                else:
                    self.send_error(404)

            def _enviar(self, corpo: bytes, tipo: str, cache: bool = False) -> None:
                self.send_response(200)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(corpo)))
                self.send_header("Cache-Control", "max-age=86400" if cache else "no-store")
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *_args) -> None:
                pass

        try:
            self._servidor = ThreadingHTTPServer(("0.0.0.0" if rede else "127.0.0.1", porta), Pedido)
        except OSError as erro:
            self.erro = f"Porta {porta} indisponível ({erro.strerror or erro})."
            log.warning("HUD: %s", self.erro)
            return False
        self._servidor.daemon_threads = True
        self.porta = self._servidor.server_address[1]
        self.erro = ""
        threading.Thread(target=self._servidor.serve_forever, name="hud", daemon=True).start()
        log.info("HUD de transmissão em http://%s:%d", "0.0.0.0" if rede else "127.0.0.1", porta)
        return True

    def parar(self) -> None:
        if self._servidor is not None:
            self._servidor.shutdown()
            self._servidor.server_close()
            self._servidor = None

    def atualizar(self, estado: Estado, opcoes: dict[str, Any]) -> None:
        agora = time.monotonic()
        if not self.rodando or agora - self._ultimo < INTERVALO_DADOS:
            return
        self._ultimo = agora
        self.voltas.atualizar(estado.carros)
        corpo = json.dumps(montar_dados(estado, opcoes, self.voltas), ensure_ascii=False).encode("utf-8")
        with self._trava:
            self._json = corpo
