"""Testes para o provisionamento da skill OpenCode pelo install."""

import os
import subprocess
import sys

CLONE_SKILL_REL = os.path.join(".opencode", "skills", "agent-hygiene-flow")
CLONE_SKILL_FILE = os.path.join(CLONE_SKILL_REL, "SKILL.md")


def _run_cli(*args, cwd, timeout=10):
    return subprocess.run(
        [sys.executable, "-m", "auditoria_higiene.cli", *args, str(cwd)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _expected_skill_bytes():
    from importlib.resources import files

    recurso = (
        files("auditoria_higiene.templates")
        .joinpath("skills")
        .joinpath("agent-hygiene-flow")
        .joinpath("SKILL.md")
    )
    return recurso.read_bytes()


class TestInstallSkill:
    def test_install_provisiona_skill(self, tmp_path):
        result = _run_cli("install", cwd=tmp_path)

        assert result.returncode == 0
        arquivo = tmp_path / CLONE_SKILL_FILE
        assert arquivo.exists()
        assert arquivo.read_bytes() == _expected_skill_bytes()

    def test_install_reinstall_preserva_skill_existente(self, tmp_path):
        primeiro = _run_cli("install", cwd=tmp_path)
        assert primeiro.returncode == 0

        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("conteudo local do usuario")

        segundo = _run_cli("install", cwd=tmp_path)
        assert segundo.returncode == 0
        assert destino.read_text() == "conteudo local do usuario"
        assert "Skipping" in segundo.stdout

    def test_install_force_sobrescreve_skill(self, tmp_path):
        _run_cli("install", cwd=tmp_path)
        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("conteudo local do usuario")

        result = _run_cli("install", "--force", cwd=tmp_path)
        assert result.returncode == 0
        assert destino.read_bytes() == _expected_skill_bytes()

    def test_install_dry_run_nao_escreve_skill(self, tmp_path):
        result = _run_cli("install", "--dry-run", cwd=tmp_path)

        assert result.returncode == 0
        assert not (tmp_path / CLONE_SKILL_FILE).exists()
        assert not (tmp_path / CLONE_SKILL_REL).exists()
        assert ".opencode/skills/agent-hygiene-flow" in result.stdout

    def test_install_skill_subcommand_idempotente(self, tmp_path):
        primeiro = _run_cli("install", cwd=tmp_path)
        assert primeiro.returncode == 0

        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("alterado")

        segundo = _run_cli("install", cwd=tmp_path)
        assert segundo.returncode == 0
        assert destino.read_text() == "alterado"

    def test_install_skill_diretorio_inexistente_exit_2(self, tmp_path):
        inexistente = tmp_path / "nao-existe"
        result = _run_cli("install", cwd=inexistente)

        assert result.returncode == 2
        assert "nao-existe" in result.stderr or "não encontrado" in result.stderr


class TestInstallSkillBundle:
    def test_skill_bundle_alcanca_via_importlib(self):
        from importlib.resources import files

        raiz = files("auditoria_higiene.templates").joinpath("skills")
        assert raiz.is_dir()
        skill = raiz.joinpath("agent-hygiene-flow")
        assert skill.is_dir()
        assert skill.joinpath("SKILL.md").is_file()

    def test_skill_bundle_tem_frontmatter_yaml(self):
        from importlib.resources import files

        conteudo = (
            files("auditoria_higiene.templates")
            .joinpath("skills")
            .joinpath("agent-hygiene-flow")
            .joinpath("SKILL.md")
            .read_text()
        )
        assert conteudo.startswith("---")
        assert "name: agent-hygiene-flow" in conteudo
