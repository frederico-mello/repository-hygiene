# repository-hygiene

Auditor de higiene para repositórios Git. Verifica segredos, links quebrados,
referências inexistentes, artefatos fora do `.gitignore`, segurança de
workflows GitHub Actions e mais.

## Instalação

```bash
# ephemeral (recomendado — sem instalação global)
uvx repository-hygiene install .

# persistente
uv tool install repository-hygiene
# ou
pip install repository-hygiene
```

**Atenção:** após `pip install`, execute `repository-hygiene install .` **no
repositório alvo** para provisionar a configuração, o workflow CI e a skill
OpenCode `agent-hygiene-flow`.

Para instalar direto do GitHub (versões não publicadas no PyPI):

```bash
pip install git+https://github.com/frederico-mello/repository-hygiene.git
```

## Uso

### Inicializar repositório (`install`)

```bash
repository-hygiene install .             # cria auditoria.yaml + workflow + skill
repository-hygiene install --force .     # sobrescreve existentes
repository-hygiene install --dry-run .   # preview sem gravar
```

`install` cria:
- `auditoria.yaml` — configuração de regras e exceções
- `.github/workflows/repository-hygiene.yml` — workflow CI semanal
- `.opencode/skills/agent-hygiene-flow/` — skill OpenCode para agentes

### Auditoria (`audit`)

```bash
repository-hygiene .                        # relatório texto (stdout) + JSON (.repository-hygiene/)
repository-hygiene . --format json          # só JSON
repository-hygiene . --format sarif         # só SARIF
repository-hygiene . --output auditoria.txt # grava em arquivo
```

### Hook pre-commit

```bash
repository-hygiene install --install-hook .   # hook na primeira vez
```

Bloqueia commits com erros de severidade `error` no conteúdo staged. Avisos
(`warning`) são exibidos mas não bloqueiam. Para pular:

```bash
git commit --no-verify
```

### Códigos de saída

| Código | Auditoria          | Hook pre-commit     |
|--------|-------------------|---------------------|
| 0      | limpa             | commit permitido    |
| 1      | erros encontrados | commit bloqueado    |
| 2      | config inválida   | falha de execução   |

## Configuração

Arquivo `auditoria.yaml` na raiz:

```yaml
versao_configuracao: 1

regras:
  segredos_rastreados:
    habilitada: true
    severidade: error
  links_internos_quebrados:
    habilitada: true
    severidade: error
  referencias_inexistentes:
    habilitada: true
    severidade: error
  artefatos_fora_gitignore:
    habilitada: true
    severidade: error
  gitkeep_sem_conteudo:
    habilitada: true
    severidade: warning
  arquivos_sem_referencia:
    habilitada: true
    severidade: warning
  documentacao_desatualizada:
    habilitada: true
    severidade: warning
  configuracao_sem_integracao:
    habilitada: true
    severidade: warning
  openspec_parada:
    habilitada: true
    severidade: warning
  workflows_inseguros:
    habilitada: true
    severidade: warning

excecoes:
  segredos_rastreados:
    - .secrets.baseline
    - .env.example
  artefatos_fora_gitignore:
    - .git
  arquivos_sem_referencia:
    - .gitignore
    - Makefile
```

### Regras

| Regra | Severidade | Descrição |
|-------|-----------|-----------|
| `segredos_rastreados` | error | Senhas, tokens e credenciais em arquivos rastreados |
| `links_internos_quebrados` | error | Links markdown para arquivos inexistentes |
| `referencias_inexistentes` | error | Referências a arquivos que não existem no repo |
| `artefatos_fora_gitignore` | error | Arquivos gerados não cobertos pelo `.gitignore` |
| `gitkeep_sem_conteudo` | warning | Diretórios com apenas `.gitkeep` |
| `arquivos_sem_referencia` | warning | Arquivos não referenciados por nenhum outro |
| `documentacao_desatualizada` | warning | Documentação referenciando arquivos inexistentes |
| `configuracao_sem_integracao` | warning | Tool config sem workflow, comando ou doc |
| `openspec_parada` | warning | Mudanças OpenSpec paradas há 30+ dias |
| `workflows_inseguros` | warning | Permissões excessivas, actions sem versão fixa |

## GitHub Actions

O workflow gerado (`repository-hygiene.yml`):

- Executa semanalmente e em push/PR nos caminhos relevantes
- Publica relatório no `$GITHUB_STEP_SUMMARY`
- Cria/atualiza issue consolidada com achados (`error`); fecha quando limpa

Permissões mínimas:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: read
```

## Migração v0.1 → v0.2

| Comando v0.1 | Equivalente v0.2+ |
|-------------|-------------------|
| `repository-hygiene audit .` | `repository-hygiene .` |
| `repository-hygiene install .` | `repository-hygiene install .` |
| `repository-hygiene update` | removido |

## Desenvolvimento

```bash
uv pip install -e . pytest
uv run pytest tests_package/
```

## Licença

MIT
