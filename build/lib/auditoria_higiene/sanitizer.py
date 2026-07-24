"""Sanitização de dados sensíveis em resultados de auditoria."""

_CAMPOS_SENSIVEIS = frozenset({"mensagem", "evidencias"})


def sanitizar_resultado(resultado):
    sanitizado = {
        "resultados": [_sanitizar_item(r) for r in resultado.get("resultados", [])],
        "status": resultado.get("status", "sucesso"),
        "regras_desativadas": resultado.get("regras_desativadas", []),
    }
    return sanitizado


def _sanitizar_item(item):
    copia = dict(item)
    for campo in _CAMPOS_SENSIVEIS:
        if campo in copia and isinstance(copia[campo], str):
            copia[campo] = _mascarar_valores(copia[campo])
    return copia


_PADRAO_VALOR_SENSIVEL = __import__("re").compile(
    r"(?i)(senha|password|api_key|secret|token)\s*[=:]\s*\S+"
)


def _mascarar_valores(texto):
    return _PADRAO_VALOR_SENSIVEL.sub(r"\1=***", texto)
