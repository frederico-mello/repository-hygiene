"""Tests for semantic evidence module."""


class TestCarregarReferenciasOpenspec:
    def test_extrai_caminhos_de_specs_md(self, tmp_path):
        from auditoria_higiene.semantic import carregar_referencias_openspec

        specs_dir = tmp_path / "openspec" / "specs" / "my-spec"
        specs_dir.mkdir(parents=True)
        (specs_dir / "spec.md").write_text(
            "See `src/auditoria_higiene/core.py` for details.\n"
            "Also references `tests_package/conftest.py`.\n"
        )

        refs = carregar_referencias_openspec(str(tmp_path))

        assert "src/auditoria_higiene/core.py" in refs
        assert "tests_package/conftest.py" in refs

    def test_extrai_caminhos_de_changes_md(self, tmp_path):
        from auditoria_higiene.semantic import carregar_referencias_openspec

        changes_dir = tmp_path / "openspec" / "changes" / "some-change"
        changes_dir.mkdir(parents=True)
        (changes_dir / "proposal.md").write_text(
            "Affected: `src/auditoria_higiene/semantic.py`\n"
        )
        (changes_dir / "design.md").write_text(
            "Create `tests_package/test_semantic.py`.\n"
        )

        refs = carregar_referencias_openspec(str(tmp_path))

        assert "src/auditoria_higiene/semantic.py" in refs
        assert "tests_package/test_semantic.py" in refs

    def test_openspec_ausente_retorna_vazio(self, tmp_path):
        from auditoria_higiene.semantic import carregar_referencias_openspec

        refs = carregar_referencias_openspec(str(tmp_path))

        assert refs == set()


class TestCarregarReferenciasGraphify:
    def test_extrai_source_locations_do_graph_json(self, tmp_path):
        from auditoria_higiene.semantic import carregar_referencias_graphify

        graph_dir = tmp_path / "graphify-out"
        graph_dir.mkdir()
        import json

        data = {
            "nodes": [
                {"id": "n1", "source_location": "src/auditoria_higiene/core.py"},
                {"id": "n2", "label": "semantic.py"},
                {"id": "n3", "source_location": "tests_package/test_semantic.py"},
            ]
        }
        (graph_dir / "graph.json").write_text(json.dumps(data))

        refs = carregar_referencias_graphify(str(tmp_path))

        assert "src/auditoria_higiene/core.py" in refs
        assert "tests_package/test_semantic.py" in refs
        assert "semantic.py" not in refs

    def test_graph_json_ausente_retorna_vazio(self, tmp_path):
        from auditoria_higiene.semantic import carregar_referencias_graphify

        refs = carregar_referencias_graphify(str(tmp_path))

        assert refs == set()


class TestMontarEvidencias:
    def test_orquestra_openspec_e_graphify(self, tmp_path):
        from auditoria_higiene.semantic import montar_evidencias

        specs_dir = tmp_path / "openspec" / "specs" / "my-spec"
        specs_dir.mkdir(parents=True)
        (specs_dir / "spec.md").write_text("See `src/core.py` for details.\n")

        graph_dir = tmp_path / "graphify-out"
        graph_dir.mkdir()
        import json

        (graph_dir / "graph.json").write_text(
            json.dumps({"nodes": [{"id": "n1", "source_location": "src/core.py"}]})
        )

        config = {
            "fontes_semanticas": {"openwiki": None, "graphify": None, "openspec": True}
        }

        evidencias = montar_evidencias(str(tmp_path), config)

        assert "src/core.py" in evidencias
        assert "openspec" in evidencias["src/core.py"].lower()

    def test_cache_invalida_entre_chamadas(self, tmp_path):
        from auditoria_higiene.semantic import montar_evidencias, _EVIDENCIAS_CACHE

        _EVIDENCIAS_CACHE.clear()
        config = {
            "fontes_semanticas": {"openwiki": None, "graphify": None, "openspec": True}
        }

        e1 = montar_evidencias(str(tmp_path), config)
        assert e1 == {}

        (tmp_path / "openspec").mkdir()
        e2 = montar_evidencias(str(tmp_path), config)

        assert e2 == {}


class TestVerificarSemReferenciaComEvidencia:
    def test_arquivo_em_openspec_nao_eh_reportado(self, git_repo):
        import subprocess

        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.semantic import _EVIDENCIAS_CACHE

        _EVIDENCIAS_CACHE.clear()

        repo = git_repo
        (repo / "src" / "meu_modulo.py").parent.mkdir()
        (repo / "src" / "meu_modulo.py").write_text("def f():\n    pass\n")
        changes_dir = repo / "openspec" / "changes" / "add-module"
        changes_dir.mkdir(parents=True)
        (changes_dir / "proposal.md").write_text(
            "Create `src/meu_modulo.py` for the new feature.\n"
        )
        subprocess.run(
            [
                "git",
                "add",
                "src/meu_modulo.py",
                "openspec/changes/add-module/proposal.md",
            ],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

        config = {
            "versao_configuracao": 1,
            "regras": {
                "arquivos_sem_referencia": {
                    "habilitada": True,
                    "severidade": "warning",
                }
            },
            "excecoes": {"arquivos_sem_referencia": []},
        }
        resultado = executar_auditoria(str(repo), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "arquivos_sem_referencia"
            and r["caminho"] == "src/meu_modulo.py"
        ]
        assert achados == []


class TestVerificarDocumentacaoComEvidencia:
    def test_ref_inexistente_com_evidencia_openspec_nao_reportada(self, git_repo):
        import subprocess

        from auditoria_higiene.core import executar_auditoria
        from auditoria_higiene.semantic import _EVIDENCIAS_CACHE

        _EVIDENCIAS_CACHE.clear()

        repo = git_repo
        readme = repo / "README.md"
        readme.write_text("See `src/planned_module.py` for the new feature.\n")
        changes_dir = repo / "openspec" / "changes" / "add-planned"
        changes_dir.mkdir(parents=True)
        (changes_dir / "proposal.md").write_text(
            "Will create `src/planned_module.py`.\n"
        )
        subprocess.run(
            ["git", "add", "README.md", "openspec/changes/add-planned/proposal.md"],
            cwd=repo,
            capture_output=True,
            timeout=10,
            shell=False,
        )

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
        resultado = executar_auditoria(str(repo), config)
        achados = [
            r
            for r in resultado["resultados"]
            if r["regra"] == "documentacao_desatualizada"
            and "src/planned_module.py" in r["mensagem"]
        ]
        assert achados == []
