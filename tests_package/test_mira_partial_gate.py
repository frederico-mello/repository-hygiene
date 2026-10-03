"""Testes do parser Python embutido no workflow de revisão MIRA.

O parser vive como heredoc dentro de `.github/workflows/mira-review-reusable.yml`.
Estes testes extraem esse código real do YAML e o executam como subprocesso,
para que a regra de status (`ok`/`partial`) seja exercitada exatamente como o
workflow a executa — sem duplicar a lógica no teste.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "mira-review-reusable.yml"
DROP_MARKER = "failed to parse, skipping"


def _parser_source():
    """Devolve o código do parse.py escrito pelo passo `review` do workflow."""
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    run = next(
        step["run"]
        for step in doc["jobs"]["review"]["steps"]
        if step.get("id") == "review"
    )
    _, _, rest = run.partition("<<'PY'\n")
    assert rest, "heredoc do parser não encontrado em mira-review-reusable.yml"
    body, sep, tail = rest.partition("\nPY\n")
    assert sep, "terminador do heredoc do parser não encontrado"
    assert body.strip(), "heredoc do parser vazio"
    return body


def _run_parser(tmp_path, raw, exit_code=0):
    """Executa o parser real com o stdout simulado e devolve (outputs, verdicto, stdout)."""
    parser = tmp_path / "parse.py"
    parser.write_text(_parser_source(), encoding="utf-8")

    mira_out = tmp_path / "mira-out.txt"
    mira_out.write_text(raw, encoding="utf-8")

    github_output = tmp_path / "github_output"
    github_output.write_text("", encoding="utf-8")

    env = dict(os.environ)
    env["GITHUB_OUTPUT"] = str(github_output)
    env["RUNNER_TEMP"] = str(tmp_path)
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, str(parser), str(mira_out), str(exit_code)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"parser terminou com {result.returncode}\n{result.stdout}\n{result.stderr}"
    )

    outputs = dict(
        line.split("=", 1)
        for line in github_output.read_text(encoding="utf-8").splitlines()
        if "=" in line
    )
    verdict = (tmp_path / "mira-verdict.txt").read_text(encoding="utf-8").strip()
    return outputs, verdict, result.stdout


def _raw(payload_json):
    """Stdout do Mira com um chunk descartado pelo harness e o payload recuperado."""
    return (
        "mira.core.engine WARNING: Chunk 1/1 "
        + DROP_MARKER
        + ": LLM response is not valid JSON\n"
        + payload_json
    )


def test_payload_recuperado_com_reviewed_files_conta_como_cobertura(tmp_path):
    """Cenário 1 do spec: payload recuperado com reviewed_files, zero comentários
    e walkthrough desligado → veredito `ok`, não `partial`."""
    raw = _raw(json.dumps({"comments": [], "reviewed_files": 14}))

    outputs, verdict, stdout = _run_parser(tmp_path, raw)

    assert outputs["status"] == "ok"
    assert verdict == "ok"
    assert outputs["comments"] == "0"
    assert outputs["blockers"] == "0"
    assert outputs["dropped_chunks"] == "1"
    assert "counting as covered" in stdout


def test_chunk_descartado_sem_payload_coberto_permanece_partial(tmp_path):
    """Cenário 2 do spec: chunk descartado e nenhum payload recuperável fornece
    cobertura (sem comentários, sem walkthrough, reviewed_files nulo) → `partial`."""
    raw = _raw(json.dumps({"comments": [], "reviewed_files": 0}))

    outputs, verdict, _ = _run_parser(tmp_path, raw)

    assert outputs["status"] == "partial"
    assert verdict == "partial"
    assert outputs["dropped_chunks"] == "1"
