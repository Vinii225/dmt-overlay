from __future__ import annotations

import csv
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .calculos.formatacao import tempo_volta
from .telemetria.modelos import NOMES_SESSAO, Carro, Estado

log = logging.getLogger(__name__)

RODAS = ("de", "dd", "te", "td")
# Posição e voltas vêm do scoring, que atualiza depois da telemetria: espera um pouco (segundos de jogo) antes de fechar a linha.
ESPERA_SCORING = 1.0

COLUNAS = (
    "data_hora", "pista", "sessao", "stint", "volta", "volta_no_stint", "tempo", "tempo_s", "valida", "box", "posicao",
    "combustivel_gasto", "combustivel_fim", "energia_gasta", "energia_fim",
    *(f"temp_{r}" for r in RODAS), *(f"pressao_{r}" for r in RODAS),
    *(f"desgaste_{r}" for r in RODAS), *(f"pneu_{r}" for r in RODAS),
    "composto", "temp_pista", "temp_ar", "chuva",
)


@dataclass(slots=True)
class _Volta:
    inicio: float
    combustivel: float
    energia: float
    pneus: tuple[float, ...]
    parcial: bool = False
    invalida: bool = False
    box: bool = False
    servico: bool = False
    temps: list[float] = field(default_factory=lambda: [0.0] * 4)
    amostras: int = 0


@dataclass(slots=True)
class _Fechada:
    volta: _Volta
    fim: Estado
    tempo: float
    stint: int
    volta_no_stint: int
    prazo: float


class RegistroVoltas:
    """Acompanha a telemetria e devolve uma linha por volta completada."""

    def __init__(self) -> None:
        self.reiniciar()

    def reiniciar(self) -> None:
        self._numero = -1
        self._volta: _Volta | None = None
        self._fechada: _Fechada | None = None
        self._ultimo_combustivel = 0.0
        self._ultimos_pneus: tuple[float, ...] = ()
        self.stint = 0
        self._voltas_stint = 0

    def atualizar(self, estado: Estado) -> list[dict[str, Any]]:
        j = estado.jogador
        carro = estado.carro_jogador
        if carro is None:
            return []
        linhas = []
        agora = estado.sessao.tempo_decorrido
        pneus = tuple(p.restante for p in j.pneus)
        # Stint novo só quando há serviço (abastecer ou trocar pneu); passar pelo box sem parar não conta.
        trocou_pneu = any(a > b + 0.02 for a, b in zip(pneus, self._ultimos_pneus, strict=False))
        servico = bool(self._ultimos_pneus) and (j.combustivel > self._ultimo_combustivel + 0.3 or trocou_pneu)
        self._ultimo_combustivel = j.combustivel
        self._ultimos_pneus = pneus
        if self.stint == 0 or servico:
            self.stint += 1
            self._voltas_stint = 0

        if self._fechada is not None and agora >= self._fechada.prazo:
            linhas.append(self._linha(self._fechada, carro))
            self._fechada = None

        if j.volta != self._numero:
            anterior = self._volta
            if anterior is not None and not anterior.parcial and j.volta == self._numero + 1:
                self._voltas_stint += 1
                tempo = j.inicio_volta - anterior.inicio
                self._fechada = _Fechada(anterior, estado, tempo, self.stint, self._voltas_stint, agora + ESPERA_SCORING)
            self._volta = _Volta(j.inicio_volta, j.combustivel, j.energia_virtual, pneus, parcial=anterior is None)
            self._numero = j.volta

        v = self._volta
        v.invalida |= j.volta_invalidada
        v.box |= carro.nos_boxes
        v.servico |= servico
        for i, pneu in enumerate(j.pneus):
            v.temps[i] += sum(pneu.temp_superficie) / 3
        v.amostras += 1
        return linhas

    @staticmethod
    def _linha(f: _Fechada, carro: Carro) -> dict[str, Any]:
        v, j, s = f.volta, f.fim.jogador, f.fim.sessao
        tempo_ok = 0 < f.tempo < 3600
        usa_energia = j.energia_virtual > 0 or v.energia > 0
        linha: dict[str, Any] = {
            "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pista": s.pista,
            "sessao": NOMES_SESSAO.get(s.tipo, ""),
            "stint": f.stint,
            "volta": carro.voltas,
            "volta_no_stint": f.volta_no_stint,
            "tempo": tempo_volta(f.tempo) if tempo_ok else "",
            "tempo_s": round(f.tempo, 3) if tempo_ok else "",
            "valida": "sim" if tempo_ok and not v.invalida else "não",
            "box": "sim" if v.box else "",
            "posicao": carro.posicao,
            "combustivel_gasto": "" if v.servico else round(v.combustivel - j.combustivel, 2),
            "combustivel_fim": round(j.combustivel, 2),
            "energia_gasta": round((v.energia - j.energia_virtual) * 100, 1) if usa_energia and not v.servico else "",
            "energia_fim": round(j.energia_virtual * 100, 1) if usa_energia else "",
            "composto": j.composto_dianteiro if j.composto_dianteiro == j.composto_traseiro
            else f"{j.composto_dianteiro}/{j.composto_traseiro}",
            "temp_pista": round(s.temp_pista, 1),
            "temp_ar": round(s.temp_ar, 1),
            "chuva": round(s.chuva * 100),
        }
        for i, r in enumerate(RODAS):
            pneu = j.pneus[i]
            linha[f"temp_{r}"] = round(v.temps[i] / v.amostras, 1) if v.amostras else ""
            linha[f"pressao_{r}"] = round(pneu.pressao, 1)
            linha[f"desgaste_{r}"] = "" if v.servico else round((v.pneus[i] - pneu.restante) * 100, 2)
            linha[f"pneu_{r}"] = round(pneu.restante * 100, 1)
        return linha


def nome_arquivo(estado: Estado, quando: datetime) -> str:
    s = estado.sessao
    pista = re.sub(r"[^\w-]+", "-", s.pista, flags=re.UNICODE).strip("-") or "pista"
    return f"{quando:%Y-%m-%d_%H%M}_{pista}_{NOMES_SESSAO.get(s.tipo, 'sessao')}.csv"


def formatar(valor: Any) -> str:
    # Vírgula decimal: abre direto no Excel em português.
    if isinstance(valor, float):
        return f"{valor}".replace(".", ",")
    return str(valor)


class GravadorVoltas:
    """Grava as voltas da sessão em um CSV por sessão dentro de `pasta`."""

    def __init__(self, pasta: Path) -> None:
        self.pasta = pasta
        self._registro = RegistroVoltas()
        self._arquivo: Path | None = None

    def nova_sessao(self) -> None:
        self._registro.reiniciar()
        self._arquivo = None

    def atualizar(self, estado: Estado) -> None:
        linhas = self._registro.atualizar(estado)
        if not linhas:
            return
        try:
            if self._arquivo is None:
                self.pasta.mkdir(parents=True, exist_ok=True)
                self._arquivo = self.pasta / nome_arquivo(estado, datetime.now())
            novo = not self._arquivo.exists()
            with self._arquivo.open("a", encoding="utf-8-sig" if novo else "utf-8", newline="") as arquivo:
                escritor = csv.writer(arquivo, delimiter=";")
                if novo:
                    escritor.writerow(COLUNAS)
                for linha in linhas:
                    escritor.writerow(formatar(linha[c]) for c in COLUNAS)
        except OSError:
            log.exception("não foi possível gravar as voltas")
