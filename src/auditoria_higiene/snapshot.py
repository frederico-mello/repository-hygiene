"""Snapshot do índice Git para auditoria de staged."""
import os
import subprocess
import tempfile
import shutil

from auditoria_higiene.core import executar_auditoria, validar_configuracao


def criar_snapshot(raiz):
    snapshot_dir = tempfile.mkdtemp(prefix="auditoria-snapshot-")
    result = subprocess.run(
        ["git", "ls-files", "--cached"],
        capture_output=True, text=True, cwd=raiz, timeout=30, shell=False,
    )
    if result.returncode != 0:
        shutil.rmtree(snapshot_dir, ignore_errors=True)
        raise RuntimeError("Falha ao listar arquivos do índice Git")
    arquivos = [linha.strip() for linha in result.stdout.splitlines() if linha.strip()]
    for caminho_rel in arquivos:
        caminho_dest = os.path.join(snapshot_dir, caminho_rel)
        os.makedirs(os.path.dirname(caminho_dest), exist_ok=True)
        try:
            result_show = subprocess.run(
                ["git", "show", f":{caminho_rel}"],
                capture_output=True, cwd=raiz, timeout=30,
                check=True, shell=False,
            )
        except subprocess.CalledProcessError:
            shutil.rmtree(snapshot_dir, ignore_errors=True)
            raise RuntimeError(f"Falha ao materializar arquivo do índice: {caminho_rel}")
        with open(caminho_dest, "wb") as f:
            f.write(result_show.stdout)
    return snapshot_dir


def limpar_snapshot(caminho):
    shutil.rmtree(caminho, ignore_errors=True)


def executar_pre_commit(raiz, config):
    validar_configuracao(config)
    snapshot_dir = criar_snapshot(raiz)
    try:
        return executar_auditoria(snapshot_dir, config)
    finally:
        limpar_snapshot(snapshot_dir)
