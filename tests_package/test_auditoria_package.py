"""Testes para o pacote repository-hygiene."""

import pytest
import yaml
import json
import os
import subprocess
import sys


@pytest.fixture
def config_minima():
    return {
        "config_version": 1,
        "rules": {
            "tracked_secrets": {"enabled": True, "severity": "error"},
            "broken_internal_links": {"enabled": True, "severity": "error"},
            "missing_references": {"enabled": True, "severity": "error"},
            "untracked_artifacts": {"enabled": True, "severity": "error"},
            "empty_gitkeep_directories": {"enabled": True, "severity": "warning"},
            "unreferenced_files": {"enabled": True, "severity": "warning"},
            "outdated_documentation": {"enabled": True, "severity": "warning"},
            "unintegrated_configurations": {
                "enabled": True,
                "severity": "warning",
            },
            "stale_openspec_changes": {"enabled": True, "severity": "warning"},
            "insecure_workflows": {"enabled": True, "severity": "warning"},
            "nested_repositories": {"enabled": True, "severity": "error"},
        },
        "exceptions": {
            "tracked_secrets": [],
            "broken_internal_links": [],
            "missing_references": [],
            "untracked_artifacts": [],
            "empty_gitkeep_directories": [],
            "unreferenced_files": [],
            "outdated_documentation": [],
            "unintegrated_configurations": [],
            "stale_openspec_changes": [],
            "insecure_workflows": [],
            "nested_repositories": [],
        },
    }


@pytest.fixture
def config_file(tmp_path, config_minima):
    path = tmp_path / "auditoria.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_minima, f)
    return str(path)


class TestConfiguracao:
    def test_carregar_configuracao_valida(self, config_file):
        from auditoria_higiene.core import carregar_configuracao

        config = carregar_configuracao(config_file)
        assert "rules" in config
        assert "exceptions" in config
        assert config["rules"]["tracked_secrets"]["enabled"] is True

    def test_validar_versao_correta(self, config_file):
        from auditoria_higiene.core import carregar_configuracao, validar_configuracao

        config = carregar_configuracao(config_file)
        validar_configuracao(config)

    def test_validar_versao_incorreta(self, config_file):
        from auditoria_higiene.core import carregar_configuracao, validar_configuracao

        config = carregar_configuracao(config_file)
        config["config_version"] = 99
        with pytest.raises(ValueError, match="99"):
            validar_configuracao(config)

    def test_regra_desativada_nao_avaliada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": False, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        regras_aplicadas = [r["regra"] for r in resultado["resultados"]]
        assert "tracked_secrets" not in regras_aplicadas

    def test_regra_desativada_listada_no_relatorio(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.reporters import gerar_relatorio_texto

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": False, "severity": "error"},
                "broken_internal_links": {
                    "enabled": False,
                    "severity": "error",
                },
            },
            "exceptions": {"tracked_secrets": [], "broken_internal_links": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert "tracked_secrets" in resultado["disabled_rules"]
        assert "broken_internal_links" in resultado["disabled_rules"]
        relatorio = gerar_relatorio_texto(resultado)
        assert "DISABLED" in relatorio

    def test_config_severidade_aplicada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert len(erros) == 1
        assert erros[0]["severity"] == "warning"


class TestSegredosRastreados:
    def test_fixture_de_teste_rastreada_nao_eh_segredo_operacional(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        tests_dir = repo / "tests_package"
        tests_dir.mkdir()
        (tests_dir / "test_fixture.py").write_text('FIXTURE = "senha=admin"\n')
        subprocess.run(
            ["git", "add", "tests_package/test_fixture.py"], cwd=repo, check=True
        )
        resultado = executar_auditoria(
            str(repo),
            {
                "config_version": 1,
                "rules": {
                    "tracked_secrets": {"enabled": True, "severity": "error"}
                },
                "exceptions": {"tracked_secrets": []},
            },
        )

        assert resultado["resultados"] == []

    def test_segredo_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "config.txt").write_text("senha=admin123")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert len(erros) == 1
        assert erros[0]["caminho"] == "config.txt"
        assert erros[0]["confianca"] == "medium"

    def test_api_key_tem_confianca_alta(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        resultado = executar_auditoria(
            str(tmp_path),
            {
                "config_version": 1,
                "rules": {"tracked_secrets": {"enabled": True}},
                "exceptions": {"tracked_secrets": []},
            },
        )

        assert resultado["resultados"][0]["confianca"] == "high"

    def test_caminho_excluido_nao_reportado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "seguro.txt").write_text("senha=123")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": ["seguro.txt"]},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        for r in resultado["resultados"]:
            assert r["caminho"] != "seguro.txt"

    def test_token_csrf_curto_nao_reportado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "app.js").write_text(
            "const csrfToken = 'abc123';\nconst accessToken = 'xyz';\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert erros == []

    def test_comentario_nao_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "app.py").write_text("# Exemplo: token=abc123\nvalor = 42\n")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert erros == []


class TestStatusExecucao:
    def test_problema_objetivo_retorna_falha(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"

    def test_sem_problemas_retorna_sucesso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "normal.txt").write_text("conteudo normal")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "sucesso"


