"""Install and update commands: generate config and workflow for a project."""

import os
import pkgutil
import sys
from importlib.resources import files


def cmd_init(directory, force=False, install_hook=False):
    cmd_install(directory, force=force, dry_run=False)
    _instalar_hook_commit_msg(os.path.abspath(directory), force)
    if install_hook:
        _instalar_hook(os.path.abspath(directory), force)


def cmd_install(directory, force=False, dry_run=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Error: directory not found: {raiz}", file=sys.stderr)
        sys.exit(2)

    if dry_run:
        _dry_run_msg(raiz, "auditoria.yaml", "templates/auditoria.yaml")
        _dry_run_msg(raiz, ".github/workflows/repository-hygiene.yml", "templates/workflow.yml")
        _dry_run_msg_skills(raiz)
        return

    _gerar_arquivo(raiz, "auditoria.yaml", "templates/auditoria.yaml", force)
    _gerar_arquivo(raiz, ".github/workflows/repository-hygiene.yml", "templates/workflow.yml", force)
    _instalar_skills(raiz, force)
    print(f"Files generated in {raiz}")

    _instalar_commit_msg(raiz, force)

    if install_hook:
        _instalar_hook(raiz, force)


def _instalar_hook(raiz, force):
    git_dir = _caminho_no_diretorio(raiz, ".git")
    if not os.path.isdir(git_dir):
        print(f"  Error: {raiz} is not a Git repository (no .git directory)", file=sys.stderr)
        return
    hook_dir = _caminho_no_diretorio(git_dir, "hooks")
    hook_path = _caminho_no_diretorio(hook_dir, "pre-commit")
    if os.path.exists(hook_path) and not force:
        print("  Skipping (already exists): .git/hooks/pre-commit")
        return
    os.makedirs(hook_dir, exist_ok=True)
    dados = pkgutil.get_data(__package__, "templates/pre-commit")
    if dados is None:
        print("  Error: template not found: templates/pre-commit", file=sys.stderr)
        return
    with open(hook_path, "wb") as f:
        f.write(dados)
    os.chmod(hook_path, 0o700)
    print("  Created: .git/hooks/pre-commit")


def _instalar_hook_commit_msg(raiz, force):
    git_dir = _caminho_no_diretorio(raiz, ".git")
    if not os.path.isdir(git_dir):
        print(f"  Error: {raiz} is not a Git repository (no .git directory)", file=sys.stderr)
        return
    hook_dir = _caminho_no_diretorio(git_dir, "hooks")
    hook_path = _caminho_no_diretorio(hook_dir, "commit-msg")
    if os.path.exists(hook_path) and not force:
        print("  Skipping (already exists): .git/hooks/commit-msg")
        return
    os.makedirs(hook_dir, exist_ok=True)
    dados = pkgutil.get_data(__package__, "templates/commit-msg")
    if dados is None:
        print("  Error: template not found: templates/commit-msg", file=sys.stderr)
        return
    with open(hook_path, "wb") as f:
        f.write(dados)
    os.chmod(hook_path, 0o700)
    print("  Created: .git/hooks/commit-msg")


def _instalar_commit_msg(raiz, force):
    git_dir = _caminho_no_diretorio(raiz, ".git")
    if not os.path.isdir(git_dir):
        print(f"  Aviso: {raiz} não é um repositório Git; hook commit-msg não instalado")
        return
    hook_dir = _caminho_no_diretorio(git_dir, "hooks")
    hook_path = _caminho_no_diretorio(hook_dir, "commit-msg")
    if os.path.exists(hook_path) and not force:
        print("  Pulando (já existe): .git/hooks/commit-msg")
        return
    os.makedirs(hook_dir, exist_ok=True)
    dados = pkgutil.get_data(__package__, "templates/commit-msg")
    if dados is None:
        print("  Erro: template não encontrado: templates/commit-msg", file=sys.stderr)
        return
    with open(hook_path, "wb") as f:
        f.write(dados)
    os.chmod(hook_path, 0o700)
    print("  Criado: .git/hooks/commit-msg")


def _gerar_arquivo(raiz, caminho_rel, template_recurso, force):
    caminho_abs = _caminho_no_diretorio(raiz, caminho_rel)
    if os.path.exists(caminho_abs) and not force:
        print(f"  Skipping (already exists): {caminho_rel}")
        return
    os.makedirs(os.path.dirname(caminho_abs), exist_ok=True)
    dados = pkgutil.get_data(__package__, template_recurso)
    if dados is None:
        print("  Error: template not found: " + template_recurso, file=sys.stderr)
        return
    with open(caminho_abs, "wb") as f:
        f.write(dados)
    print("  Created: " + caminho_rel)


def _caminho_no_diretorio(diretorio, caminho_rel):
    base = os.path.realpath(diretorio)
    caminho = os.path.realpath(os.path.join(base, caminho_rel))
    if caminho != base and not caminho.startswith(base + os.sep):
        raise ValueError(f"Path outside permitted directory: {caminho_rel}")
    return caminho
