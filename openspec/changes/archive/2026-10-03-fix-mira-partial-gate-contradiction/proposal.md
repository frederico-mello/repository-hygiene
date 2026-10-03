# Proposal

## Why

O gate da revisão MIRA contradiz a própria regra documentada: informa que `reviewed_files` recuperados contam como cobertura, mas calcula `partial` ignorando essa cobertura. Em revisões limpas com chunk descartado e payload recuperável, isso reprova deterministicamente o gate `block-on-blocker`, mesmo sem blockers.

## What Changes

- Fazer a decisão `partial` considerar cobertura recuperada por `reviewed_files`, além de comentários e walkthrough.
- Definir o contrato da cobertura: somente chunk descartado sem payload recuperável deixa a revisão `partial`.
- Cobrir o caso limpo com teste do parser e validar os artefatos OpenSpec.

## Capabilities

### New Capabilities
- `mira-review-gate`: Comportamento do veredito de cobertura no gate de revisão MIRA.

### Modified Capabilities

## Impact

- `.github/workflows/mira-review-reusable.yml`, na condição que determina o status `partial`.
- Teste do parser da saída/payload de revisão MIRA.
- Contrato OpenSpec do novo capability `mira-review-gate`.
