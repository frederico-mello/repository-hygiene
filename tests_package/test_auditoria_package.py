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
        "versao_configuracao": 1,
        "regras": {
            "segredos_rastreados": {"habilitada": True, "severidade": "error"},
            "links_internos_quebrados": {"habilitada": True, "severidade": "error"},
            "referencias_inexistentes": {"habilitada": True, "severidade": "error"},
            "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"},
            "gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"},
            "arquivos_sem_referencia": {"habilitada": True, "severidade": "warning"},
            "documentacao_desatualizada": {"habilitada": True, "severidade": "warning"},
            "configuracao_sem_integracao": {
                "habilitada": True,
                "severidade": "warning",
            },
            "openspec_parada": {"habilitada": True, "severidade": "warning"},
            "workflows_inseguros": {"habilitada": True, "severidade": "warning"},
        },
        "excecoes": {
            "segredos_rastreados": [],
            "links_internos_quebrados": [],
            "referencias_inexistentes": [],
            "artefatos_fora_gitignore": [],
            "gitkeep_sem_conteudo": [],
            "arquivos_sem_referencia": [],
            "documentacao_desatualizada": [],
            "configuracao_sem_integracao": [],
            "openspec_parada": [],
            "workflows_inseguros": [],
        },
    }


@pytest.fixture
def config_file(tmp_path, config_minima):
    path = tmp_path / "auditoria.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config_minima, f)
    return str(path)


@pytest.fixture
def git_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(
        ["git", "init"], cwd=repo, capture_output=True, timeout=10, shell=False
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=repo,
        capture_output=True,
        timeout=10,
        shell=False,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=repo,
        capture_output=True,
        timeout=10,
        shell=False,
    )
    return repo


class TestConfiguracao:
    def test_carregar_configuracao_valida(self, config_file):
        from auditoria_higiene.core import carregar_configuracao

        config = carregar_configuracao(config_file)
        assert "regras" in config
        assert "excecoes" in config
        assert config["regras"]["segredos_rastreados"]["habilitada"] is True

    def test_validar_versao_correta(self, config_file):
        from auditoria_higiene.core import carregar_configuracao, validar_configuracao

        config = carregar_configuracao(config_file)
        validar_configuracao(config)

    def test_validar_versao_incorreta(self, config_file):
        from auditoria_higiene.core import carregar_configuracao, validar_configuracao

        config = carregar_configuracao(config_file)
        config["versao_configuracao"] = 99
        with pytest.raises(ValueError, match="99"):
            validar_configuracao(config)

    def test_regra_desativada_nao_avaliada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": False, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        regras_aplicadas = [r["regra"] for r in resultado["resultados"]]
        assert "segredos_rastreados" not in regras_aplicadas

    def test_regra_desativada_listada_no_relatorio(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.reporters import gerar_relatorio_texto

        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": False, "severidade": "error"},
                "links_internos_quebrados": {
                    "habilitada": False,
                    "severidade": "error",
                },
            },
            "excecoes": {"segredos_rastreados": [], "links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert "segredos_rastreados" in resultado["regras_desativadas"]
        assert "links_internos_quebrados" in resultado["regras_desativadas"]
        relatorio = gerar_relatorio_texto(resultado)
        assert "DESATIVADAS" in relatorio

    def test_config_severidade_aplicada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"
        ]
        assert len(erros) == 1
        assert erros[0]["severidade"] == "warning"


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
                "versao_configuracao": 1,
                "regras": {
                    "segredos_rastreados": {"habilitada": True, "severidade": "error"}
                },
                "excecoes": {"segredos_rastreados": []},
            },
        )

        assert resultado["resultados"] == []

    def test_segredo_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "config.txt").write_text("senha=admin123")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"
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
                "versao_configuracao": 1,
                "regras": {"segredos_rastreados": {"habilitada": True}},
                "excecoes": {"segredos_rastreados": []},
            },
        )

        assert resultado["resultados"][0]["confianca"] == "high"

    def test_caminho_excluido_nao_reportado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "seguro.txt").write_text("senha=123")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": ["seguro.txt"]},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"
        ]
        assert erros == []

    def test_comentario_nao_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "app.py").write_text("# Exemplo: token=abc123\nvalor = 42\n")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"
        ]
        assert erros == []


