"""Run Mira with an ordered OpenRouter/OpenCode Go fallback chain.

A workflow check is successful only when Mira returns a complete review payload.
Quota/operational failures try the next route; exhausting the chain fails the
step so an unavailable reviewer cannot appear as a green review.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml

DROP_MARKER = "failed to parse, skipping"
QUOTA_MARKERS = (
    "gousagelimiterror",
    "usage limit",
    "http 429",
    "insufficient credit",
    "http 402",
)
MODEL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")


@dataclass(frozen=True)
class ReviewResult:
    status: str
    comments: int = 0
    blockers: int = 0
    dropped_chunks: int = 0
    detail: str = ""


def parse_model_chain(primary: str, legacy_fallback: str, fallbacks: str) -> list[str]:
    """Return a validated, ordered, deduplicated list of model ids."""
    raw = [primary, legacy_fallback, *fallbacks.split(",")]
    models: list[str] = []
    for item in raw:
        model = item.strip()
        if not model or model in models:
            continue
        if not MODEL_ID_RE.fullmatch(model):
            raise ValueError(f"invalid Mira model id: {model!r}")
        resolve_model_route(model)
        models.append(model)
    if not models:
        raise ValueError("Mira model chain is empty")
    return models


def resolve_model_route(model: str) -> tuple[str, str]:
    """Resolve an explicit provider prefix or infer a legacy model route.

    Vendor/model slugs default to OpenRouter; legacy single-part model ids
    default to OpenCode Go. Prefix routes are stripped before Mira sees them.
    """
    prefix, separator, model_id = model.partition("/")
    if separator and prefix.casefold() == "openrouter":
        if not model_id:
            raise ValueError("OpenRouter route must include a vendor/model id")
        return "openrouter", model_id
    if separator and prefix.casefold() in {"opencode-go", "opencodego"}:
        if not model_id:
            raise ValueError("OpenCode Go route must include a model id")
        return "opencode-go", model_id
    if separator:
        return "openrouter", model
    return "opencode-go", model


def parse_mira_output(stdout: str, exit_code: int, stderr: str = "") -> ReviewResult:
    """Classify Mira's JSON payload; exit code alone is intentionally ignored."""
    payloads = []
    for start in (i for i, char in enumerate(stdout) if char == "{"):
        try:
            candidate = json.loads(stdout[start:])
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(candidate, dict) and "comments" in candidate:
            payloads.append(candidate)

    comments = []
    seen_keys = set()
    reviewed_files = 0
    walkthrough_seen = False
    for payload in payloads:
        for comment in payload.get("comments") or []:
            if not isinstance(comment, dict):
                continue
            key = (
                comment.get("file_path") or comment.get("path"),
                comment.get("line") or comment.get("start_line"),
                comment.get("title"),
            )
            if key in seen_keys:
                continue
            seen_keys.add(key)
            comments.append(comment)
        walkthrough = payload.get("walkthrough")
        if isinstance(walkthrough, dict) and walkthrough:
            walkthrough_seen = True
        try:
            reviewed_files = max(reviewed_files, int(payload.get("reviewed_files") or 0))
        except (TypeError, ValueError):
            pass

    raw = stdout + "\n" + stderr
    if not payloads:
        if any(marker in raw.lower() for marker in QUOTA_MARKERS):
            return ReviewResult("quota")
        return ReviewResult("failed")

    blockers = sum(1 for comment in comments if (comment.get("severity") or "").lower() == "blocker")
    dropped = raw.count(DROP_MARKER)
    covered = bool(comments or walkthrough_seen or reviewed_files)
    status = "partial" if dropped and not covered else "ok"
    return ReviewResult(status, len(comments), blockers, dropped)


def config_for_model(base_config: Path, model: str, output_config: Path) -> None:
    """Pin every Mira role to one candidate and its endpoint for this attempt."""
    config = yaml.safe_load(base_config.read_text(encoding="utf-8")) or {}
    if not isinstance(config, dict):
        raise TypeError("effective Mira config must be a mapping")
    llm = config.setdefault("llm", {})
    if not isinstance(llm, dict):
        raise TypeError("effective Mira config llm section must be a mapping")
    provider, model_id = resolve_model_route(model)
    if provider == "openrouter":
        llm["base_url"] = "https://openrouter.ai/api/v1"
        llm["api_key_env"] = "OPENROUTER_API_KEY"
    else:
        llm["base_url"] = "https://opencode.ai/zen/go/v1"
        llm["api_key_env"] = "OPENCODE_GO_API_KEY"
    for key in ("model", "review_model", "indexing_model"):
        llm[key] = model_id
    # The outer loop owns fallback order so each result is attributable to the
    # model shown in the summary; do not let Mira silently switch models inside
    # an attempt.
    llm["fallback_model"] = None
    output_config.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")


