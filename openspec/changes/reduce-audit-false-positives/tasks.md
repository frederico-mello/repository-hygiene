## 1. Contexto e modelo de resultados

- [x] 1.1 Definir classificação comum de caminhos para testes, fixtures, exemplos, OpenSpec e artefatos gerados
- [x] 1.2 Adicionar confiança e evidências ao modelo de resultado sem remover campos existentes
- [x] 1.3 Atualizar cálculo de status para considerar apenas erros de confiança alta ou média
- [x] 1.4 Adicionar opções de configuração para exclusões, padrões de artefatos e permissões de workflow

## 2. Detecção de segredos

- [x] 2.1 Separar padrões fortes de credenciais de padrões fracos de exemplo
- [x] 2.2 Ignorar ou rebaixar fixtures, exemplos e valores deliberadamente sintéticos conforme contexto configurado
- [x] 2.3 Preservar detecção de credenciais em código e configurações operacionais
- [x] 2.4 Adicionar testes RED-GREEN para fixtures de teste e credenciais operacionais

## 3. Referências e documentação

- [x] 3.1 Restringir referências inexistentes a contextos reconhecidos de caminhos
- [x] 3.2 Excluir mensagens, asserts, comandos, versões, módulos, URLs e nomes de fixtures da detecção genérica
- [x] 3.3 Reutilizar resolução segura de caminhos para links Markdown e referências de arquivo
- [x] 3.4 Adicionar testes para links quebrados, versões, comandos e referências em testes

## 4. Arquivos sem referência

- [x] 4.1 Detectar referências estruturais de imports Python, workflows, entry points e relações OpenSpec
- [x] 4.2 Classificar ausência de referência como heurística de baixa confiança
- [x] 4.3 Evitar marcar arquivos usados por referências indiretas conhecidas
- [x] 4.4 Adicionar testes para módulos importados e documentos realmente sem referências

## 5. Artefatos e workflows

- [x] 5.1 Fazer artefatos fora do `.gitignore` considerarem apenas caminhos não rastreados e padrões gerados configurados
- [x] 5.2 Evitar classificação de diretórios-fonte rastreados como artefatos gerados
- [x] 5.3 Avaliar permissões de workflow contra scopes permitidos e detectar apenas permissões amplas ou perigosas
- [x] 5.4 Adicionar testes para caches não ignorados, código rastreado e `issues: write` permitido

## 6. Relatórios e validação

- [x] 6.1 Exibir confiança e evidência no JSON, terminal e demais formatos de relatório
- [x] 6.2 Atualizar configuração e documentação com políticas padrão e overrides
- [x] 6.3 Executar suíte completa de testes e corrigir regressões
- [x] 6.4 Reexecutar auditoria no repositório e comparar redução de falsos-positivos com baseline
