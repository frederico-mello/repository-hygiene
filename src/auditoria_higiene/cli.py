"""Repository hygiene auditor CLI."""

import argparse
import sys
import os

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
    gerar_relatorio_json_agente,
    gerar_relatorio_sarif,
    gerar_resumo,
    escrever_relatorio,
)
from auditoria_higiene.init import cmd_init, cmd_install, cmd_update
from auditoria_higiene.snapshot import (
    executar_pre_commit as executar_pre_commit_snapshot,
)


def _resolver_config(directory, config_path):
    try:
        config_path_resolved = caminho_seguro(directory, config_path)
    except ValueError:
        print(f"Error: invalid config path: {config_path}", file=sys.stderr)
        sys.exit(2)
    if not os.path.exists(config_path_resolved):
        print(
            f"Error: configuration file not found at {config_path_resolved}",
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
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(2)


def _processar_resultado(
    resultado, formato=None, directory=".", output=None, resumo=True
):
    resultado_sanitizado = sanitizar_resultado(resultado)
    if formato is None:
        report_path = output or os.path.join(
            directory, ".repository-hygiene", "auditoria.json"
        )
        report_path = _resolver_saida(directory, report_path)
        try:
            if output is None:
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
            escrever_relatorio(
                gerar_relatorio_json_agente(
                    resultado_sanitizado, __version__, directory
                ),
                report_path,
                directory,
            )
        except OSError as e:
            print(f"Error persisting report: {e}", file=sys.stderr)
            sys.exit(2)
        if resumo:
            print(
                gerar_resumo(
                    resultado_sanitizado, os.path.relpath(report_path, directory)
                )
            )
    elif formato == "json":
        conteudo = gerar_relatorio_json(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output, directory)
        print(conteudo)
    elif formato == "sarif":
        conteudo = gerar_relatorio_sarif(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output, directory)
        print(conteudo)
    else:
        conteudo = gerar_relatorio_texto(resultado_sanitizado)
        _gravar_se_solicitado(conteudo, output, directory)
        print(conteudo)
    if resultado["status"] == "falha":
        sys.exit(1)
    sys.exit(0)


def _gravar_se_solicitado(conteudo, output, directory):
    if not output:
        return
    try:
        escrever_relatorio(conteudo, output, directory)
    except OSError as e:
        print(f"Error persisting report: {e}", file=sys.stderr)
        sys.exit(2)


def _resolver_saida(directory, output):
    try:
        return caminho_seguro(directory, output)
    except ValueError:
        print(f"Error: invalid output path: {output}", file=sys.stderr)
        sys.exit(2)


def main():
    argv = sys.argv[1:] if len(sys.argv) > 1 else []
    if not argv or argv[0] in ("install", "audit", "update", "--help", "-h"):
        _run_subcommand(argv if argv else ["--help"])
    else:
        _run_legacy(argv)


def _run_subcommand(argv):
    parser = argparse.ArgumentParser(
        prog="repository-hygiene",
        description="Repository hygiene auditor for Git repositories",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"repository-hygiene {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("install", help="Install configuration and workflow in a repository")
    p.add_argument("directory", nargs="?", default=".",
                   help="Repository root directory (default: .)")
    p.add_argument("--force", action="store_true",
                   help="Overwrite existing files without confirmation")
    p.add_argument("--dry-run", action="store_true",
                   help="Show planned operations without modifying files")

    p = subparsers.add_parser("audit", help="Run audit on a repository")
    p.add_argument("directory", nargs="?", default=".",
                   help="Repository root directory (default: .)")
    p.add_argument("--config", default="auditoria.yaml",
                   help="Configuration file path (default: auditoria.yaml)")
    p.add_argument("--format", choices=["text", "json", "sarif"], default=None,
                   help="Report format (default: summary + JSON)")
    p.add_argument("--mode", choices=["pre-commit", "ci"], default=None,
                   help="Execution mode")

    p = subparsers.add_parser("update", help="Update configuration to a specific version")
    p.add_argument("directory", nargs="?", default=".",
                   help="Repository root directory (default: .)")
    p.add_argument("--version", default=None,
                   help="Target version (default: latest)")
    p.add_argument("--dry-run", action="store_true",
                   help="Show planned changes without modifying files")

    args = parser.parse_args(argv)

    if args.command == "install":
        cmd_install(args.directory, force=args.force, dry_run=args.dry_run)
    elif args.command == "audit":
        _executar_auditoria(args.directory, config_path=args.config,
                            formato=args.format, mode=args.mode)
    elif args.command == "update":
        cmd_update(args.directory, version=args.version, dry_run=args.dry_run)


def _run_legacy(argv):
    parser = argparse.ArgumentParser(
        prog="repository-hygiene",
        description="Repository hygiene auditor for Git repositories",
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="Repository root directory (default: .)")
    parser.add_argument("--config", default="auditoria.yaml",
                        help="Configuration file path (default: auditoria.yaml)")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default=None,
                        help="Report format (default: summary + JSON)")
    parser.add_argument("--output", help="Report output path")
    parser.add_argument("--version", action="version",
                        version=f"repository-hygiene {__version__}")
    parser.add_argument("--init", action="store_true",
                        help="Initialize configuration and workflow in the directory")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing files without confirmation")
    parser.add_argument("--install-hook", action="store_true",
                        help="Install native pre-commit hook")
    parser.add_argument("--pre-commit", action="store_true",
                        help="Pre-commit mode: audit staged content only")

    args = parser.parse_args(argv)

    if args.init:
        cmd_init(args.directory, force=args.force, install_hook=args.install_hook)
    elif args.pre_commit:
        _executar_pre_commit(args.directory, args.config, args.format, args.output)
    else:
        _executar_auditoria(args.directory, config_path=args.config,
                            formato=args.format, output=args.output)


def _executar_auditoria(directory, config_path="auditoria.yaml",
                        formato=None, output=None, mode=None):
    config_path = _resolver_config(directory, config_path)
    config = _carregar_config(config_path)

    if mode is not None:
        config["modo"] = mode

    try:
        resultado = executar_auditoria(directory, config)
    except Exception as e:
        print(f"Error during audit: {e}", file=sys.stderr)
        sys.exit(2)

    if output and not os.path.isabs(output):
        output = os.path.join(directory, output)
    if output:
        output = _resolver_saida(directory, output)
    _processar_resultado(resultado, formato, directory, output)


def _executar_pre_commit(directory, config_path, formato=None, output=None):
    config_path_resolved = _resolver_config(directory, config_path)
    config = _carregar_config(config_path_resolved)

    try:
        resultado = executar_pre_commit_snapshot(directory, config)
    except Exception as e:
        print(f"Error during pre-commit audit: {e}", file=sys.stderr)
        sys.exit(2)

    if output and not os.path.isabs(output):
        output = os.path.join(directory, output)
    if output:
        output = _resolver_saida(directory, output)
    _processar_resultado(resultado, formato or "text", directory, output, resumo=False)


if __name__ == "__main__":
    main()
