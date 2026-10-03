## Context

O comando atual executa regras sobre o estado de trabalho e retorna `0` para auditoria limpa, `1` para erros e `2` para falhas de configuração ou execução. O hook precisa reutilizar esse contrato, mas um commit pode conter somente parte das mudanças locais. A instalação também precisa ser explícita e segura, pois hooks dentro de `.git` não são versionados.

## Goals / Non-Goals

**Goals:**

- Oferecer um comando dedicado para uso pelo Git `pre-commit`.
- Avaliar arquivos staged, preservando arquivos não staged durante a checagem.
- Bloquear erros e falhas operacionais/configuração, exibindo relatório sanitizado.
- Permitir instalação idempotente pelo fluxo de inicialização.
- Manter o workflow remoto como verificação completa e independente.

**Non-Goals:**

- Não instalar dependências externas ou adotar o framework `pre-commit`.
- Não impedir `git commit --no-verify`.
- Não transformar warnings em falhas de commit por padrão.
- Não substituir a auditoria completa do CI.

## Decisions

- **Modo CLI dedicado:** adicionar uma opção própria para o hook, em vez de fazer o script reproduzir lógica Python. Isso mantém o hook pequeno e preserva um único ponto de decisão para códigos de saída e relatórios.
- **Snapshot staged:** o modo de hook executará a auditoria contra uma cópia temporária materializada a partir do índice, combinada com a árvore necessária para regras que dependem do repositório. A cópia será removida sempre ao terminar. Isso evita que alterações unstaged sejam confundidas com o conteúdo a ser commitado.
- **Hook nativo gerado:** `--init` oferecerá instalação do hook em `.git/hooks/pre-commit`, usando um template empacotado. A instalação será idempotente e não sobrescreverá um hook existente sem `--force`.
- **Contrato de falha:** código `0` permite o commit; códigos `1` e `2` bloqueiam. O relatório usa a saída textual sanitizada e indica que o problema veio do pre-commit.
- **Auditoria remota preservada:** o workflow continuará executando o comando normal na árvore completa, cobrindo o caso em que o hook não foi instalado ou foi ignorado.

## Risks / Trade-offs

- [Diferença entre índice e árvore de trabalho] -> testar arquivos adicionados, modificados, removidos e mudanças unstaged simultâneas; garantir limpeza de temporários.
- [Hook local não compartilhado automaticamente] -> documentar a instalação e manter o CI como barreira final.
- [Hook existente pode conter lógica do usuário] -> não sobrescrever por padrão; `--force` exige ação explícita.
- [Regras que dependem de histórico ou arquivos não staged] -> definir no modo hook quais dados permanecem disponíveis e testar comportamento; regras incompatíveis devem falhar de modo claro, não permitir silenciosamente.

## Migration Plan

1. Atualizar o pacote e executar a inicialização com a opção de instalação do hook.
2. Confirmar o hook instalado e fazer um commit limpo de validação.
3. Corrigir ou revisar achados antes de commits bloqueados; usar `--no-verify` somente como escape operacional documentado.
4. Remover manualmente o hook para rollback local; o workflow remoto não muda.

## Open Questions

- A instalação do hook deve ocorrer somente com uma flag explícita (`--install-hook`) ou ser incluída automaticamente em `--init`?
- O modo staged deve suportar todas as regras atuais desde a primeira versão ou excluir regras de análise global que não podem ser materializadas com segurança?
