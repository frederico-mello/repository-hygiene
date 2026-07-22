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

_PADROES_SEGREDOS = [
    re.compile(r"(?i)(?<!\w)senha\s*[=:]\s*\S+"),
    re.compile(r"(?i)(?<!\w)password\s*[=:]\s*\S+"),
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
    modo = config.get("modo")
    if modo is not None and modo not in ("pre-commit", "ci"):
        raise ValueError(
            f"Modo '{modo}' inválido. Valores aceitos: pre-commit, ci"
        )
    return True


def _classificar_ref_por_extensao(ref):
    if ref.endswith(".py"):
        return {
            "classificacao": "confirmed",
            "confianca": "alta",
            "kind": "file_reference",
            "policy_action": "fail",
            "reason": "Referência em código Python (.py) — alta confiança",
        }
    if ref.endswith((".md", ".yaml", ".yml")):
        return {
            "classificacao": "probable",
            "confianca": "media",
            "kind": "file_reference",
            "policy_action": None,
            "reason": "Referência em documentação ou configuração (.md/.yaml/.yml) — confiança média",
        }
    if ref.endswith((".csv", ".json", ".txt")):
        return {
            "classificacao": "ambiguous",
            "confianca": "baixa",
            "kind": "file_reference",
            "policy_action": "report",
            "reason": "Referência em arquivo de dados (.csv/.json/.txt) — confiança baixa",
        }
    return {
        "classificacao": "rejected",
        "confianca": "baixa",
        "kind": "file_reference",
        "policy_action": "report",
        "reason": "Referência em tipo de arquivo não classificado — rejeitada",
    }


_REGRAS_COM_CLASSIFICACAO = frozenset(
    {"referencias_inexistentes", "documentacao_desatualizada"}
)


def _aplicar_politica_modo(ocorrencia, politica):
    if "classificacao" not in ocorrencia:
        return ocorrencia, True
    cls = ocorrencia["classificacao"]
    if politica == "ci":
        if cls == "confirmed":
            policy_action, conta_como_erro = "fail", True
        else:
            policy_action, conta_como_erro = "report", False
    elif politica == "pre-commit":
        if cls == "confirmed":
            policy_action, conta_como_erro = "fail", True
        elif cls == "probable":
            policy_action, conta_como_erro = "fail", True
        else:
            policy_action, conta_como_erro = "report", False
    else:
        return ocorrencia, True
    ocorrencia["policy_action"] = policy_action
    return ocorrencia, conta_como_erro


def executar_auditoria(raiz, config):
    validar_configuracao(config)
    resultados = []
    regras = config.get("regras", {})
    excecoes = config.get("excecoes", {})
    regras_desativadas = []
    modo = config.get("modo")

    for nome_regra, cfg in regras.items():
        if not cfg.get("habilitada", True):
            regras_desativadas.append(nome_regra)
            continue
        caminhos_excluidos = excecoes.get(nome_regra, [])
        _avaliar_regra(nome_regra, cfg, raiz, caminhos_excluidos, resultados)

    if modo:
        resultados_processados = []
        tem_erro = False
        for r in resultados:
            if r.get("regra") in _REGRAS_COM_CLASSIFICACAO:
                r_atualizado, conta_como_erro = _aplicar_politica_modo(r, modo)
                resultados_processados.append(r_atualizado)
                if r["severidade"] == "error" and conta_como_erro:
                    tem_erro = True
            else:
                resultados_processados.append(r)
                if r["severidade"] == "error":
                    tem_erro = True
        resultados = resultados_processados
    else:
        tem_erro = any(r["severidade"] == "error" for r in resultados)

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
        _verificar_artefatos(raiz, caminhos_excluidos, resultados, severidade)
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
        _verificar_workflows_inseguros(raiz, caminhos_excluidos, resultados, severidade)


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


def _caminho_seguro(raiz, *partes):
    caminho = os.path.normpath(os.path.join(raiz, *partes))
    raiz_abs = os.path.realpath(raiz)
    caminho_abs = os.path.realpath(caminho)
    if not caminho_abs.startswith(raiz_abs + os.sep) and caminho_abs != raiz_abs:
        raise ValueError(f"Path traversal detectado: {caminho}")
    return caminho_abs


def _arquivos_rastreados(raiz):
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=30,
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
        caminho_abs = _caminho_seguro(raiz, caminho_rel)
        if not os.path.isfile(caminho_abs):
            continue
        _escanear_linhas_por_segredos(caminho_abs, caminho_rel, resultados, severidade)


def _escanear_linhas_por_segredos(caminho_abs, caminho_rel, resultados, severidade):
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            for i, linha in enumerate(f, 1):
                if _linha_eh_comentario(linha):
                    continue
                for padrao in _PADROES_SEGREDOS:
                    if padrao.search(linha):
                        resultados.append(
                            {
                                "regra": "segredos_rastreados",
                                "caminho": caminho_rel,
                                "linha": i,
                                "severidade": severidade,
                                "mensagem": "Segredo ou credencial encontrado",
                            }
                        )
                        break
    except (OSError, UnicodeDecodeError):
        pass


def _em_diretorio_ruidoso_segredos(caminho_rel):
    return caminho_rel.startswith(
        (_DIR_ARCHIVE, _DIR_OPENSPEC_CHANGES, _DIR_OPENSPEC_PROPOSTAS, "tests/")
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
    caminho_abs = _caminho_seguro(raiz, caminho_rel)
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
            if not os.path.exists(_caminho_seguro(raiz, caminho_alvo)):
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
        r"""["'`]([\w./-]+\.(?:py|md|yaml|yml|txt|json|csv|html|css|js))["'`]"""
    )
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if _em_diretorio_ruidoso_referencias(caminho_rel):
            continue
        if not caminho_rel.endswith((".py", ".md", ".yaml", ".yml", ".json", ".html")):
            continue
        _verificar_refs_em_arquivo(
            raiz, caminho_rel, padrao_ref, resultados, severidade
        )


def _verificar_refs_em_arquivo(raiz, caminho_rel, padrao_ref, resultados, severidade):
    caminho_abs = _caminho_seguro(raiz, caminho_rel)
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
        cls = _classificar_ref_por_extensao(ref)
        existe, candidatos = _referencia_existe(raiz, caminho_rel, ref)
        if not existe:
            resultados.append(
                {
                    "regra": "referencias_inexistentes",
                    "caminho": caminho_rel,
                    "severidade": severidade,
                    "mensagem": f"Referência a arquivo inexistente: {ref}",
                    **cls,
                    "candidatos": candidatos,
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
            "tests/",
        )
    )


def _referencia_existe(raiz, caminho_rel, ref):
    candidatos = []
    candidatos.append(os.path.normpath(ref))
    if caminho_rel:
        candidatos.append(
            os.path.normpath(os.path.join(os.path.dirname(caminho_rel), ref))
        )
    base = os.path.basename(ref)
    if base:
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
                if any(p.endswith("/" + base) or p == base for p in tracked):
                    return True, candidatos
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    for cand in candidatos:
        try:
            if os.path.exists(_caminho_seguro(raiz, cand)):
                return True, candidatos
        except ValueError:
            continue
    return False, candidatos


def _verificar_artefatos(raiz, caminhos_excluidos, resultados, severidade="error"):
    gitignore_path = _caminho_seguro(raiz, ".gitignore")
    if not os.path.exists(gitignore_path):
        return
    with open(gitignore_path, "r", encoding="utf-8") as f:
        gitignore_lines = f.read().splitlines()
    for caminho_rel in _todos_arquivos(raiz):
        if caminho_rel == ".gitignore":
            continue
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if _em_gitignore(caminho_rel, gitignore_lines):
            continue
        if _em_git(raiz, caminho_rel):
            continue
        resultados.append(
            {
                "regra": "artefatos_fora_gitignore",
                "caminho": caminho_rel,
                "severidade": severidade,
                "mensagem": "Artefato gerado não coberto pelo .gitignore",
            }
        )


def _em_git(raiz, caminho_rel):
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", caminho_rel],
            capture_output=True,
            text=True,
            cwd=raiz,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _em_gitignore(caminho, gitignore_lines):
    import fnmatch

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
        if not caminho_rel.endswith(
            (".py", ".md", ".yaml", ".yml", ".json", ".txt", ".html", ".css", ".js")
        ):
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
        caminho_abs = _caminho_seguro(raiz, caminho_rel)
        try:
            with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
        except (OSError, UnicodeDecodeError):
            continue
        palavras = set(re.findall(r"\b\w+\b", conteudo))
        for nome in todos_nomes & palavras:
            nomes_referenciados.update(nome_para_arquivos[nome])
    return nomes_referenciados


def _verificar_documentacao(raiz, caminhos_excluidos, resultados, severidade="warning"):
    padrao_ref = re.compile(r"""["'`]([^"'`]+\.\w+)["'`]""")
    for caminho_rel in _arquivos_rastreados(raiz):
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        if not caminho_rel.endswith(".md"):
            continue
        _verificar_refs_doc_em_arquivo(
            raiz, caminho_rel, padrao_ref, resultados, severidade
        )


def _verificar_refs_doc_em_arquivo(
    raiz, caminho_rel, padrao_ref, resultados, severidade
):
    caminho_abs = _caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    for match in padrao_ref.finditer(conteudo):
        ref = match.group(1)
        if _eh_url_http(ref):
            continue
        if ref.startswith(("/", "\\", "~")):
            continue
        caminho_ref = os.path.normpath(os.path.join(os.path.dirname(caminho_rel), ref))
        try:
            caminho_abs_ref = _caminho_seguro(raiz, caminho_ref)
        except ValueError:
            continue
        if not os.path.exists(caminho_abs_ref):
            resultados.append(
                {
                    "regra": "documentacao_desatualizada",
                    "caminho": caminho_rel,
                    "severidade": severidade,
                    "mensagem": f"Documentação referencia arquivo inexistente: {ref}",
                    "evidencias": f"Arquivo {caminho_rel} contém referência a {ref} que não existe no repositório",
                    "recomendacao": "Atualizar documentação ou criar o arquivo referenciado",
                }
            )


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
        caminho_abs = _caminho_seguro(raiz, caminho_rel)
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
    changes_dir = _caminho_seguro(raiz, "openspec", "changes")
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
    raiz, caminhos_excluidos, resultados, severidade="warning"
):
    workflows_dir = _caminho_seguro(raiz, ".github", "workflows")
    if not os.path.isdir(workflows_dir):
        return
    for entry in os.listdir(workflows_dir):
        if not entry.endswith((".yml", ".yaml")):
            continue
        caminho_rel = os.path.join(".github", "workflows", entry)
        if _esta_excluido(caminho_rel, caminhos_excluidos):
            continue
        _analisar_workflow(raiz, caminho_rel, resultados, severidade)


def _analisar_workflow(raiz, caminho_rel, resultados, severidade):
    caminho_abs = _caminho_seguro(raiz, caminho_rel)
    try:
        with open(caminho_abs, "r", encoding="utf-8", errors="replace") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError):
        return
    workflow = yaml.safe_load(conteudo)
    if not isinstance(workflow, dict):
        return
    permissoes = workflow.get("permissions", {})
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
        for scope, level in permissoes.items():
            if level in ("write", "write-all"):
                resultados.append(
                    {
                        "regra": "workflows_inseguros",
                        "caminho": caminho_rel,
                        "severidade": severidade,
                        "mensagem": f"Permissão excessiva: {scope}={level}",
                        "recomendacao": f"Restringir {scope} ao nível 'read' ou 'none' se possível",
                    }
                )
    jobs = workflow.get("jobs", {})
    if not isinstance(jobs, dict):
        return
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
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
        steps = job.get("steps", [])
        if not isinstance(steps, list):
            continue
        for step_idx, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "")
            if not uses:
                continue
            if _uses_action_sem_versao_fixa(uses):
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
