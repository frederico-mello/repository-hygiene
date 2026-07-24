## Context

O projeto já fornece a CLI `repository-hygiene`, o relatório sanitizado em `.repository-hygiene/auditoria.json` e regras globais de isolamento por worktree e PR. A mudança adiciona uma skill OpenCode como fonte normativa do comportamento do agente e um comando `/hygiene` como entrada explícita. O fluxo permanece no agente LLM: a CLI executa as verificações, o relatório fornece o estado auditado e a skill coordena triagem, remediação, re-auditoria e limpeza.

Não haverá novo runtime, serviço, dependência, formato de relatório ou alteração na CLI. A skill não modifica o auditor nem o formato do relatório. O relatório é temporário e deve ser removido ao final de uma execução limpa.

## Goals / Non-Goals

**Goals:**

- Oferecer uma única fonte normativa para o fluxo de higiene do agente.
- Disponibilizar `/hygiene` como entrada explícita, mantendo ativação automática por descrição da skill em pedidos relacionados.
- Consumir `.repository-hygiene/auditoria.json` como fonte canônica após cada auditoria.
- Priorizar achados `error`, agrupar achados por regra e orientar remediação segura.
- Re-auditar após cada lote coerente de correções e só encerrar com estado limpo ou bloqueio explícito.
- Verificar ou inicializar `auditoria.yaml` somente quando necessário, sem sobrescrever configuração existente.
- Remover `.repository-hygiene/auditoria.json` e `.repository-hygiene/` somente após auditoria limpa e conclusão das correções.
- Preservar valores sensíveis mascarados e exigir worktree isolada, push e PR para alterações de código.

**Non-Goals:**

- Alterar código Python, regras, CLI, configuração, formato de relatório ou dependências.
- Criar ou modificar `AGENTS.md` automaticamente.
- Introduzir automação de CI, issues, novos formatos ou chaves de configuração.
- Corrigir problemas de domínio não relacionados à regra que produziu o achado.
- Remover arquivos fora de `.repository-hygiene/` ou aceitar exceções silenciosamente.

## Decisions

### Skill normativa com comando fino

`SKILL.md` será a fonte única das instruções de fluxo, critérios de segurança, matriz de triagem e condições de parada. `.opencode/commands/hygiene.md` fornecerá somente a entrada operacional `/hygiene` e encaminhará para a skill, sem duplicar sua lógica. Isso mantém acionamento explícito sem criar duas fontes divergentes.

### CLI e relatório como fronteira de integração

O agente executará a CLI existente e tratará seu código de saída como sinal inicial: `0` indica auditoria limpa, `1` indica achados e `2` indica erro de configuração ou execução. Depois, sempre lerá o relatório JSON sanitizado. Relatório ausente, inválido ou não confiável interrompe o fluxo; a skill não inferirá achados de saída parcial nem alterará o formato do relatório.

### Fluxo iterativo com ownership no agente

O agente verificará o alvo e a configuração. Se `auditoria.yaml` não existir, poderá inicializá-lo conforme o fluxo suportado pela CLI; se existir, deverá preservá-lo e usá-lo sem sobrescrever. Em seguida executará a auditoria, lerá o relatório, ordenará `error` antes de `warning`, corrigirá somente o necessário e reexecutará a auditoria após cada lote coerente. O estado do repositório e decisões de aceitação permanecem sob controle do agente e do usuário. Correções de código usam worktree isolada, push e PR conforme as regras do projeto.

### Limpeza delimitada e posterior à validação

Após uma auditoria limpa e a conclusão das correções, o agente removerá apenas `.repository-hygiene/auditoria.json` e o diretório `.repository-hygiene/`. Antes da remoção, validará que o caminho está sob a raiz do repositório auditado, não segue caminho externo e contém somente o relatório esperado. Se houver qualquer outro conteúdo, a remoção do diretório será recusada. Falhas, links ou ambiguidade interrompem a limpeza; nenhum modo de remoção ampla ou forçada será usado.

Achados residuais só podem ser classificados como não acionáveis mediante decisão explícita do usuário, acompanhada de justificativa registrada no resultado da execução. Sem essa aceitação, o fluxo termina como bloqueado, não como concluído.

### Validação estrutural, comportamental e de segurança

A validação verificará a estrutura e o front matter dos arquivos OpenCode, cenários de auditoria limpa, erros, avisos, relatório inválido, falha de execução, ausência de progresso e limpeza final. A suíte existente será executada para garantir que a CLI permaneça inalterada. Uma revisão manual confirmará que valores sensíveis não são reproduzidos, que somente o diretório temporário é removido e que o isolamento por worktree é preservado.

### Rollout aditivo e reversível

O rollout adicionará a skill e o comando sem alterar o uso direto da CLI. `/hygiene` será opt-in, enquanto a ativação automática dependerá da descrição da skill. Rollback consiste em reverter os arquivos adicionados; não afeta auditorias anteriores nem o comportamento da CLI.

## Risks / Trade-offs

- [Relatório temporário pode permanecer após falha de limpeza] → Relatar explicitamente a falha e não declarar a limpeza concluída; limitar a remoção ao caminho validado.
- [Agente pode repetir correções sem progresso] → Detectar achado persistente, evitar alterações cegas e tentar alternativa segura ou relatar bloqueio.
- [Valores sensíveis podem ser expostos na resposta do agente] → Usar somente conteúdo sanitizado e proibir reprodução, busca ou reconstrução de valores mascarados.
- [Comando e skill podem divergir] → Manter o comando fino e a skill como única fonte normativa.
- [Limpeza pode remover conteúdo inesperado] → Validar raiz, rejeitar caminhos externos e permitir somente os dois caminhos exatos sob `.repository-hygiene/`.
- [Automação pode alterar arquivos sem intenção do usuário] → Não sobrescrever configuração existente, pausar em alterações ambíguas e exigir worktree/PR para código.
