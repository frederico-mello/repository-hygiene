"""CLI do auditor de higiene."""

import argparse
import sys
import os

from auditoria_higiene import __version__
from auditoria_higiene.core import carregar_configuracao, validar_configuracao, executar_auditoria
from auditoria_higiene.sanitizer import sanitizar_resultado
from auditoria_higiene.reporters import gerar_relatorio_texto, gerar_relatorio_json, gerar_relatorio_sarif
from auditoria_higiene.init import cmd_init


def _caminho_seguro(raiz, *partes):
    caminho = os.path.normpath(os.path.join(raiz, *partes))
    raiz_abs = os.path.realpath(raiz)
    caminho_abs = os.path.realpath(caminho)
    if not caminho_abs.startswith(raiz_abs + os.sep) and caminho_abs != raiz_abs:
        raise ValueError(f"Path traversal detectado: {caminho}")
    return caminho_abs


def main():
    parser = argparse.ArgumentParser(
        prog="auditoria-higiene",
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
        default="text",
        help="Formato do relatório (padrão: text)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"auditoria-higiene {__version__}",
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

    args = parser.parse_args()

    if args.init:
        cmd_init(args.directory, force=args.force)
        return

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


if __name__ == "__main__":
    main()
