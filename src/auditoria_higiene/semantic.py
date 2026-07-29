import glob as _glob
import json
import os
import re

_EXTENSOES_REFERENCIAS = (
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".txt",
    ".json",
    ".csv",
    ".html",
    ".css",
    ".js",
)

_PADRAO_PATH_REF = re.compile(
    r"\b([\w./-]+\.(?:"
    + "|".join(ext.lstrip(".") for ext in _EXTENSOES_REFERENCIAS)
    + r"))\b"
)


def _caminho_seguro(raiz, *partes):
    caminho = os.path.normpath(os.path.join(raiz, *partes))
    raiz_abs = os.path.realpath(raiz)
    caminho_abs = os.path.realpath(caminho)
    if not caminho_abs.startswith(raiz_abs + os.sep) and caminho_abs != raiz_abs:
        raise ValueError(f"Path traversal detectado: {caminho}")
    return caminho_abs


def carregar_referencias_openspec(raiz):
    refs = set()
    for subdir in ("specs", "changes"):
        try:
            dir_path = _caminho_seguro(raiz, "openspec", subdir)
        except ValueError:
            continue
        if not os.path.isdir(dir_path):
            continue
        pattern = os.path.join(dir_path, "**", "*.md")
        for md_path in _glob.glob(pattern, recursive=True):
            try:
                with open(md_path, "r", encoding="utf-8", errors="replace") as f:
                    conteudo = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            for match in _PADRAO_PATH_REF.finditer(conteudo):
                refs.add(match.group(1))
    return refs


def carregar_referencias_graphify(raiz):
    try:
        graph_path = _caminho_seguro(raiz, "graphify-out", "graph.json")
    except ValueError:
        return set()
    if not os.path.isfile(graph_path):
        return set()
    try:
        with open(graph_path, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return set()
    refs = set()
    for node in data.get("nodes", []):
        source_loc = node.get("source_location")
        if source_loc:
            refs.add(source_loc)
    return refs


_EVIDENCIAS_CACHE = {}


def montar_evidencias(raiz, config):
    raiz_cache = os.path.realpath(raiz)
    if raiz_cache in _EVIDENCIAS_CACHE:
        return _EVIDENCIAS_CACHE[raiz_cache]
    evidencias = {}
    fontes = config.get("semantic_sources", {})
    if fontes.get("openspec", True):
        for ref in carregar_referencias_openspec(raiz):
            evidencias[ref] = "referenced in OpenSpec"
    for ref in carregar_referencias_graphify(raiz):
        if ref not in evidencias:
            evidencias[ref] = "present in Graphify knowledge graph"
    _EVIDENCIAS_CACHE[raiz_cache] = evidencias
    return evidencias
