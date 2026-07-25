# Controle de Versão & Release Automatizado

## Why

O projeto acumulou 30 commits desde o tag `v0.2.0` sem nenhum bump de versão — o `pyproject.toml` continua em `0.2.0` e o PyPI serve código obsoleto. Sem um mecanismo de versionamento e release, novas features, correções e melhorias nunca chegam aos usuários finais, e o problema se repetirá a cada ciclo de desenvolvimento.

## What Changes

- **Release semântico automatizado** — pipeline que detecta commits convencionais, calcula a próxima versão, gera changelog categorizado, faz build e publica no PyPI
- **Auditoria de conventional commits** — regra integrada ao `repository-hygiene` que detecta commits fora do padrão Conventional Commits e gera alertas
- **Hook pre-commit de validação de mensagem** — valida formato da mensagem de commit antes de commitar, instalável via `--init --install-hook`
- **Diretriz de conventional commits** — adicionada ao `AGENTS.md` como padrão do projeto
- **Bump para 0.3.0** — versão atualizada no pacote, documentação e template de workflow, refletindo 30 commits acumulados
- **Template de workflow dinâmico** — template gerado por `--init` referencia a versão do pacote dinamicamente, não uma versão hardcoded

## Capabilities

### New Capabilities
- `automated-release-workflow`: pipeline de release semântico — detecta commits convencionais, calcula bump, gera changelog, faz build e publica no PyPI
- `conventional-commit-audit`: regra de auditoria que valida aderência ao padrão Conventional Commits no histórico de commits, gerando alertas para mensagens fora do formato

### Modified Capabilities
- `publish-pypi-v020`: ampliar escopo para versionamento contínuo — suporte a release semântico automatizado para qualquer versão futura (não mais restrito ao release 0.2.0)

## Impact

- `AGENTS.md` — diretriz de conventional commits
- `pyproject.toml` — bump de versão para 0.3.0 e metadados de build
- Workflows CI/CD — novo pipeline de release semântico + auditoria de commits
- README e documentação — comandos de instalação com nova versão
- Código-fonte — output de `--version`, template de workflow, regra de auditoria de commits, hook pre-commit
- `openspec/specs/publish-pypi-v020/` — delta spec com requisitos ampliados
