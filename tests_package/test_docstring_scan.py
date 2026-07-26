"""CI docstring scan: reject Portuguese tokens in Python docstrings."""

import ast
import os
import re
import glob as _glob

SRC_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "src", "auditoria_higiene")
)

_PT_TOKENS = ("não", "para", "com", "sem", "como", "uma", "pelo", "pela", "seus", "sobre", "entre")

_ALLOWLIST = frozenset([])


def _extract_docstrings(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return []

    docstrings = []

    module_doc = ast.get_docstring(tree)
    if module_doc:
        docstrings.append(("module", filepath, module_doc, 1))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node)
            if doc:
                docstrings.append((type(node).__name__, filepath, doc, node.lineno))

    return docstrings


def _find_pt_tokens(text):
    findings = []
    for token in _PT_TOKENS:
        pattern = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
        for match in pattern.finditer(text):
            word = match.group()
            if word not in _ALLOWLIST:
                findings.append((token, word, match.start()))
    return findings


def test_docstrings_have_no_portuguese_tokens():
    py_files = sorted(
        f for f in _glob.glob(os.path.join(SRC_DIR, "*.py")) if not f.endswith("__pycache__")
    )

    assert py_files, f"No Python files found in {SRC_DIR}"

    violations = []
    for filepath in py_files:
        for kind, path, doc, lineno in _extract_docstrings(filepath):
            matches = _find_pt_tokens(doc)
            for token, found, pos in matches:
                rel = os.path.relpath(path, os.path.dirname(__file__))
                violations.append(
                    f"{rel}:{lineno} [{kind}] Portuguese token '{found}'"
                    f" (matches '{token}') at col {pos}"
                )

    assert not violations, (
        f"Found {len(violations)} Portuguese token(s) in docstrings:\n"
        + "\n".join(violations)
    )
