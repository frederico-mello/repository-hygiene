"""Supported agent roots: single source for provisioning and audit scope."""

import os

RAIZES_AGENTES = (".opencode", ".kilocode", ".kilo", ".omp", ".hermes")
RAIZ_PADRAO_AGENTE = ".opencode"


def raizes_alvo(raiz, agents=None):
    """Agent roots that receive the skill in the repository at `raiz`.

    With `agents` (raw names, with or without leading dot) the selection is
    explicit; without it every supported agent root present in the repository is
    selected, falling back to `.opencode` when none exists.

    Every selected root is validated: a root that resolves outside the
    repository (e.g. a symlink pointing elsewhere) raises `ValueError` instead
    of being provisioned to a path outside the target repository.
    """
    if agents is not None:
        selecionadas = _normalizar_agentes(agents)
    else:
        selecionadas = _raizes_presentes(raiz) or (RAIZ_PADRAO_AGENTE,)
    for raiz_agente in selecionadas:
        _validar_destino(raiz, raiz_agente)
    return selecionadas


def _raizes_presentes(raiz):
    return tuple(
        raiz_agente
        for raiz_agente in RAIZES_AGENTES
        if os.path.isdir(os.path.join(raiz, raiz_agente))
    )


def _validar_destino(raiz, raiz_agente):
    base = os.path.realpath(raiz)
    destino = os.path.realpath(os.path.join(base, raiz_agente))
    if destino != base and not destino.startswith(base + os.sep):
        raise ValueError(
            f"invalid skill destination: {raiz_agente} resolves to {destino}, "
            f"outside the repository {base}"
        )


def _normalizar_agentes(agents):
    selecionadas = []
    for agente in agents:
        nome = (agente or "").strip()
        if not nome:
            continue
        if not nome.startswith("."):
            nome = "." + nome
        if nome not in RAIZES_AGENTES:
            raise ValueError(
                f"unsupported agent: {agente} "
                f"(supported: {', '.join(r.lstrip('.') for r in RAIZES_AGENTES)})"
            )
        if nome not in selecionadas:
            selecionadas.append(nome)
    if not selecionadas:
        raise ValueError("no agent selected by --agents")
    return tuple(selecionadas)


def prefixos_ruido_referencias():
    """Path prefixes exempt from missing-reference enforcement per agent root."""
    prefixos = []
    for raiz_agente in RAIZES_AGENTES:
        prefixos.append(f"{raiz_agente}/commands/")
        prefixos.append(f"{raiz_agente}/skills/openspec-")
    prefixos.append(".kilocode/workflows/")
    return tuple(prefixos)


def prefixos_diretorio_fonte():
    """Agent roots treated as repository source by the audit."""
    return tuple(f"{raiz_agente}/" for raiz_agente in RAIZES_AGENTES)
