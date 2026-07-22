## Context

O pacote `repository-hygiene` está publicado no PyPI como `0.1.0`, mas a CLI exposta difere da implementação atual. O README local afirma incorretamente que o pacote não está publicado, e o workflow gerado instala o código diretamente do Git em vez de usar o PyPI.

## Goals / Non-Goals

**Goals:**
- Publicar implementação atual como `0.2.0` no PyPI
- Alinhar README com instalação via PyPI
- Atualizar workflow gerado para instalar versão fixada do PyPI
- Documentar migração da CLI `0.1.0` para `0.2.0`
- Garantir consistência de versão entre `pyproject.toml` e `__init__.py`

**Non-Goals:**
- Manter aliases ou compatibilidade com subcomandos `audit`, `install`, `update`
- Reintroduzir comando `update`
- Alterar regras de auditoria ou CLI existente

## Decisions

| Decisão | Opção escolhida | Alternativas | Rationale |
|---|---|---|---|
| Versionamento | `0.2.0` | `0.1.1`, `1.0.0` | CLI incompatível → SemVer minor quebra pre-1.0. `0.1.1` seria enganoso. `1.0.0` prematuro |
| Fonte da versão | `importlib.metadata` no `__init__.py` | Duplicar string | Única fonte de verdade, evita mismatch |
| Instalação no workflow | `pip install repository-hygiene==0.2.0` | Git URL | PyPI é mais rápido, confiável, e é o canal oficial |
| Documentação de migração | Seção no README | Página separada | Mantém descoberta no lugar mais visitado |

## Risks / Trade-offs

| Risco | Mitigação |
|---|---|
| PyPI upload falha mas tag existe | Script de publish verifica `twine upload` antes de criar tag |
| Usuário `0.1.0` tenta `audit` e falha | README documenta migração; `0.2.0` sinaliza breaking change |
| Versão duplicada entre `pyproject.toml` e `__init__.py` | `__init__.py` lê de `importlib.metadata` |
| Workflow antigo continua usando Git URL | Workflow template é atualizado; re-init gera novo workflow |
