# repository-hygiene

Repository hygiene auditor for Git repositories. Checks for secrets, broken links, missing references, artifacts outside `.gitignore`, GitHub Actions workflow security, and more.

## Installation

```bash
pip install repository-hygiene
```

## Usage

### Audit a repository

```bash
repository-hygiene audit .                    # text (default)
repository-hygiene audit . --format json      # JSON
repository-hygiene audit . --format sarif     # SARIF
repository-hygiene audit --config path/to/auditoria.yaml .
```

### Initialize a project

```bash
repository-hygiene install .                  # creates auditoria.yaml + workflow
repository-hygiene install --force .          # overwrites existing files
```

### Update

```bash
repository-hygiene update                     # check for updates
repository-hygiene update --version 0.1.0     # update to specific version
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0    | Clean audit (no errors) |
| 1    | Error(s) found |
| 2    | Invalid configuration or execution |

## Configuration

File `auditoria.yaml` in the project root:

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
  referencias_inexistentes:
    - audit-report.txt
  artefatos_fora_gitignore:
    - .git
  arquivos_sem_referencia:
    - .gitignore
    - Makefile
```

## Rules

| Rule | Default severity | Description |
|------|-----------------|-------------|
| `segredos_rastreados` | error | Detects passwords, tokens, and credentials in tracked files |
| `links_internos_quebrados` | error | Markdown links to non-existent files |
| `referencias_inexistentes` | error | References to files that don't exist in the repository |
| `artefatos_fora_gitignore` | error | Generated files not covered by `.gitignore` |
| `gitkeep_sem_conteudo` | warning | Directories with only `.gitkeep` |
| `arquivos_sem_referencia` | warning | Files not mentioned anywhere else |
| `documentacao_desatualizada` | warning | Documentation referencing non-existent files |
| `configuracao_sem_integracao` | warning | Config without workflow, command, or docs |
| `openspec_parada` | warning | OpenSpec changes stalled for 30+ days |
| `workflows_inseguros` | warning | Excessive permissions, actions without fixed version |

## GitHub Actions

The `install` command generates a caller workflow in `.github/workflows/repository-hygiene.yml` that:

- Runs weekly and on push/PR in relevant paths
- Calls the reusable workflow from `frederico-mello/repository-hygiene` at a fixed version
- Publishes report in the execution summary
- Creates/updates a consolidated issue when errors are found
- Closes the issue when the audit is clean

### Minimum workflow permissions

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: read
```

## Versioning

The package follows SemVer. Configuration declares `versao_configuracao` for future compatibility.

- `v0.1.x` — initial version
- Workflow tags follow package tags

## Development

```bash
pip install -e .
pytest tests_package/
```

## License

MIT
