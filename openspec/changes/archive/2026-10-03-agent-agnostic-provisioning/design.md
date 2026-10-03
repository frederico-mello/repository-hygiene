## Context

O provisionamento (`init.py`) fixa o destino da skill em `.opencode/skills/` nos dois pontos em que ele existe (`_dry_run_msg_skills` e `_instalar_skills`). O escopo da auditoria (`core.py`) fixa, em duas listas separadas, quais caminhos contam como fonte (`_eh_diretorio_fonte`) e quais são ruído de referência (`_em_diretorio_ruidoso_referencias`). O template do workflow fixa os gatilhos `paths`. São três pontos de código com a mesma premissa embutida — o repositório usa OpenCode — enquanto o próprio repositório hospeda cinco agentes e a auditoria acusa os quatro diretórios não cobertos.

## Goals / Non-Goals

**Goals:**

- Provisionar a skill em múltiplos destinos, detectáveis automaticamente e configuráveis explicitamente.
- Tratar os cinco diretórios de agente como escopo de fonte e cobrir commands/skills/workflows deles como ruído de referência, com a mesma granularidade já usada para `.opencode`.
- Fazer o workflow gerado disparar quando qualquer diretório de agente mudar.
- Preservar o comportamento existente: idempotência por destino, `--force`, `--dry-run` e fallback para `.opencode`.

**Non-Goals:**

- Resolver as duas peculiaridades documentadas (a lista `disabled_rules` perdida no mascarador e a chave `conventional_commits` que não dispara) — são changes separadas, fora deste escopo.
- Suportar agentes além dos cinco já hospedados no repositório (`.opencode`, `.kilocode`, `.kilo`, `.omp`, `.hermes`).
- Alterar exit codes, o contrato de saída da auditoria ou o formato do relatório.
- Revisar os requisitos das capacidades `context-aware-audit-findings` e `agent-hygiene-flow` — os ajustes de escopo em `core.py` materializam exigências já declaradas lá.

## Decisions

- **Fonte única dos caminhos de agente:** um módulo pequeno (ex.: `auditoria_higiene/agentes.py`) exporta as cinco raízes suportadas e deriva os prefixos de ruído (`<raiz>/commands/`, `<raiz>/skills/openspec-`, `.kilocode/workflows/`) e de fonte (as próprias raízes). `init.py` e `core.py` importam dele, evitando três listas que divergem com o tempo.
- **Seleção de destinos por detecção, com override:** por padrão provisiona em todas as raízes presentes no repositório alvo; se nenhuma existir, usa `.opencode` (compatibilidade com o comportamento atual e com os testes existentes). A nova flag `--agents` (lista separada por vírgula) restringe a seleção explicitamente.
- **Idempotência por destino:** cada destino é avaliado individualmente (`Skipping (already exists)` por caminho); `--force` substitui em todos os destinos selecionados.
- **Gatilhos explícitos no workflow:** lista explícita dos cinco diretórios nos dois gatilhos, no mesmo estilo da linha atual — previsível e revisável, sem glob que arraste diretórios não desejados.
- **Ruído de referência por prefixo, não por raiz:** mantém-se a granularidade atual (só `commands/` e `skills/openspec-`), para que a skill `agent-hygiene-flow` recém-provisionada continue com suas referências checadas.

## Risks / Trade-offs

- [Ampliar a lista de ruído pode esconder referências quebradas reais em commands/skills de agentes] -> mesmo racional já aceito para `.opencode/commands/`; fica registrado no spec.
- [Repositórios com vários agentes passam a receber a skill em vários diretórios] -> esperado e documentado; idempotente e sem sobrescrita sem `--force`.
- [Sobreposição com a change aberta `reduzir-falsos-positivos-auditoria`] -> se ambas avançarem, reconciliar as listas de classificação de referências antes do merge.
- [As raízes viram contrato] -> manter a lista centralizada torna adicionar um agente futuro uma edição única.

## Migration Plan

1. Atualizar o pacote e rodar `repository-hygiene install` nos repositórios alvo.
2. Conferir, via `--dry-run`, que todos os destinos esperados estão listados e que o install os cria.
3. Rodar a auditoria e confirmar que os diretórios dos agentes deixam de gerar achados espúrios.
4. Rollback: remover os diretórios de skill criados e voltar a versão do pacote — nada migra em dados.

## Open Questions

- A seleção de agentes deve viver só na flag `--agents` ou também em uma chave de `auditoria.yaml`?
- `--agents` deve aceitar exatamente as raízes (`kilocode`) ou também apelidos normalizados?
