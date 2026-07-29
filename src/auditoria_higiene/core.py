"""Audit core: configuration loading and rule execution."""

import os
import re
import subprocess
from datetime import datetime, timezone

import yaml

_MIGRATION_GUIDE_PATH = "docs/MIGRATION.md"


class ConfigError(ValueError):
    """Raised when a configuration file violates the localization contract."""


_PT_TO_EN: dict[str, str] = {
    "versao_configuracao": "config_version",
    "regras": "rules",
    "excecoes": "exceptions",
    "segredos_rastreados": "tracked_secrets",
    "links_internos_quebrados": "broken_internal_links",
    "referencias_inexistentes": "missing_references",
    "artefatos_fora_gitignore": "untracked_artifacts",
    "gitkeep_sem_conteudo": "empty_gitkeep_directories",
    "arquivos_sem_referencia": "unreferenced_files",
    "documentacao_desatualizada": "outdated_documentation",
    "configuracao_sem_integracao": "unintegrated_configurations",
    "openspec_parada": "stale_openspec_changes",
    "workflows_inseguros": "insecure_workflows",
    "repositorios_aninhados": "nested_repositories",
    "conventional-commits": "conventional_commits",
    "fontes_semanticas": "semantic_sources",
    "padroes_artefatos": "artifact_patterns",
    "permissoes_write_permitidas": "allowed_write_permissions",
    "habilitada": "enabled",
    "severidade": "severity",
    "openwiki": "openwiki",
    "graphify": "graphify",
    "openspec": "openspec",
}

_LOCALIZED_CONFIG_KEYS: frozenset[str] = frozenset(_PT_TO_EN.values())


def _visitar_chaves(no):
    if isinstance(no, dict):
        for chave, valor in no.items():
            if isinstance(chave, str):
                yield chave
            yield from _visitar_chaves(valor)
    elif isinstance(no, list):
        for item in no:
            yield from _visitar_chaves(item)


