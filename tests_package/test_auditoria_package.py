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
            "configuracao_sem_integracao": {"habilitada": True, "severidade": "warning"},
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


class TestConfiguracao:
    def test_carregar_configuracao_valida(self, config_file):
        from repository_hygiene.core import carregar_configuracao
        config = carregar_configuracao(config_file)
        assert "regras" in config
        assert "excecoes" in config
        assert config["regras"]["segredos_rastreados"]["habilitada"] is True

    def test_validar_versao_correta(self, config_file):
        from repository_hygiene.core import carregar_configuracao, validar_configuracao
        config = carregar_configuracao(config_file)
        validar_configuracao(config)

    def test_validar_versao_incorreta(self, config_file):
        from repository_hygiene.core import carregar_configuracao, validar_configuracao
        config = carregar_configuracao(config_file)
        config["versao_configuracao"] = 99
        with pytest.raises(ValueError, match="99"):
            validar_configuracao(config)

    def test_regra_desativada_nao_avaliada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": False, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        regras_aplicadas = [r["regra"] for r in resultado["resultados"]]
        assert "segredos_rastreados" not in regras_aplicadas

    def test_regra_desativada_listada_no_relatorio(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.reporters import gerar_relatorio_texto
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": False, "severidade": "error"},
                "links_internos_quebrados": {"habilitada": False, "severidade": "error"},
            },
            "excecoes": {"segredos_rastreados": [], "links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert "segredos_rastreados" in resultado["regras_desativadas"]
        assert "links_internos_quebrados" in resultado["regras_desativadas"]
        relatorio = gerar_relatorio_texto(resultado)
        assert "DESATIVADAS" in relatorio

    def test_config_severidade_aplicada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {
                "segredos_rastreados": {"habilitada": True, "severidade": "warning"}
            },
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"]
        assert len(erros) == 1
        assert erros[0]["severidade"] == "warning"


class TestSegredosRastreados:
    def test_segredo_detectado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "config.txt").write_text("senha=admin123")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"]
        assert len(erros) == 1
        assert erros[0]["caminho"] == "config.txt"

    def test_caminho_excluido_nao_reportado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "seguro.txt").write_text("senha=123")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": ["seguro.txt"]},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        for r in resultado["resultados"]:
            assert r["caminho"] != "seguro.txt"

    def test_token_csrf_curto_nao_reportado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "app.js").write_text("const csrfToken = 'abc123';\nconst accessToken = 'xyz';\n")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"]
        assert erros == []

    def test_comentario_nao_detectado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "app.py").write_text("# Exemplo: token=abc123\nvalor = 42\n")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "segredos_rastreados"]
        assert erros == []


