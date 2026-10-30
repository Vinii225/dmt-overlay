from __future__ import annotations

import math
import random
import time

from .modelos import Carro, Estado, Jogador, Pneu, Posicao, Sessao, TipoSessao

TAMANHO_PISTA = 13626.0
VOLTA_BASE = 210.0
CLASSES = (("Hypercar", 0.0), ("LMP2", 9.0), ("GT3", 21.0))
PILOTOS = (
    "V. Ares", "L. Damata", "R. Siqueira", "M. Costa", "P. Almeida", "F. Rocha", "T. Nunes",
    "J. Moura", "A. Lima", "C. Prado", "E. Barros", "D. Teixeira", "G. Pires", "H. Campos",
    "I. Duarte", "K. Freitas", "N. Melo", "O. Vidal",
)


class FonteDemo:
    nome = "Demonstração"

    def __init__(self, semente: int = 7) -> None:
        aleatorio = random.Random(semente)
        self._inicio = time.monotonic()
        self._carros = []
        for i, piloto in enumerate(PILOTOS):
            classe, atraso = CLASSES[i % len(CLASSES)]
            ritmo = VOLTA_BASE + atraso + aleatorio.uniform(-1.5, 1.5)
            self._carros.append((i, piloto, classe, ritmo, aleatorio.uniform(0, ritmo)))
        self._combustivel_inicial = 95.0
        self._consumo = 3.1

    def abrir(self) -> bool:
        return True

    def fechar(self) -> None:
        pass

    def ler(self, intervalo_scoring: float = 0.1) -> Estado:
        t = time.monotonic() - self._inicio + 600
        progresso = []
        for id_, piloto, classe, ritmo, deslocamento in self._carros:
            voltas_float = (t + deslocamento) / ritmo
            progresso.append((voltas_float, id_, piloto, classe, ritmo))
        progresso.sort(reverse=True)
        lider = progresso[0][0]
        carros = []
        anterior = lider
        for pos, (vf, id_, piloto, classe, ritmo) in enumerate(progresso, start=1):
            carros.append(
                Carro(
                    id=id_,
                    piloto=piloto,
                    equipe=f"DMT Damata Racing #{id_ + 10}" if id_ < 2 else f"Equipe #{id_ + 10}",
                    classe=classe,
                    posicao=pos,
                    voltas=int(vf),
                    distancia_volta=(vf % 1) * TAMANHO_PISTA,
                    melhor_volta=ritmo - 0.8,
                    ultima_volta=ritmo + math.sin(t / 50 + id_) * 0.6,
                    tempo_lider=(lider - vf) * ritmo,
                    voltas_lider=int(lider - vf),
                    tempo_frente=(anterior - vf) * ritmo,
                    voltas_frente=int(anterior - vf),
                    nos_boxes=False,
                    paradas=int(vf // 12),
                    jogador=id_ == 0,
                    tempo_estimado=ritmo,
                )
            )
            anterior = vf
        jogador_vf, _, _, _, ritmo_jogador = next(c for c in progresso if c[1] == 0)
        fase = (jogador_vf % 1) * 2 * math.pi * 9
        acelerador = max(0.0, min(1.0, 0.6 + 0.6 * math.sin(fase)))
        freio = max(0.0, min(1.0, -0.9 * math.sin(fase) - 0.2))
        rpm = 5200 + 3000 * acelerador
        voltas_jogador = int(jogador_vf)
        combustivel = max(2.0, self._combustivel_inicial - (jogador_vf % 28) * self._consumo)

        def pneu(base: float, i: int) -> Pneu:
            return Pneu(
                temp_superficie=(base + 4 + i, base + 2 * math.sin(t / 3), base - 3 + i),
                temp_carcaca=base + 6,
                temp_ideal=85.0,
                pressao=178.0 + i * 2 + math.sin(t / 10),
                restante=max(0.0, 1.0 - (jogador_vf % 28) * 0.025 - i * 0.01),
                temp_freio=420 + 250 * freio + i * 15,
            )

        jogador = Jogador(
            id=0,
            marcha=max(1, min(7, int(1 + acelerador * 6))),
            marchas=7,
            rpm=rpm,
            rpm_max=8500,
            velocidade=40 + 40 * acelerador,
            acelerador=acelerador,
            freio=freio,
            volante=0.4 * math.sin(fase * 0.7),
            combustivel=combustivel,
            tanque=100.0,
            energia_virtual=combustivel / 100,
            bateria=0.5 + 0.4 * math.sin(t / 7),
            delta_melhor=0.9 * math.sin(t / 15),
            volta=voltas_jogador,
            inicio_volta=t - (jogador_vf % 1) * ritmo_jogador,
            track_limits=min(3.5, int(jogador_vf / 4) * 0.5),
            tc=4, tc_max=11, tc_corte=3, tc_slip=5, abs=6, abs_max=12, mapa_motor=2,
            balanco_freio=0.534,
            temp_agua=88.0,
            temp_oleo=104.0,
            composto_dianteiro="Medium",
            composto_traseiro="Medium",
            tc_ativo=acelerador > 0.95,
            abs_ativo=freio > 0.8,
            pneus=tuple(pneu(84 + 2 * i, i) for i in range(4)),
        )
        sessao = Sessao(
            tipo=TipoSessao.CORRIDA,
            pista="Circuit de la Sarthe",
            tamanho_pista=TAMANHO_PISTA,
            tempo_decorrido=t,
            tempo_final=6 * 3600,
            voltas_max=2147483647,
            fase=5,
            temp_ar=24.0,
            temp_pista=35.0,
            hora_do_dia=15 * 3600 + t,
            track_limits_punicao=4.0,
        )
        identidade = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        posicoes = {
            c.id: Posicao(2.4 * math.sin(c.id * 1.7 + t / 9), 0.0, -c.distancia_volta, identidade) for c in carros
        }
        return Estado(conectado=True, pilotando=True, sessao=sessao, jogador=jogador, carros=carros, posicoes=posicoes)
