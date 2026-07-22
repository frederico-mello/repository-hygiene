"""Renderizadores de relatório: texto, JSON e SARIF."""

import json


def gerar_relatorio_texto(resultado):
    erros = [r for r in resultado["resultados"] if r["severidade"] == "error"]
    avisos = [r for r in resultado["resultados"] if r["severidade"] == "warning"]
    regras_desativadas = resultado.get("regras_desativadas", [])
    linhas = []
    linhas.append("=" * 60)
    linhas.append("RELATORIO DE AUDITORIA DE HIGIENE")
    linhas.append("=" * 60)
    linhas.append("")
    _adicionar_secao(linhas, "ERROR", erros)
    _adicionar_secao(linhas, "WARNING", avisos)
    if regras_desativadas:
        linhas.append(f"--- DESATIVADAS ({len(regras_desativadas)} regra(s)) ---")
        for nome in regras_desativadas:
            linhas.append(f"  [{nome}]")
        linhas.append("")
    linhas.append(f"Status: {resultado['status']}")
    linhas.append("=" * 60)
    return "\n".join(linhas)


def _adicionar_secao(linhas, titulo, itens):
    if not itens:
        return
    linhas.append(f"--- {titulo} ({len(itens)} ocorrencia(s)) ---")
    for r in itens:
        linhas.append(f"  [{r['regra']}] {r['caminho']}")
        linhas.append(f"    {r['mensagem']}")
        if "evidencias" in r:
            linhas.append(f"    Evidencias: {r['evidencias']}")
        if "recomendacao" in r:
            linhas.append(f"    Recomendacao: {r['recomendacao']}")
    linhas.append("")


def gerar_relatorio_json(resultado):
    return json.dumps(resultado, ensure_ascii=False, indent=2)


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
                "shortDescription": {"text": f"Regra de auditoria: {nome}"},
                "defaultConfiguration": {"level": "error" if r["severidade"] == "error" else "warning"},
            }
    results = []
    for r in resultado["resultados"]:
        result = {
            "ruleId": r["regra"],
            "level": "error" if r["severidade"] == "error" else "warning",
            "message": {"text": r["mensagem"]},
        }
        if "caminho" in r:
            result["locations"] = [{
                "physicalLocation": {
                    "artifactLocation": {"uri": r["caminho"]},
                }
            }]
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
            "regras_desativadas": resultado.get("regras_desativadas", []),
        },
    }
