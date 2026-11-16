# Como contribuir

## Ambiente

Requer Python 3.11 ou mais novo.

```bash
git clone git@github.com:Vinii225/dmt-overlay.git
cd dmt-overlay
python -m venv .venv
.venv\Scripts\activate          # Linux: source .venv/bin/activate
pip install -e ".[dev]"

python run.py --demo            # abre com dados de demonstração
pytest                          # testes
ruff check .                    # lint
python scripts/previa.py        # atualiza docs/previa.png
python scripts/build.py         # gera o .exe em dist/
```

## Estrutura

```
dmt_overlay/
├── telemetria/       leitura do LMU (memória compartilhada) e fonte de demonstração
├── calculos/         relativo, combustível, estratégia, multiclasse, radar e formatação
├── widgets/          um arquivo por overlay, todos herdam de base.WidgetOverlay
├── app.py            liga tudo: widgets, bandeja, atalhos e janela de configurações
├── provedor.py       lê a fonte no ritmo configurado e distribui os quadros
├── bandeja.py        menu do ícone na bandeja (ações de sessão)
├── configuracoes.py  janela de configurações, montada a partir dos metadados dos widgets
├── atalhos.py        atalhos globais (RegisterHotKey no Windows)
├── gravador.py       voltas em CSV
├── layouts.py        layout por classe
├── hud.py            HUD de transmissão (servidor local para o OBS; página em recursos/hud)
├── atualizacao.py    aviso de versão nova (API do GitHub)
├── config.py         configuração em JSON
└── tema.py           cores, fontes e cores das classes
```

## Criando um widget

1. Herde de `WidgetOverlay` e implemente `preparar` (extrai só os dados exibidos; o widget só redesenha quando eles mudam) e `desenhar`.
2. Preencha `descricao` e, para cada chave de `opcoes_padrao`, uma `Opcao` em `opcoes` com rótulo, ajuda, faixa e unidade. A janela de configurações se monta sozinha a partir disso, e um teste falha se faltar alguma.
3. Se a altura depender das opções, sobrescreva `tamanho_base`; `reconfigurar()` é chamado quando o usuário muda algo.
4. Registre em `widgets/__init__.py`.

```python
class Exemplo(WidgetOverlay):
    nome = "exemplo"
    titulo = "Exemplo"
    descricao = "Uma linha explicando o que o widget mostra."
    opcoes_padrao = {"alerta": 3.0}
    opcoes = {"alerta": Opcao("Alerta", "Quando ficar vermelho.", 1, 10, 0.5, " voltas")}
```

## Branches

- `main` sempre estável: tudo que entra nela pode virar release.
- Trabalhe em uma branch a partir da `main`, com o mesmo prefixo do commit:
  - `feat/relativo-multiclasse`
  - `fix/combustivel-apos-box`
  - `docs/instalacao`
- Abra um Pull Request para a `main`. O CI roda lint, testes (Windows e Linux) e confere os commits.

## Commits semânticos

Formato: `tipo(escopo opcional): descrição no imperativo`

| Tipo | Quando usar |
|---|---|
| `feat` | funcionalidade nova (widget, opção, dado novo) |
| `fix` | correção de bug |
| `docs` | só documentação |
| `refactor` | mudança de código sem mudar comportamento |
| `perf` | melhoria de desempenho |
| `test` | testes |
| `build` | empacotamento e dependências |
| `ci` | GitHub Actions |
| `chore` | manutenção geral |

Exemplos:

```
feat(widgets): adicionar radar de proximidade
fix(combustivel): ignorar volta com safety car na média
docs: explicar configuração em psi
```

Use `!` para mudanças que quebram a configuração existente: `feat(config)!: renomear chaves dos widgets`.

Referencie a issue no corpo do commit ou do PR: `Closes #12`.

## Planejamento

O roadmap fica no [kanban do projeto](https://github.com/users/Vinii225/projects/5).

- Sprints de 2 semanas, começando na segunda-feira.
- Cada milestone é uma versão e dura 2 sprints. Feature pronta entra na `main` e espera o fim do ciclo, sem release avulsa por feature.
- Beta só no meio do ciclo, quando algo precisa ser testado em pista pela equipe.
- Correção urgente que atrapalha corrida (P0) pode sair como patch a qualquer momento.
- Depois do merge, o card vai para **Testar em pista**. Só passa para **Concluído** depois de conferido no LMU, porque o CI não roda o jogo.

## Release

1. Atualize `__version__` em `dmt_overlay/__init__.py` seguindo o semver:
   - `fix` → patch (`0.1.1`)
   - `feat` → minor (`0.2.0`)
   - `!` → major (`1.0.0`)
2. Mova os itens de **Não lançado** para a nova versão no `CHANGELOG.md`.
3. Faça o commit `chore(release): v0.2.0` na `main` e crie a tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

O workflow **Release** gera o `.zip` do Windows e publica em Releases. Tags com hífen (`v0.2.0-beta.1`) saem como pré-release.
