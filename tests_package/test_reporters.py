"""Tests for Slice 3: English CLI, errors, and text report."""

import json
import os
import re
import subprocess
import sys

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HAS_PORTUGUESE_ACCENTS = re.compile(r"[áàãâéêíóôõúçÁÀÃÂÉÊÍÓÔÕÚÇ]")

# Portuguese section labels and field names that were translated to English.
# Rule IDs (e.g., segredos_rastreados) and filenames (auditoria.yaml) are
# internal identifiers and may legitimately appear in output.
_PT_LABELS = [
    "ocorrência", "ocorrencia",
    "DESATIVADAS", "DESATIVADA",
    "Confianca:", "Confiança:",
    "Evidencias:", "Evidências:",
    "Recomendacao:", "Recomendação:",
    "RELATORIO DE AUDITORIA DE HIGIENE",
    "Auditor de higiene",
]


def _assert_no_portuguese_labels(text, label=""):
    violations = []
    for word in _PT_LABELS:
        if word in text or word.lower() in text:
            violations.append(word)
    if violations:
        raise AssertionError(
            f"{label} contains Portuguese labels: {violations}"
        )


def _assert_no_portuguese_accents(text, label=""):
    matches = _HAS_PORTUGUESE_ACCENTS.findall(text)
    if matches:
        raise AssertionError(
            f"{label} contains Portuguese accented chars: {matches}"
        )


def _build_result(errors=(), warnings=(), disabled=()):
    return {
        "resultados": list(errors) + list(warnings),
        "status": "falha" if errors else "sucesso",
        "disabled_rules": list(disabled),
    }


def _finding(regra, caminho, severidade, mensagem, **kwargs):
    r = {
        "regra": regra,
        "caminho": caminho,
        "severity": severidade,
        "mensagem": mensagem,
    }
    r.update(kwargs)
    return r


# ---------------------------------------------------------------------------
# 3.5: Snapshot test — text report English
# ---------------------------------------------------------------------------

class TestTextReportEnglish:
    def test_text_report_is_english(self):
        from auditoria_higiene.reporters import gerar_relatorio_texto

        result = _build_result(
            errors=[
                _finding(
                    "segredos_rastreados",
                    "config.txt",
                    "error",
                    "Secret or credential found",
                    confianca="high",
                    recomendacao="investigate",
                ),
            ],
            warnings=[
                _finding(
                    "gitkeep_sem_conteudo",
                    "vazio/",
                    "warning",
                    "Directory contains only .gitkeep with no additional content",
                    recomendacao="investigate",
                ),
            ],
            disabled=["links_internos_quebrados"],
        )

        report = gerar_relatorio_texto(result)

        _assert_no_portuguese_labels(report, "text report")
        _assert_no_portuguese_accents(report, "text report")

        assert "REPOSITORY HYGIENE AUDIT REPORT" in report
        assert "ERROR" in report
        assert "WARNING" in report
        assert "DISABLED" in report
        assert "occurrence(s)" in report
        assert "Confidence:" in report
        assert "Recommendation:" in report
        assert "Status:" in report

    def test_text_report_resumo_is_english(self):
        from auditoria_higiene.reporters import gerar_resumo

        result = _build_result(
            errors=[
                _finding(
                    "segredos_rastreados",
                    "x.txt",
                    "error",
                    "Secret or credential found",
                ),
            ],
        )

        summary = gerar_resumo(result, ".repository-hygiene/auditoria.json")

        _assert_no_portuguese_labels(summary, "summary")
        _assert_no_portuguese_accents(summary, "summary")
        assert "Status:" in summary
        assert "Errors:" in summary
        assert "Warnings:" in summary
        assert "Report:" in summary

    def test_text_report_with_finding_details(self):
        from auditoria_higiene.reporters import gerar_relatorio_texto

        result = _build_result(
            errors=[
                _finding(
                    "referencias_inexistentes",
                    "src/module.py",
                    "error",
                    "Secret or credential found",
                    confianca="high",
                    evidencias="Evidence text here",
                    recomendacao="fix-reference",
                ),
            ],
        )

        report = gerar_relatorio_texto(result)
        _assert_no_portuguese_labels(report, "detailed text report")
        _assert_no_portuguese_accents(report, "detailed text report")
        assert "Evidence:" in report

    def test_text_report_empty_result(self):
        from auditoria_higiene.reporters import gerar_relatorio_texto

        result = _build_result()
        report = gerar_relatorio_texto(result)

        _assert_no_portuguese_labels(report, "empty text report")
        _assert_no_portuguese_accents(report, "empty text report")


# ---------------------------------------------------------------------------
# 3.6: JSON contract test — keys unchanged
# ---------------------------------------------------------------------------

EXPECTED_JSON_TOP_KEYS = {"resultados", "status", "disabled_rules"}
EXPECTED_FINDING_KEYS = {"regra", "caminho", "severity", "mensagem"}


