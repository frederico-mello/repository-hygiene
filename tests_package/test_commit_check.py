"""Testes para commit_check.py."""

import subprocess


def _fazer_commit(repo, mensagem, arquivo="arquivo.txt", conteudo="x"):
    (repo / arquivo).write_text(conteudo)
    subprocess.run(
        ["git", "add", arquivo], cwd=repo, capture_output=True, timeout=10, shell=False
    )
    subprocess.run(
        ["git", "commit", "-m", mensagem],
        cwd=repo,
        capture_output=True,
        timeout=10,
        shell=False,
    )


class TestValidarCommits:
    def test_commit_segue_formato_conventional_nao_gera_finding(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "feat(auth): add OAuth2 support")

        findings = validar_commits(str(git_repo))

        assert findings == []