## Context

O comando atualmente seleciona um renderizador por formato e envia o resultado para a saída padrão. O resultado já é sanitizado antes da renderização. A mudança precisa adicionar Markdown e gravação opcional sem quebrar o comportamento padrão nem os formatos existentes.

## Goals / Non-Goals

**Goals:**

- Centralizar a seleção do conteúdo do relatório e do destino de saída.
- Produzir Markdown com status, resumo por severidade, regras desativadas e detalhes acionáveis de cada ocorrência.
- Permitir gravação em arquivo com codificação UTF-8 e manter a saída padrão quando nenhum arquivo for solicitado.
- Preservar a sanitização para todos os destinos e formatos.

**Non-Goals:**

- Não alterar as regras de auditoria ou o modelo de resultados.
- Não integrar diretamente com provedores de LLM.
- Não remover nem modificar o conteúdo dos formatos existentes.

## Decisions

- **Novo renderizador Markdown:** adicionar um renderizador dedicado, paralelo aos renderizadores existentes, para evitar que o formato textual legado seja reinterpretado como Markdown. O documento usará cabeçalhos, listas e blocos de detalhes previsíveis para facilitar parsing por LLM.
- **Destino separado da formatação:** manter a geração do relatório como uma operação que retorna texto e tratar `--output` no CLI. Isso permite gravar `text`, `json`, `sarif` e `markdown` sem duplicar renderizadores.
- **Formato explícito:** ampliar as opções de formato com `markdown`, mantendo `text` como padrão. A alternativa de inferir o formato pela extensão do arquivo foi rejeitada porque torna o comportamento menos previsível.
- **Comportamento do destino:** sem `--output`, o relatório vai para stdout. Com `--output`, o conteúdo vai para o arquivo e stdout recebe uma confirmação curta; o arquivo existente é sobrescrito, diretórios-pai não são criados automaticamente e o caminho é escrito em UTF-8.
- **Falha de escrita explícita:** erros ao abrir ou escrever o destino devem ser reportados no stderr e resultar em código `2`, sem apresentar um relatório parcial como se tivesse sido salvo. O relatório de auditoria continua usando código `1` quando há erros encontrados.
- **Sanitização antes do destino:** o resultado continuará sendo sanitizado antes de qualquer renderização, garantindo que terminal e arquivos recebam o mesmo tratamento.
- **Estrutura Markdown determinística:** o documento terá título, status, resumo com contagens de errors e warnings, seções separadas por severidade, seção opcional de regras desativadas e uma subseção por ocorrência. Campos opcionais ausentes não geram linhas vazias nem valores inventados; valores textuais serão escapados para não quebrar a estrutura Markdown.

## Risks / Trade-offs

- [Compatibilidade com consumidores do texto padrão] → manter `text` como formato padrão e preservar sua estrutura atual.
- [Relatório Markdown pode expor dados sensíveis se um novo campo ignorar sanitização] → renderizar somente o resultado já sanitizado e cobrir o caminho de arquivo com testes.
- [Caminho de saída inválido ou sem permissão] → retornar mensagem clara no stderr e código de erro distinto de auditoria com falha.
- [LLMs interpretarem recomendações como autorização para mudanças perigosas] → declarar o Markdown como representação informativa, sem integração automática nem comandos executáveis.