class TestJSONContract:
    def test_json_output_preserves_top_level_keys(self):
        from auditoria_higiene.reporters import gerar_relatorio_json

        result = _build_result(
            errors=[
                _finding(
                    "segredos_rastreados",
                    "x.txt",
                    "error",
                    "Secret or credential found",
                    confianca="high",
                    recomendacao="investigate",
                ),
            ],
        )
        report = gerar_relatorio_json(result)
        data = json.loads(report)

        assert EXPECTED_JSON_TOP_KEYS.issubset(data.keys()), (
            f"Missing top-level keys: {EXPECTED_JSON_TOP_KEYS - set(data.keys())}"
        )

    def test_json_output_preserves_finding_keys(self):
        from auditoria_higiene.reporters import gerar_relatorio_json

        result = _build_result(
            errors=[
                _finding(
                    "tracked_secrets",
                    "file.txt",
                    "error",
                    "Secret found",
                    confianca="medium",
                    evidencias="some evidence",
                    recomendacao="investigate",
                    linha=42,
                ),
            ],
        )
        report = gerar_relatorio_json(result)
        data = json.loads(report)

        finding = data["resultados"][0]
        assert EXPECTED_FINDING_KEYS.issubset(finding.keys()), (
            f"Missing finding keys: {EXPECTED_FINDING_KEYS - set(finding.keys())}"
        )

    def test_json_agent_output_preserves_schema_keys(self):
        from auditoria_higiene.reporters import gerar_relatorio_json_agente

        result = _build_result()
        report = gerar_relatorio_json_agente(result, "0.2.0", "/tmp/repo")
        data = json.loads(report)

        assert data["schema_version"] == 1
        assert "auditor_version" in data
        assert "timestamp" in data
        assert "audited_directory" in data
        assert EXPECTED_JSON_TOP_KEYS.issubset(data.keys())


# ---------------------------------------------------------------------------
# 3.7: SARIF contract test
# ---------------------------------------------------------------------------

SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/openc2-schema/main/sarif/sarif-2-1.json"


class TestSARIFContract:
    def test_sarif_output_is_valid_json(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result(
            errors=[
                _finding(
                    "segredos_rastreados",
                    "secret.txt",
                    "error",
                    "Secret or credential found",
                    evidencias="token=abc",
                    recomendacao="investigate",
                ),
            ],
        )
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        assert data["$schema"] == SARIF_SCHEMA
        assert data["version"] == "2.1.0"

    def test_sarif_output_has_required_top_level(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result()
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        assert "$schema" in data
        assert "version" in data
        assert "runs" in data
        assert len(data["runs"]) >= 1

    def test_sarif_run_has_required_sections(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result(
            errors=[
                _finding(
                    "broken_internal_links",
                    "doc.md",
                    "error",
                    "Broken internal link: missing.txt",
                    recomendacao="fix-reference",
                ),
            ],
        )
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        run = data["runs"][0]
        assert "tool" in run
        assert "results" in run
        assert "tool" in run
        assert "driver" in run["tool"]
        assert "name" in run["tool"]["driver"]
        assert run["tool"]["driver"]["name"] == "repository-hygiene"

    def test_sarif_result_has_required_fields(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result(
            errors=[
                _finding(
                    "tracked_secrets",
                    "app.py",
                    "error",
                    "Secret found",
                    linha=10,
                    recomendacao="investigate",
                ),
            ],
        )
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        sarif_result = data["runs"][0]["results"][0]
        assert "ruleId" in sarif_result
        assert "level" in sarif_result
        assert "message" in sarif_result
        assert "locations" in sarif_result

    def test_sarif_warning_level_maps_correctly(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result(
            warnings=[
                _finding(
                    "gitkeep_sem_conteudo",
                    "empty/",
                    "warning",
                    "Empty gitkeep dir",
                    recomendacao="investigate",
                ),
            ],
        )
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        sarif_result = data["runs"][0]["results"][0]
        assert sarif_result["level"] == "warning"

    def test_sarif_message_is_english(self):
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        result = _build_result(
            errors=[
                _finding(
                    "segredos_rastreados",
                    "config.txt",
                    "error",
                    "Secret or credential found",
                    evidencias="api_key=***",
                    recomendacao="investigate",
                ),
            ],
        )
        report = gerar_relatorio_sarif(result)
        data = json.loads(report)

        msg = data["runs"][0]["results"][0]["message"]["text"]
        assert "Secret or credential found" in msg

        short_desc = data["runs"][0]["tool"]["driver"]["rules"][0]["shortDescription"]["text"]
        assert "Audit rule:" in short_desc


# ---------------------------------------------------------------------------
# 3.8: CLI help is English
# ---------------------------------------------------------------------------

class TestCLIHelpEnglish:
    def test_help_text_is_english(self):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

        combined = result.stdout + result.stderr
        _assert_no_portuguese_labels(combined, "CLI help")
        _assert_no_portuguese_accents(combined, "CLI help")
        assert "Repository hygiene auditor" in combined

    def test_install_help_is_english(self):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "install", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        combined = result.stdout + result.stderr
        _assert_no_portuguese_labels(combined, "install help")
        _assert_no_portuguese_accents(combined, "install help")

    def test_audit_help_is_english(self):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "audit", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        combined = result.stdout + result.stderr
        _assert_no_portuguese_labels(combined, "audit help")
        _assert_no_portuguese_accents(combined, "audit help")

    def test_error_messages_are_english(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "audit",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        combined = result.stdout + result.stderr
        _assert_no_portuguese_labels(combined, "error messages")
        _assert_no_portuguese_accents(combined, "error messages")
