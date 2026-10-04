import re
from pathlib import Path

import yaml

from auditoria_higiene.core import _LOCALIZED_CONFIG_KEYS, _PT_TO_EN

ROOT = Path(__file__).resolve().parent.parent
MIGRATION_MD = ROOT / "docs" / "MIGRATION.md"
REPO_WORKFLOW = ROOT / ".github" / "workflows" / "repository-hygiene.yml"
TEMPLATE_WORKFLOW = ROOT / "src" / "auditoria_higiene" / "templates" / "workflow.yml"
EVENTS = ("push", "pull_request")
AGENT_ROOTS = (".opencode", ".kilocode", ".kilo", ".omp", ".hermes")


def _load_event_triggers(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), f"{path} is not a YAML mapping"
    if "on" in data:
        triggers = data["on"]
    else:
        triggers = data.get(True)
    assert triggers is not None, f"{path} has no 'on' trigger block"
    return triggers


def _trigger_paths(path, event):
    triggers = _load_event_triggers(path)
    assert event in triggers, f"{path.name} has no '{event}' trigger"
    paths = triggers[event].get("paths")
    assert isinstance(paths, list), f"{path.name} {event}.paths is not a list"
    return paths


def _parse_migration_table():
    text = MIGRATION_MD.read_text(encoding="utf-8")
    rows = re.findall(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|', text, re.MULTILINE)
    header = ("Portuguese Key", "English Key")
    result = {}
    for pt, en in rows:
        pt_clean = pt.strip()
        en_clean = en.strip()
        if pt_clean == header[0] and en_clean == header[1]:
            continue
        if re.fullmatch(r'-{3,}', pt_clean):
            continue
        if not pt_clean or not en_clean:
            continue
        result[pt_clean] = en_clean
    return result


def test_migration_guide_contains_all_pt_keys():
    """MIGRATION.md col1 == set(_PT_TO_EN.keys())"""
    table = _parse_migration_table()
    assert set(table.keys()) == set(_PT_TO_EN.keys())


def test_pt_values_are_valid_en_keys():
    """set(_PT_TO_EN.values()) ⊆ _LOCALIZED_CONFIG_KEYS"""
    pt_values = set(_PT_TO_EN.values())
    assert pt_values.issubset(_LOCALIZED_CONFIG_KEYS)


def test_en_key_without_pt_counterpart_needs_no_migration_row():
    """EN-only keys (in _LOCALIZED_CONFIG_KEYS but not _PT_TO_EN.values())
    do not need MIGRATION.md rows. The drift guards should still pass."""
    table = _parse_migration_table()
    en_only_keys = _LOCALIZED_CONFIG_KEYS - set(_PT_TO_EN.values())
    for key in en_only_keys:
        assert key not in table


def test_workflow_paths_match_template_paths_for_every_event():
    """repo .github/workflows/repository-hygiene.yml paths == template paths (order included)"""
    for event in EVENTS:
        repo_paths = _trigger_paths(REPO_WORKFLOW, event)
        template_paths = _trigger_paths(TEMPLATE_WORKFLOW, event)
        assert repo_paths == template_paths, (
            f"{event}.paths drifted between {REPO_WORKFLOW.name} and "
            f"templates/workflow.yml: {repo_paths!r} != {template_paths!r}"
        )


def test_every_event_path_list_contains_the_five_agent_roots():
    """both events list .opencode/**, .kilocode/**, .kilo/**, .omp/**, .hermes/**"""
    for event in EVENTS:
        paths = _trigger_paths(REPO_WORKFLOW, event)
        for root in AGENT_ROOTS:
            glob = f"{root}/**"
            assert glob in paths, f"{glob} ausente de {REPO_WORKFLOW.name} {event}.paths"

