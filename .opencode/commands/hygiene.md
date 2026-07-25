---
description: Run the repository hygiene audit-and-remediation loop. Accepts an optional repository target or hygiene objective.
---

Execute the repository hygiene flow as defined in the `agent-hygiene-flow` skill.
Follow that skill's full instruction set — including target verification, audit
execution, canonical report consumption, triage by severity, remediation per
rule, worktree isolation, re-audit, termination conditions, and temporary
artifact cleanup.

If a repository target or hygiene objective is supplied, apply the flow to that
target. Otherwise, audit the current repository.
