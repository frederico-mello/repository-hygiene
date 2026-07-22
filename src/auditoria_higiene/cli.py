"""CLI do auditor de higiene."""

import argparse
import json
import sys
import os
from datetime import datetime, timezone

from auditoria_higiene import __version__
from auditoria_higiene.core import (
    carregar_configuracao,
    validar_configuracao,
    executar_auditoria,
    caminho_seguro,
)
from auditoria_higiene.sanitizer import sanitizar_resultado
from auditoria_higiene.reporters import (
    gerar_relatorio_texto,
    gerar_relatorio_json,
    gerar_relatorio_sarif,
    gerar_resumo,
    escrever_relatorio,
)
from auditoria_higiene.init import cmd_init
from auditoria_higiene.snapshot import (
    executar_pre_commit as executar_pre_commit_snapshot,
)


def _resolver_config(directory, config_path):
    try:
        config_path_resolved = caminho_seguro(directory, config_path)
    except ValueError:
        print(f"Erro: caminho de configuração inválido: {config_path}", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(config_path_resolved):
        print(
            f"Erro: arquivo de configuração não encontrado em {config_path_resolved}",
            file=sys.stderr,
        )
        sys.exit(2)
    return config_path_resolved


def _carregar_config(config_path_resolved):
    try:
        config = carregar_configuracao(config_path_resolved)
        validar_configuracao(config)
        return config
    except ValueError as e:
        print(f"Erro de configuração: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}", file=sys.stderr)
        sys.exit(2)


def _processar_resultado(
    resultado, formato=None, directory=".", output=None, resumo=True
):
    resultado_sanitizado = sanitizar_resultado(resultado)
    if formato is None:
        report_path = output or os.path.join(
            directory, ".repository-hygiene", "auditoria.json"
        )
        relatorio_json = gerar_relatorio_json(resultado_sanitizado)
        metadados = {
            "schema_version": 1,
            "auditor_version": __version__,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "audited_directory": os.path.normpath(directory),
            **json.loads(relatorio_json),
        }
        try:
            if output is None:
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
            escrever_relatorio(
                json.dumps(metadados, ensure_ascii=False, indent=2), report_path
            )
        except OSError as e:
            print(f"Erro ao persistir relatório: {e}", file=sys.stderr)
            sys.exit(2)
        if resumo:
            print(
                gerar_resumo(
                    resultado_sanitizado, os.path.relpath(report_path, directory)
                )
            )
    elif formato == "json":
        conteudo = gerar_relatorio_json(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output)
        print(conteudo)
    elif formato == "sarif":
        conteudo = gerar_relatorio_sarif(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output)
        print(conteudo)
    else:
        conteudo = gerar_relatorio_texto(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output)
        print(conteudo)
    if resultado["status"] == "falha":
        sys.exit(1)
    sys.exit(0)


def _gravar_se_solicitado(conteudo, output):
    if not output:
        return
    try:
        escrever_relatorio(conteudo, output)
    except OSError as e:
        print(f"Erro ao persistir relatório: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        prog="repository-hygiene",
        description="Auditor de higiene para repositórios Git",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Diretório raiz do repositório a auditar (padrão: .)",
    )
    parser.add_argument(
        "--config",
        default="auditoria.yaml",
        help="Caminho do arquivo de configuração (padrão: auditoria.yaml)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default=None,
        help="Formato do relatório (padrão: resumo + JSON)",
    )
    parser.add_argument(
        "--output",
        help="Caminho do relatório; sem --format, grava JSON",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"repository-hygiene {__version__}",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Inicializar configuração e workflow no diretório",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescrever arquivos existentes sem confirmação (usado com --init)",
    )
    parser.add_argument(
        "--install-hook",
        action="store_true",
        help="Instalar hook pre-commit nativo (usado com --init)",
    )
    parser.add_argument(
        "--pre-commit",
        action="store_true",
        help="Modo pre-commit: audita apenas o conteúdo staged",
    )

    args = parser.parse_args()

    if args.init:
        cmd_init(args.directory, force=args.force, install_hook=args.install_hook)
        return

    if args.pre_commit:
        _executar_pre_commit(args.directory, args.config, args.format, args.output)
        return

    config_path = _resolver_config(args.directory, args.config)
    config = _carregar_config(config_path)

    try:
        resultado = executar_auditoria(args.directory, config)
    except Exception as e:
        print(f"Erro durante auditoria: {e}", file=sys.stderr)
        sys.exit(2)

    output = args.output
    if output and not os.path.isabs(output):
        output = os.path.join(args.directory, output)
    _processar_resultado(resultado, args.format, args.directory, output)


def _executar_pre_commit(directory, config_path, formato=None, output=None):
    config_path_resolved = _resolver_config(directory, config_path)
    config = _carregar_config(config_path_resolved)

    try:
        resultado = executar_pre_commit_snapshot(directory, config)
    except Exception as e:
        print(f"Erro durante auditoria pre-commit: {e}", file=sys.stderr)
        sys.exit(2)

    if output and not os.path.isabs(output):
        output = os.path.join(directory, output)
    _processar_resultado(resultado, formato or "text", directory, output, resumo=False)


if __name__ == "__main__":
    main()
