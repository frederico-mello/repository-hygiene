## Why

O comando de auditoria atualmente imprime relatórios no terminal e oferece texto, JSON e SARIF, mas não produz um documento Markdown próprio. Isso dificulta encaminhar o resultado a uma LLM para análise e correção, além de exigir redirecionamento manual e gerar arquivos `.txt` pouco estruturados para leitura humana.

## What Changes

- Adicionar um formato de relatório Markdown estruturado para consumo humano e por LLMs.
- Adicionar uma opção `--output` para gravar o relatório em arquivo.
- Manter a saída no terminal quando `--output` não for informado.
- Permitir que `--output` seja usado com os formatos existentes e com o novo formato Markdown.
- Garantir que relatórios gravados preservem a sanitização de dados sensíveis já aplicada aos relatórios exibidos.
- Retornar erro claro quando o arquivo de saída não puder ser criado ou escrito.
- Não incluir integração automática com uma LLM nem alterar o conteúdo das regras de auditoria.

## Capabilities

### New Capabilities

- `markdown-audit-report`: Geração de relatórios de auditoria em Markdown, estruturados para leitura humana e correção assistida por LLM.
- `audit-report-output`: Gravação opcional dos relatórios gerados pelo comando em um caminho escolhido pelo usuário.

### Modified Capabilities

- `audit-reporting`: amplia a interface de saída com o formato Markdown e destino opcional em arquivo, sem alterar o comportamento padrão.

## Impact

- Usuários poderão escolher entre visualizar o relatório no terminal ou salvá-lo em arquivo, sem perder os formatos existentes.
- A documentação de uso e os testes do pacote precisarão cobrir o novo formato e a gravação opcional.
- O suporte a `--output` será aditivo e não alterará o contrato dos formatos `text`, `json` ou `sarif` quando usados sem essa opção.
- Não requer nova dependência externa nem muda as regras de auditoria.
