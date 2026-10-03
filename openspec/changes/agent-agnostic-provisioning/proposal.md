## Why

Hoje a ferramenta trata apenas o OpenCode: o destino da skill `agent-hygiene-flow` está fixo em `.opencode/skills/` (`init.py`), e o escopo da auditoria — pastas de ruído, diretórios de fonte e gatilhos do workflow — só reconhece `.opencode/` (`core.py`, `templates/workflow.yml`). O próprio repositório já hospeda cópias das skills e comandos do OpenSpec para cinco agentes: `.opencode/` (24 arquivos), `.kilocode/` (18), `.omp/` (12), `.kilo/` (11) e `.hermes/` (9).

Numa auditoria real deste repositório, a maioria dos 38 `unreferenced_files` e dos 160 `outdated_documentation` caiu justamente em diretórios fora das listas atuais (`.kilo/`, `.omp/`, `.hermes/`, `.kilocode/`): o escopo amarrado a um único agente produz ruído e lacunas ao mesmo tempo.

## What Changes

- Destino da skill configurável e múltiplo: `install` e `install-skill` provisionam `agent-hygiene-flow` em todos os diretórios de agente presentes no repositório alvo (`.opencode`, `.kilocode`, `.kilo`, `.omp`, `.hermes`), com fallback para `.opencode` quando nenhum existe e seleção explícita via `--agents`; `--dry-run` lista todos os destinos planejados.
- `core.py`: a lista de diretórios de ruído (`_em_diretorio_ruidoso_referencias`) passa a cobrir `commands/`, `skills/openspec-` e os workflows OpenSpec dos cinco agentes; a lista de diretórios de fonte (`_eh_diretorio_fonte`) passa a aceitar as cinco raízes.
- `templates/workflow.yml`: os gatilhos `paths` de `push` e `pull_request` incluem os diretórios dos demais agentes além de `.opencode/**`.
- `README.md` e testes acompanhando: provisionamento multi-destino, seleção explícita, dry-run e escopo de auditoria.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `skill-provisioning`: provisionamento agnóstico de agente — múltiplos destinos configuráveis, idempotência por destino, escopo de auditoria cobrindo os diretórios dos agentes suportados e gatilhos do workflow gerado incluindo esses diretórios.

## Impact

- Afeta `auditoria_higiene/init.py` (destinos da skill e dry-run), `auditoria_higiene/cli.py` (flag `--agents`), `auditoria_higiene/core.py` (listas de ruído e fonte), `auditoria_higiene/templates/workflow.yml` (gatilhos), `README.md` e `tests_package/`.
- Contrato do CLI preservado: sem novas dependências de runtime, sem mudança nos exit codes, e repositórios sem nenhum diretório de agente continuam recebendo `.opencode/skills/agent-hygiene-flow/`.
- As correções de escopo em `core.py` materializam exigências já declaradas em `context-aware-audit-findings` (diretórios de fonte não devem virar achados de artefato/referência); nenhum requisito novo é aberto nessa capacidade.
- Interação a reconciliar com a change aberta `reduzir-falsos-positivos-auditoria` (capability `reference-classification`), que também trata classificação de referências — se ambas avançarem, as listas precisam ser alinhadas antes do merge.
