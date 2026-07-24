## Context

A instalação direta via `pip` pode concluir com sucesso e ainda deixar o executável `repository-hygiene` fora do `PATH`, principalmente em instalações de usuário no Windows. O pacote Python já fornece a CLI e os templates; o problema está no caminho de distribuição e descoberta do executável, não na lógica de auditoria.

Python continua sendo pré-requisito do projeto. A solução selecionada usa `uv` como camada de distribuição da CLI, sem substituir o pacote PyPI nem alterar silenciosamente o ambiente do usuário.

## Goals / Non-Goals

**Goals:**

- Oferecer fluxo uniforme de primeiro uso em Windows, macOS e Linux.
- Usar `uvx repository-hygiene install .` para execução efêmera sem depender do `PATH` do executável do pacote.
- Oferecer `uv tool install repository-hygiene` para uso persistente e isolado.
- Preservar execução via `pip` e `python -m repository_hygiene` como alternativas compatíveis.
- Tornar explícitos requisitos de Python, resolução de versão, comportamento do `PATH` e recuperação de falhas.
- Validar empacotamento e execução em matriz multiplataforma.

**Non-Goals:**

- Não substituir Python ou `pip`.
- Não distribuir executável standalone.
- Não alterar `PATH` ou perfis de shell silenciosamente pelo pacote.
- Não modificar regras de auditoria, templates ou comportamento de `install` fora da distribuição da CLI.
- Não exigir migração imediata de usuários ou workflows existentes.

## Decisions

### Arquitetura de distribuição

```text
PyPI: repository-hygiene
        |
        +--> uvx repository-hygiene install .
        |       execução efêmera para primeiro uso
        |
        +--> uv tool install repository-hygiene
                instalação persistente para uso recorrente
```

- O pacote continua sendo a única fonte da CLI, dos templates e do entry point.
- `uvx` resolve o pacote em ambiente isolado e executa a CLI sem instalar o executável globalmente.
- `uv tool install` cria ambiente persistente gerenciado pelo `uv` e expõe o comando no diretório de ferramentas.
- `uvx` é o fluxo inicial confiável e o fluxo recomendado para uso ocasional.
- `uv tool install` é uma otimização opcional para uso frequente; sua disponibilidade como comando curto depende do diretório de ferramentas estar no `PATH`, e a documentação deve encaminhar para `uv tool update-shell` quando necessário.

### Estrutura de componentes

- **Pacote `repository-hygiene`**: fornece CLI, entry points, templates e fallback `python -m`.
- **`uvx`**: executa a CLI em ambiente efêmero.
- **`uv tool install`**: mantém instalação persistente isolada.
- **`uv tool update-shell`**: integra opcionalmente o diretório de ferramentas ao shell.
- **Documentação**: define `uvx` como caminho padrão e explica limitações do modo persistente.
- **Testes de empacotamento**: verificam instalação, execução, descoberta e mensagens nos sistemas suportados.

Nenhum componente novo altera regras de auditoria ou configurações do repositório consumidor.

### Fluxo de dados e ownership do estado

Execução efêmera:

```text
usuário
  |
  v
uvx repository-hygiene install .
  |
  +--> resolve pacote e dependências
  +--> reutiliza/cria cache isolado do uv
  +--> executa entry point da CLI
  |
  v
repositório consumidor recebe auditoria.yaml e workflow
```

Execução persistente:

```text
uv tool install repository-hygiene
  |
  +--> cria ambiente gerenciado pelo uv
  +--> registra executável no diretório de ferramentas
  |
  v
repository-hygiene audit .
  |
  v
mesma implementação da CLI
```

- `uv` é dono de cache, ambiente isolado e resolução de dependências.
- O pacote é stateless e não mantém banco, configuração global ou registro próprio.
- O repositório consumidor continua sendo dono de `auditoria.yaml` e dos workflows gerados.
- A instalação não altera o repositório até o usuário executar explicitamente `install`.
- A seleção de versão fica sob controle do comando `uvx` ou `uv tool install`, permitindo versão atual ou fixada.

### Validação

- Manter testes unitários e de subprocesso existentes para CLI e comandos públicos.
- Construir o artefato distribuível e executar smoke tests via `uvx`, apontando o teste para o artefato local recém-construído em vez de resolver uma versão do índice público.
- Executar smoke tests para `uv tool install`, usando o mesmo artefato local e incluindo criação do ambiente e disponibilidade do entry point.
- Validar Windows, macOS e Linux nas versões de Python suportadas.
- Testar diretório de ferramentas fora do `PATH`, instalação repetida, versão fixada e falhas de resolução.
- Confirmar que falhas não alteram arquivos do consumidor.
- Usar infraestrutura de CI existente, sem adicionar dependências de runtime ao pacote.

### Migração e rollout

- Atualizar documentação para apresentar `uvx` como fluxo recomendado.
- Manter `pip` e `python -m repository_hygiene` documentados e funcionais.
- Não alterar o comportamento de usuários que já instalaram via `pip`.
- Não exigir migração imediata de workflows existentes.
- Publicar a mudança junto com validação de empacotamento e instalação.
- Reverter a recomendação documental se necessário, sem exigir rollback do pacote.
- Manter versões anteriores disponíveis para instalação explícita.

### Segurança e reprodutibilidade

- `uvx` sem versão fixa será o fluxo conveniente de primeiro uso.
- Documentação oferecerá versão explícita para CI, automações e auditorias reproduzíveis.
- Workflows existentes continuarão fixando a versão do pacote.
- O pacote será obtido do índice público esperado, sem introduzir índices alternativos silenciosos.
- Atualizações não ocorrerão automaticamente durante execução persistente.
- Alterações em `PATH` ou perfis de shell ocorrerão apenas por ação explícita do usuário através do `uv`.
- A documentação distinguirá claramente fluxo rápido de fluxo reproduzível.

## Risks / Trade-offs

- **`uv` ausente** → A documentação deve identificar a instalação necessária antes da execução.
- **Falha de rede ou resolução do pacote** → O erro do `uv` permanece visível e a execução não altera o repositório.
- **Python incompatível** → A instalação falha explicitamente com requisito de versão claro.
- **Cache ou ambiente isolado inválido** → O usuário pode limpar ou recriar o ambiente pelo próprio `uv`.
- **Diretório de ferramentas fora do `PATH`** → O fluxo `uvx` continua funcionando; o modo persistente orienta `uv tool update-shell`.
- **Terminal aberto antes da alteração de shell** → A documentação informa que uma nova sessão pode ser necessária.
- **Resolução de versão mais nova e inesperada** → CI e automações usam versão explícita; o fluxo sem versão fica restrito à conveniência local.
- **Mudança silenciosa de ambiente** → O pacote não altera `PATH`, perfis ou instalações Python automaticamente.
- **Maior dependência de ferramenta externa** → `pip` e `python -m repository_hygiene` permanecem disponíveis como fallback.
- **Falha durante `install`** → As regras atuais de idempotência e confirmação continuam protegendo arquivos existentes.
