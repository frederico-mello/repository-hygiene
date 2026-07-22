"""CLI for repository-hygiene."""

import argparse
import sys
import os

from repository_hygiene import __version__
from repository_hygiene.core import carregar_configuracao, validar_configuracao, executar_auditoria
from repository_hygiene.sanitizer import sanitizar_resultado
from repository_hygiene.reporters import gerar_relatorio_texto, gerar_relatorio_json, gerar_relatorio_sarif
from repository_hygiene.init import cmd_install, cmd_update


def _caminho_seguro(raiz, *partes):
    caminho = os.path.normpath(os.path.join(raiz, *partes))
    raiz_abs = os.path.realpath(raiz)
    caminho_abs = os.path.realpath(caminho)
    if not caminho_abs.startswith(raiz_abs + os.sep) and caminho_abs != raiz_abs:
        raise ValueError(f"Path traversal detectado: {caminho}")
    return caminho_abs


def _cmd_audit(args):
    try:
        config_path = _caminho_seguro(args.directory, args.config)
    except ValueError:
        print(f"Erro: caminho de configuração inválido: {args.config}", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(config_path):
        print(f"Erro: arquivo de configuração não encontrado em {config_path}", file=sys.stderr)
        sys.exit(2)

    try:
        config = carregar_configuracao(config_path)
        validar_configuracao(config)
    except ValueError as e:
        print(f"Erro de configuração: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}", file=sys.stderr)
        sys.exit(2)

    if args.mode is not None:
        config["modo"] = args.mode

    try:
        resultado = executar_auditoria(args.directory, config)
    except Exception as e:
        print(f"Erro durante auditoria: {e}", file=sys.stderr)
        sys.exit(2)

    resultado_sanitizado = sanitizar_resultado(resultado)

    if args.format == "json":
        print(gerar_relatorio_json(resultado_sanitizado))
    elif args.format == "sarif":
        print(gerar_relatorio_sarif(resultado_sanitizado))
    else:
        print(gerar_relatorio_texto(resultado_sanitizado))

    if resultado["status"] == "falha":
        sys.exit(1)
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog="repository-hygiene",
        description="Repository hygiene auditor for Git repositories",
    )
    parser.add_argument("--version", action="version", version=f"repository-hygiene {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Run audit on a repository")
    audit_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory of the repository to audit (default: .)",
    )
    audit_parser.add_argument(
        "--config",
        default="auditoria.yaml",
        help="Path to configuration file (default: auditoria.yaml)",
    )
    audit_parser.add_argument(
        "--format",
        choices=["text", "json", "sarif"],
        default="text",
        help="Report format (default: text)",
    )
    audit_parser.add_argument(
        "--mode",
        choices=["pre-commit", "ci"],
        default=None,
        help="Modo de execução: pre-commit (padrão local) ou ci (mais restritivo)",
    )

    install_parser = subparsers.add_parser("install", help="Install audit configuration in a repository")
    install_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory of the repository (default: .)",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without confirmation",
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned operations without modifying files",
    )

    update_parser = subparsers.add_parser("update", help="Update audit configuration to a specific version")
    update_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory of the repository (default: .)",
    )
    update_parser.add_argument(
        "--version",
        default=None,
        help="Target version to update to (default: latest)",
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned changes without modifying files",
    )

    args = parser.parse_args()

    if args.command == "audit":
        _cmd_audit(args)
    elif args.command == "install":
        cmd_install(args.directory, force=args.force, dry_run=args.dry_run)
    elif args.command == "update":
        cmd_update(args.directory, version=args.version, dry_run=args.dry_run)


if __name__ == "__main__":
    main()