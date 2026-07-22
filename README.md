# repository-hygiene

Auditor de higiene para repositórios Git. Verifica segredos, links quebrados, referências inexistentes, artefatos fora do `.gitignore`, segurança de workflows GitHub Actions e mais.

## Instalação

```bash
pip install repository-hygiene
# ou
uv tool install repository-hygiene
```

Para usar a versão local clonada:

```bash
uv tool install --editable .
```

## Uso

### Inicializar projeto

Para um repositório ainda não configurado, o fluxo recomendado começa com a inicialização:

```bash
repository-hygiene --init .             # cria auditoria.yaml + workflow
repository-hygiene --init --force .     # sobrescreve existentes
repository-hygiene --init --install-hook .   # cria arquivos + instala hook pre-commit
repository-hygiene --init --install-hook --force .  # força substituição do hook existente
```

Após a inicialização, revise o arquivo `auditoria.yaml` gerado e ajuste regras, severidades e exceções conforme necessário. Em seguida, execute a auditoria.

### Configuração

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
    # Opcional: limita alertas a padrões de artefatos gerados.
    # padroes_artefatos: [".ruff_cache/", ".pytest_cache/", "dist/"]
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
    # Permissões write necessárias ao workflow podem ser explicitamente permitidas.
    permissoes_write_permitidas: [issues]

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

### Regras

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

### Auditoria local

```bash
repository-hygiene .                    # texto (padrão)
repository-hygiene . --format json      # JSON
repository-hygiene . --format sarif     # SARIF
repository-hygiene --config caminho/auditoria.yaml .
```

Por padrão, a auditoria exibe um resumo no terminal e grava relatório JSON sanitizado em `.repository-hygiene/auditoria.json`. Para manter o relatório completo no terminal, informe explicitamente o formato:

```bash
repository-hygiene . --format text
repository-hygiene . --format json
repository-hygiene . --format sarif
```

Use `--output` para escolher outro caminho. Sem `--format`, o arquivo será JSON; com formato explícito, o arquivo usará o formato selecionado:

```bash
repository-hygiene . --output relatorios/auditoria.json
repository-hygiene . --format sarif --output relatorios/auditoria.sarif
```

O diretório padrão é artefato local gerado e não deve ser versionado. Para agentes LLM, adicione opcionalmente às instruções do agente:

```md
## Repository Hygiene

Após executar `repository-hygiene`, leia `.repository-hygiene/auditoria.json` como fonte completa da auditoria. Priorize achados `error`, não exponha valores sensíveis e execute a auditoria novamente após corrigir arquivos.
```

### Códigos de saída

| Código | Significado |
|--------|-------------|
| 0      | Auditoria limpa (sem erros) |
| 1      | Erro(s) encontrado(s) |
| 2      | Configuração ou execução inválida |

### Hook pre-commit nativo

O auditor pode ser instalado como hook nativo do Git para validar o conteúdo **staged** antes de cada commit:

```bash
repository-hygiene --init --install-hook .
```

O hook executa `repository-hygiene --pre-commit .` e bloqueia o commit se encontrar erros de severidade `error`. A auditoria opera apenas sobre o índice staged — alterações não staged não afetam o resultado.

Para isso, o auditor cria um snapshot temporário a partir do índice Git, executa todas as regras nesse snapshot e o remove ao terminar. Arquivos staged novos, modificados ou removidos são avaliados conforme o conteúdo que será commitado, sem alterar a árvore de trabalho.

| Código | Comportamento no hook |
|--------|-----------------------|
| 0      | Commit permitido      |
| 1      | Commit bloqueado (erros encontrados) |
| 2      | Commit bloqueado (falha de configuração ou execução) |

Avisos (`warning`) são exibidos mas não bloqueiam o commit.

Para ignorar o hook em situações pontuais:

```bash
git commit --no-verify
```

> O hook é uma barreira local. O workflow do GitHub Actions continua sendo a auditoria completa e independente do repositório — mesmo que o hook não esteja instalado ou seja ignorado.

O hook não substitui hooks existentes: sem `--force`, a instalação é ignorada quando `.git/hooks/pre-commit` já existe. Com `--force`, o arquivo existente é substituído.

## GitHub Actions

O comando `--init` gera um workflow em `.github/workflows/repository-hygiene.yml` que:

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

O workflow instala a versão `0.2.0` do pacote, executa a auditoria mesmo quando ela retorna erro, publica o relatório em `$GITHUB_STEP_SUMMARY` e usa uma issue marcada com `maintenance` para consolidar falhas. Em eventos `pull_request`, a issue não é criada nem atualizada.

O workflow dispara em mudanças de `auditoria.yaml`, `.github/**`, `.opencode/**`, `openspec/**`, `docs/**`, `README.md`, `.gitignore` e `Makefile`, além da execução semanal e manual (`workflow_dispatch`). Actions de terceiros são fixadas em versões principais (`@v4`, `@v5` e `@v7`); a regra `workflows_inseguros` sinaliza permissões excessivas e referências de actions sem versão.

### Segurança e isolamento

- Caminhos de configuração, arquivos gerados e arquivos materializados do índice são validados contra a raiz do repositório.
- O modo pre-commit rejeita caminhos inválidos no índice e não executa comandos de shell para materializar arquivos.
- Referências a arquivos rastreados são consultadas com cache durante uma auditoria, evitando chamadas repetidas ao Git sem mudar o resultado.
- Relatórios JSON e SARIF passam por sanitização antes de serem exibidos.

## Migração da v0.1.0

A versão `0.2.0` altera a interface de linha de comando. Comandos da `0.1.0` não funcionam mais:

| Comando v0.1.0 | Equivalente v0.2.0 |
|----------------|-------------------|
| `repository-hygiene audit .` | `repository-hygiene .` |
| `repository-hygiene install .` | `repository-hygiene --init .` |
| `repository-hygiene install --force .` | `repository-hygiene --init --force .` |
| `repository-hygiene update` | Removido (sem substituto) |

## Versionamento

O pacote segue SemVer. A configuração declara `versao_configuracao` para compatibilidade futura.

- `v0.1.x` — versão inicial (CLI com subcomandos `audit`, `install`, `update`)
- `v0.2.x` — CLI atual (auditoria direta, `--init`, `--install-hook`)
- Tags do workflow seguem as tags do pacote

## Desenvolvimento

```bash
uv venv
uv pip install -e . pytest
uv run pytest tests_package/
```

## Licença

MIT
