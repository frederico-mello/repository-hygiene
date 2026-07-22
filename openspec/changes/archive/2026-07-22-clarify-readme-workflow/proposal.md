## Why

O README apresenta o fluxo de inicialização depois da auditoria e contém detalhes que podem divergir do template de workflow gerado pelo `--init`. Isso dificulta a adoção por novos usuários e pode criar uma expectativa incorreta sobre o tratamento de falhas no GitHub Actions.

## What Changes

- Reorganizar o README para apresentar inicialização, configuração e auditoria na ordem recomendada.
- Atualizar exemplos e descrições da CLI para refletir o comportamento atual.
- Alinhar o template de workflow gerado com o comportamento documentado de continuar após falhas da auditoria.
- Documentar as opções de configuração existentes que estão ausentes do exemplo atual.
- Remover ou corrigir afirmações desatualizadas sobre relatórios, sanitização e workflow.

## Capabilities

### New Capabilities

- `documentation-consistency`: Documentação de uso e templates de integração permanecem coerentes com a implementação atual.

### Modified Capabilities

Nenhuma capacidade existente tem requisitos de produto alterados; a mudança cobre documentação e consistência do template.

## Impact

- `README.md`
- `src/auditoria_higiene/templates/workflow.yml`
- Possíveis testes de template/documentação em `tests_package/`
- Nenhuma mudança de API pública ou dependência de runtime.
