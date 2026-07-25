## Why

A auditoria está confundindo conteúdo realmente excedente com conteúdo válido ou necessário. Um repositório `quiz` clonado acidentalmente dentro de `principal-tarefas-aleatorias` foi tratado como padrão a ser ignorado, embora devesse ser removido; da mesma forma, workflows necessários ao GitHub Actions estão sendo apresentados como inseguros sem considerar seu propósito e escopo. Isso reduz a confiança nos achados e pode orientar a limpeza para ações incorretas.

A limpeza precisa combinar evidências estruturais e semânticas antes de recomendar remoção, preservação, correção ou aceitação explícita de um achado.

## What Changes

- Distinguir conteúdo estranho ou acidental que deve ser removido de artefatos gerados que devem ser ignorados.
- Avaliar diretórios aninhados que parecem repositórios clonados, incluindo seu relacionamento com o repositório auditado, antes de recomendar qualquer alteração no `.gitignore`.
- Avaliar workflows pelo propósito, pelos eventos, pelas permissões efetivamente usadas e pelo escopo necessário ao GitHub Actions, reduzindo falsos-positivos de segurança sem ocultar permissões amplas ou não justificadas.
- Cruzar documentos OpenSpec, documentação OpenWiki e evidências do Graphify para identificar conteúdo sobrando, referências faltantes, relações sem documentação e mudanças planejadas que ainda não foram aplicadas.
- Produzir recomendações explicáveis, separando remoção, preservação, correção, investigação adicional e falso-positivo aceito.
- Preservar o relatório canônico e a possibilidade de reauditoria após cada correção, sem remover conteúdo apenas por ausência de referência textual.
- Fora do escopo: apagar automaticamente conteúdo ambíguo, reescrever documentos OpenSpec existentes, modificar o Graphify, ou alterar a estrutura de diretórios de outros repositórios que não o auditado.

## Capabilities

### New Capabilities
- `semantic-repository-reconciliation`: Reconciliação semântica entre estrutura do repositório, documentos de planejamento, documentação relacionada e grafo de conhecimento para classificar conteúdo excedente, ausente, necessário ou ambíguo.

### Modified Capabilities
- `context-aware-audit-findings`: Os achados de artefatos, arquivos sem referência, documentação desatualizada e workflows inseguros passam a considerar evidências de relacionamento e intenção antes de recomendar ação.
- `agent-hygiene-flow`: O fluxo de remediação passa a distinguir remoção de conteúdo acidental, inclusão de padrões para artefatos gerados e aceitação documentada de falsos-positivos, sempre com reauditoria.
- `documentation-consistency`: A verificação de consistência passa a considerar documentos OpenSpec, OpenWiki e relações relevantes do grafo, além da documentação textual convencional.

## Impact

- Afeta as regras de classificação e o modelo de evidências do auditor em `src/`.
- Afeta a interpretação de diretórios aninhados, referências de arquivos, artefatos gerados e workflows em repositórios auditados.
- Afeta `auditoria.yaml`, relatórios JSON e as recomendações exibidas ao agente.
- Afeta os testes de regressão para o caso `quiz` em `principal-tarefas-aleatorias` e para workflows legítimos do GitHub Actions.
- Afeta as instruções e os artefatos OpenSpec relacionados ao fluxo de higiene, consistência documental e achados contextuais.
- Não deve apagar automaticamente conteúdo ambíguo nem desativar regras de segurança sem evidência e justificativa registradas.
