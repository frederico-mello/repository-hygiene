"""Report renderers: text, JSON, and SARIF."""

import json
import os
import tempfile
from datetime import datetime, timezone


def gerar_resumo(resultado, report_path):
    erros = len([r for r in resultado["resultados"] if r["severity"] == "error"])
    avisos = len([r for r in resultado["resultados"] if r["severity"] == "warning"])
    status = resultado["status"]
    linhas = []
    linhas.append(f"Status: {status}")
    linhas.append(f"Errors: {erros}")
    linhas.append(f"Warnings: {avisos}")
    linhas.append(f"Report: {report_path}")
    return "\n".join(linhas)


def escrever_relatorio(conteudo, caminho, raiz_permitida, criar_pai=True):
    _validar_caminho_saida(caminho, raiz_permitida)
    diretorio = os.path.dirname(caminho)
    if criar_pai:
        os.makedirs(diretorio, exist_ok=True)  # NOSONAR
    elif not os.path.isdir(diretorio):
        raise OSError(f"Output directory not found: {diretorio}")
    fd, tmp = tempfile.mkstemp(prefix=".auditoria-", dir=diretorio, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
            f.write("\n")
        os.replace(tmp, caminho)  # NOSONAR validated by cli._resolver_saida
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _validar_caminho_saida(caminho, raiz_permitida):
    raiz = os.path.realpath(raiz_permitida)
    destino = os.path.realpath(caminho)
    if destino != raiz and not destino.startswith(raiz + os.sep):
        raise OSError(f"Output path outside permitted directory: {caminho}")


def gerar_relatorio_texto(resultado):
    erros = [r for r in resultado["resultados"] if r["severity"] == "error"]
    avisos = [r for r in resultado["resultados"] if r["severity"] == "warning"]
    regras_desativadas = resultado.get("disabled_rules", [])
    linhas = []
    linhas.append("=" * 60)
    linhas.append("REPOSITORY HYGIENE AUDIT REPORT")
    linhas.append("=" * 60)
    linhas.append("")
    _adicionar_secao(linhas, "ERROR", erros)
    _adicionar_secao(linhas, "WARNING", avisos)
    if regras_desativadas:
        linhas.append(f"--- DISABLED ({len(regras_desativadas)} rule(s)) ---")
        for nome in regras_desativadas:
            linhas.append(f"  [{nome}]")
        linhas.append("")
    linhas.append(f"Status: {resultado['status']}")
    linhas.append("=" * 60)
    return "\n".join(linhas)


def _adicionar_secao(linhas, titulo, itens):
    if not itens:
        return
    linhas.append(f"--- {titulo} ({len(itens)} occurrence(s)) ---")
    for r in itens:
        linhas.append(f"  [{r['regra']}] {r['caminho']}")
        linhas.append(f"    {r['mensagem']}")
        if "confianca" in r:
            linhas.append(f"    Confidence: {r['confianca']}")
        if "evidencias" in r:
            linhas.append(f"    Evidence: {r['evidencias']}")
        if "recomendacao" in r:
            linhas.append(f"    Recommendation: {r['recomendacao']}")
    linhas.append("")


def gerar_relatorio_json(resultado):
    return json.dumps(resultado, ensure_ascii=False, indent=2)


def gerar_relatorio_json_agente(resultado, auditor_version, diretorio):
    return gerar_relatorio_json(
        {
            "schema_version": 1,
            "auditor_version": auditor_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "audited_directory": os.path.realpath(diretorio),
            **resultado,
        }
    )


def gerar_relatorio_sarif(resultado):
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/openc2-schema/main/sarif/sarif-2-1.json",
        "version": "2.1.0",
        "runs": [_run_sarif(resultado)],
    }
    return json.dumps(sarif, ensure_ascii=False, indent=2)


def _run_sarif(resultado):
    regras_unicas = {}
    for r in resultado["resultados"]:
        nome = r["regra"]
        if nome not in regras_unicas:
            regras_unicas[nome] = {
                "id": nome,
                "name": nome,
                "shortDescription": {"text": f"Audit rule: {nome}"},
                "defaultConfiguration": {
                    "level": "error" if r["severity"] == "error" else "warning"
                },
            }
    results = []
    for r in resultado["resultados"]:
        result = {
            "ruleId": r["regra"],
            "level": "error" if r["severity"] == "error" else "warning",
            "message": {"text": r["mensagem"]},
        }
        if "caminho" in r:
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": r["caminho"]},
                    }
                }
            ]
        if "evidencias" in r:
            result["message"]["text"] += f" | {r['evidencias']}"
        if "recomendacao" in r:
            result["properties"] = {"recomendacao": r["recomendacao"]}
        results.append(result)
    return {
        "tool": {
            "driver": {
                "name": "repository-hygiene",
                "version": "0.1.0",
                "informationUri": "https://github.com/frederico-mello/repository-hygiene",
                "rules": list(regras_unicas.values()),
            }
        },
        "results": results,
        "properties": {
            "status": resultado.get("status", "sucesso"),
            "disabled_rules": resultado.get("disabled_rules", []),
        },
    }
