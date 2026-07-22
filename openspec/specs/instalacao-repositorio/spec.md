## Purpose

Define how `repository-hygiene install` configures a consumer repository with audit configuration and workflow.

## Requirements

### Requirement: Instalação idempotente

O comando `repository-hygiene install` MUST configurar um repositório Python GitHub com configuração e workflow necessários, sem sobrescrever arquivos existentes sem confirmação explícita.

#### Scenario: Primeiro setup
- **WHEN** o comando é executado em um repositório Python sem auditoria configurada
- **THEN** cria a configuração e o workflow consumidor e informa os arquivos criados

#### Scenario: Setup repetido
- **WHEN** o comando é executado novamente no mesmo repositório
- **THEN** não duplica conteúdo nem altera configurações locais silenciosamente

### Requirement: Prévia e confirmação

O instalador MUST oferecer `--dry-run` e MUST informar conflitos antes de modificar arquivos.

#### Scenario: Prévia sem alterações
- **WHEN** o desenvolvedor executa `repository-hygiene install --dry-run`
- **THEN** o comando mostra operações planejadas e não altera o repositório

#### Scenario: Arquivo existente
- **WHEN** um arquivo gerenciado já existe com conteúdo diferente
- **THEN** o instalador solicita confirmação ou encerra sem alterar o arquivo

### Requirement: Configuração completa por padrão

O setup MUST gerar configuração com todas as regras disponíveis habilitadas, classificando problemas objetivos como erros e heurísticas como avisos, com suporte a exceções locais.

#### Scenario: Configuração inicial
- **WHEN** o setup cria `auditoria.yaml`
- **THEN** o arquivo contém todas as regras padrão e uma seção de exceções editável
