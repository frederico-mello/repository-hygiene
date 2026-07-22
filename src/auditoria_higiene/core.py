"""Núcleo de auditoria: carregamento de configuração e execução de regras."""

import os
import re
import subprocess
from datetime import datetime, timezone

import yaml

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
        return {}
    return config


def validar_configuracao(config):
    versao = config.get("versao_configuracao", 1)
    if versao != CONFIG_VERSION:
        raise ValueError(
            f"Versão de configuração {versao} não suportada. Esperada: {CONFIG_VERSION}"
        )
    return True


def executar_auditoria(raiz, config):
    _TRACKED_CACHE.pop(os.path.realpath(raiz), None)
    resultados = []
    regras = config.get("regras", {})
    excecoes = config.get("excecoes", {})
    regras_desativadas = []

    for nome_regra, cfg in regras.items():
        if not cfg.get("habilitada", True):
            regras_desativadas.append(nome_regra)
            continue
        caminhos_excluidos = excecoes.get(nome_regra, [])
        _avaliar_regra(nome_regra, cfg, raiz, caminhos_excluidos, resultados)

    tem_erro = any(
        r["severidade"] == "error" and r.get("confianca", "high") in ("high", "medium")
        for r in resultados
    )
    return {
        "resultados": resultados,
        "status": "falha" if tem_erro else "sucesso",
        "regras_desativadas": regras_desativadas,
    }


