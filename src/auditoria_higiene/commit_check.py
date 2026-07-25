"""Validação de mensagens de commit contra o padrão Conventional Commits."""

import re
import subprocess


_PADRAO_CONVENCIONAL = re.compile(
    r"^(?:feat|fix|docs|style|refactor|perf|test|chore|ci|build)"
    r"(?:\([^)]+\))?"
    r"!?"
    r": \S.*$"
)


def validar_commits(repo_path, severidade="warning"):
    try:
        resultado = subprocess.run(
            ["git", "log", "--no-merges", "--format=%H%x00%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
    except FileNotFoundError:
        return [
            {
                "regra": "conventional-commits",
                "caminho": repo_path,
                "severidade": "error",
                "mensagem": "git não disponível no PATH — auditoria de commits não executada",
            }
        ]
    except subprocess.SubprocessError:
        return []

    if resultado.returncode != 0:
        return []

    findings = []
    for linha in resultado.stdout.splitlines():
        if "\x00" not in linha:
            continue
        hash_commit, _, mensagem = linha.partition("\x00")
        if not _mensagem_conventional(mensagem):
            findings.append(
                {
                    "regra": "conventional-commits",
                    "caminho": hash_commit,
                    "severidade": severidade,
                    "mensagem": f"Commit não segue Conventional Commits: {mensagem!r}",
                }
            )
    return findings


def _mensagem_conventional(mensagem):
    if not mensagem:
        return False
    return bool(_PADRAO_CONVENCIONAL.match(mensagem))