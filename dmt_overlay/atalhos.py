from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication, QObject, Signal

log = logging.getLogger(__name__)

# Na ordem em que aparecem no texto: Ctrl+Shift+Alt+Win.
MODIFICADORES = {"ctrl": 0x0002, "shift": 0x0004, "alt": 0x0001, "win": 0x0008}
NOMES_MODIFICADORES = {"ctrl": "Ctrl", "shift": "Shift", "alt": "Alt", "win": "Win"}
MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
TECLAS_ESPECIAIS = {
    "insert": (0x2D, "Insert"), "delete": (0x2E, "Delete"), "home": (0x24, "Home"), "end": (0x23, "End"),
    "pgup": (0x21, "PgUp"), "pgdown": (0x22, "PgDown"), "pause": (0x13, "Pause"), "space": (0x20, "Space"),
}
# Nomes que o QKeySequence usa.
TECLAS_ESPECIAIS |= {"ins": TECLAS_ESPECIAIS["insert"], "del": TECLAS_ESPECIAIS["delete"]}
MODIFICADORES_ALIAS = {"meta": "win", "control": "ctrl"}


def interpretar(sequencia: str) -> tuple[int, int, str] | None:
    """Converte "Ctrl+Shift+H" em (modificadores, código virtual, texto normalizado)."""
    partes = [p.strip().lower() for p in sequencia.split("+") if p.strip()]
    if len(partes) < 2:
        return None
    *mods, tecla = partes
    mods = [MODIFICADORES_ALIAS.get(m, m) for m in mods]
    if any(m not in MODIFICADORES for m in mods) or len(set(mods)) != len(mods):
        return None
    if len(tecla) == 1 and tecla.isascii() and tecla.isalnum():
        codigo, nome = ord(tecla.upper()), tecla.upper()
    elif tecla[0] == "f" and tecla[1:].isdigit() and 1 <= int(tecla[1:]) <= 24:
        codigo, nome = 0x70 + int(tecla[1:]) - 1, tecla.upper()
    elif tecla in TECLAS_ESPECIAIS:
        codigo, nome = TECLAS_ESPECIAIS[tecla]
    else:
        return None
    ordem = [m for m in MODIFICADORES if m in mods]
    valor = sum(MODIFICADORES[m] for m in ordem)
    texto = "+".join([NOMES_MODIFICADORES[m] for m in ordem] + [nome])
    return valor, codigo, texto


class _FiltroWindows(QAbstractNativeEventFilter):
    def __init__(self, callback) -> None:
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, tipo, mensagem):
        # WM_HOTKEY sem janela chega como mensagem da thread, só pelo dispatcher.
        if bytes(tipo) != b"windows_dispatcher_MSG":
            return False, 0
        from ctypes import wintypes

        msg = wintypes.MSG.from_address(int(mensagem))
        if msg.message == WM_HOTKEY:
            self._callback(int(msg.wParam))
            return True, 0
        return False, 0


class AtalhosGlobais(QObject):
    """Atalhos que funcionam com o jogo em foco. Só no Windows; em outros sistemas não registra nada."""

    acionado = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._ids: dict[int, str] = {}
        self.registrados: dict[str, str] = {}
        self._filtro: _FiltroWindows | None = None
        self.suportado = sys.platform == "win32"
        if self.suportado:
            self._filtro = _FiltroWindows(self._recebido)
            QCoreApplication.instance().installNativeEventFilter(self._filtro)

    def registrar(self, nome: str, sequencia: str) -> bool:
        interpretado = interpretar(sequencia)
        if interpretado is None:
            log.warning("atalho inválido para %s: %r", nome, sequencia)
            return False
        mods, codigo, texto = interpretado
        if self._filtro is None:
            return False
        import ctypes

        identificador = len(self._ids) + 1
        if not ctypes.windll.user32.RegisterHotKey(None, identificador, mods | MOD_NOREPEAT, codigo):
            log.warning("atalho %s já está em uso por outro programa", texto)
            return False
        self._ids[identificador] = nome
        self.registrados[nome] = texto
        return True

    def liberar(self) -> None:
        if self._filtro is not None:
            import ctypes

            for identificador in self._ids:
                ctypes.windll.user32.UnregisterHotKey(None, identificador)
        self._ids.clear()
        self.registrados.clear()

    def _recebido(self, identificador: int) -> None:
        nome = self._ids.get(identificador)
        if nome:
            self.acionado.emit(nome)
