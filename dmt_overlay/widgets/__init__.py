from .classificacao import Classificacao
from .combustivel import Combustivel
from .delta import Delta
from .eletronica import Eletronica
from .motor import Motor
from .pedais import Pedais
from .pneus import Pneus
from .relativo import Relativo
from .sessao import Sessao

WIDGETS = (Relativo, Classificacao, Delta, Motor, Pedais, Combustivel, Pneus, Sessao, Eletronica)

__all__ = ["WIDGETS"]
