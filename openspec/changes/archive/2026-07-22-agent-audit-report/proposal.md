## Why

O auditor atualmente imprime o relatório completo no terminal, o que é útil para pessoas, mas não deixa um artefato persistente e estruturado para um agente LLM analisar depois da execução. O comando padrão deve continuar oferecendo feedback imediato ao usuário, enquanto também disponibiliza uma fonte JSON sanitizada e estável para análise automatizada.

## What Changes

- **BREAKING** Alterar a saída padrão da auditoria para exibir um resumo curto no terminal em vez do relatório completo; consumidores que precisam do relatório completo deverão selecionar um formato de relatório explicitamente ou ler o arquivo JSON.
- Gerar automaticamente um relatório JSON sanitizado em diretório próprio do auditor.
- Permitir caminho de saída personalizado quando o consumidor precisar armazenar o relatório em outro local.
- Preservar os formatos de relatório existentes para usos explícitos e integrações atuais.
- Documentar instrução opcional para `AGENTS.md`, orientando agentes a lerem o relatório JSON, priorizarem erros e executarem nova auditoria após correções.
- Manter códigos de saída e semântica dos achados existentes.
- Não executar correções automáticas, não executar agentes LLM e não ampliar o conjunto de regras de auditoria como parte desta mudança.

## Capabilities

### New Capabilities

- `agent-friendly-audit-report`: Geração de relatório JSON persistente e resumo terminal para consumo humano e por agentes LLM.

### Modified Capabilities


## Impact

- Afeta a experiência de saída da CLI e o fluxo de geração de relatórios.
- Afeta documentação de uso e orientação opcional para agentes de código.
- Afeta testes de integração da CLI e testes dos formatos de relatório.
- Não adiciona dependências de runtime nem serviços externos.
- O relatório padrão será sanitizado antes de ser persistido e deverá ser tratado como artefato gerado, não como fonte versionada do projeto.
