from dmt_overlay.telemetria.modelos import Carro, Estado, Jogador, Sessao, TipoSessao


def carro(id_, posicao, voltas, distancia, jogador=False, classe="Hypercar", **extra):
    base = dict(
        id=id_, piloto=f"Piloto {id_}", equipe=f"Equipe #{id_}", classe=classe, posicao=posicao, voltas=voltas,
        distancia_volta=distancia, melhor_volta=200.0, ultima_volta=200.0, tempo_lider=0.0, voltas_lider=0,
        tempo_frente=0.0, voltas_frente=0, nos_boxes=False, paradas=0, jogador=jogador, tempo_estimado=200.0,
    )
    base.update(extra)
    return Carro(**base)


def estado(carros, **sessao):
    s = Sessao(tipo=TipoSessao.CORRIDA, tamanho_pista=10000.0, **sessao)
    return Estado(conectado=True, pilotando=True, sessao=s, jogador=Jogador(), carros=carros)
