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


def cmd_install_skill(directory, force=False, dry_run=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Error: directory not found: {raiz}", file=sys.stderr)
        sys.exit(2)
    if dry_run:
        _dry_run_msg_skills(raiz)
        return
    _instalar_skills(raiz, force)


def cmd_update(directory, version=None, dry_run=False):
    raiz = os.path.abspath(directory)
    if not os.path.isdir(raiz):
        print(f"Error: directory not found: {raiz}", file=sys.stderr)
        sys.exit(2)

    if dry_run:
        _dry_run_msg(raiz, "auditoria.yaml", "templates/auditoria.yaml")
        _dry_run_msg(raiz, ".github/workflows/repository-hygiene.yml", "templates/workflow.yml")
        return

    _gerar_arquivo(raiz, "auditoria.yaml", "templates/auditoria.yaml", True)
    _gerar_arquivo(raiz, ".github/workflows/repository-hygiene.yml", "templates/workflow.yml", True)
    print(f"Files updated in {raiz}")


def _dry_run_msg(raiz, caminho_rel, _template_recurso):
    caminho = os.path.join(raiz, caminho_rel).replace(os.sep, "/")
    print(f"  dry-run: {caminho}")


def _skills_root():
    templates_root = files("auditoria_higiene.templates")
    skills_root = templates_root.joinpath("skills")
    if not skills_root.is_dir():
        return None
    return skills_root


def _listar_skills():
    raiz_skills = _skills_root()
    if raiz_skills is None:
        return []
    return sorted([p.name for p in raiz_skills.iterdir() if p.is_dir()])


def _dry_run_msg_skills(raiz):
    for skill_name in _listar_skills():
        skill_dir_rel = os.path.join(".opencode", "skills", skill_name)
        caminho = os.path.join(raiz, skill_dir_rel).replace(os.sep, "/")
        print(f"  dry-run: {caminho}")


def _instalar_skills(raiz, force):
    raiz_skills = _skills_root()
    if raiz_skills is None:
        return
    for skill_name in _listar_skills():
        skill_src = raiz_skills.joinpath(skill_name)
        skill_dest_rel = os.path.join(".opencode", "skills", skill_name)
        skill_dest_abs = _caminho_no_diretorio(raiz, skill_dest_rel)
        if os.path.exists(skill_dest_abs) and not force:
            print(f"  Skipping (already exists): {skill_dest_rel}")
            continue
        os.makedirs(skill_dest_abs, exist_ok=True)
        for entrada in skill_src.iterdir():
            if not entrada.is_file():
                continue
            destino_arquivo = os.path.join(skill_dest_abs, entrada.name)
            with open(destino_arquivo, "wb") as saida:
                saida.write(entrada.read_bytes())
        print(f"  Created: {skill_dest_rel}")


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
