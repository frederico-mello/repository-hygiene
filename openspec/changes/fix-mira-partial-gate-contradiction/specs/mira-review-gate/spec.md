# Spec Delta

## Purpose

Define como o gate de revisão MIRA identifica cobertura incompleta e distingue um chunk perdido sem recuperação de uma revisão recuperada sem comentários.

## ADDED Requirements

### Requirement: Cobertura recuperada impede veredito partial
O gate SHALL considerar um payload recuperado que contenha `reviewed_files` como cobertura da revisão, mesmo quando não houver comentários e o walkthrough estiver desativado. O veredito SHALL ser `partial` somente quando a cobertura estiver ausente por chunk descartado sem payload recuperável.

#### Scenario: Payload recuperado cobre revisão limpa
- **WHEN** um chunk descartado tem payload recuperado com `reviewed_files`, zero comentários e walkthrough desativado
- **THEN** o veredito é `ok`, não `partial`

#### Scenario: Chunk descartado sem payload recuperável
- **WHEN** um chunk é descartado e não existe payload recuperável que forneça cobertura
- **THEN** o veredito é `partial`
