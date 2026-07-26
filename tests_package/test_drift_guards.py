import re
from pathlib import Path

from auditoria_higiene.core import _LOCALIZED_CONFIG_KEYS, _PT_TO_EN

ROOT = Path(__file__).resolve().parent.parent
MIGRATION_MD = ROOT / "docs" / "MIGRATION.md"


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