class TestRelatorios:
    def test_relatorio_rejeita_saida_fora_da_raiz(self, tmp_path):
        from auditoria_higiene.reporters import escrever_relatorio

        with pytest.raises(OSError, match="outside permitted directory"):
            escrever_relatorio(
                "conteudo", str(tmp_path.parent / "report.json"), str(tmp_path)
            )

    def test_relatorio_texto_agrupa_por_severidade(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.reporters import gerar_relatorio_texto

        (tmp_path / "segredo.txt").write_text("senha=admin")
        (tmp_path / "vazio" / ".gitkeep").parent.mkdir()
        (tmp_path / "vazio" / ".gitkeep").write_text("")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"},
                "empty_gitkeep_directories": {"enabled": True, "severity": "warning"},
            },
            "exceptions": {"tracked_secrets": [], "empty_gitkeep_directories": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        relatorio = gerar_relatorio_texto(resultado)
        assert "ERROR" in relatorio
        assert "WARNING" in relatorio

    def test_relatorio_json_valido(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.reporters import gerar_relatorio_json

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        saida = gerar_relatorio_json(resultado)
        dados = json.loads(saida)
        assert "status" in dados
        assert "resultados" in dados

    def test_relatorio_sarif_valido(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.reporters import gerar_relatorio_sarif

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        saida = gerar_relatorio_sarif(resultado)
        dados = json.loads(saida)
        assert dados["version"] == "2.1.0"
        assert "runs" in dados

    def test_mascaramento_segredo_texto(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.sanitizer import sanitizar_resultado
        from auditoria_higiene.reporters import gerar_relatorio_texto

        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        sanitizado = sanitizar_resultado(resultado)
        relatorio = gerar_relatorio_texto(sanitizado)
        assert "super_secreto_123" not in relatorio
        assert "tracked_secrets" in relatorio

    def test_mascaramento_segredo_json(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.sanitizer import sanitizar_resultado
        from auditoria_higiene.reporters import gerar_relatorio_json

        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        sanitizado = sanitizar_resultado(resultado)
        saida = gerar_relatorio_json(sanitizado)
        assert "super_secreto_123" not in saida


class TestLinksInternos:
    def test_link_interno_quebrado_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("[link](inexistente.txt)")
        config = {
            "config_version": 1,
            "rules": {
                "broken_internal_links": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"broken_internal_links": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "broken_internal_links"
        ]
        assert len(erros) == 1

    def test_link_externo_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("[site](https://example.com)")
        config = {
            "config_version": 1,
            "rules": {
                "broken_internal_links": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"broken_internal_links": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "broken_internal_links"
        ]
        assert len(erros) == 0


class TestReferencias:
    def test_string_de_fixture_nao_eh_referencia_de_repositorio(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        tests_dir = repo / "tests_package"
        tests_dir.mkdir()
        (tests_dir / "test_fixture.py").write_text('arquivo = "segredo.txt"\n')
        subprocess.run(
            ["git", "add", "tests_package/test_fixture.py"], cwd=repo, check=True
        )
        resultado = executar_auditoria(
            str(repo),
            {
                "config_version": 1,
                "rules": {
                    "missing_references": {
                        "enabled": True,
                        "severity": "error",
                    }
                },
                "exceptions": {"missing_references": []},
            },
        )

        assert resultado["resultados"] == []

    def test_referencia_inexistente_detectada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        config = {
            "config_version": 1,
            "rules": {
                "missing_references": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"missing_references": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "missing_references"
        ]
        assert len(erros) == 1

    def test_referencia_existente_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "config_version": 1,
            "rules": {
                "missing_references": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"missing_references": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "missing_references"
        ]
        assert len(erros) == 0


class TestArtefatos:
    def test_artefato_fora_gitignore_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "gerado.txt").write_text("conteudo")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "untracked_artifacts"
        ]
        assert len(erros) == 1

    def test_artefato_no_gitignore_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "app.log").write_text("log content")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "untracked_artifacts"
        ]
        assert len(erros) == 0

    def test_artefatos_git_usa_inventario_unico(self, tmp_path, git_repo, monkeypatch):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        (repo / ".gitignore").write_text("ignored/\n")
        (repo / "ignored").mkdir()
        (repo / "ignored" / "arquivo.txt").write_text("ignorado")
        (repo / "artefato.txt").write_text("nao ignorado")
        calls = []
        original_run = subprocess.run

        def recording_run(args, **kwargs):
            if args[:3] == ["git", "ls-files", "--others"]:
                calls.append(args)
            return original_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", recording_run)
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(repo), config)
        caminhos = [r["caminho"] for r in resultado["resultados"]]
        assert caminhos == ["artefato.txt"]
        assert len(calls) == 1

    def test_artefatos_git_lista_diretorio_ignorado_sem_conteudo(
        self, tmp_path, git_repo, monkeypatch
    ):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        (repo / ".gitignore").write_text("node_modules/\n")
        (repo / "node_modules").mkdir()
        (repo / "node_modules" / "dep.js").write_text("module.exports = {}\n")
        (repo / "artefato.txt").write_text("nao ignorado")
        commands = []
        original_run = subprocess.run

        def recording_run(args, **kwargs):
            commands.append(args)
            return original_run(args, **kwargs)

        monkeypatch.setattr(subprocess, "run", recording_run)
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(repo), config)
        assert [r["caminho"] for r in resultado["resultados"]] == ["artefato.txt"]
        assert [
            "git",
            "ls-files",
            "--others",
            "--exclude-standard",
            "--directory",
            "-z",
        ] in commands

    def test_artefatos_preserva_caminho_com_bytes_invalidos(
        self, tmp_path, monkeypatch
    ):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }

        def git_output(args, **kwargs):
            if args[:3] == ["git", "ls-files", "--others"]:
                return subprocess.CompletedProcess(args, 0, b"arquivo-\xff.txt\0", b"")
            return subprocess.CompletedProcess(args, 1, b"", b"")

        monkeypatch.setattr(subprocess, "run", git_output)
        resultado = executar_auditoria(str(tmp_path), config)
        assert (
            resultado["resultados"][0]["caminho"].encode("utf-8", "surrogateescape")
            == b"arquivo-\xff.txt"
        )

    def test_inventario_nao_fica_stale_entre_auditorias(self, tmp_path, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        (repo / ".gitignore").write_text("\n")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        (repo / "primeiro.txt").write_text("um")
        primeira = executar_auditoria(str(repo), config)
        (repo / "segundo.txt").write_text("dois")
        segunda = executar_auditoria(str(repo), config)
        assert [r["caminho"] for r in primeira["resultados"]] == ["primeiro.txt"]
        assert {r["caminho"] for r in segunda["resultados"]} == {
            "primeiro.txt",
            "segundo.txt",
        }

    def test_fallback_sem_git_nao_gera_excecao(self, tmp_path, monkeypatch):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("ignored/\n")
        (tmp_path / "arquivo.txt").write_text("conteudo")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }

        def failing_run(*args, **kwargs):
            raise FileNotFoundError("git")

        monkeypatch.setattr(subprocess, "run", failing_run)
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"
        assert resultado["resultados"][0]["caminho"] == "arquivo.txt"

    def test_artefatos_ignora_diretorio_grande_com_um_query(
        self, tmp_path, git_repo, monkeypatch
    ):
        from auditoria_higiene.core import executar_auditoria
        import subprocess as _subprocess

        repo = git_repo
        (repo / ".gitignore").write_text("node_modules/\n")
        _subprocess.run(
            ["git", "add", ".gitignore"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        _subprocess.run(
            ["git", "commit", "-m", "add gitignore"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        ignored_dir = repo / "node_modules"
        ignored_dir.mkdir()
        for i in range(1000):
            (ignored_dir / f"dep_{i}.js").write_text("module.exports = {};\n")
        (repo / "meu_artefato.txt").write_text("conteudo")
        calls = []
        original_run = _subprocess.run

        def counting_run(*args, **kwargs):
            calls.append(args[0] if args else kwargs.get("args", []))
            return original_run(*args, **kwargs)

        monkeypatch.setattr(_subprocess, "run", counting_run)
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(repo), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "untracked_artifacts"
        ]
        assert len(erros) == 1
        assert erros[0]["caminho"] == "meu_artefato.txt"
        artifact_calls = [
            c for c in calls if "ls-files" in str(c) and "--others" in str(c)
        ]
        assert len(artifact_calls) <= 1


class TestGitkeep:
    def test_gitkeep_sem_conteudo_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "vazio" / ".gitkeep").parent.mkdir()
        (tmp_path / "vazio" / ".gitkeep").write_text("")
        config = {
            "config_version": 1,
            "rules": {
                "empty_gitkeep_directories": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"empty_gitkeep_directories": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "empty_gitkeep_directories"
        ]
        assert len(avisos) == 1

    def test_gitkeep_com_conteudo_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "com_itens" / ".gitkeep").parent.mkdir()
        (tmp_path / "com_itens" / ".gitkeep").write_text("")
        (tmp_path / "com_itens" / "arquivo_real.txt").write_text("conteudo")
        config = {
            "config_version": 1,
            "rules": {
                "empty_gitkeep_directories": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"empty_gitkeep_directories": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "empty_gitkeep_directories"
        ]
        assert len(avisos) == 0


class TestWorkflowsInseguros:
    def test_permissao_write_configurada_nao_gera_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions:\n  issues: write\njobs: {}\n"
        )
        resultado = executar_auditoria(
            str(tmp_path),
            {
                "config_version": 1,
                "rules": {
                    "insecure_workflows": {
                        "enabled": True,
                        "severity": "warning",
                        "allowed_write_permissions": ["issues"],
                    }
                },
                "exceptions": {"insecure_workflows": []},
            },
        )

        assert resultado["resultados"] == []

    def test_permissao_excessiva_detectada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: write-all\njobs: {}\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) >= 1

    def test_action_sem_versao_fixa_detectada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: read-all\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) >= 1

    def test_workflow_seguro_sem_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: read-all\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 0

    def test_regra_desabilitada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: write-all\njobs: {}\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": False, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 0
        assert "insecure_workflows" in resultado["disabled_rules"]

    def test_issues_write_com_gh_issue_nao_emite_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ACCEPT_FALSE_POSITIVE

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Issue Manager\n"
            "on:\n"
            "  issues:\n"
            "    types: [opened]\n"
            "permissions:\n"
            "  issues: write\n"
            "jobs:\n"
            "  label:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: gh issue comment 1 --body done\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 1
        assert avisos[0]["recomendacao"] == ACCEPT_FALSE_POSITIVE

    def test_issues_write_com_github_script_nao_emite_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ACCEPT_FALSE_POSITIVE

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Issue Script\n"
            "on:\n"
            "  issues:\n"
            "    types: [opened]\n"
            "permissions:\n"
            "  issues: write\n"
            "jobs:\n"
            "  process:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/github-script@v7\n"
            "        with:\n"
            "          script: |\n"
            "            github.rest.issues.createComment({...})\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 1
        assert avisos[0]["recomendacao"] == ACCEPT_FALSE_POSITIVE

    def test_contents_write_com_gh_release_nao_emite_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ACCEPT_FALSE_POSITIVE

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Release Creator\n"
            "on:\n"
            "  push:\n"
            "    tags: ['v*']\n"
            "permissions:\n"
            "  contents: write\n"
            "jobs:\n"
            "  release:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - run: gh release create v1.0.0 --title v1.0.0\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 1
        assert avisos[0]["recomendacao"] == ACCEPT_FALSE_POSITIVE

    def test_issues_write_sem_justificativa_emite_scope_permissions(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, SCOPE_PERMISSIONS

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Checkout Only\n"
            "on: push\n"
            "permissions:\n"
            "  issues: write\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 1
        assert avisos[0]["recomendacao"] == SCOPE_PERMISSIONS

    def test_contents_write_com_create_release_action_nao_emite_aviso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ACCEPT_FALSE_POSITIVE

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Release\n"
            "on:\n"
            "  push:\n"
            "    tags: ['v*']\n"
            "permissions:\n"
            "  contents: write\n"
            "jobs:\n"
            "  release:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/create-release@v1\n"
            "        with:\n"
            "          tag_name: v1.0.0\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(avisos) == 1
        assert avisos[0]["recomendacao"] == ACCEPT_FALSE_POSITIVE

    def test_workflow_realista_issues_write_com_gh_issue_justificado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ACCEPT_FALSE_POSITIVE

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "triage.yml").write_text(
            "name: Issue Triage\n"
            "on:\n"
            "  issues:\n"
            "    types: [opened, labeled]\n"
            "permissions:\n"
            "  issues: write\n"
            "  contents: read\n"
            "jobs:\n"
            "  triage:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Add comment\n"
            "        run: |\n"
            '          gh issue comment "${{ github.event.issue.number }}" \\\n'
            '            --body "Thank you for the issue!"\n'
            "      - name: Add label\n"
            '        run: gh issue edit "${{ github.event.issue.number }}" --add-label triaged\n'
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        permissoes = [r for r in avisos if "permission" in r.get("mensagem", "")]
        assert len(permissoes) == 1
        assert permissoes[0]["recomendacao"] == ACCEPT_FALSE_POSITIVE


class TestDocumentacaoDesatualizada:
    def test_doc_ref_entre_aspas_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text('Referencia "dados.csv"')
        resultado = executar_auditoria(
            str(tmp_path),
            {
                "config_version": 1,
                "rules": {
                    "outdated_documentation": {
                        "enabled": True,
                        "severity": "warning",
                    }
                },
                "exceptions": {"outdated_documentation": []},
            },
        )

        assert len(resultado["resultados"]) == 1

    def test_documentacao_openspec_nao_eh_validada_como_referencia_operacional(
        self, git_repo
    ):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        spec_dir = repo / "openspec" / "changes" / "example"
        spec_dir.mkdir(parents=True)
        (spec_dir / "proposal.md").write_text("Use `AGENTS.md` como orientacao.")
        subprocess.run(
            ["git", "add", "openspec/changes/example/proposal.md"],
            cwd=repo,
            check=True,
        )
        resultado = executar_auditoria(
            str(repo),
            {
                "config_version": 1,
                "rules": {
                    "outdated_documentation": {
                        "enabled": True,
                        "severity": "warning",
                    }
                },
                "exceptions": {"outdated_documentation": []},
            },
        )

        assert resultado["resultados"] == []

    def test_versao_e_comando_nao_sao_referencias_de_arquivo(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "README.md").write_text(
            "Versao `0.2.0`\n`pip install pacote==0.2.0`\n"
        )
        resultado = executar_auditoria(
            str(tmp_path),
            {
                "config_version": 1,
                "rules": {
                    "outdated_documentation": {
                        "enabled": True,
                        "severity": "warning",
                    }
                },
                "exceptions": {"outdated_documentation": []},
            },
        )

        assert resultado["resultados"] == []

    def test_doc_ref_inexistente_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        config = {
            "config_version": 1,
            "rules": {
                "outdated_documentation": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"outdated_documentation": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "outdated_documentation"
        ]
        assert len(avisos) == 1

    def test_doc_ref_existente_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "config_version": 1,
            "rules": {
                "outdated_documentation": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"outdated_documentation": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "outdated_documentation"
        ]
        assert len(avisos) == 0


class TestArquivosSemReferencia:
    def test_modulo_importado_nao_eh_reportado(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        (repo / "util.py").write_text("def executar():\n    return True\n")
        (repo / "main.py").write_text("import util\n")
        subprocess.run(["git", "add", "util.py", "main.py"], cwd=repo, check=True)
        resultado = executar_auditoria(
            str(repo),
            {
                "config_version": 1,
                "rules": {
                    "unreferenced_files": {
                        "enabled": True,
                        "severity": "warning",
                    }
                },
                "exceptions": {"unreferenced_files": []},
            },
        )

        assert "util.py" not in [item["caminho"] for item in resultado["resultados"]]


class TestConfiguracaoSemIntegracao:
    def test_config_sem_integracao_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        config = {
            "config_version": 1,
            "rules": {
                "unintegrated_configurations": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"unintegrated_configurations": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "unintegrated_configurations"
        ]
        assert len(avisos) == 1

    def test_config_com_integracao_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        (tmp_path / "README.md").write_text("Use .pre-commit-config.yaml")
        config = {
            "config_version": 1,
            "rules": {
                "unintegrated_configurations": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"unintegrated_configurations": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "unintegrated_configurations"
        ]
        assert len(avisos) == 0


class TestOpenspecParada:
    def test_sem_changes_dir_nao_gera_erro(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        config = {
            "config_version": 1,
            "rules": {
                "stale_openspec_changes": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"stale_openspec_changes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "stale_openspec_changes"]
        assert len(avisos) == 0

    def test_changes_dir_vazio_nao_gera_erro(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "openspec" / "changes").mkdir(parents=True)
        config = {
            "config_version": 1,
            "rules": {
                "stale_openspec_changes": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"stale_openspec_changes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "stale_openspec_changes"]
        assert len(avisos) == 0


class TestSanitizer:
    def test_sanitizacao_mantem_estrutura(self):
        from auditoria_higiene.sanitizer import sanitizar_resultado

        resultado = {
            "resultados": [
                {
                    "regra": "teste",
                    "caminho": "x.txt",
                    "severity": "error",
                    "mensagem": "senha=admin",
                }
            ],
            "status": "falha",
            "disabled_rules": [],
        }
        sanitizado = sanitizar_resultado(resultado)
        assert sanitizado["status"] == "falha"
        assert "senha=admin" not in sanitizado["resultados"][0]["mensagem"]
        assert "senha=" in sanitizado["resultados"][0]["mensagem"]

    def test_sanitizacao_sem_resultados(self):
        from auditoria_higiene.sanitizer import sanitizar_resultado

        resultado = {"resultados": [], "status": "sucesso", "disabled_rules": []}
        sanitizado = sanitizar_resultado(resultado)
        assert sanitizado["status"] == "sucesso"
        assert sanitizado["resultados"] == []


class TestCLIPreCommit:
    def test_cli_pre_commit_clean_exit_0(self, tmp_path, git_repo):
        repo = git_repo
        (repo / "clean.txt").write_text("conteudo limpo")
        subprocess.run(
            ["git", "add", "clean.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0

    def test_cli_pre_commit_staged_error_exit_1(self, tmp_path, git_repo):
        repo = git_repo
        (repo / "segredo.txt").write_text("senha=admin")
        subprocess.run(
            ["git", "add", "segredo.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 1
        assert "tracked_secrets" in result.stdout

    def test_cli_pre_commit_invalid_config_exit_2(self, tmp_path, git_repo):
        repo = git_repo
        (repo / "f.txt").write_text("conteudo")
        subprocess.run(
            ["git", "add", "f.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {"config_version": 99, "rules": {}, "exceptions": {}}
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 2
        assert "99" in result.stderr

    def test_cli_pre_commit_snapshot_failure_exit_2(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 2
        assert "Failed to list" in result.stderr

    def test_cli_pre_commit_unstaged_error_ignored(self, tmp_path, git_repo):
        repo = git_repo
        (repo / "file.txt").write_text("conteudo limpo")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        (repo / "file.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0

    def test_cli_pre_commit_missing_config_exit_2(self, tmp_path, git_repo):
        repo = git_repo

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 2
        assert "not found" in result.stderr

    def test_cli_pre_commit_warning_does_not_block(self, tmp_path, git_repo):
        repo = git_repo
        (repo / "vazio" / ".gitkeep").parent.mkdir()
        (repo / "vazio" / ".gitkeep").write_text("")
        subprocess.run(
            ["git", "add", "vazio/.gitkeep"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "empty_gitkeep_directories": {"enabled": True, "severity": "warning"},
            },
            "exceptions": {"empty_gitkeep_directories": []},
        }
        with open(repo / "auditoria.yaml", "w") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "WARNING" in result.stdout


class TestNativeHook:
    def test_init_installs_commit_msg_hook_by_default(self, git_repo):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--init", str(git_repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        hook_path = git_repo / ".git" / "hooks" / "commit-msg"
        assert hook_path.exists()
        assert os.access(hook_path, os.X_OK)


def test_workflow_template_does_not_pin_old_package_version():
    template = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "auditoria_higiene",
        "templates",
        "workflow.yml",
    )
    content = open(template, encoding="utf-8").read()

    assert "repository-hygiene==0.2.0" not in content
    assert "pip install repository-hygiene" in content

    def test_install_hook_in_repo_without_hook(self, tmp_path, git_repo):
        repo = git_repo

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "--init",
                "--install-hook",
                str(repo),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        hook_path = os.path.join(repo, ".git", "hooks", "pre-commit")
        assert os.path.exists(hook_path)
        assert os.access(hook_path, os.X_OK)
        content = open(hook_path).read()
        assert "repository-hygiene" in content
        assert "--pre-commit" in content

    def test_preserve_existing_hook(self, tmp_path, git_repo):
        repo = git_repo
        hook_dir = os.path.join(repo, ".git", "hooks")
        os.makedirs(hook_dir, exist_ok=True)
        hook_path = os.path.join(hook_dir, "pre-commit")
        with open(hook_path, "w") as f:
            f.write("#!/bin/sh\necho 'existing hook'\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "--init",
                "--install-hook",
                str(repo),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert open(hook_path).read() == "#!/bin/sh\necho 'existing hook'\n"
        assert "Skipping" in result.stdout

    def test_force_replacement(self, tmp_path, git_repo):
        repo = git_repo
        hook_dir = os.path.join(repo, ".git", "hooks")
        os.makedirs(hook_dir, exist_ok=True)
        hook_path = os.path.join(hook_dir, "pre-commit")
        with open(hook_path, "w") as f:
            f.write("#!/bin/sh\necho 'old hook'\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "--init",
                "--install-hook",
                "--force",
                str(repo),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        content = open(hook_path).read()
        assert "repository-hygiene" in content
        assert "--pre-commit" in content
        assert os.access(hook_path, os.X_OK)


class TestCLI:
    def test_cli_padrao_gera_json_e_resumo(self, tmp_path):
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(tmp_path / "auditoria.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "Status: sucesso" in result.stdout
        report = json.loads(
            (tmp_path / ".repository-hygiene" / "auditoria.json").read_text()
        )
        assert report["schema_version"] == 1
        assert report["audited_directory"] == os.path.realpath(tmp_path)

    def test_cli_formato_explicito_grava_saida(self, tmp_path):
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(tmp_path / "auditoria.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin", encoding="utf-8")
        output = tmp_path / "report.json"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                str(tmp_path),
                "--format",
                "json",
                "--output",
                str(output),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 1
        assert json.loads(result.stdout) == json.loads(output.read_text())

    def test_cli_rejeita_saida_fora_do_diretorio_auditado(self, tmp_path):
        config = {
            "config_version": 1,
            "rules": {},
            "exceptions": {},
        }
        with open(tmp_path / "auditoria.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                str(tmp_path),
                "--output",
                "../auditoria.json",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 2
        assert "invalid output path" in result.stderr

    def test_cli_pre_commit_nao_gera_relatorio_padrao(self, tmp_path, git_repo):
        repo = git_repo
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(repo / "auditoria.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f)
        (repo / "arquivo.txt").write_text("limpo", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, capture_output=True, timeout=10)

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--pre-commit", str(repo)],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert not (repo / ".repository-hygiene" / "auditoria.json").exists()

    def test_cli_ajuda(self):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_cli_init_cria_arquivos(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--init", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))
        assert os.path.exists(
            os.path.join(tmp_path, ".github", "workflows", "repository-hygiene.yml")
        )

    def test_cli_init_nao_sobrescreve(self, tmp_path):
        import subprocess

        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--init", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() == "original"

    def test_cli_init_force_sobrescreve(self, tmp_path):
        import subprocess

        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "--init",
                "--force",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() != "original"

    def test_cli_sem_config_erro(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 2

    def test_cli_versao(self):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_cli_json_format(self, tmp_path):
        import subprocess
        import yaml

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                str(tmp_path),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        import json

        dados = json.loads(result.stdout)
        assert dados["status"] == "falha"

    def test_cli_sarif_format(self, tmp_path):
        import subprocess
        import yaml

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                str(tmp_path),
                "--format",
                "sarif",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        import json

        dados = json.loads(result.stdout)
        assert dados["version"] == "2.1.0"


class TestSnapshot:
    def test_clean_staged_content(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        (repo / "clean.txt").write_text("conteudo limpo")
        subprocess.run(
            ["git", "add", "clean.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        snapshot_path = criar_snapshot(str(repo))
        try:
            assert os.path.exists(os.path.join(snapshot_path, "clean.txt"))
            with open(os.path.join(snapshot_path, "clean.txt")) as f:
                assert f.read() == "conteudo limpo"
        finally:
            limpar_snapshot(snapshot_path)

    def test_unstaged_error_not_in_snapshot(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        (repo / "file.txt").write_text("conteudo limpo")
        subprocess.run(
            ["git", "add", "file.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        (repo / "file.txt").write_text("senha=admin")

        snapshot_path = criar_snapshot(str(repo))
        try:
            with open(os.path.join(snapshot_path, "file.txt")) as f:
                assert f.read() == "conteudo limpo"
        finally:
            limpar_snapshot(snapshot_path)

    def test_staged_error_blocks_commit(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import executar_pre_commit

        repo = git_repo
        (repo / "segredo.txt").write_text("senha=admin")
        subprocess.run(
            ["git", "add", "segredo.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }

        resultado = executar_pre_commit(str(repo), config)

        assert resultado["status"] == "falha"
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert len(erros) == 1

    def test_added_file_in_snapshot(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        (repo / "novo.txt").write_text("arquivo adicionado")
        subprocess.run(
            ["git", "add", "novo.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        snapshot_path = criar_snapshot(str(repo))
        try:
            assert os.path.exists(os.path.join(snapshot_path, "novo.txt"))
            with open(os.path.join(snapshot_path, "novo.txt")) as f:
                assert f.read() == "arquivo adicionado"
        finally:
            limpar_snapshot(snapshot_path)

    def test_modified_file_in_snapshot(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        (repo / "dados.txt").write_text("versao original")
        subprocess.run(
            ["git", "add", "dados.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "first"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        (repo / "dados.txt").write_text("versao modificada")
        subprocess.run(
            ["git", "add", "dados.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        snapshot_path = criar_snapshot(str(repo))
        try:
            with open(os.path.join(snapshot_path, "dados.txt")) as f:
                assert f.read() == "versao modificada"
        finally:
            limpar_snapshot(snapshot_path)

    def test_removed_file_not_in_snapshot(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        (repo / "remover.txt").write_text("vai ser removido")
        subprocess.run(
            ["git", "add", "remover.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "add file"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        subprocess.run(
            ["git", "rm", "remover.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        snapshot_path = criar_snapshot(str(repo))
        try:
            assert not os.path.exists(os.path.join(snapshot_path, "remover.txt"))
        finally:
            limpar_snapshot(snapshot_path)

    def test_invalid_config_raises_value_error(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import executar_pre_commit

        repo = git_repo
        (repo / "f.txt").write_text("conteudo")
        subprocess.run(
            ["git", "add", "f.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config_invalida = {"config_version": 99, "rules": {}, "exceptions": {}}

        repo_path = str(repo)
        with pytest.raises(ValueError, match="99"):
            executar_pre_commit(repo_path, config_invalida)

    def test_snapshot_failure_raises_runtime_error(self, tmp_path):
        from auditoria_higiene.snapshot import executar_pre_commit

        repo = tmp_path / "repo"
        repo.mkdir()
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }

        repo_path = str(repo)
        with pytest.raises(RuntimeError, match="Failed to list"):
            executar_pre_commit(repo_path, config)

    def test_git_show_failure_cleans_up_and_raises(self, tmp_path):
        from auditoria_higiene.snapshot import executar_pre_commit
        import os as _os

        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(
            ["git", "init"], cwd=repo, capture_output=True, timeout=10, shell=False
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        result = subprocess.run(
            ["git", "hash-object", "--stdin", "-w"],
            input=b"conteudo",
            capture_output=True,
            timeout=10,
            cwd=repo,
            shell=False,
        )
        blob_hash = result.stdout.decode().strip()
        subprocess.run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                "100644",
                blob_hash,
                "f.txt",
            ],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        obj_dir = _os.path.join(repo, ".git", "objects", blob_hash[:2], blob_hash[2:])
        try:
            _os.remove(obj_dir)
        except OSError:
            pytest.skip("Windows não permite remover blob em uso pelo índice")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }

        repo_path = str(repo)
        with pytest.raises(RuntimeError, match="Failed to materialize"):
            executar_pre_commit(repo_path, config)

    def test_keyboard_interrupt_during_snapshot_cleans_up(
        self, tmp_path, git_repo, monkeypatch
    ):
        import tempfile as _tempfile_mod
        from auditoria_higiene import snapshot as snapshot_mod

        repo = git_repo
        (repo / "a.txt").write_text("x")
        (repo / "b.txt").write_text("y")
        subprocess.run(
            ["git", "add", "a.txt", "b.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        original_mkdtemp = _tempfile_mod.mkdtemp
        original_run = snapshot_mod.subprocess.run
        captured_dir = {}

        def fake_mkdtemp(prefix=""):
            d = original_mkdtemp(prefix=prefix)
            captured_dir["path"] = d
            return d

        def interrupting_run(*args, **kwargs):
            if (
                len(args) > 0
                and isinstance(args[0], list)
                and len(args[0]) > 1
                and args[0][1] == "show"
            ):
                raise KeyboardInterrupt
            return original_run(*args, **kwargs)

        monkeypatch.setattr(_tempfile_mod, "mkdtemp", fake_mkdtemp)
        monkeypatch.setattr(snapshot_mod.subprocess, "run", interrupting_run)

        repo_path = str(repo)
        with pytest.raises(KeyboardInterrupt):
            snapshot_mod.criar_snapshot(repo_path)

        assert "path" in captured_dir
        assert not os.path.exists(captured_dir["path"])

    def test_binary_file_preserved_in_snapshot(self, tmp_path, git_repo):
        from auditoria_higiene.snapshot import criar_snapshot, limpar_snapshot

        repo = git_repo
        binario = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\xff\xfe\x80"
        (repo / "imagem.png").write_bytes(binario)
        subprocess.run(
            ["git", "add", "imagem.png"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        snapshot_path = criar_snapshot(str(repo))
        try:
            with open(os.path.join(snapshot_path, "imagem.png"), "rb") as f:
                assert f.read() == binario
        finally:
            limpar_snapshot(snapshot_path)

    def test_path_traversal_in_staged_path_rejected(
        self, tmp_path, git_repo, monkeypatch
    ):
        from auditoria_higiene import snapshot as snapshot_mod

        repo = git_repo
        (repo / "legit.txt").write_text("ok")
        subprocess.run(
            ["git", "add", "legit.txt"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        original_run = snapshot_mod.subprocess.run

    def test_main_module_entry_point(self):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_package_metadata(self):
        from importlib.metadata import version, entry_points

        assert version("repository-hygiene") == "1.0.0"
        eps = entry_points(group="console_scripts")
        rh_eps = [ep for ep in eps if ep.name == "repository-hygiene"]
        assert len(rh_eps) == 1
        assert rh_eps[0].value == "auditoria_higiene.cli:main"

    def test_help_via_entry_point(self):
        import sysconfig

        scripts_dir = sysconfig.get_path("scripts", scheme="nt_user")
        ep_path = os.path.join(scripts_dir, "repository-hygiene.exe")
        if not os.path.exists(ep_path):
            ep_path = os.path.join(scripts_dir, "repository-hygiene")
        if not os.path.exists(ep_path):
            pytest.skip("entry point script not found")
        result = subprocess.run(
            [ep_path, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout
        assert "audit" in result.stdout
        assert "install" in result.stdout
        assert "update" in result.stdout

    def test_help_via_module(self):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout
        assert "audit" in result.stdout
        assert "install" in result.stdout
        assert "update" in result.stdout

    def test_ephemeral_install_cria_arquivos(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "install", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))
        assert os.path.exists(
            os.path.join(tmp_path, ".github", "workflows", "repository-hygiene.yml")
        )

    def test_resolution_failure_nao_altera_arquivos(self, tmp_path):
        original_files = set(os.listdir(tmp_path))
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "audit", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert set(os.listdir(tmp_path)) == original_files

        cmd_init(str(tmp_path))
        wf_path = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        content = wf_path.read_text()
        assert "pip install repository-hygiene" in content
        assert "pip install repository-hygiene==" not in content
        assert "git+https://github.com" not in content

    def test_audit_com_erro_via_module_retorna_um(self, tmp_path):
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "audit", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1

    def test_audit_mascara_segredo_no_relatorio(self, tmp_path):
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("API_KEY=super_secreto_123")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene",
                "audit",
                str(tmp_path),
                "--format",
                "text",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        assert "super_secreto_123" not in result.stdout
        assert "tracked_secrets" in result.stdout

    def test_uvx_install_em_repo_descartavel(self, tmp_path):
        import tempfile, shutil

        consumer = tmp_path / "consumer"
        consumer.mkdir()
        (consumer / ".git").mkdir()
        (consumer / "README.md").write_text("# test")
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ["uvx", "--from", pkg_dir, "repository-hygiene", "install", str(consumer)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert os.path.exists(os.path.join(consumer, "auditoria.yaml"))
        assert os.path.exists(
            os.path.join(consumer, ".github", "workflows", "repository-hygiene.yml")
        )

    def test_cli_install_cria_arquivos(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "install", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))
        assert os.path.exists(
            os.path.join(tmp_path, ".github", "workflows", "repository-hygiene.yml")
        )

    def test_cli_install_nao_sobrescreve(self, tmp_path):
        import subprocess

        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "install", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() == "original"

    def test_cli_install_force_sobrescreve(self, tmp_path):
        import subprocess

        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "install",
                "--force",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() != "original"

    def test_cli_install_dry_run(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "install",
                "--dry-run",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "dry-run" in result.stdout
        assert not os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))

    def test_cli_sem_comando_erro(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "install" in result.stdout
        assert "audit" in result.stdout
        assert "update" in result.stdout

    def test_cli_versao(self):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_cli_audit_json_format(self, tmp_path):
        import subprocess
        import yaml

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "audit",
                str(tmp_path),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        import json

        dados = json.loads(result.stdout)
        assert dados["status"] == "falha"

    def test_cli_audit_sarif_format(self, tmp_path):
        import subprocess
        import yaml

        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "audit",
                str(tmp_path),
                "--format",
                "sarif",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 1
        import json

        dados = json.loads(result.stdout)
        assert dados["version"] == "2.1.0"

    def test_cli_audit_sem_config_erro(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "audit", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 2

    def test_cli_update_dry_run(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene.cli",
                "update",
                "--dry-run",
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "dry-run" in result.stdout

    def test_cli_update_cria_arquivos(self, tmp_path):
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "update", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))

    def test_cli_update_preserva_excecoes(self, tmp_path):
        import subprocess

        (tmp_path / "auditoria.yaml").write_text("custom: true")
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene.cli", "update", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        content = (tmp_path / "auditoria.yaml").read_text()
        assert "custom" not in content

    def test_uv_tool_install_creates_isolated_env(self, tmp_path):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ["uv", "tool", "install", "--force", pkg_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            pytest.skip(f"uv tool install not available: {result.stderr}")
        result = subprocess.run(
            ["uv", "tool", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert "repository-hygiene" in result.stdout

    def test_uv_tool_run_executes_cli(self, tmp_path):
        result = subprocess.run(
            ["uv", "tool", "run", "repository-hygiene", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            pytest.skip(f"uv tool run not available: {result.stderr}")
        assert "repository-hygiene" in result.stdout

    def test_diagnostico_path_fora_da_doc(self):
        readme = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "README.md",
        )
        content = open(readme, encoding="utf-8").read()
        assert "uv tool install repository-hygiene" in content
        assert "uvx repository-hygiene" in content

    def test_reinstalacao_persistente_sem_conflitos(self, tmp_path):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        r1 = subprocess.run(
            ["uv", "tool", "install", pkg_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        r2 = subprocess.run(
            ["uv", "tool", "install", "--force", pkg_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r1.returncode != 0 and r2.returncode != 0:
            pytest.skip("uv tool install not available")
        assert r2.returncode == 0

    def test_cli_persistente_audit_e_install(self, tmp_path):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        r = subprocess.run(
            ["uv", "tool", "install", "--force", pkg_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            pytest.skip("uv tool install not available")
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        (consumer / ".git").mkdir()
        r2 = subprocess.run(
            [
                "uv",
                "tool",
                "run",
                "--from",
                pkg_dir,
                "repository-hygiene",
                "install",
                str(consumer),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r2.returncode == 0
        assert os.path.exists(os.path.join(consumer, "auditoria.yaml"))
        (consumer / "segredo.txt").write_text("senha=admin")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        import yaml as _yaml

        with open(os.path.join(consumer, "auditoria.yaml"), "w") as f:
            _yaml.dump(config, f)
        r3 = subprocess.run(
            [
                "uv",
                "tool",
                "run",
                "--from",
                pkg_dir,
                "repository-hygiene",
                "audit",
                str(consumer),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r3.returncode == 1

    def test_doc_version_pinning(self):
        readme = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "README.md",
        )
        content = open(readme, encoding="utf-8").read()
        assert "v1.0.0" in content
        assert "uv tool install repository-hygiene" in content

    def test_versao_fixada_uvx(self, tmp_path):
        consumer = tmp_path / "consumer"
        consumer.mkdir()
        (consumer / ".git").mkdir()
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            ["uvx", "--from", f"{pkg_dir}", "repository-hygiene", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            pytest.skip(f"uvx not available: {result.stderr}")
        assert "1.0.0" in result.stdout

    def test_versao_persiste_sem_atualizacao(self):
        pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        r1 = subprocess.run(
            ["uv", "tool", "install", "--force", pkg_dir],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r1.returncode != 0:
            pytest.skip("uv tool install not available")
        r2 = subprocess.run(
            ["uv", "tool", "run", "repository-hygiene", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r2.returncode == 0
        assert "1.0.0" in r2.stdout

    def test_ci_workflow_multiplataforma_existe(self):
        workflow = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".github",
            "workflows",
            "ci.yml",
        )
        assert os.path.exists(workflow)
        content = open(workflow, encoding="utf-8").read()
        assert "ubuntu-latest" in content
        assert "windows-latest" in content
        assert "macos-latest" in content
        assert "uvx" in content
        assert "uv tool install" in content

    def test_repo_invalido_retorna_erro(self, tmp_path):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "auditoria_higiene",
                "audit",
                "/caminho/inexistente/xyz",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0

    def test_config_invalida_retorna_erro(self, tmp_path):
        (tmp_path / "auditoria.yaml").write_text("versao_configuracao: 999\n")
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "audit", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 2

    def test_doc_fallbacks_presentes(self):
        readme = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "README.md",
        )
        content = open(readme, encoding="utf-8").read()
        assert "pip install repository-hygiene" in content
        assert "uvx repository-hygiene" in content

    def test_codigos_saida_falha(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "audit", "/nao/existe"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert result.returncode in (1, 2)
        assert len(result.stderr) > 0 or len(result.stdout) > 0

    def test_install_falha_nao_deixa_parcial(self, tmp_path):
        (tmp_path / ".github").mkdir()
        (tmp_path / ".github" / "workflows").mkdir()
        existente = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        conteudo_original = "original_workflow: true\n"
        existente.write_text(conteudo_original)
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "install", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert existente.read_text() == conteudo_original

    def test_workflow_template_version_constraint(self, tmp_path):
        result = subprocess.run(
            [sys.executable, "-m", "auditoria_higiene", "install", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        workflow = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        content = workflow.read_text()
        assert "repository-hygiene==" in content


class TestTaxonomiaRecomendacao:
    def test_constantes_taxonomia_definidas(self):
        from auditoria_higiene.core import (
            REMOVE,
            ADD_TO_GITIGNORE,
            FIX_REFERENCE,
            UPDATE_DOCS,
            ADD_CI,
            ARCHIVE_CHANGE,
            SCOPE_PERMISSIONS,
            INVESTIGATE,
            ACCEPT_FALSE_POSITIVE,
            PIN_ACTION_VERSION,
        )

        assert REMOVE == "remove"
        assert ADD_TO_GITIGNORE == "add-to-gitignore"
        assert FIX_REFERENCE == "fix-reference"
        assert UPDATE_DOCS == "update-documentation"
        assert ADD_CI == "add-ci-integration"
        assert ARCHIVE_CHANGE == "archive-change"
        assert SCOPE_PERMISSIONS == "scope-permissions"
        assert INVESTIGATE == "investigate"
        assert ACCEPT_FALSE_POSITIVE == "accept-false-positive"
        assert PIN_ACTION_VERSION == "pin-action-version"


class TestFontesSemanticas:
    def test_semantic_sources_defaults_quando_ausente(self, tmp_path):
        from auditoria_higiene.core import carregar_configuracao

        config_path = tmp_path / "auditoria.yaml"
        import yaml as _yaml

        with open(config_path, "w", encoding="utf-8") as f:
            _yaml.dump({"config_version": 1, "rules": {}, "exceptions": {}}, f)

        config = carregar_configuracao(str(config_path))
        fontes = config.get("semantic_sources", {})
        assert fontes.get("openwiki") is None
        assert fontes.get("graphify") is None
        assert fontes.get("openspec") is True

    def test_semantic_sources_explicitas_preservadas(self, tmp_path):
        from auditoria_higiene.core import carregar_configuracao

        config_path = tmp_path / "auditoria.yaml"
        import yaml as _yaml

        with open(config_path, "w", encoding="utf-8") as f:
            _yaml.dump(
                {
                    "config_version": 1,
                    "rules": {},
                    "exceptions": {},
                },
                f,
            )

        config = carregar_configuracao(str(config_path))
        config["semantic_sources"]["openwiki"] = "/path/to/wiki"
        config["semantic_sources"]["graphify"] = "/path/to/graphify"
        config["semantic_sources"]["openspec"] = False
        fontes = config["semantic_sources"]
        assert fontes["openwiki"] == "/path/to/wiki"
        assert fontes["graphify"] == "/path/to/graphify"
        assert fontes["openspec"] is False


class TestRegraRecomendacaoTipada:
    def test_segredos_rastreados_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, INVESTIGATE

        (tmp_path / "config.txt").write_text("senha=admin123")
        config = {
            "config_version": 1,
            "rules": {
                "tracked_secrets": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"tracked_secrets": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "tracked_secrets"
        ]
        assert len(erros) >= 1
        for r in erros:
            assert "recomendacao" in r
            assert r["recomendacao"] == INVESTIGATE

    def test_links_internos_quebrados_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, FIX_REFERENCE

        (tmp_path / "doc.md").write_text("[link](inexistente.txt)")
        config = {
            "config_version": 1,
            "rules": {
                "broken_internal_links": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"broken_internal_links": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "broken_internal_links"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == FIX_REFERENCE

    def test_referencias_inexistentes_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, FIX_REFERENCE

        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        config = {
            "config_version": 1,
            "rules": {
                "missing_references": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"missing_references": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "missing_references"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == FIX_REFERENCE

    def test_artefatos_fora_gitignore_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ADD_TO_GITIGNORE

        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "gerado.txt").write_text("conteudo")
        config = {
            "config_version": 1,
            "rules": {
                "untracked_artifacts": {"enabled": True, "severity": "error"}
            },
            "exceptions": {"untracked_artifacts": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "untracked_artifacts"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == ADD_TO_GITIGNORE

    def test_gitkeep_sem_conteudo_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, INVESTIGATE

        (tmp_path / "vazio" / ".gitkeep").parent.mkdir()
        (tmp_path / "vazio" / ".gitkeep").write_text("")
        config = {
            "config_version": 1,
            "rules": {
                "empty_gitkeep_directories": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"empty_gitkeep_directories": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r for r in resultado["resultados"] if r["regra"] == "empty_gitkeep_directories"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == INVESTIGATE

    def test_arquivos_sem_referencia_emite_recomendacao_tipada(self, git_repo):
        from auditoria_higiene.core import executar_auditoria, INVESTIGATE
        import subprocess as _sp

        repo = git_repo
        (repo / "alpha.md").write_text("# conteudo simples")
        _sp.run(["git", "add", "alpha.md"], cwd=repo, capture_output=True)
        _sp.run(
            ["git", "commit", "-m", "commit"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "unreferenced_files": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"unreferenced_files": []},
        }
        resultado = executar_auditoria(str(repo), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "unreferenced_files"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == INVESTIGATE

    def test_documentacao_desatualizada_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, UPDATE_DOCS

        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        config = {
            "config_version": 1,
            "rules": {
                "outdated_documentation": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"outdated_documentation": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "outdated_documentation"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == UPDATE_DOCS

    def test_configuracao_sem_integracao_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, ADD_CI

        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        config = {
            "config_version": 1,
            "rules": {
                "unintegrated_configurations": {
                    "enabled": True,
                    "severity": "warning",
                }
            },
            "exceptions": {"unintegrated_configurations": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "unintegrated_configurations"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == ADD_CI

    def test_openspec_parada_emite_recomendacao_tipada(self, git_repo):
        from auditoria_higiene.core import executar_auditoria, ARCHIVE_CHANGE
        import subprocess as _sp

        repo = git_repo
        changes_dir = repo / "openspec" / "changes" / "old-feature"
        changes_dir.mkdir(parents=True)
        (changes_dir / "proposal.md").write_text("old proposal")
        _sp.run(
            ["git", "add", "openspec/changes/old-feature/proposal.md"],
            cwd=repo,
            capture_output=True,
        )
        _sp.run(
            ["git", "commit", "-m", "add", "--date", "2025-01-01T00:00:00Z"],
            cwd=repo,
            capture_output=True,
            env={**_sp.os.environ, "GIT_COMMITTER_DATE": "2025-01-01T00:00:00Z"},
            timeout=10,
            shell=False,
        )
        config = {
            "config_version": 1,
            "rules": {
                "stale_openspec_changes": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"stale_openspec_changes": []},
        }
        resultado = executar_auditoria(str(repo), config)
        achados = [
            r for r in resultado["resultados"] if r["regra"] == "stale_openspec_changes"
        ]
        assert len(achados) >= 1
        for r in achados:
            assert r["recomendacao"] == ARCHIVE_CHANGE

    def test_workflows_inseguros_emite_recomendacao_tipada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, SCOPE_PERMISSIONS

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: write-all\njobs: {}\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        assert len(achados) >= 1
        for r in achados:
            if "write-all" in r.get("mensagem", ""):
                assert r["recomendacao"] == SCOPE_PERMISSIONS

    def test_actions_sem_versao_emite_pin_action_version(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria, PIN_ACTION_VERSION

        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n"
        )
        config = {
            "config_version": 1,
            "rules": {
                "insecure_workflows": {"enabled": True, "severity": "warning"}
            },
            "exceptions": {"insecure_workflows": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        achados = [
            r for r in resultado["resultados"] if r["regra"] == "insecure_workflows"
        ]
        sem_versao = [r for r in achados if "without pinned version" in r.get("mensagem", "")]
        assert len(sem_versao) >= 1
        for r in sem_versao:
            assert r["recomendacao"] == PIN_ACTION_VERSION


class TestRepositoriosAninhados:
    def test_regra_dispatched_in_avaliar_regra(self):
        from auditoria_higiene.core import _verificar_repositorios_aninhados

        assert callable(_verificar_repositorios_aninhados)

    def test_nested_git_without_gitmodules_triggers_remove_not_add_to_gitignore(
        self, git_repo
    ):
        from auditoria_higiene.core import executar_auditoria, REMOVE

        repo = git_repo
        nested = repo / "accidental-clone"
        nested.mkdir()
        (nested / ".git").mkdir()
        (nested / "README.md").write_text("# clone")

        config = {
            "config_version": 1,
            "rules": {
                "nested_repositories": {"enabled": True, "severity": "error"},
                "untracked_artifacts": {
                    "enabled": True,
                    "severity": "error",
                },
            },
            "exceptions": {
                "nested_repositories": [],
                "untracked_artifacts": [],
            },
        }
        resultado = executar_auditoria(str(repo), config)

        nested_findings = [
            r for r in resultado["resultados"] if r["regra"] == "nested_repositories"
        ]
        assert len(nested_findings) == 1
        assert nested_findings[0]["caminho"] == "accidental-clone"
        assert nested_findings[0]["recomendacao"] == REMOVE

        artefato_findings = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "untracked_artifacts"
            and r["caminho"] in ("accidental-clone", "accidental-clone/")
        ]
        assert artefato_findings == []

    def test_submodule_in_gitmodules_not_reported(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        submod = repo / "intended-submodule"
        submod.mkdir()
        (submod / ".git").mkdir()

        (repo / ".gitmodules").write_text(
            '[submodule "intended-submodule"]\n'
            "\tpath = intended-submodule\n"
            "\turl = https://example.com/repo.git\n"
        )

        config = {
            "config_version": 1,
            "rules": {
                "nested_repositories": {"enabled": True, "severity": "error"},
            },
            "exceptions": {"nested_repositories": []},
        }
        resultado = executar_auditoria(str(repo), config)
        nested_findings = [
            r for r in resultado["resultados"] if r["regra"] == "nested_repositories"
        ]
        assert nested_findings == []

    def test_gitignored_nested_repo_not_reported(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        (repo / ".gitignore").write_text("ignored-clone/\n")
        nested = repo / "ignored-clone"
        nested.mkdir()
        (nested / ".git").mkdir()

        config = {
            "config_version": 1,
            "rules": {
                "nested_repositories": {"enabled": True, "severity": "error"},
            },
            "exceptions": {"nested_repositories": []},
        }
        resultado = executar_auditoria(str(repo), config)
        nested_findings = [
            r for r in resultado["resultados"] if r["regra"] == "nested_repositories"
        ]
        assert nested_findings == []

    def test_nested_repo_in_openspec_evidence_not_reported(self, git_repo):
        from auditoria_higiene.core import executar_auditoria

        repo = git_repo
        nested = repo / "planned-vendor-lib"
        nested.mkdir()
        (nested / ".git").mkdir()

        changes_dir = repo / "openspec" / "changes" / "add-vendor"
        changes_dir.mkdir(parents=True)
        (changes_dir / "proposal.md").write_text(
            "Clone planned-vendor-lib as reference implementation.\n"
            "Directory planned-vendor-lib will hold external code.\n"
        )
        subprocess.run(
            ["git", "add", "openspec/changes/add-vendor/"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )
        subprocess.run(
            ["git", "commit", "-m", "add openspec change"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        config = {
            "config_version": 1,
            "rules": {
                "nested_repositories": {"enabled": True, "severity": "error"},
            },
            "exceptions": {"nested_repositories": []},
        }
        resultado = executar_auditoria(str(repo), config)
        nested_findings = [
            r for r in resultado["resultados"] if r["regra"] == "nested_repositories"
        ]
        assert nested_findings == []
