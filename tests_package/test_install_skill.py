"""Testes para o provisionamento da skill pelos subcomandos install e install-skill."""

import os
import subprocess
import sys

import pytest

CLONE_SKILL_REL = os.path.join(".opencode", "skills", "agent-hygiene-flow")
CLONE_SKILL_FILE = os.path.join(CLONE_SKILL_REL, "SKILL.md")
SUBCOMANDOS = ("install", "install-skill")


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


@pytest.mark.parametrize("subcomando", SUBCOMANDOS)
class TestInstallSkill:
    def test_install_provisiona_skill(self, tmp_path, subcomando):
        result = _run_cli(subcomando, cwd=tmp_path)

        assert result.returncode == 0
        arquivo = tmp_path / CLONE_SKILL_FILE
        assert arquivo.exists()
        assert arquivo.read_bytes() == _expected_skill_bytes()

    def test_install_reinstall_preserva_skill_existente(self, tmp_path, subcomando):
        primeiro = _run_cli(subcomando, cwd=tmp_path)
        assert primeiro.returncode == 0

        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("conteudo local do usuario")

        segundo = _run_cli(subcomando, cwd=tmp_path)
        assert segundo.returncode == 0
        assert destino.read_text() == "conteudo local do usuario"
        assert "Skipping" in segundo.stdout

    def test_install_force_sobrescreve_skill(self, tmp_path, subcomando):
        _run_cli(subcomando, cwd=tmp_path)
        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("conteudo local do usuario")

        result = _run_cli(subcomando, "--force", cwd=tmp_path)
        assert result.returncode == 0
        assert destino.read_bytes() == _expected_skill_bytes()

    def test_install_dry_run_nao_escreve_skill(self, tmp_path, subcomando):
        result = _run_cli(subcomando, "--dry-run", cwd=tmp_path)

        assert result.returncode == 0
        assert not (tmp_path / CLONE_SKILL_FILE).exists()
        assert not (tmp_path / CLONE_SKILL_REL).exists()
        assert ".opencode/skills/agent-hygiene-flow" in result.stdout

    def test_install_skill_subcommand_idempotente(self, tmp_path, subcomando):
        primeiro = _run_cli(subcomando, cwd=tmp_path)
        assert primeiro.returncode == 0

        destino = tmp_path / CLONE_SKILL_FILE
        destino.write_text("alterado")

        segundo = _run_cli(subcomando, cwd=tmp_path)
        assert segundo.returncode == 0
        assert destino.read_text() == "alterado"

    def test_install_skill_diretorio_inexistente_exit_2(self, tmp_path, subcomando):
        inexistente = tmp_path / "nao-existe"
        result = _run_cli(subcomando, cwd=inexistente)

        assert result.returncode == 2
        assert "nao-existe" in result.stderr or "não encontrado" in result.stderr

    def test_agents_invalido_exit_2_sem_escrever_nada(self, tmp_path, subcomando):
        (tmp_path / ".omp").mkdir()

        result = _run_cli(subcomando, "--agents", "nao-existe", cwd=tmp_path)

        assert result.returncode == 2
        assert "unsupported agent" in result.stderr
        assert not (tmp_path / "auditoria.yaml").exists()
        assert not (tmp_path / ".github").exists()
        assert not (tmp_path / ".omp" / "skills").exists()


class TestInstallSkillEscopo:
    def test_install_skill_nao_gera_config_nem_workflow(self, tmp_path):
        result = _run_cli("install-skill", cwd=tmp_path)

        assert result.returncode == 0
        assert (tmp_path / CLONE_SKILL_FILE).exists()
        assert not (tmp_path / "auditoria.yaml").exists()
        assert not (tmp_path / ".github").exists()

    def test_install_gera_config_e_workflow(self, tmp_path):
        result = _run_cli("install", cwd=tmp_path)

        assert result.returncode == 0
        assert (tmp_path / CLONE_SKILL_FILE).exists()
        assert (tmp_path / "auditoria.yaml").exists()
        assert (tmp_path / ".github" / "workflows" / "repository-hygiene.yml").exists()


class TestDestinoSymlinkExterno:
    def _repo_com_symlink_externo(self, tmp_path):
        externo = tmp_path / "externa"
        externo.mkdir()
        raiz = tmp_path / "repo"
        raiz.mkdir()
        (raiz / ".omp").symlink_to(externo, target_is_directory=True)
        return raiz, externo

    @pytest.mark.parametrize("subcomando", SUBCOMANDOS)
    def test_destino_invalido_exit_2_sem_escrever_nada(self, tmp_path, subcomando):
        raiz, externo = self._repo_com_symlink_externo(tmp_path)

        result = _run_cli(subcomando, cwd=raiz)

        assert result.returncode == 2
        assert "Error: invalid skill destination" in result.stderr
        assert not (raiz / "auditoria.yaml").exists()
        assert not (raiz / ".github").exists()
        assert not (raiz / CLONE_SKILL_REL).exists()
        assert not (externo / "skills").exists()

    @pytest.mark.parametrize("subcomando", SUBCOMANDOS)
    def test_dry_run_reflete_o_mesmo_veredito(self, tmp_path, subcomando):
        raiz, externo = self._repo_com_symlink_externo(tmp_path)

        result = _run_cli(subcomando, "--dry-run", cwd=raiz)

        assert result.returncode == 2
        assert "Error: invalid skill destination" in result.stderr
        assert not (raiz / "auditoria.yaml").exists()
        assert not (raiz / ".github").exists()
        assert not (externo / "skills").exists()

    def test_symlink_apontando_para_dentro_do_repositorio_e_permitido(
        self, tmp_path
    ):
        raiz = tmp_path / "repo"
        alvo = raiz / "vendor" / "omp"
        alvo.mkdir(parents=True)
        (raiz / ".omp").symlink_to(alvo, target_is_directory=True)

        result = _run_cli("install", cwd=raiz)

        assert result.returncode == 0
        assert (
            alvo / "skills" / "agent-hygiene-flow" / "SKILL.md"
        ).read_bytes() == _expected_skill_bytes()


