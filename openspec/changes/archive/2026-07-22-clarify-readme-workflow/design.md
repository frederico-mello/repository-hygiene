## Context

O projeto tem uma implementação de CLI, um template de configuração, um template de workflow gerado por `--init` e um workflow versionado no próprio repositório. O README precisa explicar o caminho de adoção sem exigir que o usuário compare esses arquivos. A correção deve preservar a interface atual e evitar duplicar detalhes que possam divergir novamente.

## Goals / Non-Goals

**Goals:**

- Apresentar o fluxo `--init` antes da auditoria manual.
- Fazer o template gerado continuar, publicar o relatório e processar o código de saída quando a auditoria encontrar erros.
- Documentar apenas opções e comportamentos confirmados pela CLI e pelos templates.
- Tornar a consistência verificável por testes simples de conteúdo e por validação manual do README.

**Non-Goals:**

- Alterar a CLI, regras de auditoria ou formato dos relatórios.
- Alterar permissões, gatilhos ou política de issues além do necessário para alinhar o template ao comportamento já adotado pelo workflow versionado.
- Criar uma nova camada de geração automática do README.

## Decisions

### Manter `--init` como primeiro passo recomendado

O README será reorganizado para mostrar instalação, inicialização, revisão da configuração, auditoria e integrações opcionais nessa ordem. A auditoria direta continuará documentada para repositórios que já possuem `auditoria.yaml`.

Alternativa rejeitada: manter a ordem atual e apenas adicionar uma nota, pois isso preserva o caminho confuso para novos usuários.

### Alinhar o template ao workflow versionado

O template `src/auditoria_higiene/templates/workflow.yml` receberá o tratamento explícito do código de saída da auditoria antes de publicar o relatório, permitindo que as etapas posteriores executem com códigos 0, 1 ou 2. O README descreverá esse comportamento sem depender de detalhes de shell desnecessários.

Alternativa rejeitada: documentar a diferença entre template e workflow versionado, pois `--init` deve gerar uma integração funcional por padrão.

### Validar consistência por testes focados

Serão adicionados ou ajustados testes para garantir que o template contenha o tratamento de falha e que os exemplos/documentação permaneçam coerentes com opções existentes. A validação não exigirá executar GitHub Actions.

## Risks / Trade-offs

- [README pode voltar a divergir da CLI] -> Referenciar comandos e opções diretamente nos testes e revisar a documentação junto com alterações de interface.
- [Workflow mascarar falha de configuração] -> Preservar o código de saída em `$GITHUB_OUTPUT`; somente a publicação e a gestão da issue continuam após a falha.
- [Testes de texto ficarem frágeis] -> Verificar comportamentos e marcadores essenciais, não posições exatas de linhas.

## Migration Plan

1. Atualizar template, README e testes.
2. Rodar a suíte de testes e validar o YAML gerado.
3. Usuários existentes não precisam migrar arquivos automaticamente; podem comparar e atualizar workflows gerados anteriormente se desejarem o tratamento corrigido de falhas.
4. Rollback: reverter o commit da documentação/template, sem migração de dados.

## Open Questions

Nenhuma pendência conhecida para esta mudança.
