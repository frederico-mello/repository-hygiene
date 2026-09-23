"""Testes para commit_check.py."""

import subprocess

import pytest


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


def _validar_apos_commit(repo, mensagem, **kwargs):
    from auditoria_higiene.commit_check import validar_commits

    _fazer_commit(repo, mensagem)
    return validar_commits(str(repo), **kwargs)


def _auditar_apos_commit(repo, regra_config, mensagem):
    from auditoria_higiene.core import executar_auditoria

    _fazer_commit(repo, mensagem)
    config = {
        "config_version": 1,
        "rules": {"conventional-commits": regra_config},
    }
    return executar_auditoria(str(repo), config)


@pytest.mark.parametrize(
    "mensagem",
    [
        "feat(auth): add OAuth2 support",
        "docs: update README",
        "feat(api): add rate limiting",
        "feat!: drop Python 3.8 support",
        "style: fix indentation",
        "refactor(core): extract validation",
        "perf: optimize query",
        "test: add coverage",
        "chore: update deps",
        "ci: add actionlint",
        "build: bump setuptools",
    ],
)
def test_mensagens_validas_nao_geram_findings(git_repo, mensagem):
    assert _validar_apos_commit(git_repo, mensagem) == []


@pytest.mark.parametrize(
    "mensagem",
    [
        "added OAuth2 support",
        "wip: partial work",
        "feat(auth: add login",
    ],
)
def test_mensagens_invalidas_geram_findings(git_repo, mensagem):
    findings = _validar_apos_commit(git_repo, mensagem)
    assert len(findings) == 1
    assert findings[0]["regra"] == "conventional-commits"


def test_finding_carrega_mensagem_original(git_repo):
    mensagem = "added OAuth2 support"
    findings = _validar_apos_commit(git_repo, mensagem)
    assert findings[0]["mensagem"].startswith("Commit não segue Conventional Commits")
    assert mensagem in findings[0]["mensagem"]


def test_tipo_invalido_refletido_no_finding(git_repo):
    findings = _validar_apos_commit(git_repo, "wip: partial work")
    assert "wip" in findings[0]["mensagem"]


def test_escopo_malformado_gera_finding(git_repo):
    assert len(_validar_apos_commit(git_repo, "feat(auth: add login")) == 1


def test_merge_commit_ignorado(git_repo):
    from auditoria_higiene.commit_check import validar_commits

    _fazer_merge(git_repo, "Merge pull request #42 from feature")
    assert validar_commits(str(git_repo)) == []


def test_repositorio_vazio_sem_findings(git_repo):
    from auditoria_higiene.commit_check import validar_commits

    assert validar_commits(str(git_repo)) == []


def test_git_inexistente_retorna_erro(monkeypatch):
    from auditoria_higiene.commit_check import validar_commits

    def mock_run(*args, **kwargs):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(subprocess, "run", mock_run)
    findings = validar_commits("/fake/repo")
    assert len(findings) == 1
    assert findings[0]["regra"] == "conventional-commits"
    assert findings[0]["severity"] == "error"
    assert "git" in findings[0]["mensagem"].lower()


def test_nivel_error_por_parametro(git_repo):
    findings = _validar_apos_commit(git_repo, "invalid message", severidade="error")
    assert len(findings) == 1
    assert findings[0]["severity"] == "error"


def test_regra_desabilitada_sem_findings(git_repo):
    resultado = _auditar_apos_commit(
        git_repo,
        {"enabled": False, "severity": "warning"},
        "invalid message",
    )
    findings = [
        r for r in resultado["resultados"] if r["regra"] == "conventional-commits"
    ]
    assert findings == []


def test_commit_invalido_gera_finding_via_auditoria(git_repo):
    resultado = _auditar_apos_commit(
        git_repo,
        {"enabled": True, "severity": "warning"},
        "invalid message",
    )
    assert resultado["status"] == "sucesso"
    findings = [
        r for r in resultado["resultados"] if r["regra"] == "conventional-commits"
    ]
    assert len(findings) == 1


def test_revert_conventional_inner_nao_gera_findings(git_repo):
    assert _validar_apos_commit(git_repo, 'Revert "feat: add OAuth2 support"') == []


def test_revert_nonconventional_inner_nao_gera_findings(git_repo):
    assert _validar_apos_commit(git_repo, 'Revert "added OAuth2"') == []


def test_nonrevert_conventional_ainda_validado(git_repo):
    assert _validar_apos_commit(git_repo, "feat: remove broken feature") == []


def test_nonrevert_nonconventional_ainda_flagado(git_repo):
    findings = _validar_apos_commit(git_repo, "rolled back the auth changes")
    assert len(findings) == 1
    assert findings[0]["regra"] == "conventional-commits"
