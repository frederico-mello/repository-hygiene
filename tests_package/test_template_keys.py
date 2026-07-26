"""Tests for English template key enforcement (spec R3)."""

import os
import subprocess
import sys

import yaml

from auditoria_higiene.core import _LOCALIZED_CONFIG_KEYS, _visitar_chaves


def _load_template_config():
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "auditoria_higiene",
        "templates",
        "auditoria.yaml",
    )
    template_path = os.path.normpath(template_path)
    with open(template_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_template_auditoria_yaml_has_only_valid_english_keys():
    config = _load_template_config()
    keys = set(_visitar_chaves(config))

    invalid = keys - _LOCALIZED_CONFIG_KEYS
    assert not invalid, (
        f"Template contains invalid keys not in _LOCALIZED_CONFIG_KEYS: {sorted(invalid)}"
    )


def test_ci_assertion_every_template_key_in_localized_config_keys():
    config = _load_template_config()
    all_keys = set(_visitar_chaves(config))

    for key in all_keys:
        assert key in _LOCALIZED_CONFIG_KEYS, (
            f"Template key '{key}' is not in _LOCALIZED_CONFIG_KEYS"
        )


def test_install_produces_english_files(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "auditoria_higiene.cli", "install", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"install failed: {result.stderr}"

    audit_yaml = tmp_path / "auditoria.yaml"
    assert audit_yaml.is_file(), "auditoria.yaml was not generated"
    with open(audit_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    keys = set(_visitar_chaves(config))
    invalid = keys - _LOCALIZED_CONFIG_KEYS
    assert not invalid, (
        f"Installed auditoria.yaml contains invalid keys: {sorted(invalid)}"
    )

    workflow_yml = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
    assert workflow_yml.is_file(), "repository-hygiene.yml was not generated"
    with open(workflow_yml, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Run audit" in content, "Workflow should contain 'Run audit' step name"
    assert "Repository Hygiene Audit" in content, "Workflow should use English title"
    assert "Auditoria" not in content, "Workflow should not contain Portuguese text"
