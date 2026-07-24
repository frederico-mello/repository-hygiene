## Purpose

Define the official installation and execution flows of the `repository-hygiene` CLI based on `uv`, covering ephemeral use via `uvx`, persistent installation via `uv tool install`, and multi-platform validation.

## Requirements

### Requirement: Fluxo efêmero com uvx

O projeto MUST documentar e suportar execução da CLI por `uvx repository-hygiene`, com resolução em ambiente isolado e sem depender do `PATH` do executável persistente do pacote.

#### Scenario: Primeiro uso sem instalação global
- **GIVEN** o usuário possui `uv` instalado e Python compatível disponível
- **WHEN** executa `uvx repository-hygiene install .`
- **THEN** a CLI executa o setup, cria `auditoria.yaml` e `.github/workflows/repository-hygiene.yml`, e termina com status de sucesso
- **AND** o pacote não precisa ser instalado globalmente para essa execução

#### Scenario: Diretório persistente fora do PATH
- **GIVEN** o diretório de ferramentas persistentes do `uv` não está no `PATH`
- **WHEN** o usuário executa `uvx repository-hygiene audit .`
- **THEN** a auditoria é executada com sucesso ou retorna o resultado da auditoria
- **AND** a execução não depende da descoberta global de `repository-hygiene`

#### Scenario: Falha ao resolver pacote
- **GIVEN** o pacote não pode ser obtido ou suas dependências não podem ser resolvidas
- **WHEN** o usuário executa o fluxo `uvx`
- **THEN** o comando termina com status diferente de zero e mostra causa acionável
- **AND** nenhum arquivo do repositório consumidor é alterado

### Requirement: Fluxo persistente com uv

O projeto MUST documentar e suportar instalação persistente da CLI por `uv tool install repository-hygiene`, mantendo ambiente isolado e explicando a condição necessária para o comando curto ficar disponível no shell.

#### Scenario: Ferramenta persistente disponível
- **GIVEN** o diretório de ferramentas do `uv` está integrado ao `PATH`
- **WHEN** o usuário instala `repository-hygiene` como ferramenta persistente
- **THEN** o comando `repository-hygiene` fica disponível em uma nova execução do shell
- **AND** usa a mesma implementação da CLI distribuída pelo pacote

#### Scenario: Ferramenta persistente fora do PATH
- **GIVEN** a instalação persistente foi concluída
- **AND** o diretório de ferramentas não está no `PATH`
- **WHEN** o usuário consulta a documentação de diagnóstico do fluxo persistente
- **THEN** a documentação orienta integração explícita do shell com `uv tool update-shell`
- **AND** oferece `uvx repository-hygiene` como alternativa funcional

### Requirement: Versão e diagnóstico de instalação

A documentação MUST distinguir execução conveniente sem versão fixa de execução reproduzível com versão explícita, informar o requisito de Python e descrever recuperação para `uv` ausente, Python incompatível, falha de resolução e diretório de ferramentas fora do `PATH`.

#### Scenario: Execução reproduzível
- **GIVEN** uma automação exige comportamento determinístico
- **WHEN** o usuário consulta o fluxo recomendado para automação
- **THEN** encontra instrução para selecionar uma versão explícita do pacote

#### Scenario: Requisito de Python incompatível
- **GIVEN** a versão de Python não atende ao requisito do pacote
- **WHEN** o usuário tenta instalar ou executar a CLI
- **THEN** o fluxo termina com status diferente de zero e informa o requisito incompatível

#### Scenario: uv ausente
- **GIVEN** o usuário tenta usar um fluxo oficial sem `uv` instalado
- **WHEN** consulta a documentação de instalação
- **THEN** encontra instrução para instalar `uv` antes de repetir o fluxo

### Requirement: Atualização controlada

A documentação MUST explicar como atualizar, fixar e reverter a versão usada pela CLI, e os fluxos persistentes MUST exigir ação explícita para atualização.

#### Scenario: Atualização explícita
- **GIVEN** uma versão mais nova do pacote está disponível
- **WHEN** o usuário consulta o fluxo de atualização da instalação persistente
- **THEN** encontra um procedimento explícito para selecionar e instalar a nova versão

#### Scenario: Nenhuma atualização silenciosa
- **GIVEN** o usuário instalou uma versão persistente da CLI
- **WHEN** executa a CLI novamente sem solicitar atualização
- **THEN** a versão instalada permanece selecionada

#### Scenario: Versão fixada para automação
- **GIVEN** uma automação exige comportamento reproduzível
- **WHEN** o usuário consulta o fluxo de automação
- **THEN** encontra instrução para executar uma versão explícita do pacote

### Requirement: Validação multiplataforma

Os fluxos oficiais MUST ser validados em Windows, macOS e Linux usando o artefato distribuível da própria mudança, sem depender acidentalmente de uma versão já publicada.

#### Scenario: Smoke test em sistema suportado
- **GIVEN** o artefato distribuível foi construído para o sistema operacional em teste
- **WHEN** a suíte de smoke tests executa os fluxos `uvx` e `uv tool install`
- **THEN** valida instalação, execução da CLI e disponibilidade do entry point
- **AND** usa o artefato recém-construído

#### Scenario: Matriz de sistemas operacionais
- **GIVEN** a matriz de CI contém Windows, macOS e Linux
- **WHEN** a validação da change é executada
- **THEN** cada sistema suportado executa os fluxos oficiais

#### Scenario: Instalação repetida
- **GIVEN** o fluxo de instalação já foi executado no mesmo ambiente
- **WHEN** o usuário executa o fluxo novamente
- **THEN** a instalação permanece válida e não cria instalações concorrentes ou conflitantes

#### Scenario: Falha durante setup
- **GIVEN** a CLI falha antes de concluir `install`
- **WHEN** o fluxo termina
- **THEN** retorna status diferente de zero e não deixa arquivos parcialmente gerados no repositório consumidor
