## Context

O auditor existente é um script Python autocontido, configurado por YAML e executado localmente ou em um workflow específico do repositório original. O objetivo é extraí-lo para um repositório público dedicado, mantendo execução local simples e oferecendo uma integração GitHub Actions centralizada para múltiplos repositórios Python.

## Goals / Non-Goals

**Goals:**

- Permitir `pip install repository-hygiene` e um comando de ativação no repositório atual.
- Executar a mesma lógica localmente e no CI.
- Centralizar a implementação e o workflow reutilizável, com releases versionadas.
- Criar issue consolidada com permissões mínimas no repositório consumidor.
- Ativar todas as regras existentes por padrão e permitir exceções locais explícitas.
- Atualizar arquivos gerenciados sem destruir personalizações do consumidor.

**Non-Goals:**

- Suportar repositórios que não sejam Python nesta primeira versão.
- Remover ou corrigir automaticamente os problemas encontrados.
- Alterar dependências de runtime dos projetos consumidores.
- Fazer atualização silenciosa ou automática sem aprovação do desenvolvedor.
- Substituir ferramentas especializadas de segurança, lint ou dependência.

## Decisions

### Pacote Python público

O auditor será distribuído no PyPI com metadados, versões semânticas e dependência `PyYAML` declarada pelo próprio pacote. Isso evita modificar `requirements.txt` ou `pyproject.toml` da aplicação consumidora. Um pacote privado ou instalação direta do Git foram descartados por adicionarem autenticação e fricção desnecessárias.

### CLI como interface principal

Os comandos serão `repository-hygiene install`, `repository-hygiene audit` e `repository-hygiene update`. A CLI fornece uma experiência única para instalação e uso local, enquanto `python -m` permanece como alternativa técnica. `pipx` poderá ser documentado como opção para isolamento, mas não será requisito.

### Workflow reutilizável centralizado

Cada consumidor terá um workflow pequeno com gatilhos de agenda, push/PR e execução manual, chamando um workflow reutilizável do novo repositório por tag ou release. O workflow central instalará uma versão fixa do pacote, executará a auditoria e manterá Summary e issue consolidada. Copiar o workflow completo para cada consumidor foi descartado por dificultar correções e criar divergência.

### Artefatos gerenciados e locais

O script/CLI e o workflow gerado serão identificados como gerenciados pela ferramenta. O `auditoria.yaml` terá configuração padrão completa, mas exceções locais serão preservadas e atualizadas apenas com confirmação. O instalador nunca sobrescreverá arquivos existentes silenciosamente e oferecerá `--dry-run` e `--force`.

### Atualização explícita e versionada

`auditoria-higiene update` consultará uma versão-alvo, mostrará o plano/diff e atualizará somente artefatos gerenciados após confirmação. O workflow usará tags imutáveis ou versões explícitas. Rollback será feito reinstalando uma versão anterior e executando `update` para essa versão.

### Segurança operacional

Relatórios continuarão mascarando valores sensíveis. O workflow declarará somente `contents: read`, `pull-requests: read` e `issues: write`. O pacote público não conterá dados privados do repositório original. Atualizações não executarão código remoto fora do pacote selecionado pelo usuário.

## Risks / Trade-offs

- **[Supply chain no PyPI]** Pacote público pode ser substituído ou confundido com nome semelhante. → Publicar com namespace/nome definitivo, releases versionadas, dependências limitadas e documentação de verificação.
- **[Exposição de achados em issues públicas]** Caminhos e nomes podem revelar contexto interno. → Mascarar segredos, documentar o comportamento e permitir desativar ou excluir regras/caminhos.
- **[Divergência de configuração]** Consumidores podem customizar excessivamente o YAML. → Configuração padrão completa, validação de schema e preservação explícita das exceções.
- **[Mudança incompatível]** Atualização pode alterar resultados do CI. → Tags versionadas, preview/diff, changelog e atualização manual.
- **[Permissão insuficiente no workflow]** Forks e PRs externos não podem atualizar issues. → Publicar Summary/status sem falhar por falta de escrita.

## Migration Plan

1. Extrair a implementação atual para o pacote e adicionar testes de contrato.
2. Publicar uma primeira versão no PyPI e uma release do workflow reutilizável.
3. Testar `install`, `audit` e `update` em um repositório Python descartável.
4. Migrar o repositório original para consumir o pacote e workflow centralizados.
5. Para rollback, fixar a release anterior no workflow e executar `update` para a versão anterior.

## Open Questions

- Qual nome/organização GitHub e qual nome final do pacote no PyPI serão usados?
- O workflow reutilizável ficará no mesmo repositório do pacote ou em um repositório separado?
- O instalador deverá criar um `pyproject.toml` mínimo quando o consumidor não possuir arquivo de empacotamento?
- Releases do pacote e do workflow terão o mesmo número de versão?
