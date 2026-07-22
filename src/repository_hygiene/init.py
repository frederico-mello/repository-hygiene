"""Commands: install and update audit configuration in a repository."""

import os
import sys
import pkgutil


_MANAGED_FILES = [
    ("auditoria.yaml", "templates/auditoria.yaml"),
    (".github/workflows/repository-hygiene.yml", "templates/workflow.yml"),
]


def cmd_install(directory, force=False, dry_run=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Erro: diretório não encontrado: {raiz}", file=sys.stderr)
        sys.exit(2)

    if dry_run:
        print(f"Modo dry-run — operações planejadas para {raiz}:")
        for caminho_rel, _ in _MANAGED_FILES:
            caminho_abs = os.path.join(raiz, caminho_rel)
            if os.path.exists(caminho_abs):
                print(f"  [conflito] {caminho_rel} (já existe)")
            else:
                print(f"  [criar] {caminho_rel}")
        return

    for caminho_rel, template_recurso in _MANAGED_FILES:
        _gerar_arquivo(raiz, caminho_rel, template_recurso, force)

    print(f"Arquivos gerados em {raiz}")
    print("Execute 'repository-hygiene audit' para auditar o repositório.")


def cmd_update(directory, version=None, dry_run=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Erro: diretório não encontrado: {raiz}", file=sys.stderr)
        sys.exit(2)

    if dry_run:
        print(f"Modo dry-run — versão alvo: {version or 'latest'}")
        print("Operações planejadas:")
        for caminho_rel, _ in _MANAGED_FILES:
            caminho_abs = os.path.join(raiz, caminho_rel)
            if os.path.exists(caminho_abs):
                print(f"  [atualizar] {caminho_rel}")
            else:
                print(f"  [criar] {caminho_rel}")
        return

    for caminho_rel, template_recurso in _MANAGED_FILES:
        _gerar_arquivo(raiz, caminho_rel, template_recurso, force=True)

    print(f"Artefatos atualizados em {raiz} para versão {version or 'latest'}")


def _gerar_arquivo(raiz, caminho_rel, template_recurso, force):
    caminho_abs = os.path.join(raiz, caminho_rel)
    if os.path.exists(caminho_abs) and not force:
        print(f"  Pulando (já existe): {caminho_rel}")
        return
    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)
    dados = pkgutil.get_data(__package__, template_recurso)
    if dados is None:
        print(f"  Erro: template não encontrado: {template_recurso}", file=sys.stderr)
        return
    with open(caminho_abs, "wb") as f:
        f.write(dados)
    print(f"  Criado: {caminho_rel}")