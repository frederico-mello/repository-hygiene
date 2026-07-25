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


def _fazer_merge(repo, mensagem="Merge pull request #42 from feature"):
    _fazer_commit(repo, "feat: base commit")
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=10,
    )
    branch_original = result.stdout.strip()
    subprocess.run(
        ["git", "checkout", "-b", "feature-branch"],
        cwd=repo,
        capture_output=True,
        timeout=10,
    )
    _fazer_commit(repo, "feat: branch work")
    subprocess.run(
        ["git", "checkout", branch_original],
        cwd=repo,
        capture_output=True,
        timeout=10,
    )
    subprocess.run(
        ["git", "merge", "--no-ff", "feature-branch", "-m", mensagem],
        cwd=repo,
        capture_output=True,
        timeout=10,
    )


class TestValidarCommits:
    def test_commit_segue_formato_conventional_nao_gera_finding(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "feat(auth): add OAuth2 support")

        findings = validar_commits(str(git_repo))

        assert findings == []

    def test_commit_sem_formato_gera_finding(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "added OAuth2 support")
        mensagem = "added OAuth2 support"

        findings = validar_commits(str(git_repo))

        assert len(findings) == 1
        assert findings[0]["regra"] == "conventional-commits"
        assert findings[0]["severidade"] == "warning"
        assert mensagem in findings[0]["mensagem"]

    def test_tipo_valido_docs_aceito(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "docs: update README")

        findings = validar_commits(str(git_repo))

        assert findings == []

    def test_tipo_invalido_wip_gera_finding(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "wip: partial work")

        findings = validar_commits(str(git_repo))

        assert len(findings) == 1
        assert "wip" in findings[0]["mensagem"]

    def test_commit_com_escopo_aceito(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "feat(api): add rate limiting")

        findings = validar_commits(str(git_repo))

        assert findings == []

    def test_breaking_change_aceito(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "feat!: drop Python 3.8 support")

        findings = validar_commits(str(git_repo))

        assert findings == []

    def test_escopo_malformado_gera_finding(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "feat(auth: add login")

        findings = validar_commits(str(git_repo))

        assert len(findings) == 1

    def test_merge_commit_ignorado(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_merge(git_repo, "Merge pull request #42 from feature")

        findings = validar_commits(str(git_repo))

        assert len(findings) == 0

    def test_repositorio_vazio_sem_findings(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        findings = validar_commits(str(git_repo))

        assert isinstance(findings, list)
        assert len(findings) == 0

    def test_git_inexistente_retorna_erro(self, monkeypatch):
        from auditoria_higiene.commit_check import validar_commits

        def mock_run(*args, **kwargs):
            raise FileNotFoundError("git not found")

        monkeypatch.setattr(subprocess, "run", mock_run)

        findings = validar_commits("/fake/repo")

        assert len(findings) == 1
        assert findings[0]["regra"] == "conventional-commits"
        assert findings[0]["severidade"] == "error"
        assert "git" in findings[0]["mensagem"].lower()

    def test_nivel_error_por_parametro(self, git_repo):
        from auditoria_higiene.commit_check import validar_commits

        _fazer_commit(git_repo, "invalid message")

        findings = validar_commits(str(git_repo), severidade="error")

        assert len(findings) == 1
        assert findings[0]["severidade"] == "error"

    def test_regra_desabilitada_sem_findings(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        _fazer_commit(git_repo, "invalid message")

        config = {
            "versao_configuracao": 1,
            "regras": {
                "conventional-commits": {
                    "habilitada": False,
                    "severidade": "warning",
                }
            },
        }
        resultado = executar_auditoria(str(git_repo), config)

        findings = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "conventional-commits"
        ]
        assert len(findings) == 0

    def test_integracao_core_commit_invalido_gera_finding(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        _fazer_commit(git_repo, "invalid message")

        config = {
            "versao_configuracao": 1,
            "regras": {
                "conventional-commits": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
        }
        resultado = executar_auditoria(str(git_repo), config)

        assert resultado["status"] == "sucesso"
        findings = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "conventional-commits"
        ]
        assert len(findings) == 1