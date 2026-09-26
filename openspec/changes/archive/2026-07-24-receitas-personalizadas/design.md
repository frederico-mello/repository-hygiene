## Context

O projeto ainda não possui aplicação ou capacidades especificadas. A primeira versão precisa transformar as receitas do Desafio Vegano em conhecimento consultável e gerar recomendações confiáveis a partir dos ingredientes da pessoa. O conteúdo deve permanecer rastreável à fonte original, respeitar as receitas publicadas e permitir atualização sem reconstruir manualmente todo o sistema.

## Goals / Non-Goals

**Goals:**

- Modelar receitas e ingredientes de forma estruturada, incluindo quantidades, unidades, porções, etapas, restrições e fonte.
- Oferecer recuperação por correspondência de ingredientes e por significado textual.
- Produzir recomendações explicáveis, com ingredientes disponíveis, ausentes e justificativa de ordenação.
- Manter citações e metadados da receita recuperada em toda resposta gerada.
- Começar com uma arquitetura simples de operar, mas com fronteiras que permitam evoluir para GraphRAG.

**Non-Goals:**

- Criar receitas completamente novas ou afirmar propriedades nutricionais que não estejam na fonte.
- Automatizar alterações culinárias que mudem substancialmente a receita original na primeira versão.
- Construir um grafo de conhecimento completo antes de validar o fluxo básico com pessoas reais.
- Resolver autenticação, pagamentos ou marketplace neste change.

## Decisions

### Começar com RAG híbrido, preparado para GraphRAG

A primeira versão usará um índice híbrido: dados estruturados para filtros e cálculo de cobertura de ingredientes, busca vetorial para intenção e texto, e recuperação lexical para nomes exatos. O modelo de linguagem apenas sintetizará resultados recuperados.

GraphRAG será tratado como evolução, não como requisito inicial. Um grafo passa a ser justificável quando relações como substituições, utensílios, técnicas, alergênicos e dependências entre ingredientes demonstrarem valor que o modelo relacional mais índices não atende. Esta escolha reduz custo e complexidade durante a validação, preservando a possibilidade de projetar entidades e relações com identificadores estáveis.

Alternativas consideradas: GraphRAG desde o início, rejeitado pelo custo operacional e pela incerteza sobre quais relações serão necessárias; somente busca vetorial, rejeitado porque não calcula cobertura de ingredientes com precisão nem garante filtros determinísticos.

### Pipeline de ingestão versionado e idempotente

Cada receita será extraída da fonte, normalizada para um esquema canônico e armazenada com URL, título da página, data de coleta, versão do conteúdo e identificador estável. Reprocessamentos da mesma fonte atualizarão a versão sem duplicar a receita. Falhas de extração deverão ser registradas para revisão, nunca preenchidas por geração automática.

### Recomendação determinística antes da geração

O serviço primeiro filtrará e ordenará receitas por cobertura dos ingredientes disponíveis, itens ausentes, restrições e preferências. A camada generativa receberá somente um conjunto limitado de receitas e deverá retornar referências, correspondências e lacunas. Assim, uma resposta não depende apenas da similaridade semântica e pode ser auditada.

### Inventário separado de normalização de ingredientes

O inventário da pessoa e os ingredientes das receitas serão entidades separadas. Um vocabulário canônico com aliases permitirá tratar variações como singular/plural e nomes equivalentes sem alterar o texto original da receita. Quantidades disponíveis ficam opcionais no primeiro corte; quando ausentes, o sistema considera disponibilidade binária e sinaliza a limitação.

### Respostas com rastreabilidade e limites explícitos

Toda recomendação conterá identificador e fonte da receita. Se a recuperação não atingir um limite mínimo de confiança ou não houver receita adequada, o sistema informará que não encontrou uma opção suficiente em vez de inventar uma. Adaptações serão apresentadas como sugestões claramente separadas da receita original e não serão persistidas como receitas oficiais.

## Risks / Trade-offs

- [Fonte muda ou fica indisponível] -> Manter versões coletadas, detectar conteúdo alterado e expor estado de atualização para revisão.
- [Aliases de ingredientes geram correspondências incorretas] -> Começar com aliases curados, registrar a origem da normalização e permitir correção manual.
- [Modelo alucina etapas ou ingredientes] -> Restringir o contexto aos documentos recuperados, exigir citações e validar a resposta contra os dados estruturados.
- [Busca vetorial retorna receitas semanticamente parecidas, mas inviáveis] -> Aplicar cobertura, restrições e itens ausentes como regras determinísticas antes da síntese.
- [GraphRAG aumenta complexidade sem benefício mensurável] -> Adiar a adoção e medir consultas sem resposta, precisão das relações e custo operacional do RAG híbrido.
- [Conteúdo do desafio possui licença ou regras de uso específicas] -> Confirmar permissões e manter atribuição e links da Vegan Outreach no produto.

## Migration Plan

Não há migração de dados existente. A implantação será incremental: definir o esquema canônico, ingerir um conjunto piloto de receitas, validar recuperação e recomendações, ampliar a ingestão e então liberar o fluxo para uso. O rollback da primeira versão consiste em desativar a geração e manter somente consulta ao catálogo; versões anteriores da base permitem reverter uma ingestão problemática.

## Open Questions

- Qual fonte e formato oficial serão usados para coletar as receitas do Desafio Vegano?
- Quais filtros iniciais são obrigatórios: alergias, preferências, tempo, utensílios ou porções?
- O inventário deve aceitar quantidades e validade já na primeira versão?
- Qual modelo de linguagem, provedor e política de retenção de dados serão aprovados?
- Quais métricas definirão precisão suficiente para decidir se GraphRAG é necessário?
