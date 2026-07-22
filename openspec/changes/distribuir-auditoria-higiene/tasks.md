## 1. Fundação do pacote

- [x] 1.1 Definir nome do pacote, metadados, versões suportadas e estrutura `src/`
- [x] 1.2 Extrair o auditor atual para módulo reutilizável sem alterar seu contrato de saída
- [x] 1.3 Declarar `PyYAML` como dependência do pacote e configurar build/publicação
- [x] 1.4 Adicionar testes de contrato para execução, código de saída e mascaramento

## 2. CLI

- [x] 2.1 Implementar comando `audit` com caminho de repositório e configuração selecionáveis
- [x] 2.2 Implementar `--help`, validação de contexto e mensagens de erro acionáveis
- [x] 2.3 Adicionar testes de CLI para sucesso, falha e configuração inválida

## 3. Instalação no consumidor

- [x] 3.1 Criar template padrão de `auditoria.yaml` com regras e exceções
- [x] 3.2 Criar template de workflow consumidor com versão fixada do workflow reutilizável
- [x] 3.3 Implementar `install` com detecção de repositório Python e arquivos existentes
- [x] 3.4 Implementar `--dry-run`, confirmação, `--force` e comportamento idempotente
- [x] 3.5 Testar instalação em repositórios vazios, existentes e com customizações

## 4. Workflow e notificações

- [x] 4.1 Implementar workflow reutilizável central e template de workflow chamador com agenda, push/PR e acionamento manual
- [x] 4.2 Instalar e executar versão fixa do pacote no workflow
- [x] 4.3 Publicar Summary com agrupamento por severidade e mascaramento
- [x] 4.4 Criar, atualizar e fechar issue consolidada com permissões mínimas
- [x] 4.5 Cobrir forks e PRs externos sem permissão de escrita

## 5. Atualização e releases

- [x] 5.1 Marcar artefatos gerenciados e preservar exceções locais
- [x] 5.2 Implementar `update` com preview, confirmação e seleção de versão
- [x] 5.3 Implementar rollback para versão anterior
- [x] 5.4 Adicionar testes de atualização, idempotência e preservação de customizações
- [x] 5.5 Configurar changelog, tags, publicação no PyPI e documentação de releases

## 6. Migração e validação

- [x] 6.1 Testar instalação completa em repositório Python descartável
- [x] 6.2 Migrar o repositório original para consumir pacote e workflow centralizados
- [x] 6.3 Validar execução local, PR, push, agenda, Summary e issue consolidada
- [x] 6.4 Documentar instalação, configuração, atualização, rollback e limitações