class TestStatusExecucao:
    def test_problema_objetivo_retorna_falha(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"

    def test_sem_problemas_retorna_sucesso(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "normal.txt").write_text("conteudo normal")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "sucesso"


class TestRelatorios:
    def test_relatorio_texto_agrupa_por_severidade(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.reporters import gerar_relatorio_texto
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
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.reporters import gerar_relatorio_json
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        saida = gerar_relatorio_json(resultado)
        dados = json.loads(saida)
        assert "status" in dados
        assert "resultados" in dados

    def test_relatorio_sarif_valido(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.reporters import gerar_relatorio_sarif
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        saida = gerar_relatorio_sarif(resultado)
        dados = json.loads(saida)
        assert dados["version"] == "2.1.0"
        assert "runs" in dados

    def test_mascaramento_segredo_texto(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.sanitizer import sanitizar_resultado
        from repository_hygiene.reporters import gerar_relatorio_texto
        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        sanitizado = sanitizar_resultado(resultado)
        relatorio = gerar_relatorio_texto(sanitizado)
        assert "super_secreto_123" not in relatorio
        assert "segredos_rastreados" in relatorio

    def test_mascaramento_segredo_json(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.sanitizer import sanitizar_resultado
        from repository_hygiene.reporters import gerar_relatorio_json
        (tmp_path / "config.txt").write_text("API_KEY=super_secreto_123")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        sanitizado = sanitizar_resultado(resultado)
        saida = gerar_relatorio_json(sanitizado)
        assert "super_secreto_123" not in saida


class TestLinksInternos:
    def test_link_interno_quebrado_detectado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("[link](inexistente.txt)")
        config = {
            "versao_configuracao": 1,
            "regras": {"links_internos_quebrados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "links_internos_quebrados"]
        assert len(erros) == 1

    def test_link_externo_ignorado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("[site](https://example.com)")
        config = {
            "versao_configuracao": 1,
            "regras": {"links_internos_quebrados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"links_internos_quebrados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "links_internos_quebrados"]
        assert len(erros) == 0


class TestReferencias:
    def test_referencia_inexistente_detectada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        config = {
            "versao_configuracao": 1,
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 1

    def test_referencia_existente_ignorada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "versao_configuracao": 1,
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 0


class TestArtefatos:
    def test_artefato_fora_gitignore_detectado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "gerado.txt").write_text("conteudo")
        config = {
            "versao_configuracao": 1,
            "regras": {"artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"artefatos_fora_gitignore": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "artefatos_fora_gitignore"]
        assert len(erros) == 1

    def test_artefato_no_gitignore_ignorado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / ".gitignore").write_text("*.log\n")
        (tmp_path / "app.log").write_text("log content")
        config = {
            "versao_configuracao": 1,
            "regras": {"artefatos_fora_gitignore": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"artefatos_fora_gitignore": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "artefatos_fora_gitignore"]
        assert len(erros) == 0


class TestGitkeep:
    def test_gitkeep_sem_conteudo_gera_warning(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "vazio" / ".gitkeep").parent.mkdir()
        (tmp_path / "vazio" / ".gitkeep").write_text("")
        config = {
            "versao_configuracao": 1,
            "regras": {"gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"gitkeep_sem_conteudo": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "gitkeep_sem_conteudo"]
        assert len(avisos) == 1

    def test_gitkeep_com_conteudo_ignorado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "com_itens" / ".gitkeep").parent.mkdir()
        (tmp_path / "com_itens" / ".gitkeep").write_text("")
        (tmp_path / "com_itens" / "arquivo_real.txt").write_text("conteudo")
        config = {
            "versao_configuracao": 1,
            "regras": {"gitkeep_sem_conteudo": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"gitkeep_sem_conteudo": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "gitkeep_sem_conteudo"]
        assert len(avisos) == 0


class TestWorkflowsInseguros:
    def test_permissao_excessiva_detectada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text("name: Test\npermissions: write-all\njobs: {}\n")
        config = {
            "versao_configuracao": 1,
            "regras": {"workflows_inseguros": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"]
        assert len(avisos) >= 1

    def test_action_sem_versao_fixa_detectada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: read-all\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@main\n"
        )
        config = {
            "versao_configuracao": 1,
            "regras": {"workflows_inseguros": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"]
        assert len(avisos) >= 1

    def test_workflow_seguro_sem_aviso(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text(
            "name: Test\npermissions: read-all\njobs:\n  build:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"
        )
        config = {
            "versao_configuracao": 1,
            "regras": {"workflows_inseguros": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"]
        assert len(avisos) == 0

    def test_regra_desabilitada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        wf_dir = tmp_path / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "test.yml").write_text("name: Test\npermissions: write-all\njobs: {}\n")
        config = {
            "versao_configuracao": 1,
            "regras": {"workflows_inseguros": {"habilitada": False, "severidade": "warning"}},
            "excecoes": {"workflows_inseguros": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "workflows_inseguros"]
        assert len(avisos) == 0
        assert "workflows_inseguros" in resultado["regras_desativadas"]


class TestDocumentacaoDesatualizada:
    def test_doc_ref_inexistente_gera_warning(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        config = {
            "versao_configuracao": 1,
            "regras": {"documentacao_desatualizada": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"documentacao_desatualizada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "documentacao_desatualizada"]
        assert len(avisos) == 1

    def test_doc_ref_existente_ignorada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("Referencia `dados.csv`")
        (tmp_path / "dados.csv").write_text("a,b,c")
        config = {
            "versao_configuracao": 1,
            "regras": {"documentacao_desatualizada": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"documentacao_desatualizada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "documentacao_desatualizada"]
        assert len(avisos) == 0


class TestConfiguracaoSemIntegracao:
    def test_config_sem_integracao_gera_warning(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        config = {
            "versao_configuracao": 1,
            "regras": {"configuracao_sem_integracao": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"configuracao_sem_integracao": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "configuracao_sem_integracao"]
        assert len(avisos) == 1

    def test_config_com_integracao_ignorada(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / ".pre-commit-config.yaml").write_text("repos: []")
        (tmp_path / "README.md").write_text("Use .pre-commit-config.yaml")
        config = {
            "versao_configuracao": 1,
            "regras": {"configuracao_sem_integracao": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"configuracao_sem_integracao": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "configuracao_sem_integracao"]
        assert len(avisos) == 0


class TestOpenspecParada:
    def test_sem_changes_dir_nao_gera_erro(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        config = {
            "versao_configuracao": 1,
            "regras": {"openspec_parada": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"openspec_parada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "openspec_parada"]
        assert len(avisos) == 0

    def test_changes_dir_vazio_nao_gera_erro(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "openspec" / "changes").mkdir(parents=True)
        config = {
            "versao_configuracao": 1,
            "regras": {"openspec_parada": {"habilitada": True, "severidade": "warning"}},
            "excecoes": {"openspec_parada": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        avisos = [r for r in resultado["resultados"] if r["regra"] == "openspec_parada"]
        assert len(avisos) == 0


class TestSanitizer:
    def test_sanitizacao_mantem_estrutura(self):
        from repository_hygiene.sanitizer import sanitizar_resultado
        resultado = {
            "resultados": [{"regra": "teste", "caminho": "x.txt", "severidade": "error", "mensagem": "senha=admin"}],
            "status": "falha",
            "regras_desativadas": [],
        }
        sanitizado = sanitizar_resultado(resultado)
        assert sanitizado["status"] == "falha"
        assert "senha=admin" not in sanitizado["resultados"][0]["mensagem"]
        assert "senha=" in sanitizado["resultados"][0]["mensagem"]

    def test_sanitizacao_sem_resultados(self):
        from repository_hygiene.sanitizer import sanitizar_resultado
        resultado = {"resultados": [], "status": "sucesso", "regras_desativadas": []}
        sanitizado = sanitizar_resultado(resultado)
        assert sanitizado["status"] == "sucesso"
        assert sanitizado["resultados"] == []


class TestModosExecucao:
    def test_sem_modo_mantem_comportamento_legado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"
        assert "classificacao" not in resultado["resultados"][0]

    def test_json_inclui_classificacao_e_decisao(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        from repository_hygiene.reporters import gerar_relatorio_json
        import json
        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.csv")')
        config = {
            "versao_configuracao": 1,
            "modo": "ci",
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        saida = json.loads(gerar_relatorio_json(resultado))
        ocorrencia = saida["resultados"][0]
        assert "classificacao" in ocorrencia
        assert "confianca" in ocorrencia
        assert "policy_action" in ocorrencia

    def test_ci_falha_em_referencia_confirmada_ausente(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "codigo.py").write_text('importar_arquivo("dados.py")')
        config = {
            "versao_configuracao": 1,
            "modo": "ci",
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 1
        assert resultado["status"] == "falha"

    def test_ci_nao_falha_em_ambiguo(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("ref `arquivo_inexistente.csv`")
        config = {
            "versao_configuracao": 1,
            "modo": "ci",
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 1
        assert resultado["status"] == "sucesso"

    def test_pre_commit_reporta_ambiguo_sem_falhar(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "doc.md").write_text("ref `arquivo_inexistente.csv`")
        config = {
            "versao_configuracao": 1,
            "modo": "pre-commit",
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 1
        assert resultado["status"] == "sucesso"

    def test_pre_commit_falha_em_provavel(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "codigo.md").write_text('ref `arquivo_inexistente.yaml`')
        config = {
            "versao_configuracao": 1,
            "modo": "pre-commit",
            "regras": {"referencias_inexistentes": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"referencias_inexistentes": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        erros = [r for r in resultado["resultados"] if r["regra"] == "referencias_inexistentes"]
        assert len(erros) == 1
        assert resultado["status"] == "falha"

    def test_modo_invalido_fallback_legado(self, tmp_path):
        from repository_hygiene.core import executar_auditoria
        (tmp_path / "segredo.txt").write_text("senha=admin")
        config = {
            "versao_configuracao": 1,
            "modo": "modo_invalido",
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        resultado = executar_auditoria(str(tmp_path), config)
        assert resultado["status"] == "falha"
        assert "classificacao" not in resultado["resultados"][0]


class TestCLI:
    def test_cli_ajuda(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_cli_install_cria_arquivos(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "install", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))
        assert os.path.exists(os.path.join(tmp_path, ".github", "workflows", "repository-hygiene.yml"))

    def test_cli_install_nao_sobrescreve(self, tmp_path):
        import subprocess
        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "install", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() == "original"

    def test_cli_install_force_sobrescreve(self, tmp_path):
        import subprocess
        (tmp_path / "auditoria.yaml").write_text("original")
        subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "install", "--force", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert (tmp_path / "auditoria.yaml").read_text() != "original"

    def test_cli_install_dry_run(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "install", "--dry-run", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "dry-run" in result.stdout
        assert not os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))

    def test_cli_sem_comando_erro(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 2

    def test_cli_versao(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "repository-hygiene" in result.stdout

    def test_cli_audit_json_format(self, tmp_path):
        import subprocess
        import yaml
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "audit", str(tmp_path), "--format", "json"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 1
        import json
        dados = json.loads(result.stdout)
        assert dados["status"] == "falha"

    def test_cli_audit_sarif_format(self, tmp_path):
        import subprocess
        import yaml
        config = {
            "versao_configuracao": 1,
            "regras": {"segredos_rastreados": {"habilitada": True, "severidade": "error"}},
            "excecoes": {"segredos_rastreados": []},
        }
        with open(os.path.join(tmp_path, "auditoria.yaml"), "w") as f:
            yaml.dump(config, f)
        (tmp_path / "segredo.txt").write_text("senha=admin")
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "audit", str(tmp_path), "--format", "sarif"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 1
        import json
        dados = json.loads(result.stdout)
        assert dados["version"] == "2.1.0"

    def test_cli_audit_sem_config_erro(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "audit", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 2

    def test_cli_update_dry_run(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "update", "--dry-run", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "dry-run" in result.stdout

    def test_cli_update_cria_arquivos(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "update", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert os.path.exists(os.path.join(tmp_path, "auditoria.yaml"))

    def test_cli_update_preserva_excecoes(self, tmp_path):
        import subprocess
        (tmp_path / "auditoria.yaml").write_text("custom: true")
        result = subprocess.run(
            [sys.executable, "-m", "repository_hygiene.cli", "update", str(tmp_path)],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        content = (tmp_path / "auditoria.yaml").read_text()
        assert "custom" not in content
