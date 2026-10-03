# Tasks

## 1. Corrigir cálculo do status

- [x] 1.1 Atualizar a condição `partial` em `.github/workflows/mira-review-reusable.yml` para considerar `reviewed_files` recuperados como cobertura; verificar que o novo predicado implementa os dois cenários de `specs/mira-review-gate/spec.md`.
- [x] 1.2 Adicionar teste do parser com payload recuperado, zero comentários e walkthrough desligado, verificando status `ok`; e chunk descartado sem payload, verificando `partial`.

## 2. Validar contrato OpenSpec

- [x] 2.1 Executar `openspec validate fix-mira-partial-gate-contradiction` e corrigir os artefatos até a validação passar.
