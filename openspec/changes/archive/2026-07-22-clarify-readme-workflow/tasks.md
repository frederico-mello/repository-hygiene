## 1. Corrigir integração gerada

- [x] 1.1 Atualizar `src/auditoria_higiene/templates/workflow.yml` para capturar códigos de saída 1 e 2 sem interromper a publicação do relatório.
- [x] 1.2 Adicionar ou ajustar testes que verifiquem os marcadores essenciais de tratamento de falha no template.

## 2. Reorganizar e alinhar documentação

- [x] 2.1 Reordenar `README.md` para apresentar `--init`, revisão da configuração, auditoria e integrações opcionais nessa sequência.
- [x] 2.2 Atualizar exemplos de configuração com opções suportadas pelo template, incluindo padrões de artefatos e permissões write permitidas.
- [x] 2.3 Corrigir descrições de formatos, saída padrão, sanitização, workflow e códigos de saída para refletir a CLI e o template atuais.

## 3. Validar mudança

- [x] 3.1 Executar a suíte `uv run pytest tests_package/` e corrigir regressões.
- [x] 3.2 Validar que a especificação de documentação está coberta por testes ou verificações de conteúdo reproduzíveis.
