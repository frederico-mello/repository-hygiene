# Design: Controle de Versão & Release Automatizado

## Context

Estado atual do projeto: 30 commits desde tag `v0.2.0` sem bump de versão. Nenhum CI/CD existe — `.github/workflows/` vazio. `pyproject.toml` com versão hardcoded `0.2.0` e build backend `setuptools`. Template `workflow.yml` fixado em `repository-hygiene==0.2.0`. `__version__` lido dinamicamente via `importlib.metadata`. Testes com `pytest` em `tests_package/` e `tests/`.

## Goals / Non-Goals

**Goals:**
- Release 100% automatizado após push na main — análise de commits, bump, changelog, build, upload PyPI
- Conventional Commits auditado pelo próprio `repository-hygiene` (dogfooding — o projeto audita a si mesmo)
- Hook pre-commit `commit-msg` como padrão (opt-out, instalado via `--init`)
- Versão no template de workflow dinâmica, não hardcoded

**Non-Goals:**
- Não alterar regras de auditoria existentes nem sua interface
- Não suportar outros gerenciadores de pacotes (brew, choco)
- Não publicar pré-releases (alpha, beta, rc)
- Não forçar conventional commits em projetos de terceiros — regra é habilitada por padrão mas configurável

## Decisions

### Release Pipeline (`.github/workflows/release.yml`)

Workflow interno do projeto `repository-hygiene`, não distribuído no template `--init`. Disparado por push na branch `main`.

```
push main
  │
  ▼
python-semantic-release version
  │ analisa git log desde último tag
  │ calcula bump (feat→minor, fix→patch, BREAKING→major)
  │ ├─ sem bump → skip, encerra
  │ └─ com bump →
  │     ├─ escreve pyproject.toml (nova versão)
  │     ├─ gera CHANGELOG.md categorizado
  │     ├─ git commit + tag vX.Y.Z + push
  │
  ▼
python -m build → dist/*.whl + dist/*.tar.gz
  │
  ▼
twine upload dist/* → PyPI (autenticação via PYPI_TOKEN secret)
```

`python-semantic-release` é dependência apenas de CI/dev, não adicionada ao `[project]` do `pyproject.toml`. Executado via `pip install` no próprio workflow.

`pyproject.toml` permanece fonte única da verdade para versão. `python-semantic-release` escreve nele. `importlib.metadata.version()` lê dele.

### Auditoria de Conventional Commits (`src/auditoria_higiene/commit_check.py`)

Novo módulo seguindo o padrão existente de regras:

| Interface | Descrição |
|---|---|
| `validar_commits(repo_path) → list[dict]` | Lê `git log --format=%H %s`, parseia cada mensagem, retorna findings |
| Finding schema | `{ "rule": "conventional-commits", "level": "warning", "file": commit_hash, "message": "..." }` |

Integra-se ao `core.py` como regra referenciada no config:

```yaml
rules:
  conventional-commits:
    enabled: true   # opt-out
    level: warning
```

Validação contra a especificação Conventional Commits: tipo obrigatório (feat, fix, docs, etc.), escopo opcional entre parênteses, breaking change via `!`, dois pontos + espaço + descrição. Merge commits e squash commits são ignorados (não geram falso-positivo). Repositório sem commits retorna lista vazia.

### Hook Pre-commit (`src/auditoria_higiene/templates/pre-commit`)

Script `commit-msg` shell que valida a mensagem do commit antes de finalizar. Instalado por padrão pelo `--init` (sem flag adicional).

Fluxo:
```
git commit
  │
  ▼
.git/hooks/commit-msg
  │ valida regex Conventional Commits
  ├─ PASS → commit segue
  └─ FAIL → bloqueia, exibe formato esperado
```

### Testes

| Camada | O que testar | Como |
|---|---|---|
| Unitário | `commit_check.py` — regex de parsing, tipos permitidos, escopos, breaking change, inválidos | `pytest` com fixtures de strings (sem git real) |
| Unitário | Hook `commit-msg` — execução com mensagens mockadas | `pytest` com `subprocess` contra o script |
| Integração | `validar_commits()` com repo git real | `pytest` + `git init` em `tmp_path`, commits válidos e inválidos |
| Integração | `--init` copia hook `commit-msg` | Expandir testes existentes em `tests_package/test_init.py` |
| Workflow | Release pipeline — YAML válido, steps testáveis | `actionlint` para lint de GitHub Actions. Release real é manual. |
| Snapshot | Template `workflow.yml` — versão não hardcoded | Expandir testes existentes para verificar ausência de `==0.2.0` |

Alinhamento com padrões existentes: `tests_package/test_*.py` para testes de unidade/integração. `pytest` como runner. Nenhum novo framework.

### Versão Dinâmica no Template

Template `workflow.yml` deixa de ter `repository-hygiene==0.2.0` hardcoded. Passa a usar `repository-hygiene>=0.3.0` ou referência dinâmica resolvida no momento do `--init`. O init injeta a versão instalada no template gerado.

### Migração / Rollout

O primeiro release após merge detectará os 30 commits acumulados desde `v0.2.0` (maioria `feat:`) e fará bump MINOR para `0.3.0` automaticamente, gerando CHANGELOG.md e publicando no PyPI.

Rollback: PyPI é imutável — versão publicada só pode ser yanked. Tag e commit de bump podem ser revertidos no git.

## Risks / Trade-offs

### Modos de Falha

| Falha | Mitigação |
|---|---|
| `PYPI_TOKEN` ausente/expirado | CI falha no step publish com erro claro. Token é GitHub Secret — nunca exposto. |
| Sem commits convencionais no histórico | Nenhum bump gerado, workflow encerra silenciosamente. |
| Build falha (setuptools) | CI falha antes do upload. Sem tag criada. Rollback trivial. |
| Upload PyPI falha (rede / versão duplicada) | PyPI imutável. Retry: contatar PyPI ou usar próximo patch. |
| `git` não encontrado no PATH | `validar_commits` levanta exceção, auditoria reporta erro de sistema. |
| Repositório sem commits | `git log` vazio → 0 findings. Sem erro. |
| `git commit --no-verify` burla hook | Documentado. CI de auditoria pega violações depois. |

### Segurança

| Risco | Mitigação |
|---|---|
| Token PyPI exposto | `PYPI_TOKEN` como GitHub Secret. Workflow nunca faz echo. `contents: write` é a única permissão elevada. |
| Artefatos de build no repo | `dist/` no `.gitignore`. Build em runner descartável. |

### Backwards Compatibility

| Mudança | Impacto |
|---|---|
| `--version` output | Mantido: `repository-hygiene {__version__}` |
| Template `workflow.yml` | Versão dinâmica. Sem quebra para novos `--init`. Templates antigos continuam funcionando. |
| Hook `commit-msg` no `--init` | Novo arquivo adicionado. Não afeta hooks existentes. |
| Regra `conventional-commits` | Novo finding type. Relatórios ganham seção adicional. Não altera findings existentes. |

### Trade-off: Conventional Commits obrigatório

Adotar `python-semantic-release` exige que os commits do projeto sigam Conventional Commits. O risco de commits mal formatados bloquearem releases é mitigado por: (1) hook pre-commit bloqueia localmente, (2) CI de auditoria alerta após push, (3) AGENTS.md documenta o padrão. Commits não-convencionais são ignorados pelo semantic-release (não quebram o pipeline, apenas não contribuem para o changelog).
