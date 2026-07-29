"""Tests for Portuguese->English localization key validation at config load time."""

import os

import pytest

from auditoria_higiene.core import ConfigError


@pytest.fixture
def pt_only_yaml(tmp_path):
    path = tmp_path / "auditoria.yaml"
    path.write_text(
        "regras:\n"
        "  segredos_rastreados:\n"
        "    habilitada: true\n"
        "    severidade: error\n"
        "  links_internos_quebrados:\n"
        "    habilitada: true\n"
        "    severidade: error\n"
        "excecoes:\n"
        "  segredos_rastreados: []\n"
        "  links_internos_quebrados: []\n",
        encoding="utf-8",
    )
    return str(path)


def test_pt_only_config_rejected_with_key_mapping_and_migration_reference(pt_only_yaml):
    from auditoria_higiene.core import carregar_configuracao

    with pytest.raises(ConfigError) as exc:
        carregar_configuracao(pt_only_yaml)
    msg = str(exc.value)
    assert "segredos_rastreados" in msg
    assert "tracked_secrets" in msg
    assert "links_internos_quebrados" in msg
    assert "broken_internal_links" in msg
    assert "docs/MIGRATION.md" in msg


@pytest.fixture
def mixed_yaml(tmp_path):
    path = tmp_path / "auditoria.yaml"
    path.write_text(
        "rules:\n"
        "  tracked_secrets:\n"
        "    enabled: true\n"
        "    severity: error\n"
        "  broken_internal_links:\n"
        "    enabled: true\n"
        "    severity: error\n"
        "  segredos_rastreados:\n"
        "    enabled: true\n"
        "    severity: error\n"
        "exceptions:\n"
        "  tracked_secrets: []\n"
        "  broken_internal_links: []\n"
        "  segredos_rastreados: []\n",
        encoding="utf-8",
    )
    return str(path)


def test_mixed_pt_and_english_lists_only_pt_keys_atomically(mixed_yaml):
    from auditoria_higiene.core import carregar_configuracao

    with pytest.raises(ConfigError) as exc:
        carregar_configuracao(mixed_yaml)
    msg = str(exc.value)
    assert "segredos_rastreados" in msg
    assert "tracked_secrets" in msg
    assert "docs/MIGRATION.md" in msg
    assert "rules" not in msg
    assert "broken_internal_links" not in msg
    assert "tracked_secrets ->" not in msg


@pytest.fixture
def unmapped_pt_yaml(tmp_path):
    path = tmp_path / "auditoria.yaml"
    path.write_text(
        "regras_personalizadas:\n"
        "  habilitada: true\n",
        encoding="utf-8",
    )
    return str(path)


def test_unmapped_portuguese_identifier_is_named_and_directs_to_migration(
    unmapped_pt_yaml,
):
    from auditoria_higiene.core import carregar_configuracao

    with pytest.raises(ConfigError) as exc:
        carregar_configuracao(unmapped_pt_yaml)
    msg = str(exc.value)
    assert "regras_personalizadas" in msg
    assert "docs/MIGRATION.md" in msg


@pytest.fixture
def typo_yaml(tmp_path):
    path = tmp_path / "auditoria.yaml"
    path.write_text(
        "rules:\n"
        "  tracked_secres:\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    return str(path)


def test_typo_close_to_valid_english_key_suggests_closest(typo_yaml):
    from auditoria_higiene.core import carregar_configuracao

    with pytest.raises(ConfigError) as exc:
        carregar_configuracao(typo_yaml)
    msg = str(exc.value)
    assert "tracked_secres" in msg
    assert "tracked_secrets" in msg


@pytest.fixture
def far_unknown_yaml(tmp_path):
    path = tmp_path / "auditoria.yaml"
    path.write_text(
        "rules:\n"
        "  xyzzy_foo:\n"
        "    enabled: true\n",
        encoding="utf-8",
    )
    return str(path)


def test_unknown_key_with_no_close_match_named_and_directs_to_migration(
    far_unknown_yaml,
):
    from auditoria_higiene.core import carregar_configuracao

    with pytest.raises(ConfigError) as exc:
        carregar_configuracao(far_unknown_yaml)
    msg = str(exc.value)
    assert "xyzzy_foo" in msg
    assert "docs/MIGRATION.md" in msg
    assert "did you mean" not in msg


def test_pt_fixture_loads_cleanly_via_yaml():
    import yaml

    fixture_path = os.path.join(
        os.path.dirname(__file__), "fixtures", "auditoria.pt.yaml"
    )
    with open(fixture_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    assert isinstance(config, dict)
    assert "regras" in config


def test_cli_against_pt_fixture_directory_lists_keys_and_migration(tmp_path):
    import shutil
    import subprocess
    import sys

    fixture_src = os.path.join(
        os.path.dirname(__file__), "fixtures", "auditoria.pt.yaml"
    )
    shutil.copy(fixture_src, tmp_path / "auditoria.yaml")

    result = subprocess.run(
        [sys.executable, "-m", "auditoria_higiene.cli", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 2
    combinado = result.stdout + result.stderr
    assert "segredos_rastreados" in combinado
    assert "tracked_secrets" in combinado
    assert "links_internos_quebrados" in combinado
    assert "broken_internal_links" in combinado
    assert "docs/MIGRATION.md" in combinado