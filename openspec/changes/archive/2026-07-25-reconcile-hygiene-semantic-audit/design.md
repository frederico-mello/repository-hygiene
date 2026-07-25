## Context

O auditor de higiene opera como CLI Python (`repository-hygiene`), com núcleo monolítico em `src/auditoria_higiene/core.py` (~916 linhas). As regras são despachadas por `_avaliar_regra()` via cadeia `if/elif`, cada uma em sua função. O modelo de resultado é um dicionário com `regra`, `caminho`, `severidade`, `mensagem` e `recomendacao`. A configuração (`auditoria.yaml`) define regras habilitadas, severidades e exceções por regra.

A auditoria atual classifica arquivos não rastreados como artefatos, verifica referências textuais e avalia permissões de workflow contra uma lista fixa de escopos permitidos. Não considera a diferença entre um clone acidental de repositório e um artefato gerado, nem cruza documentos de planejamento para decidir se um arquivo é excedente ou necessário.

## Goals / Non-Goals

**Goals:**

- Detectar repositórios aninhados acidentais e recomendar remoção em vez de adição ao `.gitignore`
- Avaliar permissões de workflow pelo propósito e uso efetivo, não por lista fixa de escopos
- Cruzar documentos OpenSpec, OpenWiki e Graphify como evidência semântica para classificação de conteúdo
- Expandir o modelo de resultado com taxonomia de recomendações (remove, add-to-gitignore, fix-reference, investigate, accept-false-positive etc.)
- Manter retrocompatibilidade com `auditoria.yaml` existente

**Non-Goals:**

- Reescrever o núcleo monolítico (refatoração estrutural fica para outra mudança)
- Modificar o Graphify ou o OpenWiki
- Implementar remoção automática de conteúdo
- Alterar o formato do relatório JSON canônico

## Decisions

### 1. Detecção de repositórios aninhados como função separada

Nova função `_verificar_repositorios_aninhados()` inspeciona diretórios não rastreados (`git ls-files --others --directory`) verificando a presença de `.git` interno. Se encontrado, consulta `.gitmodules` e `.gitignore` para classificar como acidental, submodule ou ignorado.

**Alternativa considerada:** Modificar `_verificar_artefatos` para incluir lógica de nested repo. Rejeitada — misturaria duas semânticas distintas (artefato gerado vs clone acidental) e complicaria a regra existente.

**Rationale:** Separação clara de responsabilidades. A nova regra `repositorios_aninhados` é independente, com severidade `error` e recomendação `remove`.

### 2. Leitura de fontes semânticas via módulo dedicado

Novo módulo `src/auditoria_higiene/semantic.py` com funções para:
- `carregar_referencias_openspec(raiz)` — coleta paths mencionados em `openspec/specs/**/*.md` e `openspec/changes/**/*.md`
- `carregar_referencias_openwiki(caminho_openwiki)` — coleta paths de documentação OpenWiki, se configurada
- `carregar_referencias_graphify(caminho_graph)` — coleta nodes do `graphify-out/graph.json`, se configurado
- `montar_evidencias(raiz, config)` — orquestra as três fontes e retorna dicionário path→evidências

As funções existentes (`_verificar_sem_referencia`, `_verificar_artefatos`, `_verificar_documentacao`) passam a consultar as evidências semânticas antes de emitir achados.

**Alternativa considerada:** Adicionar lógica inline em cada função existente. Rejeitada — duplicaria código de parsing de OpenSpec/Graphify em múltiplos pontos.

**Rationale:** Módulo separado permite testar a montagem de evidências isoladamente e estender fontes semânticas sem tocar nas regras.

### 3. Avaliação de workflow por propósito

Modificar `_analisar_workflow()` para, além de checar `permissions`, inspecionar `jobs.*.steps` e `on` (eventos) do workflow:
- Se `issues: write` está presente e há steps que usam `actions/github-script` com `github.rest.issues` ou GitHub CLI com `gh issue`, classificar como justificado
- Se `contents: write` está presente e o workflow tem evento `release` ou step de `actions/create-release`, classificar como justificado
- `write-all` ou `permissions: write-all` (string) continuam sendo reportados como alta confiança

A configuração `permissoes_write_permitidas` em `auditoria.yaml` continua funcionando como fallback para escopos não analisáveis automaticamente.

**Alternativa considerada:** Adicionar mais escopos à lista `permissoes_write_permitidas`. Rejeitada — não escala; cada repositório teria que configurar manualmente.

**Rationale:** A análise de steps captura a intenção real do workflow sem exigir configuração adicional.

### 4. Configuração expansível para fontes semânticas

Adicionar seção opcional `fontes_semanticas` ao `auditoria.yaml`:

```yaml
fontes_semanticas:
  openwiki: null           # caminho para wiki ou null se indisponível
  graphify: null           # caminho para graphify-out/ ou null
  openspec: true           # sempre habilitado se openspec/ existir
```

Inicialização via `--init` não adiciona a seção (retrocompatível). O auditor funciona com defaults quando ausente.

**Rationale:** Separa fontes externas da configuração de regras. Documenta a dependência opcional sem quebrar repositórios sem OpenWiki ou Graphify.

### 5. Taxonomia de recomendações no modelo de resultado

Cada resultado ganha campo `recomendacao` com um dos valores:

| Valor | Significado |
|---|---|
| `remove` | Conteúdo deve ser removido (clone acidental, órfão confirmado) |
| `add-to-gitignore` | Artefato gerado deve ser coberto por `.gitignore` |
| `fix-reference` | Referência quebrada deve ser corrigida |
| `update-documentation` | Documentação desatualizada deve ser atualizada |
| `add-ci-integration` | Configuração sem integração CI |
| `archive-change` | Mudança OpenSpec parada deve ser arquivada |
| `scope-permissions` | Workflow com permissão ampla deve ser restrito |
| `investigate` | Conteúdo ambíguo requer investigação manual |
| `accept-false-positive` | Falso-positivo documentado e aceito |

O campo `recomendacao` já existe em alguns resultados; a mudança o torna obrigatório e tipado.

**Rationale:** Permite ao agente de remediação decidir a ação correta sem interpretar mensagens textuais.

## Risks / Trade-offs

- **Falsos-positivos residuais em nested repos:** Diretórios com `.git` podem ser submodules sem `.gitmodules` (caso raro) → Mitigação: classificar como `investigate` em vez de `remove` quando há ambiguidade
- **Graphify indisponível:** Se `graphify-out/graph.json` não existir, a fonte é silenciosamente ignorada → Mitigação: logar ausência no campo `evidencias` do resultado
- **Workflow analysis incompleta:** Steps dinâmicos (matriz, expressões) podem escapar da análise estática → Mitigação: `permissoes_write_permitidas` permanece como fallback configurável
- **Performance na leitura de OpenSpec:** Parsing de todos os arquivos `openspec/specs/` e `openspec/changes/` a cada auditoria → Mitigação: cache em memória similar ao `_TRACKED_CACHE` existente
- **Retrocompatibilidade de configuração:** `auditoria.yaml` sem `fontes_semanticas` deve funcionar → Mitigação: defaults aplicados quando seção ausente
