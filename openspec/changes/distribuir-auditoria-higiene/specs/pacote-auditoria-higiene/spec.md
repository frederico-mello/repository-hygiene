## ADDED Requirements

### Requirement: Pacote instalável

O projeto MUST publicar um pacote Python instalável via `pip install auditoria-higiene`, com versão identificável e dependências declaradas.

#### Scenario: Instalação em ambiente Python
- **WHEN** o desenvolvedor instala o pacote em um ambiente Python suportado
- **THEN** a instalação termina com sucesso e disponibiliza o comando `auditoria-higiene`

### Requirement: Execução local

O comando MUST executar a auditoria no repositório informado, usando sua configuração local e retornando código diferente de zero quando houver erro objetivo.

#### Scenario: Auditoria local com erro
- **WHEN** `auditoria-higiene audit` encontra um problema objetivo
- **THEN** imprime relatório mascarado e termina com status de falha

#### Scenario: Auditoria local limpa
- **WHEN** `auditoria-higiene audit` não encontra erros objetivos
- **THEN** imprime o relatório e termina com status de sucesso

### Requirement: CLI documentada

A CLI MUST disponibilizar ajuda para os comandos públicos e mensagens de erro acionáveis para ambiente inválido, repositório ausente ou configuração inválida.

#### Scenario: Ajuda solicitada
- **WHEN** o desenvolvedor executa `auditoria-higiene --help`
- **THEN** a saída lista os comandos disponíveis e seu propósito