class TestStatusExecucao:
    def test_problema_objetivo_retorna_falha(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"

    def test_sem_problemas_retorna_sucesso(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "normal.txt").write_text("conteudo normal")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "sucesso"


class TestRelatorios:
    def test_relatorio_rejeita_saida_fora_da_raiz(self, tmp_path):
        from auditoria_higiene.reporters import escrever_relatorio

        with pytest.raises(OSError, match="fora do diretório permitido"):
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"},
                "gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"},
            },
            "excecoes": {"segredos_rastreados": [], "gitkeep_sem_conteudo": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        sanitizado = sanitizar_resultado(resultado)
        relatorio = gerar_relatorio_texto(sanitizado)
        assert "super_secreto_123" not in relatorio
        assert "segredos_rastreados" in relatorio

    def test_mascaramento_segredo_json(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.sanitizer import sanitizar_resultado
        from auditoria_higiene.reporters import gerar_relatorio_json

        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "links_internos_quebrados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "links_internos_quebrados"
        ]
        assert len(erros) == 1

    def test_link_externo_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("[site](https://example.com)")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "links_internos_quebrados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "links_internos_quebrados"
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
                "versao_configuracao": 1,
                "regras": {
                    "referencias_inexistentes": {
                        "habilitada": True,
                        "severidade": "error",
                    }
                },
                "excecoes": {"referencias_inexistentes": []},
            },
        )

        assert resultado["resultados"] == []

    def test_referencia_inexistente_detectada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        config = {
            "versao_configuracao": 1,
            "regras": {
                "referencias_inexistentes": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "referencias_inexistentes"
        ]
        assert len(erros) == 1

    def test_referencia_existente_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "referencias_inexistentes": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "referencias_inexistentes"
        ]
        assert len(erros) == 0


