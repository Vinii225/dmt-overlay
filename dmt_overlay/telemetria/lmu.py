from __future__ import annotations

import ctypes
import logging
import math
import mmap
import struct
import sys
import time

from ..terceiros.pylmu import lmu_data as ld
from .modelos import Carro, Estado, Jogador, Pneu, Sessao, TipoSessao

log = logging.getLogger(__name__)

NOME_MEMORIA = ld.LMUConstants.LMU_SHARED_MEMORY_FILE
KELVIN = 273.15
TIMEOUT_DADOS = 2.0

_TAMANHO = ctypes.sizeof(ld.LMUObjectOut)
_OFF_GENERICO = ld.LMUObjectOut.generic.offset
_OFF_VERSAO = _OFF_GENERICO + ld.LMUGeneric.gameVersion.offset
_OFF_SCORING = ld.LMUObjectOut.scoring.offset
_OFF_INFO = _OFF_SCORING + ld.LMUScoringData.scoringInfo.offset
_OFF_VEICULOS = _OFF_SCORING + ld.LMUScoringData.vehScoringInfo.offset
_TAM_VEICULO = ctypes.sizeof(ld.LMUVehicleScoring)
_OFF_TELEMETRIA = ld.LMUObjectOut.telemetry.offset
_OFF_ATIVOS = _OFF_TELEMETRIA + ld.LMUTelemetryData.activeVehicles.offset
_OFF_IDX_JOGADOR = _OFF_TELEMETRIA + ld.LMUTelemetryData.playerVehicleIdx.offset
_OFF_TEM_VEICULO = _OFF_TELEMETRIA + ld.LMUTelemetryData.playerHasVehicle.offset
_OFF_TELE = _OFF_TELEMETRIA + ld.LMUTelemetryData.telemInfo.offset
_TAM_TELE = ctypes.sizeof(ld.LMUVehicleTelemetry)
_OFF_TELE_ID = ld.LMUVehicleTelemetry.mID.offset
_MAX_VEICULOS = ld.LMUConstants.MAX_MAPPED_VEHICLES


def texto(valor: bytes) -> str:
    try:
        return valor.decode("utf-8").strip()
    except UnicodeDecodeError:
        return valor.decode("cp1252", "replace").strip()


def numero(valor: float) -> float:
    if math.isnan(valor) or math.isinf(valor):
        return 0.0
    return valor


def tipo_sessao(codigo: int) -> TipoSessao:
    if codigo >= 10:
        return TipoSessao.CORRIDA
    if codigo == 9:
        return TipoSessao.WARMUP
    if codigo >= 5:
        return TipoSessao.CLASSIFICACAO
    if codigo >= 1:
        return TipoSessao.TREINO
    return TipoSessao.TESTE


def abrir_memoria() -> mmap.mmap:
    if sys.platform == "win32":
        return mmap.mmap(-1, _TAMANHO, NOME_MEMORIA)
    with open(f"/dev/shm/{NOME_MEMORIA}", "rb") as arquivo:
        return mmap.mmap(arquivo.fileno(), _TAMANHO, access=mmap.ACCESS_READ)


