# Design

## Context

A decisão de status já recebe sinais de comentários e walkthrough, enquanto a recuperação registra arquivos cobertos em `reviewed_files`. Ver proposta para motivação; o contrato observável está em `specs/mira-review-gate/spec.md`.

## Goals / Non-Goals

**Goals:** alinhar o predicado `partial` com a cobertura recuperada e validar as transições de status no parser.

**Non-Goals:** alterar coleta de comentários, formato do payload ou política de blockers.

## Decisions

Usar `reviewed_files` não vazio como sinal de cobertura disponível no cálculo de status, junto dos sinais de comentários/walkthrough existentes. Alternativa rejeitada: inferir cobertura apenas de comentários ou walkthrough, pois isso descarta informação explicitamente recuperada.

Testar via parser os dois limites do contrato: payload recuperado com arquivos revisados e sem comentários/walkthrough resulta em `ok`; chunk descartado sem payload continua `partial`.

## Risks / Trade-offs

- [Cobertura vazia confundida com cobertura recuperada] → Condicionar a cobertura ao conteúdo efetivo de `reviewed_files`, não apenas à existência do payload.