class TestArtefatos:
    def test_artefato_fora_gitignore_detectado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "gerado.txt").write_text("conteudo")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "artefatos_fora_gitignore"
        ]
        assert len(erros) == 1

    def test_artefato_no_gitignore_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "app.log").write_text("log content")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "artefatos_fora_gitignore"
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
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
            "versao_configuracao": 1,
            "regras": {
                "artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"artefatos_fora_gitignore": []},
        }
        resultado = executar_auditoria(str(repo), config)
        erros = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "artefatos_fora_gitignore"
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
            "versao_configuracao": 1,
            "regras": {
                "gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"gitkeep_sem_conteudo": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "gitkeep_sem_conteudo"
        ]
        assert len(avisos) == 1

    def test_gitkeep_com_conteudo_ignorado(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "com_itens" / ".gitkeep").parent.mkdir()
        (tmp_path / "com_itens" / ".gitkeep").write_text("")
        (tmp_path / "com_itens" / "arquivo_real.txt").write_text("conteudo")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"gitkeep_sem_conteudo": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "gitkeep_sem_conteudo"
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
                "versao_configuracao": 1,
                "regras": {
                    "workflows_inseguros": {
                        "habilitada": True,
                        "severidade": "warning",
                        "permissoes_write_permitidas": ["issues"],
                    }
                },
                "excecoes": {"workflows_inseguros": []},
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
            "versao_configuracao": 1,
            "regras": {
                "workflows_inseguros": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"
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
            "versao_configuracao": 1,
            "regras": {
                "workflows_inseguros": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"
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
            "versao_configuracao": 1,
            "regras": {
                "workflows_inseguros": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"
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
            "versao_configuracao": 1,
            "regras": {
                "workflows_inseguros": {"habilitada": False, "severidade": "warning"}
            },
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"
        ]
        assert len(avisos) == 0
        assert "workflows_inseguros" in resultado["regras_desativadas"]


class TestDocumentacaoDesatualizada:
    def test_doc_ref_entre_aspas_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text('Referencia "dados.csv"')
        resultado = executar_auditoria(
            str(tmp_path),
            {
                "versao_configuracao": 1,
                "regras": {
                    "documentacao_desatualizada": {
                        "habilitada": True,
                        "severidade": "warning",
                    }
                },
                "excecoes": {"documentacao_desatualizada": []},
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
                "versao_configuracao": 1,
                "regras": {
                    "documentacao_desatualizada": {
                        "habilitada": True,
                        "severidade": "warning",
                    }
                },
                "excecoes": {"documentacao_desatualizada": []},
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
                "versao_configuracao": 1,
                "regras": {
                    "documentacao_desatualizada": {
                        "habilitada": True,
                        "severidade": "warning",
                    }
                },
                "excecoes": {"documentacao_desatualizada": []},
            },
        )

        assert resultado["resultados"] == []

    def test_doc_ref_inexistente_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "documentacao_desatualizada": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
            "excecoes": {"documentacao_desatualizada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "documentacao_desatualizada"
        ]
        assert len(avisos) == 1

    def test_doc_ref_existente_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "documentacao_desatualizada": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
            "excecoes": {"documentacao_desatualizada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "documentacao_desatualizada"
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
                "versao_configuracao": 1,
                "regras": {
                    "arquivos_sem_referencia": {
                        "habilitada": True,
                        "severidade": "warning",
                    }
                },
                "excecoes": {"arquivos_sem_referencia": []},
            },
        )

        assert "util.py" not in [item["caminho"] for item in resultado["resultados"]]


class TestConfiguracaoSemIntegracao:
    def test_config_sem_integracao_gera_warning(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "configuracao_sem_integracao": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
            "excecoes": {"configuracao_sem_integracao": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "configuracao_sem_integracao"
        ]
        assert len(avisos) == 1

    def test_config_com_integracao_ignorada(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        (tmp_path / "README.md").write_text("Use .pre-commit-config.yaml")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "configuracao_sem_integracao": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
            "excecoes": {"configuracao_sem_integracao": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "configuracao_sem_integracao"
        ]
        assert len(avisos) == 0


class TestOpenspecParada:
    def test_sem_changes_dir_nao_gera_erro(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        config = {
            "versao_configuracao": 1,
            "regras": {
                "openspec_parada": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"openspec_parada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "openspec_parada"]
        assert len(avisos) == 0

    def test_changes_dir_vazio_nao_gera_erro(self, tmp_path):
        from auditoria_higiene.core import executar_auditoria

        (tmp_path / "openspec" / "changes").mkdir(parents=True)
        config = {
            "versao_configuracao": 1,
            "regras": {
                "openspec_parada": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"openspec_parada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "openspec_parada"]
        assert len(avisos) == 0


class TestSanitizer:
    def test_sanitizacao_mantem_estrutura(self):
        from auditoria_higiene.sanitizer import sanitizar_resultado

        resultado = {
            "resultados": [
                {
                    "regra": "teste",
                    "caminho": "x.txt",
                    "severidade": "error",
                    "mensagem": "senha=admin",
                }
            ],
            "status": "falha",
            "regras_desativadas": [],
        }
        sanitizado = sanitizar_resultado(resultado)
        assert sanitizado["status"] == "falha"
        assert "senha=admin" not in sanitizado["resultados"][0]["mensagem"]
        assert "senha=" in sanitizado["resultados"][0]["mensagem"]

    def test_sanitizacao_sem_resultados(self):
        from auditoria_higiene.sanitizer import sanitizar_resultado

        resultado = {"resultados": [], "status": "sucesso", "regras_desativadas": []}
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
        assert "segredos_rastreados" in result.stdout

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
        config = {"versao_configuracao": 99, "regras": {}, "excecoes": {}}
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
        assert "Falha ao listar" in result.stderr

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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
        assert "não encontrado" in result.stderr

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
            "versao_configuracao": 1,
            "regras": {
                "gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"},
            },
            "excecoes": {"gitkeep_sem_conteudo": []},
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
        assert "Pulando" in result.stdout

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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {},
            "excecoes": {},
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
        assert "caminho de saída inválido" in result.stderr

    def test_cli_pre_commit_nao_gera_relatorio_padrao(self, tmp_path, git_repo):
        repo = git_repo
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }

        resultado = executar_pre_commit(str(repo), config)

        assert resultado["status"] == "falha"
        erros = [
            r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"
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
        config_invalida = {"versao_configuracao": 99, "regras": {}, "excecoes": {}}

        repo_path = str(repo)
        with pytest.raises(ValueError, match="99"):
            executar_pre_commit(repo_path, config_invalida)

    def test_snapshot_failure_raises_runtime_error(self, tmp_path):
        from auditoria_higiene.snapshot import executar_pre_commit

        repo = tmp_path / "repo"
        repo.mkdir()
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }

        repo_path = str(repo)
        with pytest.raises(RuntimeError, match="Falha ao listar"):
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
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "error"}
            },
            "excecoes": {"segredos_rastreados": []},
        }

        repo_path = str(repo)
        with pytest.raises(RuntimeError, match="Falha ao materializar"):
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

        def fake_run(args, **kwargs):
            if (
                isinstance(args, list)
                and len(args) >= 2
                and args[0] == "git"
                and args[1] == "ls-files"
            ):
                return subprocess.CompletedProcess(
                    args, 0, b"legit.txt\x00../../evil.txt\x00", b""
                )
            return original_run(args, **kwargs)

        monkeypatch.setattr(snapshot_mod.subprocess, "run", fake_run)

        repo_path = str(repo)
        with pytest.raises(RuntimeError, match="Caminho inválido"):
            snapshot_mod.criar_snapshot(repo_path)


class TestDistribuicao:
    def test_version_consistente(self):
        from auditoria_higiene import __version__
        import tomllib

        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        assert __version__ == pyproject["project"]["version"], (
            f"__init__.py version {__version__} != pyproject.toml version {pyproject['project']['version']}"
        )

    def test_workflow_template_usa_pypi(self, tmp_path):
        from auditoria_higiene.init import cmd_init

        cmd_init(str(tmp_path))
        wf_path = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        content = wf_path.read_text()
        assert "pip install repository-hygiene==" in content
        assert "git+https://github.com" not in content

    def test_workflow_template_captura_exit_code_1(self, tmp_path):
        from auditoria_higiene.init import cmd_init

        cmd_init(str(tmp_path))
        wf_path = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        content = wf_path.read_text()
        assert "|| rc=$?" in content
        assert "exit_code=$rc" in content

    def test_workflow_template_publica_relatorio_sem_if(self, tmp_path):
        from auditoria_higiene.init import cmd_init

        cmd_init(str(tmp_path))
        wf_path = tmp_path / ".github" / "workflows" / "repository-hygiene.yml"
        content = wf_path.read_text()
        publish_idx = content.index("Publish report to Summary")
        snippet = content[publish_idx : publish_idx + 200]
        assert "if:" not in snippet

    def test_readme_sem_nao_publicado(self):
        with open("README.md", encoding="utf-8") as readme_file:
            readme = readme_file.read()
        assert "não está publicado" not in readme

    def test_readme_apresenta_init_antes_auditoria(self):
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        pos_init = readme.index("### Inicializar projeto")
        pos_audit = readme.index("### Auditoria local")
        assert pos_init < pos_audit, "`--init` deve aparecer antes da auditoria local"

    def test_readme_descreve_formatos_explicitos(self):
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        assert "--format text" in readme
        assert "--format json" in readme
        assert "--format sarif" in readme
        assert "--output" in readme

    def test_readme_workflow_publica_relatorio_apos_erro(self):
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        assert "executa a auditoria mesmo quando ela retorna erro" in readme
        assert "publica o relatório" in readme
        assert "issue" in readme

    def test_readme_codigo_saida_2_documentado(self):
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        assert "2" in readme
        assert "Configuração ou execução inválida" in readme

    def test_readme_exemplo_config_inclui_permissoes_write_permitidas(self):
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        assert "permissoes_write_permitidas" in readme
        assert "[issues]" in readme