class TestInstallMultiDestino:
    def _skill(self, tmp_path, raiz_agente):
        return tmp_path / raiz_agente / "skills" / "agent-hygiene-flow" / "SKILL.md"

    def test_install_provisiona_em_todas_as_raizes_presentes(self, tmp_path):
        (tmp_path / ".omp").mkdir()
        (tmp_path / ".hermes").mkdir()

        result = _run_cli("install", cwd=tmp_path)

        assert result.returncode == 0
        assert self._skill(tmp_path, ".omp").read_bytes() == _expected_skill_bytes()
        assert (
            self._skill(tmp_path, ".hermes").read_bytes() == _expected_skill_bytes()
        )
        assert not self._skill(tmp_path, ".opencode").exists()

    def test_install_agents_restringe_destinos(self, tmp_path):
        for raiz_agente in (".opencode", ".kilocode", ".kilo", ".omp", ".hermes"):
            (tmp_path / raiz_agente).mkdir()

        result = _run_cli("install", "--agents", "opencode,kilo", cwd=tmp_path)

        assert result.returncode == 0
        assert (
            self._skill(tmp_path, ".opencode").read_bytes()
            == _expected_skill_bytes()
        )
        assert self._skill(tmp_path, ".kilo").read_bytes() == _expected_skill_bytes()
        for ausente in (".kilocode", ".omp", ".hermes"):
            assert not self._skill(tmp_path, ausente).exists()

    def test_install_destinos_sao_pulados_independentemente(self, tmp_path):
        (tmp_path / ".omp").mkdir()
        (tmp_path / ".opencode").mkdir()
        pre_existente = self._skill(tmp_path, ".opencode")
        pre_existente.parent.mkdir(parents=True)
        pre_existente.write_text("conteudo local do usuario")

        result = _run_cli("install", cwd=tmp_path)

        assert result.returncode == 0
        assert pre_existente.read_text() == "conteudo local do usuario"
        assert "Skipping" in result.stdout
        assert self._skill(tmp_path, ".omp").read_bytes() == _expected_skill_bytes()

    def test_install_force_sobrescreve_em_todos_os_destinos(self, tmp_path):
        (tmp_path / ".opencode").mkdir()
        (tmp_path / ".omp").mkdir()
        primeiro = _run_cli("install", cwd=tmp_path)
        assert primeiro.returncode == 0

        for raiz_agente in (".opencode", ".omp"):
            destino = self._skill(tmp_path, raiz_agente)
            destino.write_text("conteudo local do usuario")

        result = _run_cli("install", "--force", cwd=tmp_path)

        assert result.returncode == 0
        for raiz_agente in (".opencode", ".omp"):
            destino = self._skill(tmp_path, raiz_agente)
            assert destino.read_bytes() == _expected_skill_bytes()

    def test_install_dry_run_lista_todos_os_destinos(self, tmp_path):
        (tmp_path / ".omp").mkdir()
        (tmp_path / ".hermes").mkdir()

        result = _run_cli("install", "--dry-run", cwd=tmp_path)

        assert result.returncode == 0
        assert ".opencode/skills/agent-hygiene-flow" not in result.stdout
        assert ".omp/skills/agent-hygiene-flow" in result.stdout
        assert ".hermes/skills/agent-hygiene-flow" in result.stdout
        assert not self._skill(tmp_path, ".omp").exists()
        assert not self._skill(tmp_path, ".hermes").exists()

    def test_install_skill_subcommand_provisiona_selecao_explicita(self, tmp_path):
        (tmp_path / ".omp").mkdir()

        result = _run_cli("install-skill", "--agents", "omp", cwd=tmp_path)

        assert result.returncode == 0
        assert self._skill(tmp_path, ".omp").read_bytes() == _expected_skill_bytes()
        assert not self._skill(tmp_path, ".opencode").exists()

    def test_install_agents_desconhecido_exit_2(self, tmp_path):
        (tmp_path / ".omp").mkdir()

        result = _run_cli("install", "--agents", "nao-existe", cwd=tmp_path)

        assert result.returncode == 2
        assert "unsupported agent" in result.stderr
        assert not self._skill(tmp_path, ".omp").exists()


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
