# Publicar versão 0.2.0 no PyPI

## Problema

O projeto possui uma versão `0.1.0` publicada no PyPI, mas essa versão expõe uma CLI diferente da implementação atual. O README local também informa incorretamente que o pacote não está publicado e o workflow ainda instala o código diretamente do Git.

## Objetivo

Publicar a implementação atual como `0.2.0`, tratando a mudança da CLI como incompatível, e alinhar documentação, workflow e metadados do pacote.

## Escopo

- Atualizar versão do pacote para `0.2.0`.
- Atualizar README com instalação via PyPI e instruções da CLI atual.
- Atualizar workflow gerado para instalar versão fixada do PyPI.
- Documentar migração da CLI antiga (`audit`, `install`, `update`) para a CLI atual (`--init`, auditoria direta e `--install-hook`).
- Adicionar validações ou testes para impedir referências à instalação Git e à versão antiga nos artefatos gerados.
- Preparar publicação por tag `v0.2.0`.

## Fora de escopo

- Manter aliases ou compatibilidade com os subcomandos da versão `0.1.0`.
- Reintroduzir o comando `update`.
- Alterar regras de auditoria não relacionadas à distribuição.

## Impacto

Usuários que atualizarem de `0.1.0` precisarão adaptar comandos e scripts que dependem da CLI antiga. A versão major/minor `0.2.0` sinaliza essa incompatibilidade conforme SemVer.

## Critérios de sucesso

- `pip install repository-hygiene==0.2.0` instala pacote funcional.
- Comandos documentados no README funcionam em ambiente limpo.
- Workflow gerado instala `repository-hygiene==0.2.0` via PyPI.
- Nenhum artefato de distribuição ou documentação afirma que o pacote não está publicado.
- Tag `v0.2.0` corresponde ao pacote publicado.
