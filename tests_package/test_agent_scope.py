"""Escopo de auditoria e gatilhos do workflow para os diretórios de agente."""

import os
import subprocess

import yaml

from auditoria_higiene.agentes import RAIZES_AGENTES
from auditoria_higiene.core import executar_auditoria

CONFIG_ARTEFATOS = {
    "config_version": 1,
    "rules": {"untracked_artifacts": {"enabled": True, "severity": "error"}},
    "exceptions": {"untracked_artifacts": []},
}

CONFIG_REFERENCIAS = {
    "config_version": 1,
    "rules": {"missing_references": {"enabled": True, "severity": "error"}},
    "exceptions": {"missing_references": []},
}

WORKFLOW_TEMPLATE = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "auditoria_higiene",
        "templates",
        "workflow.yml",
    )
)


def _regras(resultado, nome):
    return [r for r in resultado["resultados"] if r["regra"] == nome]


class TestEscopoDiretoriosDeAgente:
    def test_arquivos_de_agente_nao_sao_artefatos(self, git_repo):
        repo = git_repo
        for raiz_agente in RAIZES_AGENTES:
            diretorio = repo / raiz_agente
            diretorio.mkdir()
            (diretorio / "nota.md").write_text("conteudo")
        (repo / "gerado.txt").write_text("artefato de controle")

        resultado = executar_auditoria(str(repo), CONFIG_ARTEFATOS)

        caminhos = {r["caminho"] for r in _regras(resultado, "untracked_artifacts")}
        assert "gerado.txt" in caminhos
        assert not any(caminho.startswith(RAIZES_AGENTES) for caminho in caminhos)

    def test_comandos_e_skills_openspec_escapam_de_referencias(self, git_repo):
        repo = git_repo
        ignorados = [
            *(
                f"{raiz_agente}/commands/comando.md"
                for raiz_agente in RAIZES_AGENTES
            ),
            *(
                f"{raiz_agente}/skills/openspec-fluxo/SKILL.md"
                for raiz_agente in RAIZES_AGENTES
            ),
            ".kilocode/workflows/fluxo.md",
        ]
        enforcement = [
            ".opencode/skills/agent-hygiene-flow/SKILL.md",
            ".omp/skills/agent-hygiene-flow/SKILL.md",
        ]
        for caminho_rel in ignorados + enforcement:
            destino = repo / caminho_rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text('carregar("arquivo-inexistente.md")\n')
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)

        resultado = executar_auditoria(str(repo), CONFIG_REFERENCIAS)

        caminhos = {r["caminho"] for r in _regras(resultado, "missing_references")}
        assert set(enforcement).issubset(caminhos)
        assert not (set(ignorados) & caminhos)


class TestGatilhosWorkflow:
    def _paths_dos_gatilhos(self):
        with open(WORKFLOW_TEMPLATE, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)
        gatilhos = workflow.get("on", workflow.get(True))
        return gatilhos["push"]["paths"], gatilhos["pull_request"]["paths"]

    def test_toda_raiz_de_agente_esta_nos_dois_gatilhos(self):
        push_paths, pull_request_paths = self._paths_dos_gatilhos()

        for raiz_agente in RAIZES_AGENTES:
            esperado = f"{raiz_agente}/**"
            assert esperado in push_paths, f"{esperado} ausente em push.paths"
            assert esperado in pull_request_paths, (
                f"{esperado} ausente em pull_request.paths"
            )
