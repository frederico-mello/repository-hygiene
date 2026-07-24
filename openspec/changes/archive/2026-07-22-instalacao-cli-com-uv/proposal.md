## Why

A instalação direta via `pip` pode concluir com sucesso e ainda deixar o executável `repository-hygiene` fora do `PATH`, principalmente em instalações de usuário no Windows. Isso contradiz o fluxo documentado e impede o primeiro uso, mesmo quando Python e o pacote estão corretamente instalados.

Como Python é um pré-requisito do projeto, o pacote deve oferecer um caminho de instalação e execução baseado em `uv`, consistente entre Windows, macOS e Linux. O fluxo inicial deve funcionar sem ajustes manuais no `PATH`; o modo persistente deve diagnosticar claramente quando a integração do shell for necessária.

## What Changes

- Definir um fluxo oficial de primeiro uso com `uvx`, sem exigir instalação global permanente do pacote.
- Definir um fluxo oficial de uso recorrente com `uv tool install`, expondo a CLI de forma isolada e diagnosticando explicitamente requisitos de shell.
- Documentar instalação, execução, atualização e diagnóstico do fluxo baseado em `uv` nos sistemas suportados.
- Preservar instalação via `pip` e execução via `python -m` como alternativas compatíveis.
- Tornar explícitos os requisitos de Python, o comportamento esperado do `PATH` e as ações de recuperação quando a CLI não for encontrada.
- Adicionar validação automatizada dos fluxos de instalação e execução nos sistemas suportados.
- Não substituir Python ou `pip`, distribuir executável standalone, alterar o `PATH` silenciosamente ou modificar o comportamento das regras de auditoria.

## Capabilities

### New Capabilities

- `instalacao-cli-uv`: Instalação efêmera e persistente da CLI usando `uv`, com fluxo documentado e verificável entre sistemas operacionais.

### Modified Capabilities

- `pacote-auditoria-higiene`: Ampliar o contrato de instalação e execução para incluir os fluxos oficiais com `uv` e o fallback por módulo Python.

## Impact

- Documentação pública de instalação e uso da CLI.
- Metadados e entry points do pacote Python.
- Testes de empacotamento, instalação e descoberta do executável.
- Automação de CI para validação multiplataforma.
- Usuários que atualmente executam `pip install repository-hygiene` continuam com essa alternativa, mas passam a receber um caminho recomendado mais previsível.
