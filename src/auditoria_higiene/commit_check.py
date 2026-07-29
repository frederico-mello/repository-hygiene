"""Validação de mensagens de commit no padrão Conventional Commits."""

import re
import subprocess


_TIPOS_VALIDOS = "feat|fix|docs|style|refactor|perf|test|chore|ci|build"
_PADRAO_MENSAGEM = re.compile(rf"^(?:{_TIPOS_VALIDOS})(?:\([^()]+\))?!?: .+\S$")


def validar_commits(repo_path, severidade="warning"):
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--format=%H%x00%P%x00%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        return [
            {
                "regra": "conventional-commits",
                "caminho": repo_path,
                "severidade": "error",
                "mensagem": "git não está disponível no ambiente",
            }
        ]
    if result.returncode != 0:
        return []

    findings = []
    for line in result.stdout.splitlines():
        commit_hash, parents, message = line.split("\x00", 2)
        if len(parents.split()) > 1:
            continue
        if not _PADRAO_MENSAGEM.fullmatch(message):
            findings.append(
                {
                    "regra": "commits_convencionais",
                    "caminho": commit_hash,
                    "severidade": severidade,
                    "mensagem": "Mensagem não segue Conventional Commits",
                }
            )
    return findings
