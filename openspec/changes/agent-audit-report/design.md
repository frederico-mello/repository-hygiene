## Context

O auditor atualmente executa a auditoria e imprime um relatório completo no terminal. O resultado já possui serializadores para texto, JSON e SARIF, além de sanitização antes da apresentação. O novo fluxo precisa atender dois consumidores no mesmo comando: usuário humano, que precisa de feedback rápido, e agente LLM, que precisa de um artefato estruturado e persistente.

A mudança afeta a apresentação da CLI, a persistência de relatórios e a documentação de integração com agentes. Códigos de saída, regras de auditoria, configurações existentes e formatos explícitos devem permanecer semanticamente compatíveis.

## Goals / Non-Goals

**Goals:**

- Exibir resumo curto no terminal no comando padrão.
- Gerar relatório JSON sanitizado em diretório padrão próprio do auditor.
- Permitir caminho de saída personalizado.
- Preservar relatórios completos quando `--format` for informado explicitamente.
- Manter códigos de saída baseados no resultado da auditoria.
- Documentar integração manual e opcional com `AGENTS.md`.
- Evitar falso achado causado pelo próprio diretório de relatório.

**Non-Goals:**

- Executar agentes LLM ou interpretar automaticamente o relatório.
- Corrigir achados automaticamente.
- Adicionar regras de auditoria.
- Adicionar dependências ou serviços externos.
- Alterar `AGENTS.md`, `.gitignore` ou qualquer arquivo do projeto automaticamente.
- Criar migração de dados ou formato adicional além dos serializadores existentes.

## Decisions

- **Separar resumo, relatório e persistência.** A CLI coordenará apresentação e gravação; os serializadores existentes continuarão responsáveis pelo conteúdo de texto, JSON e SARIF; um escritor de arquivo tratará a persistência de conteúdo já serializado.
- **Executar auditoria e sanitização uma vez.** O resultado será produzido uma vez e sanitizado antes de qualquer saída. O modo padrão serializará JSON, gravará o arquivo padrão e exibirá resumo com status, contagem de erros, contagem de avisos e caminho do relatório.
- **Distinguir formato omitido de formato explícito.** A CLI tratará ausência de `--format` como modo padrão, mesmo que a implementação interna use um valor sentinela diferente. Nesse modo, a saída será resumo mais JSON padrão. `--format text`, `--format json` e `--format sarif` explícitos continuarão enviando relatório completo ao terminal.
- **Definir saída padrão e `--output`.** O arquivo padrão será `.repository-hygiene/auditoria.json`, relativo ao diretório auditado. `--output` sem `--format` gravará JSON no caminho indicado e manterá o resumo no terminal; `--output` com `--format` gravará o formato selecionado e manterá a saída completa explícita no terminal. Caminhos relativos serão resolvidos contra o diretório auditado.
- **Usar relatório JSON versionado como interface de agente.** O arquivo padrão conterá `schema_version` numérico, versão do auditor, timestamp UTC, diretório auditado normalizado e o resultado sanitizado da execução atual. Campos de resultado existentes serão preservados; novos metadados serão aditivos. O relatório será substituído a cada execução.
- **Sanitizar todos os campos livres persistidos.** Mensagens, evidências, recomendações e metadados derivados de entrada serão submetidos à política de sanitização antes da serialização; caminhos serão normalizados sem alterar sua utilidade para o agente. O relatório não armazenará o resultado bruto.
- **Reservar diretório de saída padrão.** `.repository-hygiene/` será tratado como artefato gerado pelo próprio auditor e excluído da detecção de artefatos fora do controle esperado, evitando falso achado na execução seguinte. Caminhos personalizados não serão excluídos automaticamente e serão responsabilidade do consumidor adicionar ao `.gitignore` quando apropriado.
- **Validar persistência separadamente da auditoria.** O diretório pai padrão será criado quando necessário. Caminho personalizado exigirá diretório pai existente; caminho inválido ou não gravável será erro de execução. A gravação será atômica para evitar arquivo JSON truncado.
- **Manter o modo pre-commit isolado.** `--pre-commit` não gerará relatório padrão no snapshot temporário nem alterará o comportamento de saída do hook por causa desta mudança. Persistência nesse modo somente ocorrerá quando `--output` for informado explicitamente, usando JSON por padrão ou o formato explicitamente selecionado.
- **Manter códigos de saída.** Achados de severidade `error` continuam retornando `1`; erros de configuração, execução ou persistência retornam `2`; auditoria sem erros retorna `0`.
- **Documentar integração sem alterar arquivos do consumidor.** O README fornecerá bloco opcional para `AGENTS.md`, orientando o agente a ler o JSON, priorizar erros, não expor dados sensíveis e executar nova auditoria após correções.
- **Tratar mudança padrão como breaking change documentada.** Scripts que dependem do relatório completo no `stdout` deverão usar um formato explícito; o resumo padrão não será uma interface de integração.
- **Migrar sem estado persistido.** Não haverá migração de arquivos existentes. Para rollback comportamental, consumidores usarão `--format text`; a documentação apresentará essa forma de compatibilidade.
- **Escolher o modo padrão sobre alternativas.** Resumo mais JSON automático foi escolhido em vez de JSON no terminal por preservar feedback humano, e em vez de geração apenas opt-in por atender ao fluxo de agentes sem exigir flag adicional.

## Risks / Trade-offs

- [Consumidores que parseiam o `stdout` padrão podem quebrar] → Documentar a mudança como breaking e indicar `--format` explícito para manter relatório completo.
- [Relatório pode conter caminhos e mensagens sensíveis, mesmo sem segredos detectados] → Persistir somente resultado sanitizado, sobrescrever o arquivo anterior e orientar agentes a não reproduzir valores sensíveis.
- [Falha de gravação pode ser confundida com auditoria limpa] → Tratar falha de persistência como erro de execução e retornar código `2`.
- [Diretório padrão pode ser classificado como artefato não rastreado] → Reservar o diretório do próprio auditor na detecção de artefatos e documentá-lo como saída gerada local.
- [Dois consumidores podem exigir formatos diferentes] → Manter `--format` e `--output` para usos explícitos, enquanto o comando padrão otimiza simultaneamente feedback humano e análise por agente.
- [Relatórios personalizados podem ser versionados acidentalmente] → Documentar que `--output` personalizado não é ignorado automaticamente e recomendar entrada correspondente no `.gitignore`.
- [Execução pre-commit pode usar snapshot temporário] → Não gerar arquivo padrão nesse modo; exigir `--output` explícito para persistência.
