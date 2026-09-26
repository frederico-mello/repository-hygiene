## Why

Hoje a auditoria roda manualmente ou no GitHub Actions, permitindo que problemas críticos sejam commitados antes da verificação remota. Um hook nativo permite feedback imediato e bloqueia commits com achados de severidade `error`, sem adicionar dependências externas ao projeto.

## What Changes

- Adicionar um modo de execução apropriado para `pre-commit`.
- Avaliar o conteúdo staged do repositório para evitar bloquear um commit por alterações não relacionadas.
- Fazer o hook falhar para erros de auditoria e configuração/execução inválida, mantendo warnings informativos.
- Fazer `--init` instalar o hook nativo quando solicitado ou conforme a política definida pelo projeto.
- Documentar instalação, comportamento, saída e a forma explícita de ignorar o hook.
- Manter a auditoria completa existente no GitHub Actions como verificação independente.

## Capabilities

### New Capabilities

- `native-pre-commit-hook`: valida o estado staged antes de cada commit e impede commits que não atendam aos erros configurados.

### Modified Capabilities

- Nenhuma.

## Impact

- Afeta `auditoria_higiene.cli`, a execução das regras em `core.py` e a geração/instalação de arquivos em `init.py`.
- Pode adicionar um script de hook versionado ou um template de hook, sem dependências de runtime além do pacote atual.
- Altera a documentação de uso e inicialização.
- Não altera o contrato do comando de auditoria completa nem o workflow GitHub Actions.
