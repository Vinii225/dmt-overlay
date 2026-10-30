# Como contribuir

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
