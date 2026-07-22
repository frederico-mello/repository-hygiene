## ADDED Requirements

### Requirement: Atualização explícita

O comando `auditoria-higiene update` MUST atualizar o auditor e os artefatos gerenciados para uma versão selecionada, preservando configuração local e exigindo confirmação antes da escrita.

#### Scenario: Atualização disponível
- **WHEN** o desenvolvedor executa `auditoria-higiene update` com versão mais nova disponível
- **THEN** o comando mostra alterações e atualiza somente após confirmação

#### Scenario: Atualização sem versão nova
- **WHEN** a versão instalada já é a versão selecionada
- **THEN** o comando informa que não há alterações e não modifica arquivos

### Requirement: Rollback por versão

O sistema MUST permitir selecionar uma versão anterior para restaurar o auditor e o workflow gerenciados.

#### Scenario: Retorno à versão anterior
- **WHEN** o desenvolvedor executa `auditoria-higiene update --version` com uma versão anterior válida
- **THEN** os artefatos gerenciados retornam à versão selecionada sem remover exceções locais
