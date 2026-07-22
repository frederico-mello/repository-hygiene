## Context

As regras atuais usam regex e presença textual para analisar um repositório. Isso funciona para sinais simples, mas produz achados quando encontra fixtures de teste, exemplos documentais, versões, comandos, nomes de módulos ou arquivos-fonte que não possuem referência textual direta.

O auditor precisa continuar sendo determinístico, sem dependências externas e compatível com o formato atual de configuração. A mudança atravessa classificação de conteúdo, resolução de caminhos, cálculo de status e testes.

## Goals / Non-Goals

**Goals:**

- Introduzir uma camada comum de contexto para identificar arquivos de teste, fixtures, exemplos, arquivos gerados e conteúdo documental.
- Separar detecção de ocorrência de decisão de severidade por meio de confiança (`high`, `medium`, `low`).
- Fazer regras de caminho reconhecerem somente usos que representam referências reais.
- Preservar detecção de credenciais em código/configuração operacional e links quebrados.
- Produzir evidência suficiente para explicar por que cada achado foi emitido.
- Tornar políticas de exclusão e confiança configuráveis sem exigir mudanças no código.

**Non-Goals:**

- Não integrar scanners externos de segredos ou análise semântica baseada em LLM.
- Não corrigir arquivos automaticamente.
- Não remover regras existentes.
- Não garantir prova completa de reachability ou dead code.
- Não mudar o formato principal de execução da CLI além dos campos adicionais necessários.

## Decisions

### Contexto determinístico por arquivo

Criar helpers internos para classificar caminho, extensão e contexto textual. Diretórios de testes, fixtures, exemplos, OpenSpec e arquivos gerados terão política padrão explícita por regra, em vez de depender de várias tuplas independentes.

Alternativa rejeitada: excluir todos os testes globalmente. Isso esconderia testes que deliberadamente verificam configuração insegura e impediria auditoria de exemplos que são parte do produto.

### Ocorrência versus achado acionável

Detectores poderão encontrar uma ocorrência, mas devem atribuir confiança e severidade efetiva conforme contexto. Ocorrências fracas em fixtures e documentação serão omitidas ou classificadas como `low`, enquanto sinais fortes em arquivos operacionais permanecerão `high`.

Alternativa rejeitada: apenas aumentar listas de exceção. Listas não resolvem novos nomes de fixtures e criam configuração frágil.

### Parser contextual para referências

Manter regex apenas como primeiro estágio, mas aceitar referência inexistente somente quando o texto estiver em contexto reconhecível: link Markdown, chamada de leitura/escrita de arquivo, configuração de caminho, import ou comando explicitamente marcado. Nomes em mensagens, asserts e valores literais genéricos não serão suficientes.

Alternativa rejeitada: verificar qualquer string com extensão, pois essa é a causa direta dos falsos-positivos observados.

### Análise de arquivos sem referência como heurística

A regra passará a reconhecer referências estruturais simples, como imports Python, caminhos de workflow, entry points e relações OpenSpec. Quando não houver evidência suficiente, emitirá aviso de baixa confiança, sem tratar ausência de menção textual como prova de inutilidade.

Alternativa rejeitada: desativar a regra. A regra ainda é útil para candidatos a limpeza, desde que não seja apresentada como certeza.

### Política de status

Somente resultados com severidade `error` e confiança `high` ou `medium` farão a auditoria falhar. Resultados `low` continuarão visíveis no relatório, mas serão informativos.

Alternativa rejeitada: manter qualquer erro textual como falha, pois isso preservaria o principal problema de confiança.

### Workflows e artefatos

Permissões `write` serão avaliadas com escopo e configuração permitida. A regra emitirá alerta quando houver permissão ampla, combinação perigosa ou ausência de política explícita, não simplesmente por existir `issues=write`. Artefatos serão identificados por padrões configuráveis de saída gerada; diretórios-fonte e arquivos rastreados não serão tratados como artefatos não ignorados.

## Risks / Trade-offs

- [Perda de detecção] Uma heurística contextual pode ignorar um caso real pouco convencional. Mitigação: confiança configurável, evidências, testes positivos e opção de modo estrito.
- [Compatibilidade] Consumidores podem depender de todos os resultados atuais. Mitigação: preservar chaves existentes e adicionar campos, documentando mudança de status.
- [Configuração complexa] Mais políticas podem aumentar o custo de manutenção. Mitigação: padrões seguros embutidos e overrides pequenos por regra.
- [Análise estrutural incompleta] Imports dinâmicos e geração de caminhos podem continuar sem reconhecimento. Mitigação: manter o resultado como heurístico e não como decisão de remoção.
