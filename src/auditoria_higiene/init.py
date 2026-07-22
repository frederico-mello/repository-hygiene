"""Comando init: gera configuração e workflow para um projeto."""

import os
import sys
import pkgutil


def cmd_init(directory, force=False, install_hook=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Erro: diretório não encontrado: {raiz}", file=sys.stderr)
        sys.exit(2)

    _gerar_arquivo(raiz, "auditoria.yaml", "templates/auditoria.yaml", force)
    _gerar_arquivo(raiz, ".github/workflows/auditoria-higiene.yml", "templates/workflow.yml", force)
    print(f"Arquivos gerados em {raiz}")
    print("Execute 'auditoria-higiene .' para auditar o repositório.")

    if install_hook:
        _instalar_hook(raiz, force)


def _instalar_hook(raiz, force):
    git_dir = os.path.join(raiz, ".git")
    if not os.path.isdir(git_dir):
        print(f"  Erro: {raiz} não é um repositório Git (sem diretório .git)", file=sys.stderr)
        return
    hook_dir = os.path.join(git_dir, "hooks")
    hook_path = os.path.join(hook_dir, "pre-commit")
    if os.path.exists(hook_path) and not force:
        print(f"  Pulando (já existe): .git/hooks/pre-commit")
        return
    os.makedirs(hook_dir, exist_ok=True)
    dados = pkgutil.get_data(__package__, "templates/pre-commit")
    if dados is None:
        print(f"  Erro: template não encontrado: templates/pre-commit", file=sys.stderr)
        return
    with open(hook_path, "wb") as f:
        f.write(dados)
    os.chmod(hook_path, 0o755)
    print(f"  Criado: .git/hooks/pre-commit")


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
