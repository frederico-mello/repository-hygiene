## 1. Primeiro uso via uvx

- [x] 1.1 Expor fallback de execução por módulo Python e manter entry point `repository-hygiene` no pacote distribuído
- [x] 1.2 Atualizar `README.md` com pré-requisitos e fluxo inicial via `uvx`, incluindo fallback por `pip` e módulo Python
- [x] 1.3 Validar metadados, versão, dependências declaradas e entry points no artefato distribuído
- [x] 1.4 Adicionar smoke tests do artefato local para execução efêmera, criação dos arquivos gerenciados e ausência do pacote no PATH
- [x] 1.5 Cobrir falha de resolução no fluxo efêmero, garantindo status de erro e nenhum arquivo alterado no consumidor
- [x] 1.6 Validar `--help` via entry point e módulo Python, incluindo comandos públicos e seus propósitos
- [x] 1.7 Validar auditoria limpa, auditoria com erro objetivo, relatório mascarado e códigos de saída nos fluxos suportados
- [x] 1.8 Validar setup inicial completo via `uvx` em repositório consumidor descartável

## 2. Uso persistente via uv tool

- [x] 2.1 Documentar instalação persistente isolada, integração explícita do shell e fallback via `uvx`
- [x] 2.2 Adicionar smoke tests do artefato local para instalação persistente e disponibilidade do entry point com diretório de ferramentas configurado
- [x] 2.3 Cobrir diagnóstico quando o diretório de ferramentas estiver fora do PATH, incluindo orientação de recuperação
- [x] 2.4 Validar reinstalação persistente, ausência de instalações conflitantes e preservação da configuração do consumidor
- [x] 2.5 Validar uso recorrente da CLI persistente para `audit` e `install`

## 3. Execução reproduzível multiplataforma

- [x] 3.1 Documentar seleção de versão, atualização explícita, rollback e ausência de atualização silenciosa
- [x] 3.2 Adicionar testes para versão fixada, atualização solicitada e permanência da versão quando nenhuma atualização for solicitada
- [x] 3.3 Configurar validação de empacotamento e instalação em Windows, macOS e Linux com as versões de Python suportadas
- [x] 3.4 Fazer a matriz multiplataforma executar os fluxos `uvx` e `uv tool install` contra o artefato recém-construído
- [x] 3.5 Cobrir Python incompatível, `uv` ausente, repositório inválido e configuração inválida com mensagens acionáveis
- [x] 3.6 Validar documentação final e os fallbacks via `pip` e módulo Python
- [x] 3.7 Validar códigos de saída e ausência de alterações parciais em todos os fluxos de falha
