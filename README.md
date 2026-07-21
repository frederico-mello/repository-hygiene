# auditoria-higiene

Auditor de higiene para repositórios Git. Verifica segredos, links quebrados, referências inexistentes, artefatos fora do `.gitignore`, segurança de workflows GitHub Actions e mais.

## Instalação

```bash
pip install auditoria-higiene
```

## Uso

### Auditoria local

```bash
auditoria-higiene .                    # texto (padrão)
auditoria-higiene . --format json      # JSON
auditoria-higiene . --format sarif     # SARIF
auditoria-higiene --config caminho/auditoria.yaml .
```

### Inicializar projeto

```bash
auditoria-higiene --init .             # cria auditoria.yaml + workflow
auditoria-higiene --init --force .     # sobrescreve existentes
```

### Códigos de saída

| Código | Significado |
|--------|-------------|
| 0      | Auditoria limpa (sem erros) |
| 1      | Erro(s) encontrado(s) |
| 2      | Configuração ou execução inválida |

## Configuração

Arquivo `auditoria.yaml` na raiz do projeto:

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
    - auditoria-report.txt
  artefatos_fora_gitignore:
    - .git
  arquivos_sem_referencia:
    - .gitignore
    - Makefile
```

## Regras

| Regra | Severidade padrão | Descrição |
|-------|-------------------|-----------|
| `segredos_rastreados` | error | Detecta senhas, tokens e credenciais em arquivos rastreados |
| `links_internos_quebrados` | error | Links markdown para arquivos inexistentes |
| `referencias_inexistentes` | error | Referências a arquivos que não existem no repositório |
| `artefatos_fora_gitignore` | error | Arquivos gerados não cobertos pelo `.gitignore` |
| `gitkeep_sem_conteudo` | warning | Diretórios com apenas `.gitkeep` |
| `arquivos_sem_referencia` | warning | Arquivos não mencionados em nenhum outro |
| `documentacao_desatualizada` | warning | Documentação referenciando arquivos inexistentes |
| `configuracao_sem_integracao` | warning | Config sem workflow, comando ou doc |
| `openspec_parada` | warning | Mudanças OpenSpec paradas há 30+ dias |
| `workflows_inseguros` | warning | Permissões excessivas, actions sem versão fixa |

## GitHub Actions

O comando `--init` gera um workflow em `.github/workflows/auditoria-higiene.yml` que:

- Executa auditoria semanalmente e em push/PR nos caminhos relevantes
- Publica relatório no resumo da execução
- Cria/atualiza issue consolidada quando encontra erros
- Fecha a issue quando a auditoria fica limpa

### Permissões mínimas do workflow

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: read
```

## Versionamento

O pacote segue SemVer. A configuração declara `versao_configuracao` para compatibilidade futura.

- `v0.1.x` — versão inicial
- Tags do workflow seguem as tags do pacote

## Migração deste repositório

Este repositório (`principal-tarefas-aleatorias`) foi o primeiro a usar o auditor. A migração para o pacote:

1. `scripts/auditoria.py` agora é um wrapper que delega para `auditoria-higiene`
2. `auditoria.yaml` inclui `versao_configuracao: 1` e regra `workflows_inseguros`
3. Workflow local foi atualizado para instalar o pacote em vez de usar o script

## Desenvolvimento

```bash
pip install -e .
pytest tests_package/
```

## Licença

MIT