def _avaliar_regra(nome_regra, cfg, raiz, caminhos_excluidos, resultados):
    severidade = cfg.get("severidade", "error")
    if nome_regra == "segredos_rastreados":
        _verificar_segredos(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "links_internos_quebrados":
        _verificar_links_internos(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "referencias_inexistentes":
        _verificar_referencias(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "artefatos_fora_gitignore":
        _verificar_artefatos(raiz, caminhos_excluidos, resultados, severidade, cfg)
    elif nome_regra == "gitkeep_sem_conteudo":
        _verificar_gitkeep(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "arquivos_sem_referencia":
        _verificar_sem_referencia(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "documentacao_desatualizada":
        _verificar_documentacao(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "configuracao_sem_integracao":
        _verificar_config_sem_integracao(
            raiz, caminhos_excluidos, resultados, severidade
        )
    elif nome_regra == "openspec_parada":
        _verificar_openspec_parada(raiz, caminhos_excluidos, resultados, severidade)
    elif nome_regra == "workflows_inseguros":
        _verificar_workflows_inseguros(
            raiz, caminhos_excluidos, resultados, severidade, cfg
        )


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
        raise ValueError(f"Path traversal detectado: {caminho}")
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
                                "regra": "segredos_rastreados",
                                "caminho": caminho_rel,
                                "linha": i,
                                "severidade": severidade,
                                "confianca": confianca,
                                "mensagem": "Segredo ou credencial encontrado",
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
                        "regra": "links_internos_quebrados",
                        "caminho": caminho_rel,
                        "severidade": severidade,
                        "mensagem": f"Link interno quebrado: {url}",
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
                    "regra": "referencias_inexistentes",
                    "caminho": caminho_rel,
                    "severidade": severidade,
                    "mensagem": f"Referência a arquivo inexistente: {ref}",
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
        if not _deve_reportar_artefato(caminho_rel, caminhos_excluidos, cfg):
            continue
        resultados.append(
            {
                "regra": "artefatos_fora_gitignore",
                "caminho": caminho_rel,
                "severidade": severidade,
                "mensagem": "Artefato gerado não coberto pelo .gitignore",
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


def _deve_reportar_artefato(caminho_rel, caminhos_excluidos, cfg):
    if _esta_excluido(caminho_rel, caminhos_excluidos):
        return False
    if caminho_rel == _ARQUIVO_GITIGNORE or caminho_rel.startswith(
        (".git/", ".repository-hygiene/")
    ):
        return False
    return not _eh_diretorio_fonte(caminho_rel) and _eh_artefato_configurado(
        caminho_rel, cfg
    )


def _eh_diretorio_fonte(caminho_rel):
    return caminho_rel.startswith(("src/", ".github/", ".opencode/", "openspec/"))


def _eh_artefato_configurado(caminho_rel, cfg):
    padroes = (cfg or {}).get("padroes_artefatos")
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
                "regra": "gitkeep_sem_conteudo",
                "caminho": caminho_rel,
                "severidade": severidade,
                "mensagem": "Diretório contém apenas .gitkeep sem conteúdo adicional",
            }
        )


def _verificar_sem_referencia(
    raiz, caminhos_excluidos, resultados, severidade="warning"
):
    arquivos = _arquivos_rastreados(raiz)
    elegiveis = _filtrar_elegiveis_sem_referencia(arquivos, caminhos_excluidos)
    if not elegiveis:
        return
    nome_para_arquivos = _agrupar_por_nome(elegiveis)
    nomes_referenciados = _coletar_referencias(raiz, elegiveis, nome_para_arquivos)
    for caminho_rel in elegiveis:
        if caminho_rel in nomes_referenciados:
            continue
        resultados.append(
            {
                "regra": "arquivos_sem_referencia",
                "caminho": caminho_rel,
                "severidade": severidade,
                "confianca": "low",
                "mensagem": "Arquivo sem referências detectáveis em outros arquivos",
                "evidencias": f"Arquivo {caminho_rel} não é mencionado em nenhum outro arquivo rastreado",
                "recomendacao": "Revisar se o arquivo é necessário ou deve ser referenciado em documentação",
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


def _verificar_documentacao(raiz, caminhos_excluidos, resultados, severidade="warning"):
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
            raiz, caminho_rel, padrao_ref, resultados, severidade
        )


def _verificar_refs_doc_em_arquivo(
    raiz, caminho_rel, padrao_ref, resultados, severidade
):
    caminho_abs = caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    for match in padrao_ref.finditer(conteudo):
        ref = match.group(1)
        if _parece_versao(ref):
            continue
        if _eh_url_http(ref):
            continue
        if ref.startswith(("/", "\\", "~")):
            continue
        caminho_ref = os.path.normpath(os.path.join(os.path.dirname(caminho_rel), ref))
        try:
            caminho_abs_ref = caminho_seguro(raiz, caminho_ref)
        except ValueError:
            continue
        if not os.path.exists(caminho_abs_ref):
            resultados.append(
                {
                    "regra": "documentacao_desatualizada",
                    "caminho": caminho_rel,
                    "severidade": severidade,
                    "confianca": "high",
                    "mensagem": f"Documentação referencia arquivo inexistente: {ref}",
                    "evidencias": f"Arquivo {caminho_rel} contém referência a {ref} que não existe no repositório",
                    "recomendacao": "Atualizar documentação ou criar o arquivo referenciado",
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
                "regra": "configuracao_sem_integracao",
                "caminho": caminho_rel,
                "severidade": severidade,
                "confianca": "low",
                "mensagem": "Configuração sem workflow, comando ou documentação correspondente",
                "evidencias": f"Arquivo {caminho_rel} não é referenciado por nenhum outro arquivo rastreado",
                "recomendacao": "Verificar se a configuração é necessária ou adicionar referência em documentação/workflow",
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
                    "regra": "openspec_parada",
                    "caminho": f"openspec/changes/{entry}",
                    "severidade": severidade,
                    "mensagem": f"Mudança OpenSpec parada há {dias_parado} dias sem alteração",
                    "evidencias": f"Último commit em openspec/changes/{entry} há {dias_parado} dias",
                    "recomendacao": "Revisar se a mudança deve ser arquivada ou retomada",
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
        workflow.get("permissions", {}), caminho_rel, resultados, severidade, cfg
    )
    _reportar_jobs_inseguros(
        workflow.get("jobs", {}), caminho_rel, resultados, severidade
    )


def _reportar_permissoes_inseguras(
    permissoes, caminho_rel, resultados, severidade, cfg
):
    if isinstance(permissoes, str) and permissoes in ("write-all",):
        resultados.append(
            {
                "regra": "workflows_inseguros",
                "caminho": caminho_rel,
                "severidade": severidade,
                "mensagem": "Workflow com permissão excessiva: write-all",
                "recomendacao": "Restringir permissões ao mínimo necessário",
            }
        )
    if isinstance(permissoes, dict):
        permitidas = set((cfg or {}).get("permissoes_write_permitidas", []))
        for scope, level in permissoes.items():
            if level in ("write", "write-all") and scope not in permitidas:
                resultados.append(
                    {
                        "regra": "workflows_inseguros",
                        "caminho": caminho_rel,
                        "severidade": severidade,
                        "mensagem": f"Permissão excessiva: {scope}={level}",
                        "recomendacao": f"Restringir {scope} ao nível 'read' ou 'none' se possível",
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
                "regra": "workflows_inseguros",
                "caminho": caminho_rel,
                "severidade": severidade,
                "mensagem": f"Job '{job_name}' usa pull_request_target sem proteção adicional",
                "recomendacao": "Validar segurança de pull_request_target ou usar pull_request",
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
                    "regra": "workflows_inseguros",
                    "caminho": caminho_rel,
                    "severidade": severidade,
                    "mensagem": f"Step {step_idx + 1} em job '{job_name}' usa action sem versão fixa: {uses}",
                    "recomendacao": "Fixar versão com tag semver ou SHA do commit",
                }
            )


def _uses_action_sem_versao_fixa(uses):
    if uses.count("@") != 1:
        return True
    _, ref = uses.split("@", 1)
    if ref.startswith("refs/heads/"):
        return True
    if ref == "main" or ref == "master":
        return True
    return False
