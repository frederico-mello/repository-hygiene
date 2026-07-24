## Why

O projeto já entrega um relatório de auditoria persistente e sanitizado (`.repository-hygiene/auditoria.json`) e um snippet opcional de `AGENTS.md` (README:158-164) que orienta agentes a lerem esse relatório. Contudo, não existe uma skill que **orquestre o fluxo completo de higiene** — da detecção de configuração ao estado limpo — deixando cada agente LLM improvisar a sequência (garantir `auditoria.yaml`, executar a auditoria, ler o JSON, priorizar `error` sobre `warning`, remediar conforme a semântica de cada regra, isolar edições, re-auditar, convergir). Sem orquestração padronizada, agentes pulam a re-auditoria, corrigem no branch errado, expõem valores sensíveis ou tratam avisos como bloqueadores. A camada de orquestração é a peça faltante agora que o relatório JSON e o fluxo de worktree estão estáveis.

## What Changes

- Adicionar uma **skill OpenCode** (somente instrução, sem código) em `.opencode/skills/agent-hygiene-flow/` que define o loop de remediação de higiene para agentes LLM: verificar/inicializar `auditoria.yaml`, executar `repository-hygiene`, ler `.repository-hygiene/auditoria.json` como fonte canônica, triar achados por severidade, remediar cada tipo de achado conforme a semântica da regra correspondente, re-auditar após correções e só terminar quando a auditoria estiver limpa ou quando os achados residuais forem explicitamente aceitos como não acionáveis.
- Adicionar um **comando gatilho** `/hygiene` em `.opencode/commands/` como ponto de entrada explícito para o fluxo, complementado pela `description` da skill para que ela também carregue automaticamente em pedidos relacionados a higiene, auditoria ou limpeza do repositório.
- Documentar, dentro da skill, a **tabela de triagem por regra** mapeando cada regra (`segredos_rastreados`, `links_internos_quebrados`, `referencias_inexistentes`, `artefatos_fora_gitignore`, `gitkeep_sem_conteudo`, `arquivos_sem_referencia`, `documentacao_desatualizada`, `configuracao_sem_integracao`, `openspec_parada`, `workflows_inseguros`) à ação esperada de remediação e à severidade que bloqueia (error) ou apenas informa (warning).
- Incorporar as regras globais do projeto na skill: qualquer edição de código motivada por achado ocorre em worktree isolada via `git-wt` seguida de push e PR; valores sensíveis mascarados no relatório nunca são reexibidos; achados `error` são prioridade máxima.
- Definir os critérios de parada do loop: auditoria retorna código de saída `0` (limpa), ou o agente esgota remediações acionáveis e relata o estado residual ao usuário sem prosseguir cegamente.

## Capabilities

### New Capabilities

- `agent-hygiene-flow`: Comportamento esperado de um agente LLM que gerencia o fluxo de higiene do repositório — execução da auditoria, consumo do relatório JSON canônico, triagem por severidade e regra, remediação isolada, re-auditoria e convergência para estado limpo.

### Modified Capabilities

(vazio — a skill consome a capacidade `agent-friendly-audit-report` já entregue, sem alterar sua especificação.)

## Impact

- Adiciona arquivos de documentação/skill sob `.opencode/` (skill + comando gatilho); nenhum código-fonte Python, regra, CLI, formato de relatório, schema de configuração ou dependência é modificado.
- Afeta como agentes autônomos interagem com o repositório ao receberem pedidos de higiene/auditoria/limpeza; é consumidora direta da capacidade `agent-friendly-audit-report` já publicada.
- Sem impacto em APIs, empacotamento, versão (`versao_configuracao`) ou códigos de saída existentes; sem breaking changes.
- Edits motivados por achados seguem o fluxo global de worktree + PR; a skill apenas codifica essa exigência, não a introduz.
