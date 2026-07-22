## Why

O auditor de higiene atualmente está acoplado a um único repositório e exige copiar scripts, configuração e workflow manualmente. Esta change transforma a auditoria em uma ferramenta reutilizável para repositórios Python no GitHub, com instalação, atualização e integração de CI automatizadas.

## What Changes

- Criar o pacote Python público `repository-hygiene`, versionado e instalável via `pip`, no repositório GitHub `frederico-mello/repository-hygiene`.
- Disponibilizar CLI `repository-hygiene` com os subcomandos `install`, `audit` e `update` como interface pública única.
- Gerar configuração e workflow chamador do GitHub Actions no repositório consumidor.
- Fornecer workflow reutilizável centralizado, chamado pelo workflow instalado em cada consumidor; os gatilhos de agenda, push/PR e execução manual ficam no consumidor.
- Manter Summary e issue consolidada no repositório consumidor.
- Ativar todas as regras de auditoria por padrão, separando erros de avisos.
- Preservar configurações locais e evitar sobrescrita silenciosa.
- Permitir atualização explícita do auditor e do workflow por versão.
- Manter o workflow reutilizável no mesmo repositório do pacote, com releases alinhadas por versão.
- Publicar documentação de instalação, configuração, atualização e rollback.

## Capabilities

### New Capabilities

- `pacote-auditoria-higiene`: Pacote Python e CLI para instalar e executar a auditoria.
- `instalacao-repositorio`: Configuração automatizada da auditoria em repositórios Python GitHub.
- `workflow-auditoria-reutilizavel`: Execução de CI, Summary e issue consolidada em repositórios consumidores.
- `atualizacao-auditoria`: Atualização versionada do auditor e dos artefatos gerenciados.

### Modified Capabilities

- Nenhuma.

## Decisões de escopo

- O nome público do pacote, comando e repositório será `repository-hygiene`, usando `frederico-mello/repository-hygiene` como origem do workflow reutilizável.
- Cada consumidor receberá um workflow chamador com os eventos `schedule`, `push`, `pull_request` e `workflow_dispatch`. Esse workflow chamará o workflow reutilizável central por uma referência de versão fixa.
- O instalador não criará `pyproject.toml` nem alterará o empacotamento do projeto consumidor; ele somente configurará os artefatos da auditoria.
- A CLI pública usará exclusivamente subcomandos. A forma canônica será `auditoria-higiene audit`, `auditoria-higiene install` e `auditoria-higiene update`; flags legadas como `--init` não fazem parte do contrato desta change.

## Impact

- Novo pacote Python distribuído no PyPI.
- Novo workflow reutilizável no GitHub Actions.
- Templates de configuração e workflow para repositórios consumidores.
- Dependência de `PyYAML` isolada no pacote da ferramenta.
- Necessidade de testes de CLI, templates, integração GitHub e compatibilidade entre versões.
- O repositório atual do auditor será usado como referência e posteriormente migrado para consumir o novo pacote.
