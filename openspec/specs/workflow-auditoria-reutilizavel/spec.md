## Purpose

Define the reusable GitHub Actions workflow and the caller workflow installed in consumer repositories.

## Requirements

### Requirement: Execução no GitHub Actions

O pacote MUST fornecer um workflow chamador para cada consumidor, com agenda semanal, push/PR configurados e acionamento manual, que invoque o workflow reutilizável central por uma versão fixa.

#### Scenario: Execução agendada
- **WHEN** o agendamento semanal ocorre
- **THEN** o workflow chamador invoca o workflow reutilizável, que executa a auditoria no estado do repositório consumidor

#### Scenario: Execução manual
- **WHEN** o usuário aciona `workflow_dispatch`
- **THEN** o workflow chamador invoca o workflow reutilizável sem exigir alteração de código

### Requirement: Relatório e issue consolidada

O workflow MUST publicar relatório no Summary e criar ou atualizar uma única issue identificada por marcador estável quando houver pendências.

#### Scenario: Pendências encontradas
- **WHEN** a auditoria encontra erros ou avisos em execução com permissão de escrita
- **THEN** o Summary é publicado e a issue consolidada é criada ou atualizada

#### Scenario: Repositório limpo
- **WHEN** a auditoria termina sem pendências
- **THEN** o Summary indica estado limpo e a issue consolidada aberta é fechada

### Requirement: Execução sem escrita

O workflow MUST funcionar em forks e PRs externos sem exigir permissão de escrita, publicando apenas Summary e status quando não puder atualizar issues.

#### Scenario: PR externo
- **WHEN** um PR externo executa o workflow sem permissão para issues
- **THEN** a auditoria publica Summary/status e não falha por não conseguir escrever na issue