def run_chain(
    models: Sequence[str],
    run_attempt: Callable[[str], ReviewResult],
) -> tuple[ReviewResult, str | None, list[tuple[str, ReviewResult]]]:
    """Try candidates in order; retry one partial result once, then fall back."""
    history: list[tuple[str, ReviewResult]] = []
    partial_retry_used = False
    for model in models:
        result = run_attempt(model)
        history.append((model, result))
        if result.status == "ok":
            return result, model, history
        if result.status == "partial" and not partial_retry_used:
            partial_retry_used = True
            print(f"::notice::Mira review was partial; retrying {model} once", flush=True)
            retry_result = run_attempt(model)
            history.append((model, retry_result))
            if retry_result.status == "ok":
                return retry_result, model, history
    statuses = [result.status for _, result in history]
    if "partial" in statuses:
        final_status = "partial"
    elif history and history[-1][1].status == "quota":
        final_status = "quota"
    else:
        final_status = "failed"

    # Retain evidence from the best/latest informative attempt, including a
    # same-model partial retry, instead of replacing it with an empty later
    # failure or quota response.
    status_rank = {"ok": 4, "partial": 3, "quota": 2, "failed": 1}
    evidence = max(
        (result for _, result in history),
        key=lambda result: (
            status_rank.get(result.status, 0),
            result.comments,
            result.blockers,
            result.dropped_chunks,
        ),
        default=ReviewResult("failed"),
    )
    return ReviewResult(
        final_status,
        evidence.comments,
        evidence.blockers,
        evidence.dropped_chunks,
        evidence.detail,
    ), None, history


def _write_outputs(result: ReviewResult, used_model: str | None, history: list[tuple[str, ReviewResult]]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    attempted = [model for model, _ in history]
    details = [
        {"model": model, "status": outcome.status, "detail": outcome.detail}
        for model, outcome in history
    ]
    values = {
        "status": result.status,
        "comments": str(result.comments),
        "blockers": str(result.blockers),
        "dropped_chunks": str(result.dropped_chunks),
        "attempts": str(len(history)),
        "used_model": used_model or "",
        "models_attempted": json.dumps(attempted, separators=(",", ":")),
        "attempt_results": json.dumps(details, separators=(",", ":")),
    }
    with open(output_path, "a", encoding="utf-8") as output:
        output.writelines(f"{key}={value}\n" for key, value in values.items())


def _run_mira(
    model: str,
    pr_url: str,
    base_config: Path,
    runner_temp: Path,
    github_token: str,
    trust_execution_settings: bool,
    mira_command: str,
) -> ReviewResult:
    provider, _ = resolve_model_route(model)
    key_name = "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENCODE_GO_API_KEY"
    if not os.environ.get(key_name):
        message = f"missing Actions secret {key_name}; {provider} route skipped"
        print(f"::warning::{message}", flush=True)
        return ReviewResult("failed", detail=message)
    safe_model = re.sub(r"[^A-Za-z0-9._-]", "_", model)
    config_path = runner_temp / f"mira-effective-{safe_model}.yaml"
    config_for_model(base_config, model, config_path)
    command = [
        mira_command,
        "review",
        "--pr",
        pr_url,
        "--config",
        str(config_path),
        "--github-token",
        github_token,
        "--output",
        "json",
    ]
    if trust_execution_settings:
        command.append("--trust-execution-settings")
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=480,
    )
    print(f"--- Mira model {model}: stdout ---", flush=True)
    print(completed.stdout, end="", flush=True)
    print(f"--- Mira model {model}: stderr ---", flush=True)
    print(completed.stderr, end="", flush=True)
    return parse_mira_output(completed.stdout, completed.returncode, completed.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr-url", required=True)
    parser.add_argument("--base-config", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--fallback-model", default="")
    parser.add_argument("--fallback-models", default="")
    parser.add_argument("--trust-execution-settings", action="store_true")
    parser.add_argument("--mira-command", default="mira")
    args = parser.parse_args(argv)

    try:
        models = parse_model_chain(args.model, args.fallback_model, args.fallback_models)
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 2

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("::error::GITHUB_TOKEN is required to run Mira review", file=sys.stderr)
        return 2
    runner_temp = Path(os.environ.get("RUNNER_TEMP", "."))
    runner_temp.mkdir(parents=True, exist_ok=True)

    def attempt(model: str) -> ReviewResult:
        print(f"::group::Mira review attempt: {model}", flush=True)
        try:
            result = _run_mira(
                model,
                args.pr_url,
                args.base_config,
                runner_temp,
                token,
                args.trust_execution_settings,
                args.mira_command,
            )
        except subprocess.TimeoutExpired:
            print(f"::warning::Mira timed out on {model}; trying the next fallback", flush=True)
            result = ReviewResult("failed")
        except OSError as exc:
            print(f"::warning::Could not execute Mira on {model}: {exc}", flush=True)
            result = ReviewResult("failed")
        print(f"Mira result for {model}: {result.status}", flush=True)
        print("::endgroup::", flush=True)
        return result

    result, used_model, history = run_chain(models, attempt)
    _write_outputs(result, used_model, history)
    print(
        "Mira chain summary: "
        + json.dumps(
            {
                "status": result.status,
                "used_model": used_model,
                "attempts": [
                    {"model": model, "status": outcome.status, "detail": outcome.detail}
                    for model, outcome in history
                ],
            },
            separators=(",", ":"),
        ),
        flush=True,
    )
    if result.status != "ok":
        attempted = ", ".join(model for model, _ in history) or "none"
        if result.status == "quota":
            print(
                f"::error::Mira inference quota was exhausted across the configured model chain "
                f"({attempted}). No review was produced; this is not a clean review.",
                flush=True,
            )
        else:
            print(
                f"::error::Mira did not produce a complete review after trying the configured "
                f"model chain ({attempted}); final status: {result.status}.",
                flush=True,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