def _distancia_edicao(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    anterior = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        atual = [i]
        for j, cb in enumerate(b, 1):
            insercao = atual[j - 1] + 1
            delecao = anterior[j] + 1
            sub = anterior[j - 1] + (0 if ca == cb else 1)
            atual.append(min(insercao, delecao, sub))
        anterior = atual
    return anterior[-1]


def _chave_mais_proxima(chave, max_dist=2):
    melhor = None
    melhor_dist = max_dist + 1
    for en in _LOCALIZED_CONFIG_KEYS:
        d = _distancia_edicao(chave, en)
        if d < melhor_dist:
            melhor_dist = d
            melhor = en
    return melhor


def _validar_chave_localizada(config) -> None:
    if not isinstance(config, dict):
        return
    chaves = sorted(set(_visitar_chaves(config)))
    pt_chaves = [c for c in chaves if c in _PT_TO_EN]
    unknown_chaves = [
        c for c in chaves if c not in _PT_TO_EN and c not in _LOCALIZED_CONFIG_KEYS
    ]
    if not pt_chaves and not unknown_chaves:
        return
    linhas = [
        "Configuration rejected: invalid keys detected in auditoria.yaml."
    ]
    if pt_chaves:
        linhas.append("Portuguese keys detected (rename to the English equivalent):")
        for chave in pt_chaves:
            linhas.append(f"  - {chave} -> {_PT_TO_EN[chave]}")
    if unknown_chaves:
        linhas.append("Unknown keys detected:")
        for chave in unknown_chaves:
            sugestao = _chave_mais_proxima(chave)
            if sugestao:
                linhas.append(f"  - {chave} (did you mean: {sugestao}?)")
            else:
                linhas.append(f"  - {chave}")
    linhas.append(
        f"See {_MIGRATION_GUIDE_PATH} for the canonical English key table."
    )
    raise ConfigError("\n".join(linhas))


REMOVE = "remove"
ADD_TO_GITIGNORE = "add-to-gitignore"
FIX_REFERENCE = "fix-reference"
UPDATE_DOCS = "update-documentation"
ADD_CI = "add-ci-integration"
ARCHIVE_CHANGE = "archive-change"
SCOPE_PERMISSIONS = "scope-permissions"
INVESTIGATE = "investigate"
ACCEPT_FALSE_POSITIVE = "accept-false-positive"
PIN_ACTION_VERSION = "pin-action-version"

CONFIG_VERSION = 1

_DIR_ARCHIVE = ".archive/"
_DIR_OPENSPEC_CHANGES = "openspec/changes/"
_DIR_OPENSPEC_PROPOSTAS = "openspec/proposals/"
_DIR_TESTS = "tests/"
_DIR_TESTS_PACKAGE = "tests_package/"
_ARQUIVO_GITIGNORE = ".gitignore"
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

_PADROES_SEGREDOS_FRACOS = [
    re.compile(r"(?i)(?<!\w)senha\s*[=:]\s*\S+"),
    re.compile(r"(?i)(?<!\w)password\s*[=:]\s*\S+"),
]

_PADROES_SEGREDOS_FORTES = [
    re.compile(r"(?i)(?<!\w)api_key\s*[=:]\s*\S+"),
    re.compile(r"(?i)(?<!\w)secret\s*[=:]\s*\S+"),
    re.compile(r"(?i)(?<!\w)token\s*[=:]\s*\S+"),
]

_ARQUIVOS_CREDENCIAIS_RUNTIME = frozenset(
    (
        "credentials.json",
        "token.json",
        "service-account.json",
        "auditoria-report.txt",
    )
)


def _eh_url_http(url):
    return url.startswith(("http:" + chr(47) + chr(47), "https:" + chr(47) + chr(47)))


def carregar_configuracao(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    if config is None:
        config = {}
    _validar_chave_localizada(config)
    if "semantic_sources" not in config:
        config["semantic_sources"] = {
            "openwiki": None,
            "graphify": None,
            "openspec": True,
        }
    return config


def validar_configuracao(config):
    versao = config.get("config_version", 1)
    if versao != CONFIG_VERSION:
        raise ValueError(
            f"Unsupported config version {versao}. Expected: {CONFIG_VERSION}"
        )
    return True


def executar_auditoria(raiz, config):
    _TRACKED_CACHE.pop(os.path.realpath(raiz), None)
    from auditoria_higiene.semantic import _EVIDENCIAS_CACHE

    _EVIDENCIAS_CACHE.pop(os.path.realpath(raiz), None)
    resultados = []
    regras = config.get("rules", {})
    excecoes = config.get("exceptions", {})
    regras_desativadas = []

    for nome_regra, cfg in regras.items():
        if not cfg.get("enabled", True):
            regras_desativadas.append(nome_regra)
            continue
        caminhos_excluidos = excecoes.get(nome_regra, [])
        _avaliar_regra(nome_regra, cfg, raiz, caminhos_excluidos, resultados, config)

    tem_erro = any(
        r["severity"] == "error" and r.get("confianca", "high") in ("high", "medium")
        for r in resultados
    )
    return {
        "resultados": resultados,
        "status": "falha" if tem_erro else "sucesso",
        "disabled_rules": regras_desativadas,
    }


def _avaliar_regra(nome_regra, cfg, raiz, caminhos_excluidos, resultados, config=None):
    severidade = cfg.get("severity", "error")
    if nome_regra == "tracked_secrets":
        _verificar_segredos(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "broken_internal_links":
        _verificar_links_internos(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "missing_references":
        _verificar_referencias(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "untracked_artifacts":
        _verificar_artefatos(raiz, caminhos_excluidos, resultados, severidade, cfg)
    elif nome_regra == "empty_gitkeep_directories":
        _verificar_gitkeep(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "unreferenced_files":
        _verificar_sem_referencia(
            raiz, caminhos_excluidos, resultados, severidade, config
        )
    elif nome_regra == "outdated_documentation":
        _verificar_documentacao(
            raiz, caminhos_excluidos, resultados, severidade, config
        )
    elif nome_regra == "unintegrated_configurations":
        _verificar_config_sem_integracao(
            raiz, caminhos_excluidos, resultados, severidade
        )
    elif nome_regra == "stale_openspec_changes":
        _verificar_openspec_parada(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "insecure_workflows":
        _verificar_workflows_inseguros(
            raiz, caminhos_excluidos, resultados, severidade, cfg
        )
    elif nome_regra == "nested_repositories":
        _verificar_repositorios_aninhados(
            raiz, caminhos_excluidos, resultados, severidade, config
        )
    elif nome_regra == "conventional-commits":
        from auditoria_higiene.commit_check import validar_commits

        findings = validar_commits(raiz, severidade)
        resultados.extend(findings)


def _esta_excluido(caminho, caminhos_excluidos):
    caminho_norm = os.path.normpath(caminho)
    for excluido in caminhos_excluidos:
        excluido_norm = os.path.normpath(excluido)
        if caminho_norm == excluido_norm:
            return True
        prefixo = excluido_norm.rstrip(os.sep) + os.sep
        if caminho_norm.startswith(prefixo):
            return True
    return False


def caminho_seguro(raiz, *partes):
    caminho = os.path.normpath(os.path.join(raiz, *partes))
    raiz_abs = os.path.realpath(raiz)
    caminho_abs = os.path.realpath(caminho)
    if not caminho_abs.startswith(raiz_abs + os.sep) and caminho_abs != raiz_abs:
        raise ValueError(f"Path traversal detected: {caminho}")
    return caminho_abs


def _arquivos_rastreados(raiz):
    cached = _tracked_set(raiz)
    if cached:
        return list(cached)
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=30,
            shell=False,
        )
        if result.returncode != 0:
            return _todos_arquivos(raiz)
        return [linha.strip() for linha in result.stdout.splitlines() if linha.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        return _todos_arquivos(raiz)


def _todos_arquivos(raiz):
    arquivos = []
    for dirpath, _, filenames in os.walk(raiz):
        for f in filenames:
            caminho = os.path.relpath(os.path.join(dirpath, f), raiz)
            arquivos.append(caminho)
    return arquivos


def _verificar_segredos(raiz, caminhos_excluidos, resultados, severidade="error"):
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if _em_diretorio_ruidoso_segredos(caminho_rel):
            continue
        caminho_abs = caminho_seguro(raiz, caminho_rel)
        if not os.path.isfile(caminho_abs):
            continue
        _escanear_linhas_por_segredos(caminho_abs, caminho_rel, resultados, severidade)


def _escanear_linhas_por_segredos(caminho_abs, caminho_rel, resultados, severidade):
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            for i, linha in enumerate(f, 1):
                if _linha_eh_comentario(linha):
                    continue
                for padrao, confianca in (
                    *((padrao, "high") for padrao in _PADROES_SEGREDOS_FORTES),
                    *((padrao, "medium") for padrao in _PADROES_SEGREDOS_FRACOS),
                ):
                    if padrao.search(linha):
                        resultados.append(
                            {
                                "regra": "tracked_secrets",
                                "caminho": caminho_rel,
                                "linha": i,
                                "severity": severidade,
                                "confianca": confianca,
                                "mensagem": "Secret or credential found",
                                "recomendacao": INVESTIGATE,
                            }
                        )
                        break
    except (OSError, UnicodeDecodeError):
        pass


def _em_diretorio_ruidoso_segredos(caminho_rel):
    return caminho_rel.startswith(
        (
            _DIR_ARCHIVE,
            _DIR_OPENSPEC_CHANGES,
            _DIR_OPENSPEC_PROPOSTAS,
            _DIR_TESTS,
            _DIR_TESTS_PACKAGE,
        )
    )


def _linha_eh_comentario(linha):
    linha_strip = linha.lstrip()
    return linha_strip.startswith(("#", "//"))


def _verificar_links_internos(raiz, caminhos_excluidos, resultados, severidade="error"):
    padrao_link = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if caminho_rel.startswith(
            (_DIR_ARCHIVE, _DIR_OPENSPEC_CHANGES, _DIR_OPENSPEC_PROPOSTAS)
        ):
            continue
        if not caminho_rel.endswith(".md"):
            continue
        _verificar_links_em_arquivo(
            raiz, caminho_rel, padrao_link, resultados, severidade
        )


def _verificar_links_em_arquivo(raiz, caminho_rel, padrao_link, resultados, severidade):
    caminho_abs = caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    for match in padrao_link.finditer(conteudo):
        url = match.group(2)
        if _eh_url_http(url):
            continue
        if url.startswith("#"):
            continue
        alvo = url.split("#")[0]
        if not alvo:
            continue
        if alvo.startswith(("/", "\\", "~")):
            continue
        caminho_alvo = os.path.normpath(
            os.path.join(os.path.dirname(caminho_rel), alvo)
        )
        try:
            if not os.path.exists(caminho_seguro(raiz, caminho_alvo)):
                resultados.append(
                    {
                        "regra": "broken_internal_links",
                        "caminho": caminho_rel,
                        "severity": severidade,
                        "mensagem": f"Broken internal link: {url}",
                        "recomendacao": FIX_REFERENCE,
                    }
                )
        except ValueError:
            continue


def _verificar_referencias(raiz, caminhos_excluidos, resultados, severidade="error"):
    padrao_ref = re.compile(
        r"""\b\w+\(\s*["']([\w./-]+\.(?:py|md|yaml|yml|txt|json|csv|html|css|js))["']"""
    )
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if _em_diretorio_ruidoso_referencias(caminho_rel):
            continue
        if not caminho_rel.endswith(_EXTENSOES_REFERENCIAS):
            continue
        _verificar_refs_em_arquivo(
            raiz, caminho_rel, padrao_ref, resultados, severidade
        )


def _verificar_refs_em_arquivo(raiz, caminho_rel, padrao_ref, resultados, severidade):
    caminho_abs = caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    for match in padrao_ref.finditer(conteudo):
        ref = match.group(1)
        if _eh_url_http(ref):
            continue
        if ref in _ARQUIVOS_CREDENCIAIS_RUNTIME:
            continue
        if not _referencia_existe(raiz, caminho_rel, ref):
            resultados.append(
                {
                    "regra": "missing_references",
                    "caminho": caminho_rel,
                    "severity": severidade,
                    "mensagem": f"Reference to missing file: {ref}",
                    "recomendacao": FIX_REFERENCE,
                }
            )


def _em_diretorio_ruidoso_referencias(caminho_rel):
    return caminho_rel.startswith(
        (
            _DIR_ARCHIVE,
            _DIR_OPENSPEC_CHANGES,
            _DIR_OPENSPEC_PROPOSTAS,
            ".github/prompts/",
            ".github/skills/openspec-",
            ".opencode/commands/",
            ".opencode/skills/openspec-",
            _DIR_TESTS,
            _DIR_TESTS_PACKAGE,
        )
    )


_TRACKED_CACHE = {}


def _tracked_set(raiz):
    raiz_cache = os.path.realpath(raiz)
    if raiz_cache in _TRACKED_CACHE:
        return _TRACKED_CACHE[raiz_cache]
    tracked = set()
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=30,
        )
        if result.returncode == 0:
            tracked = {
                linha.strip().replace("\\", "/")
                for linha in result.stdout.splitlines()
                if linha.strip()
            }
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    _TRACKED_CACHE[raiz_cache] = tracked
    return tracked


def _referencia_existe(raiz, caminho_rel, ref):
    candidatos = []
    candidatos.append(os.path.normpath(ref))
    if caminho_rel:
        candidatos.append(
            os.path.normpath(os.path.join(os.path.dirname(caminho_rel), ref))
        )
    base = os.path.basename(ref)
    if base:
        tracked = _tracked_set(raiz)
        if tracked and any(p.endswith("/" + base) or p == base for p in tracked):
            return True
    for cand in candidatos:
        try:
            if os.path.exists(caminho_seguro(raiz, cand)):
                return True
        except ValueError:
            continue
    return False


def _verificar_artefatos(
    raiz, caminhos_excluidos, resultados, severidade="error", cfg=None
):
    for caminho_rel in _listar_artefatos(raiz, caminhos_excluidos):
        if not _deve_reportar_artefato(raiz, caminho_rel, caminhos_excluidos, cfg):
            continue
        resultados.append(
            {
                "regra": "untracked_artifacts",
                "caminho": caminho_rel,
                "severity": severidade,
                "mensagem": "Generated artifact not covered by .gitignore",
                "recomendacao": ADD_TO_GITIGNORE,
            }
        )


def _listar_artefatos(raiz, caminhos_excluidos):
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--directory", "-z"],
            capture_output=True,
            cwd=raiz,
            timeout=30,
            shell=False,
        )
        if result.returncode == 0:
            stdout = result.stdout
            if isinstance(stdout, bytes):
                stdout = stdout.decode(errors="surrogateescape")
            caminhos = stdout.split("\0")
        else:
            return _artefatos_fallback(raiz, caminhos_excluidos)
    except (subprocess.SubprocessError, FileNotFoundError):
        return _artefatos_fallback(raiz, caminhos_excluidos)
    return [caminho.replace("\\", "/") for caminho in caminhos if caminho]


def _deve_reportar_artefato(raiz, caminho_rel, caminhos_excluidos, cfg):
    if _esta_excluido(caminho_rel, caminhos_excluidos):
        return False
    if caminho_rel == _ARQUIVO_GITIGNORE or caminho_rel.startswith(
        (".git/", ".repository-hygiene/")
    ):
        return False
    if _eh_repositorio_aninhado(raiz, caminho_rel):
        return False
    return not _eh_diretorio_fonte(caminho_rel) and _eh_artefato_configurado(
        caminho_rel, cfg
    )


def _eh_repositorio_aninhado(raiz, caminho_rel):
    dir_path = caminho_rel.rstrip("/")
    dir_abs = caminho_seguro(raiz, dir_path)
    return os.path.isdir(os.path.join(dir_abs, ".git"))


def _eh_diretorio_fonte(caminho_rel):
    return caminho_rel.startswith(("src/", ".github/", ".opencode/", "openspec/"))


def _eh_artefato_configurado(caminho_rel, cfg):
    padroes = (cfg or {}).get("artifact_patterns")
    if not padroes:
        return True
    return any(_corresponde_gitignore(caminho_rel, padrao) for padrao in padroes)


def _artefatos_fallback(raiz, caminhos_excluidos):
    gitignore_path = caminho_seguro(raiz, _ARQUIVO_GITIGNORE)
    if not os.path.exists(gitignore_path):
        return []
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_lines = f.read().splitlines()
    tracked = _tracked_set(raiz)
    artefatos = []
    for caminho_rel in _todos_arquivos(raiz):
        caminho_git = caminho_rel.replace("\\", "/")
        if (
            caminho_git == _ARQUIVO_GITIGNORE
            or caminho_git == ".git"
            or caminho_git.startswith(".git/")
        ):
            continue
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if _em_gitignore(caminho_git, gitignore_lines):
            continue
        if caminho_git not in tracked:
            artefatos.append(caminho_rel)
    return artefatos


def _em_git(raiz, caminho_rel):
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", caminho_rel],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=10,
            shell=False,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _em_gitignore(caminho, gitignore_lines):
    for line in gitignore_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if _corresponde_gitignore(caminho, line):
            return True
    return False


def _corresponde_gitignore(caminho, line):
    import fnmatch

    if line.startswith("/"):
        line = line[1:]
    if line.endswith("/"):
        if caminho.startswith(line.rstrip("/")) or caminho.startswith(line):
            return True
    if fnmatch.fnmatch(caminho, line):
        return True
    if fnmatch.fnmatch(os.path.basename(caminho), line):
        return True
    return False


def _verificar_gitkeep(raiz, caminhos_excluidos, resultados, severidade="warning"):
    for dirpath, _, filenames in os.walk(raiz):
        if ".gitkeep" not in filenames:
            continue
        outros = [f for f in filenames if f != ".gitkeep"]
        if outros:
            continue
        caminho_rel = os.path.relpath(dirpath, raiz)
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        resultados.append(
            {
                "regra": "empty_gitkeep_directories",
                "caminho": caminho_rel,
                "severity": severidade,
                "mensagem": "Directory contains only .gitkeep with no additional content",
                "recomendacao": INVESTIGATE,
            }
        )


def _verificar_sem_referencia(
    raiz, caminhos_excluidos, resultados, severidade="warning", config=None
):
    from auditoria_higiene.semantic import montar_evidencias

    evidencias = montar_evidencias(raiz, config or {})
    arquivos = _arquivos_rastreados(raiz)
    elegiveis = _filtrar_elegiveis_sem_referencia(arquivos, caminhos_excluidos)
    if not elegiveis:
        return
    nome_para_arquivos = _agrupar_por_nome(elegiveis)
    nomes_referenciados = _coletar_referencias(raiz, elegiveis, nome_para_arquivos)
    for caminho_rel in elegiveis:
        if caminho_rel in nomes_referenciados:
            continue
        if caminho_rel in evidencias:
            continue
        resultados.append(
            {
                "regra": "unreferenced_files",
                "caminho": caminho_rel,
                "severity": severidade,
                "confianca": "low",
                "mensagem": "File with no detectable references in other files",
                "evidencias": f"File {caminho_rel} is not mentioned in any other tracked file",
                "recomendacao": INVESTIGATE,
            }
        )


def _filtrar_elegiveis_sem_referencia(arquivos, caminhos_excluidos):
    elegiveis = []
    for caminho_rel in arquivos:
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if caminho_rel.startswith(".github"):
            continue
        if caminho_rel.startswith(
            (
                _DIR_ARCHIVE,
                _DIR_OPENSPEC_CHANGES,
                _DIR_OPENSPEC_PROPOSTAS,
                _DIR_TESTS,
                _DIR_TESTS_PACKAGE,
            )
        ):
            continue
        if os.path.basename(caminho_rel) == "__init__.py":
            continue
        if not caminho_rel.endswith(_EXTENSOES_REFERENCIAS):
            continue
        elegiveis.append(caminho_rel)
    return elegiveis


def _agrupar_por_nome(elegiveis):
    nome_para_arquivos = {}
    for caminho_rel in elegiveis:
        nome_base = os.path.basename(caminho_rel)
        nome_sem_ext = os.path.splitext(nome_base)[0]
        nome_para_arquivos.setdefault(nome_sem_ext, []).append(caminho_rel)
    return nome_para_arquivos


def _coletar_referencias(raiz, elegiveis, nome_para_arquivos):
    todos_nomes = set(nome_para_arquivos.keys())
    nomes_referenciados = set()
    for caminho_rel in elegiveis:
        caminho_abs = caminho_seguro(raiz, caminho_rel)
        try:
            with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        palavras = set(re.findall(r"\b\w+\b", conteudo))
        palavras.update(_modulos_importados(conteudo))
        for nome in todos_nomes & palavras:
            nomes_referenciados.update(nome_para_arquivos[nome])
    return nomes_referenciados


def _modulos_importados(conteudo):
    modulos = set()
    for nome in re.findall(r"(?m)^\s*(?:from|import)\s+([\w.]+)", conteudo):
        modulos.add(nome.rsplit(".", 1)[-1])
    return modulos


def _verificar_documentacao(
    raiz, caminhos_excluidos, resultados, severidade="warning", config=None
):
    from auditoria_higiene.semantic import montar_evidencias

    evidencias = montar_evidencias(raiz, config or {})
    padrao_ref = re.compile(
        r"[\"'`]([\w./-]+\.(?:py|md|yaml|yml|txt|json|csv|html|css|js))[\"'`]"
    )
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if caminho_rel.startswith(
            (_DIR_ARCHIVE, _DIR_OPENSPEC_CHANGES, _DIR_OPENSPEC_PROPOSTAS)
        ):
            continue
        if not caminho_rel.endswith(".md"):
            continue
        _verificar_refs_doc_em_arquivo(
            raiz, caminho_rel, padrao_ref, resultados, severidade, evidencias
        )


def _verificar_refs_doc_em_arquivo(
    raiz, caminho_rel, padrao_ref, resultados, severidade, evidencias=None
):
    if evidencias is None:
        evidencias = {}
    caminho_abs = caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    for match in padrao_ref.finditer(conteudo):
        _processar_ref_doc(match, raiz, caminho_rel, resultados, severidade, evidencias)


def _processar_ref_doc(match, raiz, caminho_rel, resultados, severidade, evidencias):
    ref = match.group(1)
    if _parece_versao(ref):
        return
    if _eh_url_http(ref):
        return
    if ref.startswith(("/", "\\", "~")):
        return
    caminho_ref = os.path.normpath(os.path.join(os.path.dirname(caminho_rel), ref))
    try:
        caminho_abs_ref = caminho_seguro(raiz, caminho_ref)
    except ValueError:
        return
    if not os.path.exists(caminho_abs_ref):
        evidencia_ref = caminho_ref.replace(os.sep, "/")
        if caminho_ref in evidencias or evidencia_ref in evidencias:
            return
        resultados.append(
            {
                "regra": "outdated_documentation",
                "caminho": caminho_rel,
                "severity": severidade,
                "confianca": "high",
                "mensagem": f"Documentation references missing file: {ref}",
                "evidencias": f"File {caminho_rel} contains reference to {ref} which does not exist in the repository",
                "recomendacao": UPDATE_DOCS,
            }
        )


def _parece_versao(valor):
    return bool(re.fullmatch(r"v?\d+(?:\.\d+)+(?:\.x)?", valor))


def _verificar_config_sem_integracao(
    raiz, caminhos_excluidos, resultados, severidade="warning"
):
    config_patterns = (
        ".pre-commit-config.yaml",
        "sonar-project.properties",
        ".secrets.baseline",
    )
    arquivos = _arquivos_rastreados(raiz)
    configs = _filtrar_configs(arquivos, caminhos_excluidos, config_patterns)
    if not configs:
        return
    nomes_config = {os.path.basename(c) for c in configs}
    padroes_config = {
        n: re.compile(r"(?<!\w)" + re.escape(n) + r"(?!\w)") for n in nomes_config
    }
    nomes_referenciados = _coletar_referencias_config(
        raiz, arquivos, configs, padroes_config
    )
    _reportar_configs_sem_referencia(
        configs, nomes_referenciados, resultados, severidade
    )


def _reportar_configs_sem_referencia(
    configs, nomes_referenciados, resultados, severidade
):
    for caminho_rel in configs:
        nome_base = os.path.basename(caminho_rel)
        if nome_base in nomes_referenciados:
            continue
        resultados.append(
            {
                "regra": "unintegrated_configurations",
                "caminho": caminho_rel,
                "severity": severidade,
                "confianca": "low",
                "mensagem": "Configuration without corresponding workflow, command, or documentation",
                "evidencias": f"File {caminho_rel} is not referenced by any other tracked file",
                "recomendacao": ADD_CI,
            }
        )


def _filtrar_configs(arquivos, caminhos_excluidos, config_patterns):
    configs = []
    for caminho_rel in arquivos:
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if not caminho_rel.endswith(config_patterns):
            continue
        configs.append(caminho_rel)
    return configs


def _coletar_referencias_config(raiz, arquivos, configs, padroes_config):
    nomes_referenciados = set()
    for caminho_rel in arquivos:
        if caminho_rel in configs:
            continue
        caminho_abs = caminho_seguro(raiz, caminho_rel)
        try:
            with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        for nome, padrao in padroes_config.items():
            if padrao.search(conteudo):
                nomes_referenciados.add(nome)
    return nomes_referenciados


def _verificar_openspec_parada(
    raiz, caminhos_excluidos, resultados, severidade="warning"
):
    changes_dir = caminho_seguro(raiz, "openspec", "changes")
    if not os.path.isdir(changes_dir):
        return
    for entry in os.listdir(changes_dir):
        if entry == "archive":
            continue
        entry_path = os.path.join(changes_dir, entry)
        if not os.path.isdir(entry_path):
            continue
        if _esta_excluido(entry, caminhos_excluidos):
            continue
        _avaliar_entrada_openspec(raiz, entry, entry_path, resultados, severidade)


def _avaliar_entrada_openspec(raiz, entry, entry_path, resultados, severidade):
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", entry_path],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=10,
            shell=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return
        ultimo_commit_ts = int(result.stdout.strip())
        ultimo_commit = datetime.fromtimestamp(ultimo_commit_ts, tz=timezone.utc)
        agora = datetime.now(timezone.utc)
        dias_parado = (agora - ultimo_commit).days
        if dias_parado >= 30:
            resultados.append(
                {
                    "regra": "stale_openspec_changes",
                    "caminho": f"openspec/changes/{entry}",
                    "severity": severidade,
                    "mensagem": f"OpenSpec change stale for {dias_parado} days without modification",
                    "evidencias": f"Last commit in openspec/changes/{entry} {dias_parado} days ago",
                    "recomendacao": ARCHIVE_CHANGE,
                }
            )
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        pass


def _verificar_workflows_inseguros(
    raiz, caminhos_excluidos, resultados, severidade="warning", cfg=None
):
    workflows_dir = caminho_seguro(raiz, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        return
    for entry in os.listdir(workflows_dir):
        if not entry.endswith((".yml", ".yaml")):
            continue
        caminho_rel = os.path.join(".github", "workflows", entry)
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        _analisar_workflow(raiz, caminho_rel, resultados, severidade, cfg)


def _analisar_workflow(raiz, caminho_rel, resultados, severidade, cfg=None):
    caminho_abs = caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    workflow = yaml.safe_load(conteudo)
    if not isinstance(workflow, dict):
        return
    _reportar_permissoes_inseguras(
        workflow.get("permissions", {}),
        caminho_rel,
        resultados,
        severidade,
        cfg,
        workflow,
    )
    _reportar_jobs_inseguros(
        workflow.get("jobs", {}), caminho_rel, resultados, severidade
    )


def _permissao_justificada(permissoes, workflow):
    if not isinstance(permissoes, dict) or not isinstance(workflow, dict):
        return False
    steps = _coletar_steps(workflow)
    for scope, level in permissoes.items():
        if level not in ("write", "write-all"):
            continue
        if scope == "issues" and _steps_usam_issues(steps):
            return True
        if scope == "contents" and _steps_usam_contents_write(steps):
            return True
    return False


def _coletar_steps(workflow):
    steps = []
    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return steps
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps", []):
            if not isinstance(step, dict):
                continue
            steps.append(step)
    return steps


def _steps_usam_issues(steps):
    for step in steps:
        run_cmd = step.get("run", "")
        if isinstance(run_cmd, str) and "gh issue" in run_cmd:
            return True
        uses_action = step.get("uses", "")
        if isinstance(uses_action, str) and "actions/github-script" in uses_action:
            return True
    return False


def _steps_usam_contents_write(steps):
    for step in steps:
        run_cmd = step.get("run", "")
        if isinstance(run_cmd, str) and "gh release" in run_cmd:
            return True
        uses_action = step.get("uses", "")
        if isinstance(uses_action, str) and "actions/create-release" in uses_action:
            return True
    return False


def _reportar_permissoes_inseguras(
    permissoes, caminho_rel, resultados, severidade, cfg, workflow=None
):
    if isinstance(permissoes, str) and permissoes in ("write-all",):
        resultados.append(
            {
                "regra": "insecure_workflows",
                "caminho": caminho_rel,
                "severity": severidade,
                "mensagem": "Workflow with excessive permission: write-all",
                "recomendacao": SCOPE_PERMISSIONS,
            }
        )
    if isinstance(permissoes, dict):
        permitidas = set((cfg or {}).get("allowed_write_permissions", []))
        for scope, level in permissoes.items():
            if level in ("write", "write-all") and scope not in permitidas:
                if _permissao_justificada({scope: level}, workflow):
                    resultados.append(
                        {
                            "regra": "insecure_workflows",
                            "caminho": caminho_rel,
                            "severity": severidade,
                            "mensagem": f"Justified permission: {scope}={level}",
                            "recomendacao": ACCEPT_FALSE_POSITIVE,
                        }
                    )
                    continue
                resultados.append(
                    {
                        "regra": "insecure_workflows",
                        "caminho": caminho_rel,
                        "severity": severidade,
                        "mensagem": f"Excessive permission: {scope}={level}",
                        "recomendacao": SCOPE_PERMISSIONS,
                    }
                )


def _reportar_jobs_inseguros(jobs, caminho_rel, resultados, severidade):
    if not isinstance(jobs, dict):
        return
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        _reportar_pull_request_target(
            job_name, job, caminho_rel, resultados, severidade
        )
        _reportar_actions_sem_versao(job_name, job, caminho_rel, resultados, severidade)


def _reportar_pull_request_target(job_name, job, caminho_rel, resultados, severidade):
    if (
        job.get("if", "")
        .strip()
        .startswith("github.event_name == 'pull_request_target'")
    ):
        resultados.append(
            {
                "regra": "insecure_workflows",
                "caminho": caminho_rel,
                "severity": severidade,
                "mensagem": f"Job '{job_name}' uses pull_request_target without additional protection",
                "recomendacao": SCOPE_PERMISSIONS,
            }
        )


def _reportar_actions_sem_versao(job_name, job, caminho_rel, resultados, severidade):
    steps = job.get("steps", [])
    if not isinstance(steps, list):
        return
    for step_idx, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        uses = step.get("uses", "")
        if uses and _uses_action_sem_versao_fixa(uses):
            resultados.append(
                {
                    "regra": "insecure_workflows",
                    "caminho": caminho_rel,
                    "severity": severidade,
                    "mensagem": f"Step {step_idx + 1} in job '{job_name}' uses action without pinned version: {uses}",
                    "recomendacao": PIN_ACTION_VERSION,
                }
            )


def _verificar_repositorios_aninhados(
    raiz, caminhos_excluidos, resultados, severidade, config=None
):
    dirs_untracked = _listar_diretorios_nao_rastreados(raiz)
    for dir_path in dirs_untracked:
        if _esta_excluido(dir_path, caminhos_excluidos):
            continue
        dir_abs = caminho_seguro(raiz, dir_path)
        if not os.path.isdir(os.path.join(dir_abs, ".git")):
            continue
        if _em_gitmodules(raiz, dir_path):
            continue
        gitignore_path = caminho_seguro(raiz, _ARQUIVO_GITIGNORE)
        if os.path.isfile(gitignore_path):
            with open(gitignore_path, "r", encoding="utf-8") as f:
                if _em_gitignore(dir_path, f.read().splitlines()):
                    continue
        if _dir_em_evidencias(raiz, dir_path, config):
            continue
        resultados.append(
            {
                "regra": "nested_repositories",
                "caminho": dir_path.rstrip("/"),
                "severity": severidade,
                "mensagem": "Accidental nested repository detected",
                "recomendacao": REMOVE,
            }
        )


def _listar_diretorios_nao_rastreados(raiz):
    try:
        result = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--directory", "-z"],
            capture_output=True,
            cwd=raiz,
            timeout=30,
            shell=False,
        )
        if result.returncode != 0:
            return []
        stdout = result.stdout
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="surrogateescape")
        return [
            p.replace("\\", "/") for p in stdout.split("\0") if p and p.endswith("/")
        ]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _em_gitmodules(raiz, dir_path):
    import configparser

    gitmodules_path = caminho_seguro(raiz, ".gitmodules")
    if not os.path.isfile(gitmodules_path):
        return False
    try:
        parser = configparser.ConfigParser()
        parser.read(gitmodules_path)
        for section in parser.sections():
            submodule_path = parser.get(section, "path", fallback="")
            if submodule_path and submodule_path.rstrip("/") == dir_path.rstrip("/"):
                return True
    except configparser.Error:
        return False
    return False


def _dir_em_evidencias(raiz, dir_path, config):
    if config is None:
        return False
    from auditoria_higiene.semantic import montar_evidencias

    evidencias = montar_evidencias(raiz, config)
    nome_dir = dir_path.rstrip("/")
    if nome_dir in evidencias or nome_dir + "/" in evidencias:
        return True
    return _dir_mencionada_em_openspec(raiz, nome_dir)


def _dir_mencionada_em_openspec(raiz, dir_name):
    for subdir in ("specs", "changes"):
        dir_abs = os.path.join(raiz, "openspec", subdir)
        if not os.path.isdir(dir_abs):
            continue
        if _subdir_contem_nome(dir_abs, dir_name):
            return True
    return False


def _subdir_contem_nome(dir_abs, dir_name):
    for root, _, files in os.walk(dir_abs):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            if _arquivo_contem_texto(os.path.join(root, fname), dir_name):
                return True
    return False


def _arquivo_contem_texto(fpath, texto):
    try:
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            return texto in f.read()
    except (OSError, UnicodeDecodeError):
        return False


def _uses_action_sem_versao_fixa(uses):
    if uses.count("@") != 1:
        return True
    _, ref = uses.split("@", 1)
    if ref.startswith("refs/heads/"):
        return True
    if ref == "main" or ref == "master":
        return True
    return False
