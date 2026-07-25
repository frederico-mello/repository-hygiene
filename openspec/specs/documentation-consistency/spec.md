# Documentation Consistency

## Purpose

Garantir que a documentação de uso, exemplos de configuração e templates de integração permaneçam coerentes com a implementação atual da CLI e do pacote.

## Requirements

### Requirement: Documented onboarding flow
O README SHALL apresentar `repository-hygiene --init .` antes da auditoria como fluxo recomendado para um repositório ainda não configurado, incluindo revisão de `auditoria.yaml` antes da primeira auditoria. O README SHALL documentar que a reconciliação semântica utiliza documentos OpenSpec, documentação OpenWiki e grafo de conhecimento quando disponíveis para reduzir falsos-positivos.

#### Scenario: New repository follows documented setup
- **WHEN** um usuário instala o pacote e segue o fluxo recomendado do README
- **THEN** ele encontra inicialização, revisão da configuração e execução de `repository-hygiene .` nessa ordem

#### Scenario: User understands semantic reconciliation sources
- **WHEN** um usuário consulta o README sobre como a auditoria classifica conteúdo
- **THEN** o README descreve que documentos OpenSpec, documentação OpenWiki e o grafo de conhecimento são usados como evidência semântica quando disponíveis

### Requirement: CLI documentation matches implementation
O README SHALL document somente opções e comportamentos presentes na CLI atual, incluindo relatório padrão, formatos explícitos, `--output`, `--force`, `--install-hook` e `--pre-commit` quando aplicável.

#### Scenario: User selects an explicit report format
- **WHEN** o usuário executa a CLI com `--format text`, `--format json` ou `--format sarif`
- **THEN** o README descreve que o formato selecionado é emitido no terminal e pode ser salvo com `--output`

### Requirement: Generated workflow handles audit failures
O template de workflow SHALL preservar o código de saída da auditoria, publicar o relatório mesmo quando a auditoria retorna código 1 ou 2 e executar a gestão de issue conforme as condições documentadas.

#### Scenario: Audit finds errors in generated workflow
- **WHEN** o workflow gerado executa uma auditoria que retorna código 1
- **THEN** a etapa de auditoria registra `exit_code=1`, a etapa de resumo publica o relatório e a etapa de issue pode criar ou atualizar a issue fora de pull requests

#### Scenario: Audit fails due to configuration or execution
- **WHEN** o workflow gerado executa uma auditoria que retorna código 2
- **THEN** o relatório ainda é publicado e o código 2 permanece disponível para as condições posteriores do workflow

### Requirement: Configuration examples match template
O exemplo de `auditoria.yaml` no README SHALL incluir ou explicar as opções de configuração suportadas pelo template oficial quando elas alterarem o comportamento das regras, incluindo padrões de artefatos e permissões write permitidas.

#### Scenario: User configures workflow permission exception
- **WHEN** o usuário consulta o exemplo de configuração para permitir uma permissão write necessária
- **THEN** o README apresenta `permissoes_write_permitidas` dentro de `workflows_inseguros` ou explica seu uso

### Requirement: Documentation verification includes planning documents and knowledge graph

The auditor SHALL verify documentation consistency against OpenSpec documents in `openspec/specs/` and `openspec/changes/`, OpenWiki documentation when available, and knowledge graph nodes when a graph is present. References to files, directories, or commands described in documentation SHALL be checked against the repository structure.

#### Scenario: OpenSpec spec references a missing file
- **WHEN** an OpenSpec spec describes a file that does not exist in the repository
- **THEN** the auditor SHALL report a documentation inconsistency
- **AND** the auditor SHALL include the source document path and the expected file path

#### Scenario: OpenWiki entry is consistent with repository structure
- **WHEN** an OpenWiki entry references files and directories that exist in the repository
- **THEN** the auditor SHALL NOT report a documentation inconsistency
- **AND** the auditor SHALL confirm consistency in the audit trail

#### Scenario: Knowledge graph node references missing symbols
- **WHEN** the knowledge graph contains a node for a symbol that is not present in the current repository state
- **THEN** the auditor SHALL report stale knowledge
- **AND** the auditor SHALL recommend regenerating the knowledge graph
