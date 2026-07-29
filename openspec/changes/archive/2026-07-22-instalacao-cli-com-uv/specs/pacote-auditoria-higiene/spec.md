## MODIFIED Requirements

### Requirement: Pacote instalável

O projeto MUST publicar um pacote Python instalável via `pip install repository-hygiene`, com versão identificável, dependências declaradas, entry point `repository-hygiene` e suporte à execução por módulo Python, `uvx` e `uv tool install`.

#### Scenario: Instalação em ambiente Python
- **GIVEN** o desenvolvedor usa uma versão suportada de Python
- **WHEN** instala `repository-hygiene` via `pip`
- **THEN** a instalação termina com sucesso, registra o entry point `repository-hygiene` no ambiente Python e permite execução por `python -m repository_hygiene`

#### Scenario: Execução efêmera do pacote
- **GIVEN** `uv` está instalado e Python atende ao requisito do pacote
- **WHEN** o desenvolvedor executa a CLI por meio de `uvx`
- **THEN** a CLI é resolvida e executada em ambiente isolado sem exigir instalação global permanente do pacote

#### Scenario: Execução pelo módulo Python
- **GIVEN** o pacote está instalado no ambiente Python atual
- **WHEN** o desenvolvedor executa `python -m repository_hygiene --help`
- **THEN** a saída lista os comandos públicos e termina com status de sucesso

#### Scenario: Instalação persistente isolada
- **GIVEN** `uv` está instalado
- **WHEN** o desenvolvedor instala o pacote como ferramenta persistente
- **THEN** o pacote é instalado em ambiente isolado gerenciado pelo `uv`

### Requirement: Execução local

O comando MUST executar a auditoria no repositório informado, usando sua configuração local e retornando código diferente de zero quando houver erro objetivo, independentemente de a CLI ser iniciada pelo entry point global, por `uvx` ou pelo módulo Python.

#### Scenario: Auditoria local com erro
- **GIVEN** o repositório contém um problema objetivo configurado como erro
- **WHEN** o desenvolvedor executa `audit` por qualquer fluxo de CLI suportado
- **THEN** imprime relatório mascarado e termina com status de falha

#### Scenario: Auditoria local limpa
- **GIVEN** o repositório não contém erros objetivos
- **WHEN** o desenvolvedor executa `audit` por qualquer fluxo de CLI suportado
- **THEN** imprime o relatório e termina com status de sucesso

### Requirement: CLI documentada

A CLI MUST disponibilizar ajuda para os comandos públicos, documentar os fluxos `uvx`, `uv tool install`, `pip` e módulo Python, e fornecer mensagens de erro acionáveis para ambiente inválido, repositório ausente, configuração inválida ou comando não encontrado.

#### Scenario: Ajuda solicitada
- **GIVEN** a CLI está disponível por um fluxo suportado
- **WHEN** o desenvolvedor solicita `--help`
- **THEN** a saída lista os comandos disponíveis e seu propósito

#### Scenario: Repositório ausente
- **GIVEN** o caminho informado não corresponde a um diretório existente
- **WHEN** o desenvolvedor executa um comando que requer repositório
- **THEN** a CLI termina com status diferente de zero e informa o caminho inválido

#### Scenario: Configuração inválida
- **GIVEN** o repositório contém configuração inválida
- **WHEN** o desenvolvedor executa `audit`
- **THEN** a CLI termina com status diferente de zero e informa a necessidade de corrigir a configuração

#### Scenario: Comando global não encontrado
- **GIVEN** o diretório de ferramentas persistentes não está no `PATH`
- **WHEN** o desenvolvedor consulta a documentação do fluxo persistente
- **THEN** encontra a recuperação por integração explícita do shell e o fallback via `uvx`
