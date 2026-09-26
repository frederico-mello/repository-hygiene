## Why

As receitas do Desafio Vegano estão publicadas de forma dispersa e não ajudam diretamente a pessoa a decidir o que pode preparar com os ingredientes que já possui. Esta mudança cria uma experiência de descoberta personalizada, baseada exclusivamente no conhecimento das receitas publicadas pela Vegan Outreach, reduzindo desperdício e facilitando a adoção de refeições veganas.

## What Changes

- Criar uma base de conhecimento com as receitas publicadas no Desafio Vegano, preservando ingredientes, preparo, porções e metadados relevantes.
- Permitir que a pessoa cadastre e mantenha os ingredientes disponíveis.
- Gerar recomendações de receitas compatíveis com os ingredientes informados, indicando correspondências e eventuais itens ausentes.
- Permitir interação em linguagem natural para solicitar adaptações ou priorizar receitas conforme as possibilidades da pessoa.
- Definir no design a arquitetura de recuperação de conhecimento mais adequada entre RAG e GraphRAG, com critérios de qualidade, rastreabilidade e manutenção.

## Capabilities

### New Capabilities

- `recipe-catalog`: ingestão, normalização, armazenamento e consulta das receitas do Desafio Vegano.
- `ingredient-inventory`: cadastro e gerenciamento dos ingredientes disponíveis pela pessoa.
- `personalized-recommendations`: geração de recomendações de receitas baseadas no inventário e nas restrições informadas.
- `recipe-assistant`: interação conversacional para explicar recomendações e apoiar adaptações sem inventar informações fora da base de conhecimento.

### Modified Capabilities

Nenhuma. Não existem capacidades especificadas anteriormente neste projeto.

## Impact

- Introduz o domínio de receitas, ingredientes, preferências, restrições e recomendações.
- Exige pipeline de ingestão e atualização da base de conhecimento a partir das publicações do Desafio Vegano.
- Exige camada de recuperação e geração, possivelmente com banco vetorial, grafo de conhecimento ou arquitetura híbrida.
- Exige interfaces de API e UI para inventário, busca, recomendações e conversa.
- Pode introduzir dependências de modelo de linguagem, embeddings, armazenamento vetorial/grafo e observabilidade de respostas.
- A origem das receitas deverá ser rastreável para permitir confiança, revisão e atualização do conteúdo.
