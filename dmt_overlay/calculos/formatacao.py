from __future__ import annotations


def tempo_volta(segundos: float) -> str:
    if segundos <= 0 or segundos > 3600:
        return "-:--.---"
    minutos, resto = divmod(segundos, 60)
    return f"{int(minutos)}:{resto:06.3f}"


def duracao(segundos: float) -> str:
    segundos = max(0, int(segundos))
    horas, resto = divmod(segundos, 3600)
    minutos, seg = divmod(resto, 60)
    if horas:
        return f"{horas}:{minutos:02d}:{seg:02d}"
    return f"{minutos:02d}:{seg:02d}"


def diferenca(segundos: float, casas: int = 1) -> str:
    return f"{segundos:+.{casas}f}"


def intervalo(segundos: float, voltas: int) -> str:
    if voltas > 0:
        return f"+{voltas}V"
    if segundos <= 0:
        return "-"
    if segundos >= 60:
        minutos, resto = divmod(segundos, 60)
        return f"+{int(minutos)}:{resto:04.1f}"
    return f"+{segundos:.1f}"


def nome_curto(nome: str, limite: int = 16) -> str:
    partes = nome.split()
    if len(partes) >= 2 and len(nome) > limite:
        nome = f"{partes[0][0]}. {' '.join(partes[1:])}"
    return nome if len(nome) <= limite else nome[: limite - 1] + "…"


def numero_carro(equipe: str) -> str:
    if "#" not in equipe:
        return ""
    partes = equipe.rpartition("#")[2].split()
    return partes[0][:3] if partes else ""
