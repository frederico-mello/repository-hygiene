"""Testes Go-only do caminho pull_request e issue_comment da revisão Mira.

Prova determinística, contra os arquivos reais do worktree:
1. O chamador referencia o reusable frederico-mello/repository-hygiene pinado
   ao SHA completo do commit que arma o gate Go-only (52c0ebe1…). O teste
   prova que o pin é um objeto Git real (commit) cujo diff altera o reusable
   — não um comentário decorativo.
2. No reusable, MIRA_GO_ONLY='1' incondicional: o roteador real recusa qualquer
   rota não-go ANTES de ler credencial ou abrir transporte — nenhum payload
   chega a Ollama Cloud, em nenhum evento.
3. issue_comment permanece exatamente Go-only como antes.
"""

import importlib.util
import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parent.parent
CALLER = ROOT / ".github" / "workflows" / "mira-review.yml"
REUSABLE = ROOT / ".github" / "workflows" / "mira-review-reusable.yml"
ROUTER_STEP_NAME = "Start isolated routing proxy"
# Commit que introduz o reusable Go-only incondicional; é este SHA que o
# chamador fixa em `uses:`. Mantenha os dois em sync numa mesma revisão.
EXPECTED_PIN = "52c0ebe1057079a686191ee19ba043fdceef0fe8"


def _caller():
    return yaml.safe_load(CALLER.read_text(encoding="utf-8"))


def _reusable():
    return yaml.safe_load(REUSABLE.read_text(encoding="utf-8"))


def _routing_step(reusable):
    return next(
        step
        for step in reusable["jobs"]["review"]["steps"]
        if step.get("name") == ROUTER_STEP_NAME
    )


def _load_router(tmp_path):
    """Importa o roteador real do worktree com home sintética."""
    spec = importlib.util.spec_from_file_location(
        "mira_router_go_only_under_test",
        ROOT / ".github" / "mira" / "mira-router-new.py",
    )
    module = importlib.util.module_from_spec(spec)
    home = tmp_path / "synthetic-home"
    home.mkdir(exist_ok=True)
    with patch.object(Path, "home", return_value=home):
        spec.loader.exec_module(module)
    module.STATE_DIR = tmp_path / "routing-state"
    module.STATES.clear()
    return module


