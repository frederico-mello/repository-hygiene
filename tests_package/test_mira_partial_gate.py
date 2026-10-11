"""Tests for Mira output classification and model fallback orchestration."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "mira-review-reusable.yml"
SCRIPT = ROOT / ".github" / "scripts" / "mira_review_chain.py"
SPEC = importlib.util.spec_from_file_location("mira_review_chain", SCRIPT)
assert SPEC and SPEC.loader
mira = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mira
SPEC.loader.exec_module(mira)

DROP_MARKER = "failed to parse, skipping"


def _partial_payload(reviewed_files: int) -> str:
    return (
        f"WARNING: chunk 1/1 {DROP_MARKER}: invalid JSON\n"
        + json.dumps({"comments": [], "reviewed_files": reviewed_files})
    )


def test_recovered_payload_with_reviewed_files_is_complete():
    outcome = mira.parse_mira_output(_partial_payload(14), 0)
    assert outcome.status == "ok"
    assert outcome.comments == 0
    assert outcome.blockers == 0
    assert outcome.dropped_chunks == 1


def test_dropped_chunk_without_coverage_is_partial():
    outcome = mira.parse_mira_output(_partial_payload(0), 0)
    assert outcome.status == "partial"
    assert outcome.dropped_chunks == 1


def test_quota_is_detected_even_when_reported_on_stderr():
    outcome = mira.parse_mira_output("", 1, "HTTP 429 GoUsageLimitError: usage limit reached")
    assert outcome.status == "quota"


def test_quota_is_detected_for_openrouter_credit_exhaustion():
    outcome = mira.parse_mira_output("", 1, "HTTP 402: insufficient credit")
    assert outcome.status == "quota"


def test_model_chain_is_ordered_and_deduplicated():
    assert mira.parse_model_chain(
        "OpenRouter/xiaomi/mimo-v2.6-flash",
        "OpenCode-Go/qwen3.8-flash",
        "OpenCode-Go/qwen3.8-flash, OpenCode-Go/qwen3.7-plus",
    ) == [
        "OpenRouter/xiaomi/mimo-v2.6-flash",
        "OpenCode-Go/qwen3.8-flash",
        "OpenCode-Go/qwen3.7-plus",
    ]


def test_model_chain_rejects_shell_metacharacters():
    try:
        mira.parse_model_chain("qwen3.8-flash; touch /tmp/x", "", "")
    except ValueError as exc:
        assert "invalid Mira model id" in str(exc)
    else:
        raise AssertionError("unsafe model id was accepted")


def test_quota_uses_fallback_then_stops_on_complete_review():
    seen = []

    def attempt(model):
        seen.append(model)
        if model == "qwen3.8-flash":
            return mira.ReviewResult("quota")
        return mira.ReviewResult("ok", comments=2, blockers=1)

    outcome, used_model, history = mira.run_chain(
        ["qwen3.8-flash", "qwen3.7-plus", "qwen3.6-plus"], attempt
    )
    assert outcome == mira.ReviewResult("ok", comments=2, blockers=1)
    assert used_model == "qwen3.7-plus"
    assert seen == ["qwen3.8-flash", "qwen3.7-plus"]
    assert [entry.status for _, entry in history] == ["quota", "ok"]


def test_partial_review_retries_once_then_advances_to_next_model():
    seen = []

    def attempt(model):
        seen.append(model)
        if model == "qwen3.8-flash":
            return mira.ReviewResult("partial")
        return mira.ReviewResult("ok", comments=1)

    outcome, used_model, history = mira.run_chain(
        ["qwen3.8-flash", "qwen3.7-plus"], attempt
    )
    assert outcome.status == "ok"
    assert used_model == "qwen3.7-plus"
    assert seen == ["qwen3.8-flash", "qwen3.8-flash", "qwen3.7-plus"]
    assert [entry.status for _, entry in history] == ["partial", "partial", "ok"]


def test_all_quota_attempts_remain_unavailable_not_clean():
    outcome, used_model, history = mira.run_chain(
        ["qwen3.8-flash", "qwen3.7-plus"], lambda _: mira.ReviewResult("quota")
    )
    assert outcome.status == "quota"
    assert used_model is None
    assert len(history) == 2


def test_quota_after_an_earlier_operational_failure_keeps_quota_status():
    outcomes = iter([mira.ReviewResult("failed"), mira.ReviewResult("quota")])
    outcome, used_model, history = mira.run_chain(
        ["qwen3.8-flash", "qwen3.7-plus"], lambda _: next(outcomes)
    )

    assert outcome.status == "quota"
    assert used_model is None
    assert [result.status for _, result in history] == ["failed", "quota"]


def test_partial_retry_evidence_is_preserved_if_later_fallback_fails():
    outcomes = iter(
        [
            mira.ReviewResult("partial", comments=1, dropped_chunks=2),
            mira.ReviewResult("partial", comments=3, blockers=1, dropped_chunks=1),
            mira.ReviewResult("failed"),
        ]
    )
    outcome, used_model, history = mira.run_chain(
        ["qwen3.8-flash", "qwen3.7-plus"], lambda _: next(outcomes)
    )

    assert outcome.status == "partial"
    assert outcome.comments == 3
    assert outcome.blockers == 1
    assert outcome.dropped_chunks == 1
    assert used_model is None
    assert [result.status for _, result in history] == ["partial", "partial", "failed"]


def test_attempt_config_pins_all_mira_roles_and_disables_implicit_fallback(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text(
        "llm:\n  model: old-primary\n  review_model: repo-review\n"
        "  indexing_model: repo-index\n  fallback_model: repo-fallback\n",
        encoding="utf-8",
    )
    attempt = tmp_path / "attempt.yaml"

    mira.config_for_model(base, "qwen3.7-plus", attempt)

    import yaml

    llm = yaml.safe_load(attempt.read_text(encoding="utf-8"))["llm"]
    assert llm["model"] == "qwen3.7-plus"
    assert llm["review_model"] == "qwen3.7-plus"
    assert llm["indexing_model"] == "qwen3.7-plus"
    assert llm["fallback_model"] is None


def test_openrouter_attempt_keeps_the_vendor_model_and_uses_its_key(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text(
        "llm:\n  base_url: https://opencode.ai/zen/go/v1\n"
        "  api_key_env: OPENCODE_GO_API_KEY\n",
        encoding="utf-8",
    )
    attempt = tmp_path / "openrouter.yaml"

    mira.config_for_model(base, "OpenRouter/xiaomi/mimo-v2.6-flash", attempt)

    import yaml

    llm = yaml.safe_load(attempt.read_text(encoding="utf-8"))["llm"]
    assert llm["base_url"] == "https://openrouter.ai/api/v1"
    assert llm["api_key_env"] == "OPENROUTER_API_KEY"
    assert llm["model"] == "xiaomi/mimo-v2.6-flash"
    assert llm["review_model"] == "xiaomi/mimo-v2.6-flash"
    assert mira.resolve_model_route("OpenRouter/xiaomi/mimo-v2.6-flash") == (
        "openrouter",
        "xiaomi/mimo-v2.6-flash",
    )
    assert mira.resolve_model_route("xiaomi/mimo-v2.6-flash")[0] == "openrouter"
    assert mira.resolve_model_route("qwen3.8-flash")[0] == "opencode-go"


def test_opencode_go_attempt_uses_its_independent_endpoint_and_key(tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text(
        "llm:\n  base_url: https://openrouter.ai/api/v1\n"
        "  api_key_env: OPENROUTER_API_KEY\n",
        encoding="utf-8",
    )
    attempt = tmp_path / "opencode-go.yaml"

    mira.config_for_model(base, "OpenCode-Go/qwen3.8-flash", attempt)

    llm = yaml.safe_load(attempt.read_text(encoding="utf-8"))["llm"]
    assert llm["base_url"] == "https://opencode.ai/zen/go/v1"
    assert llm["api_key_env"] == "OPENCODE_GO_API_KEY"
    assert llm["model"] == "qwen3.8-flash"
    assert mira.resolve_model_route("OpenCode-Go/qwen3.8-flash") == (
        "opencode-go",
        "qwen3.8-flash",
    )


def test_openrouter_route_without_secret_is_skipped_before_running_mira(tmp_path, monkeypatch):
    base = tmp_path / "base.yaml"
    base.write_text("llm: {}\n", encoding="utf-8")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        mira.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Mira must not run")),
    )

    outcome = mira._run_mira(
        "OpenRouter/xiaomi/mimo-v2.6-flash",
        "https://github.com/example/repo/pull/1",
        base,
        tmp_path,
        "test-token",
        False,
        "mira",
    )

    assert outcome.status == "failed"
    assert "OPENROUTER_API_KEY" in outcome.detail


def test_opencode_go_route_without_secret_is_skipped_before_running_mira(tmp_path, monkeypatch):
    base = tmp_path / "base.yaml"
    base.write_text("llm: {}\n", encoding="utf-8")
    monkeypatch.delenv("OPENCODE_GO_API_KEY", raising=False)
    monkeypatch.setattr(
        mira.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("Mira must not run")),
    )

    outcome = mira._run_mira(
        "OpenCode-Go/qwen3.8-flash",
        "https://github.com/example/repo/pull/1",
        base,
        tmp_path,
        "test-token",
        False,
        "mira",
    )

    assert outcome.status == "failed"
    assert "OPENCODE_GO_API_KEY" in outcome.detail


def test_main_fails_visibly_if_every_model_is_over_quota(tmp_path, monkeypatch):
    base = tmp_path / "base.yaml"
    base.write_text("llm: {}\n", encoding="utf-8")
    output = tmp_path / "github-output"
    output.write_text("", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))

    attempted = []

    def fake_run(model, *_args):
        attempted.append(model)
        return mira.ReviewResult("quota")

    monkeypatch.setattr(mira, "_run_mira", fake_run)
    code = mira.main(
        [
            "--pr-url",
            "https://github.com/example/repo/pull/1",
            "--base-config",
            str(base),
            "--model",
            "qwen3.8-flash",
            "--fallback-model",
            "qwen3.7-plus",
            "--fallback-models",
            "qwen3.6-plus",
        ]
    )

    values = dict(
        line.split("=", 1)
        for line in output.read_text(encoding="utf-8").splitlines()
        if "=" in line
    )
    assert code == 1
    assert attempted == ["qwen3.8-flash", "qwen3.7-plus", "qwen3.6-plus"]
    assert values["status"] == "quota"
    assert values["used_model"] == ""
    assert json.loads(values["models_attempted"]) == attempted


def test_runner_invokes_fallback_process_after_quota(tmp_path, monkeypatch):
    base = tmp_path / "base.yaml"
    base.write_text("llm: {}\n", encoding="utf-8")
    output = tmp_path / "github-output"
    output.write_text("", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "test-opencode-token")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    attempted = []

    def fake_run(command, **_kwargs):
        config_path = Path(command[command.index("--config") + 1])
        model = yaml.safe_load(config_path.read_text(encoding="utf-8"))["llm"]["model"]
        attempted.append(model)
        if model == "qwen3.8-flash":
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="HTTP 429 GoUsageLimitError: usage limit reached",
                stderr="",
            )
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"comments": [], "reviewed_files": 3}),
            stderr="",
        )

    monkeypatch.setattr(mira.subprocess, "run", fake_run)
    code = mira.main(
        [
            "--pr-url",
            "https://github.com/example/repo/pull/1",
            "--base-config",
            str(base),
            "--model",
            "qwen3.8-flash",
            "--fallback-model",
            "qwen3.7-plus",
        ]
    )
    values = dict(
        line.split("=", 1)
        for line in output.read_text(encoding="utf-8").splitlines()
        if "=" in line
    )

    assert code == 0
    assert attempted == ["qwen3.8-flash", "qwen3.7-plus"]
    assert values["status"] == "ok"
    assert values["used_model"] == "qwen3.7-plus"
    assert values["attempts"] == "2"


def test_runner_uses_opencode_go_after_openrouter_quota(tmp_path, monkeypatch):
    base = tmp_path / "base.yaml"
    base.write_text(
        "llm:\n  base_url: https://opencode.ai/zen/go/v1\n"
        "  api_key_env: OPENCODE_GO_API_KEY\n",
        encoding="utf-8",
    )
    output = tmp_path / "github-output"
    output.write_text("", encoding="utf-8")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-openrouter-token")
    monkeypatch.setenv("OPENCODE_GO_API_KEY", "test-opencode-token")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    attempts = []

    def fake_run(command, **_kwargs):
        config_path = Path(command[command.index("--config") + 1])
        llm = yaml.safe_load(config_path.read_text(encoding="utf-8"))["llm"]
        attempts.append(
            {"model": llm["model"], "base_url": llm["base_url"], "api_key_env": llm["api_key_env"]}
        )
        if llm["base_url"] == "https://openrouter.ai/api/v1":
            return subprocess.CompletedProcess(
                command,
                1,
                stdout="HTTP 429 GoUsageLimitError: usage limit reached",
                stderr="",
            )
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=json.dumps({"comments": [], "reviewed_files": 3}),
            stderr="",
        )

    monkeypatch.setattr(mira.subprocess, "run", fake_run)
    code = mira.main(
        [
            "--pr-url",
            "https://github.com/example/repo/pull/1",
            "--base-config",
            str(base),
            "--model",
            "OpenRouter/xiaomi/mimo-v2.6-flash",
            "--fallback-model",
            "OpenCode-Go/qwen3.8-flash",
        ]
    )
    values = dict(
        line.split("=", 1)
        for line in output.read_text(encoding="utf-8").splitlines()
        if "=" in line
    )

    assert code == 0
    assert attempts == [
        {
            "model": "xiaomi/mimo-v2.6-flash",
            "base_url": "https://openrouter.ai/api/v1",
            "api_key_env": "OPENROUTER_API_KEY",
        },
        {
            "model": "qwen3.8-flash",
            "base_url": "https://opencode.ai/zen/go/v1",
            "api_key_env": "OPENCODE_GO_API_KEY",
        },
    ]
    assert values["status"] == "ok"
    assert values["used_model"] == "OpenCode-Go/qwen3.8-flash"


def test_workflow_wires_fallback_runner_and_gives_chain_time_to_run():
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    review = next(
        step for step in doc["jobs"]["review"]["steps"] if step.get("id") == "review"
    )
    helper_checkout = next(
        step for step in doc["jobs"]["review"]["steps"]
        if step.get("name") == "Check out Mira runner"
    )
    inputs = doc.get("on", doc.get(True))["workflow_call"]["inputs"]
    call_secrets = doc.get("on", doc.get(True))["workflow_call"]["secrets"]

    assert helper_checkout["with"]["repository"] == "frederico-mello/repository-hygiene"
    assert helper_checkout["with"]["ref"] == "4eb7e1bbec1ab9e25a8c38174b0ea75d3f3eb2db"
    assert helper_checkout["with"]["path"] == ".mira-workflow"
    assert ".mira-workflow/.github/scripts/mira_review_chain.py" in review["run"]
    assert "MIRA_FALLBACK_MODELS" in review["env"]
    assert "OPENROUTER_API_KEY" in review["env"]
    assert "OPENCODE_GO_API_KEY" in review["env"]
    assert call_secrets["OPENROUTER_API_KEY"]["required"] is True
    assert call_secrets["OPENCODE_GO_API_KEY"]["required"] is False
    assert inputs["model"]["default"] == "OpenRouter/xiaomi/mimo-v2.6-flash"
    assert inputs["fallback-model"]["default"] == "OpenCode-Go/qwen3.8-flash"
    assert inputs["fallback-models"]["default"]
    assert doc["jobs"]["review"]["timeout-minutes"] == 70


def test_workflow_builds_openrouter_and_opencode_provider_profiles(tmp_path):
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    build = next(
        step for step in doc["jobs"]["review"]["steps"]
        if step.get("name") == "Build effective config and provider profile"
    )
    marker = "python - \"$RUNNER_TEMP/mira-effective.yaml\" <<'PY'\n"
    _, found, rest = build["run"].partition(marker)
    code, end, _ = rest.partition("\nPY\n")
    assert found and end and code.strip()

    runner_temp = tmp_path / "runner-temp"
    runner_temp.mkdir()
    env = dict(os.environ)
    env.update(
        {
            "SESSION": "mira-example-1",
            "MODEL": "qwen3.8-flash",
            "MAX_COMMENTS": "5",
            "RUNNER_TEMP": str(runner_temp),
            "GITHUB_ENV": str(tmp_path / "github-env"),
        }
    )
    completed = subprocess.run(
        [sys.executable, "-c", code, str(runner_temp / "mira-effective.yaml")],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    profiles = json.loads((runner_temp / "providers.json").read_text(encoding="utf-8"))
    assert profiles["openrouter"] == {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "model_prefix": "keep",
        "extra_headers": {
            "HTTP-Referer": "https://github.com/frederico-mello/repository-hygiene",
            "X-Title": "Mira Code Review",
        },
        "reasoning_effort_map": {"max": "xhigh"},
    }
    assert profiles["opencode-go"] == {
        "base_url": "https://opencode.ai/zen/go/v1",
        "api_key_env": "OPENCODE_GO_API_KEY",
        "model_prefix": "strip",
        "extra_headers": {"x-opencode-session": "mira-example-1"},
        "reasoning_effort_map": {},
    }
    assert "MIRA_PROVIDERS_JSON_PATH=$RUNNER_TEMP/providers.json" in build["run"]