class FonteLMU:
    nome = "Le Mans Ultimate"

    def __init__(self) -> None:
        self._memoria: mmap.mmap | None = None
        self._ultimo_et = -1.0
        self._ultima_mudanca = 0.0
        self._carros: list[Carro] = []
        self._sessao = Sessao()
        self._id_jogador = -1
        self._ultimo_scoring = 0.0
        self._em_tempo_real = False

    def abrir(self) -> bool:
        if self._memoria is not None:
            return True
        try:
            self._memoria = abrir_memoria()
            log.info("memória compartilhada %s aberta (%d bytes)", NOME_MEMORIA, _TAMANHO)
            return True
        except (OSError, ValueError) as erro:
            log.debug("memória compartilhada indisponível: %s", erro)
            self._memoria = None
            return False

    def fechar(self) -> None:
        if self._memoria is not None:
            self._memoria.close()
            self._memoria = None

    def ler(self, intervalo_scoring: float = 0.1) -> Estado:
        if not self.abrir():
            return Estado()
        mem = self._memoria
        versao = struct.unpack_from("<i", mem, _OFF_VERSAO)[0]
        if versao <= 0:
            return Estado()

        agora = time.monotonic()
        if agora - self._ultimo_scoring >= intervalo_scoring:
            self._ultimo_scoring = agora
            self._ler_scoring(mem)

        info_et = self._sessao.tempo_decorrido
        if info_et != self._ultimo_et:
            self._ultimo_et = info_et
            self._ultima_mudanca = agora
        ativo = agora - self._ultima_mudanca < TIMEOUT_DADOS

        tem_veiculo = bool(mem[_OFF_TEM_VEICULO])
        jogador = self._ler_jogador(mem) if tem_veiculo else Jogador()
        return Estado(
            conectado=ativo,
            pilotando=ativo and self._em_tempo_real and tem_veiculo,
            sessao=self._sessao,
            jogador=jogador,
            carros=self._carros,
        )

    def _ler_scoring(self, mem: mmap.mmap) -> None:
        info = ld.LMUScoringInfo.from_buffer_copy(mem, _OFF_INFO)
        self._em_tempo_real = bool(info.mInRealtime)
        self._sessao = Sessao(
            tipo=tipo_sessao(info.mSession),
            pista=texto(info.mTrackName),
            tamanho_pista=numero(info.mLapDist),
            tempo_decorrido=numero(info.mCurrentET),
            tempo_final=numero(info.mEndET),
            voltas_max=info.mMaxLaps,
            fase=info.mGamePhase,
            temp_ar=numero(info.mAmbientTemp),
            temp_pista=numero(info.mTrackTemp),
            chuva=numero(info.mRaining),
            umidade_pista=numero(info.mAvgPathWetness),
            hora_do_dia=numero(info.mTimeOfDay),
            bandeira_amarela=info.mYellowFlagState not in (b"\x00", 0, b"\xff", -1),
        )
        total = max(0, min(info.mNumVehicles, _MAX_VEICULOS))
        carros = []
        for i in range(total):
            v = ld.LMUVehicleScoring.from_buffer_copy(mem, _OFF_VEICULOS + i * _TAM_VEICULO)
            if v.mIsPlayer:
                self._id_jogador = v.mID
            carros.append(
                Carro(
                    id=v.mID,
                    piloto=texto(v.mDriverName),
                    equipe=texto(v.mVehicleName),
                    classe=texto(v.mVehicleClass),
                    posicao=v.mPlace,
                    voltas=v.mTotalLaps,
                    distancia_volta=numero(v.mLapDist),
                    melhor_volta=numero(v.mBestLapTime),
                    ultima_volta=numero(v.mLastLapTime),
                    tempo_lider=numero(v.mTimeBehindLeader),
                    voltas_lider=v.mLapsBehindLeader,
                    tempo_frente=numero(v.mTimeBehindNext),
                    voltas_frente=v.mLapsBehindNext,
                    nos_boxes=bool(v.mInPits),
                    paradas=v.mNumPitstops,
                    jogador=bool(v.mIsPlayer),
                    tempo_estimado=numero(v.mEstimatedLapTime),
                    finalizado=v.mFinishStatus,
                )
            )
        carros.sort(key=lambda c: c.posicao)
        self._carros = carros

    def _indice_telemetria(self, mem: mmap.mmap) -> int:
        ativos = min(mem[_OFF_ATIVOS], _MAX_VEICULOS)
        indice = mem[_OFF_IDX_JOGADOR]
        if indice < ativos and self._id_tele(mem, indice) == self._id_jogador:
            return indice
        for i in range(ativos):
            if self._id_tele(mem, i) == self._id_jogador:
                return i
        return indice if indice < ativos else -1

    @staticmethod
    def _id_tele(mem: mmap.mmap, indice: int) -> int:
        return struct.unpack_from("<i", mem, _OFF_TELE + indice * _TAM_TELE + _OFF_TELE_ID)[0]

    def _ler_jogador(self, mem: mmap.mmap) -> Jogador:
        indice = self._indice_telemetria(mem)
        if indice < 0:
            return Jogador()
        t = ld.LMUVehicleTelemetry.from_buffer_copy(mem, _OFF_TELE + indice * _TAM_TELE)
        vel = t.mLocalVel
        pneus = tuple(
            Pneu(
                temp_superficie=tuple(numero(x) - KELVIN for x in r.mTemperature),
                temp_carcaca=numero(r.mTireCarcassTemperature) - KELVIN,
                temp_ideal=numero(r.mOptimalTemp),
                pressao=numero(r.mPressure),
                restante=numero(r.mWear),
                temp_freio=numero(r.mBrakeTemp) - KELVIN,
                furado=bool(r.mFlat),
            )
            for r in t.mWheels
        )
        return Jogador(
            id=t.mID,
            marcha=t.mGear,
            marchas=t.mMaxGears,
            rpm=numero(t.mEngineRPM),
            rpm_max=numero(t.mEngineMaxRPM),
            velocidade=math.hypot(numero(vel.x), numero(vel.y), numero(vel.z)),
            acelerador=numero(t.mUnfilteredThrottle),
            freio=numero(t.mUnfilteredBrake),
            embreagem=numero(t.mUnfilteredClutch),
            volante=numero(t.mUnfilteredSteering),
            combustivel=numero(t.mFuel),
            tanque=numero(t.mFuelCapacity),
            energia_virtual=numero(t.mVirtualEnergy),
            bateria=numero(t.mBatteryChargeFraction),
            delta_melhor=numero(t.mDeltaBest),
            volta=t.mLapNumber,
            inicio_volta=numero(t.mLapStartET),
            volta_invalidada=bool(t.mLapInvalidated),
            limitador=bool(t.mSpeedLimiterActive),
            abs_ativo=bool(t.mABSActive),
            tc_ativo=bool(t.mTCActive),
            tc=t.mTC,
            tc_max=t.mTCMax,
            tc_corte=t.mTCCut,
            tc_slip=t.mTCSlip,
            abs=t.mABS,
            abs_max=t.mABSMax,
            mapa_motor=t.mMotorMap,
            balanco_freio=1.0 - numero(t.mRearBrakeBias),
            temp_agua=numero(t.mEngineWaterTemp),
            temp_oleo=numero(t.mEngineOilTemp),
            composto_dianteiro=texto(t.mFrontTireCompoundName),
            composto_traseiro=texto(t.mRearTireCompoundName),
            pneus=pneus,
        )
