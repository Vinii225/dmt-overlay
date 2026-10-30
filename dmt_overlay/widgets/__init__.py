from .classificacao import Classificacao
from .combustivel import Combustivel
from .delta import Delta
from .eletronica import Eletronica
from .motor import Motor
from .multiclasse import Multiclasse
from .pedais import Pedais
from .pneus import Pneus
from .radar import Radar
from .relativo import Relativo
from .sessao import Sessao
from .stint import Stint
from .track_limits import TrackLimits

WIDGETS = (
    Relativo,
    Classificacao,
    Delta,
    Motor,
    Pedais,
    Combustivel,
    Pneus,
    Sessao,
    Eletronica,
    TrackLimits,
    Multiclasse,
    Stint,
    Radar,
)

__all__ = ["WIDGETS"]
