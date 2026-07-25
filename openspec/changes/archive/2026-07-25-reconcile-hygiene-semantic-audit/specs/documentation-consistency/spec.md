## ADDED Requirements

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

## MODIFIED Requirements

### Requirement: Documented onboarding flow

O README SHALL apresentar `repository-hygiene --init .` antes da auditoria como fluxo recomendado para um repositório ainda não configurado, incluindo revisão de `auditoria.yaml` antes da primeira auditoria. O README SHALL documentar que a reconciliação semântica utiliza documentos OpenSpec, documentação OpenWiki e grafo de conhecimento quando disponíveis para reduzir falsos-positivos.

#### Scenario: New repository follows documented setup

- **WHEN** um usuário instala o pacote e segue o fluxo recomendado do README
- **THEN** ele encontra inicialização, revisão da configuração e execução de `repository-hygiene .` nessa ordem

#### Scenario: User understands semantic reconciliation sources

- **WHEN** um usuário consulta o README sobre como a auditoria classifica conteúdo
- **THEN** o README descreve que documentos OpenSpec, documentação OpenWiki e o grafo de conhecimento são usados como evidência semântica quando disponíveis
