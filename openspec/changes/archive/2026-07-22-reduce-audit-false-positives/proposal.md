## Why

O auditor reporta exemplos de testes, fixtures, versões, comandos e arquivos de configuração como problemas reais. Na auditoria atual, aproximadamente 72% dos achados foram classificados manualmente como falsos-positivos, reduzindo a confiança no status de falha e dificultando a priorização de riscos reais.

A auditoria precisa preservar detecção de problemas genuínos, mas considerar contexto do arquivo, tipo de referência e confiança do achado antes de transformar uma ocorrência em erro acionável.

## What Changes

- Refinar detecção de segredos para diferenciar credenciais operacionais de exemplos, fixtures e valores de teste deliberados.
- Refinar detecção de referências inexistentes para reconhecer apenas referências com semântica de caminho, preservando links e usos de arquivos realmente quebrados.
- Refinar detecção de documentação desatualizada para não tratar versões, comandos, módulos, URLs e identificadores como nomes de arquivo.
- Tornar análise de arquivos sem referência contextual, considerando usos por imports, entry points, workflows, configuração e artefatos OpenSpec.
- Tornar identificação de artefatos fora do `.gitignore` específica para saídas geradas, sem marcar automaticamente código-fonte ou diretórios intencionais.
- Tornar avisos de permissões de workflow contextuais e configuráveis, sem classificar toda permissão `write` como insegura por padrão.
- Adicionar evidência e nível de confiança aos achados quando a regra não puder determinar o uso com certeza.
- Garantir que apenas achados de alta confiança e severidade de erro determinem falha da auditoria.
- Adicionar testes de regressão para os falsos-positivos observados em `tests_package`, `README.md`, documentação OpenSpec e workflow.

## Capabilities

### New Capabilities
- `context-aware-audit-findings`: Classificação contextual, confiança e evidências para achados da auditoria.

### Modified Capabilities

## Impact

- Afeta as regras e o modelo de resultado em `src/auditoria_higiene/core.py`.
- Afeta configuração em `auditoria.yaml`, incluindo exclusões e políticas por regra.
- Afeta saída JSON, terminal e relatórios ao adicionar contexto de confiança.
- Afeta testes unitários e de integração em `tests_package/test_auditoria_package.py`.
- Pode alterar quais auditorias retornam `falha`, sem desativar regras existentes.
- Não adiciona dependências externas nem corrige arquivos automaticamente.