def _git(*args):
    return subprocess.run(
        ["git", "-C", str(ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_caller_pins_reusable_to_exact_immutable_sha():
    """Chamador fixa o reusable externo no SHA completo do commit Go-only.

    O pin imutável impede redirecionamento pós-revisão — tag/branch pode ser
    movida; SHA completo de 40 hex não. O pin não é comentário decorativo:
    o teste valida o objeto Git real e que o commit pinado altera o reusable.
    """
    job = _caller()["jobs"]["mira"]
    repo_ref, sep, sha = job["uses"].partition("@")
    assert sep and repo_ref == (
        "frederico-mello/repository-hygiene"
        "/.github/workflows/mira-review-reusable.yml"
    )
    # SHA completo, 40 hex minúsculos — não abreviação.
    assert len(sha) == 40
    assert all(ch in "0123456789abcdef" for ch in sha)
    assert sha == EXPECTED_PIN
    # Pin real: o SHA existe como objeto commit no repositório.
    assert _git("cat-file", "-t", sha).strip() == "commit"
    # E o commit pinado é efetivamente o do reusable Go-only: seu diff altera
    # exatamente .github/workflows/mira-review-reusable.yml.
    changed = _git(
        "diff-tree", "--no-commit-id", "--name-only", "-r", sha
    ).splitlines()
    assert ".github/workflows/mira-review-reusable.yml" in changed
    header = CALLER.read_text(encoding="utf-8")
    # Sem resquício dos pins antigos ou de referência local sem pin.
    assert "5582d903" not in header
    assert "93db0438" not in header
    assert 'uses: ./.github/workflows/mira-review-reusable.yml' not in header
    # O comentário descreve o pin com precisão.
    assert "full commit SHA" in header
    assert "Go-only" in header


def test_reusable_arms_go_only_gate_on_every_event():
    """MIRA_GO_ONLY='1' incondicional: gate real do roteador, em todos os eventos."""
    env = _routing_step(_reusable())["env"]
    assert env["MIRA_GO_ONLY"] == "1"
    # Sem nenhuma expressão condicionada a evento no gate.
    assert "github.event_name == 'issue_comment'" not in env["MIRA_GO_ONLY"]


def test_issue_comment_behavior_unchanged():
    """issue_comment: mesmas envs do router de antes (credential + go-only)."""
    env = _routing_step(_reusable())["env"]
    assert (
        env["OLLAMA_API_KEY"]
        == "${{ github.event_name != 'issue_comment' && secrets.OLLAMA_API_KEY || '' }}"
    )
    assert env["OPENCODE_GO_API_KEY"] == "${{ secrets.OPENCODE_GO_API_KEY }}"
    assert env["MIRA_GO_ONLY"] == "1"


def test_caller_withholds_ollama_credential_on_every_event():
    """Chamador não encaminha OLLAMA_API_KEY em nenhum evento."""
    secrets = _caller()["jobs"]["mira"]["secrets"]
    assert secrets["OLLAMA_API_KEY"] == ""


def test_pull_request_run_never_selects_or_calls_ollama_route(tmp_path):
    """pull_request com Go falhando: nenhuma chamada à rota/transporte ollama.

    Reproduz o cenário antes falho — Go 500 (transiente) e depois 429 — e
    prova que o roteador real, com MIRA_GO_ONLY=1, não seleciona 'ollama'
    nem invoca o transporte com um payload, encerrando fail-closed.
    """
    router = _load_router(tmp_path)
    calls = []

    def send(route, identity, body):
        calls.append(route)
        if route != "go":
            raise AssertionError(f"rota {route!r} não deveria ser chamada")
        return 500, json.dumps({"error": {"message": "transient"}})

    # pull_request-shaped: sem MIRA_GO_ONLY via evento, credenciais presentes
    # (prova que o gate é o MIRA_GO_ONLY, não a ausência de credencial).
    env = {
        "MIRA_GO_ONLY": "1",
        "OPENCODE_GO_API_KEY": "FAKE_GO",
        "OLLAMA_API_KEY": "FAKE_OLLAMA",
    }
    with patch.object(router.os, "environ", env):
        code, body = router.route_and_call(
            {"model": router.MODEL, "tools": [], "messages": []},
            "pr-go-only",
            send=send,
            pause=lambda _seconds: None,
        )

    assert code == 500
    # Terminal fail-closed: code 500 with the upstream body passed through
    # (state.failed set; see per_route below) — no ollama route was selected.
    assert json.loads(body)["error"]["message"] == "transient"
    # Somente a rota go é chamada: uma tentativa + um retry transiente, e o
    # estado terminal — nenhuma seleção ou chamada da rota ollama.
    assert calls == ["go", "go"]
    state = router.state_for("pr-go-only")
    assert state.failed
    assert state.reason == "upstream_failure_500"
    assert state.per_route == {"go": 2, "ollama": 0}


def test_pull_request_router_never_reads_ollama_credential(tmp_path):
    """Em go-only o transporte real nunca lê OLLAMA_API_KEY."""
    router = _load_router(tmp_path)
    reads = []
    opened = []

    class SpyEnv(dict):
        def get(self, key, default=None):
            reads.append(key)
            return super().get(key, default)

    env = SpyEnv(MIRA_GO_ONLY="1", OPENCODE_GO_API_KEY="FAKE_GO", OLLAMA_API_KEY="FAKE_OLLAMA")

    def fail_open(*args, **kwargs):
        opened.append(args)
        raise OSError("network attempted")

    with patch.object(router.os, "environ", env), \
         patch.object(router.urllib.request, "urlopen", fail_open):
        code, body = router.route_and_call(
            {"model": router.MODEL, "tools": [], "messages": []},
            "pr-cred-spy",
            send=router.forward,
            pause=lambda _seconds: None,
        )

    # Transporte tentado só na rota go (falha os) e nunca na ollama; o erro
    # os-level vira 503 fail-closed.
    assert code == 503
    assert json.loads(body)["error"]["message"] == "upstream_transport_failure"
    assert len(opened) <= 2  # tentativa + retry transiente, ambos go
    assert "OLLAMA_API_KEY" not in reads
    assert reads.count("OPENCODE_GO_API_KEY") == len(opened)


def test_issue_comment_router_go_only_unchanged(tmp_path):
    """issue_comment: falha do Go termina fail-closed, sem rota ollama."""
    router = _load_router(tmp_path)
    calls = []

    def send(route, identity, body):
        calls.append(route)
        return 429, json.dumps({"error": {"message": "quota"}})

    env = {
        "MIRA_GO_ONLY": "1",
        "OPENCODE_GO_API_KEY": "FAKE_GO",
        "OLLAMA_API_KEY": "FAKE_OLLAMA",
    }
    with patch.object(router.os, "environ", env):
        code, body = router.route_and_call(
            {"model": router.MODEL, "tools": [], "messages": []},
            "ic-go-only",
            send=send,
            pause=lambda _seconds: None,
        )

    assert code == 429
    assert calls == ["go"]
    state = router.state_for("ic-go-only")
    assert state.failed
    assert state.reason == "upstream_failure_429"
    assert state.per_route["ollama"] == 0


def test_router_go_only_refuses_ollama_route_before_transport(tmp_path):
    """Prova de unidade do gate: rota ollama recusada sem tocar transporte."""
    router = _load_router(tmp_path)

    def send(route, identity, body):
        raise AssertionError(f"transporte invocado para rota {route!r}")

    env = {"MIRA_GO_ONLY": "1", "OPENCODE_GO_API_KEY": "FAKE_GO", "OLLAMA_API_KEY": "FAKE_OLLAMA"}
    with patch.object(router.os, "environ", env):
        code, body = router.forward("ollama", "gate-probe", {"model": router.MODEL})

    assert code == 503
    assert json.loads(body)["error"]["message"] == "go_only_route_disabled"