## Context

The artifact rule currently walks the complete working tree and invokes Git separately for each candidate file. Repositories containing dependency trees or generated tooling output can therefore spend an unbounded amount of time in subprocess startup and produce no output while the audit is running. Other rules also repeat equivalent tracked-file queries during one audit.

The change is performance-sensitive but behavior-preserving. It must work on Windows and existing supported Python versions, keep the current CLI and report contracts, and avoid adding runtime dependencies.

## Goals / Non-Goals

**Goals:**

- Make artifact detection use repository-level inventory operations rather than per-file Git calls.
- Reuse tracked-file inventory within one audit execution.
- Preserve artifact findings, severities, exit codes, and JSON, text, and SARIF structures.
- Retain a filesystem fallback for non-Git directories or unavailable Git.
- Cover large trees, ignore behavior, and fallback behavior with regression tests.

**Non-Goals:**

- Redesigning audit rules or changing their detection semantics.
- Adding a progress UI, new CLI options, or a new output format.
- Introducing a third-party `.gitignore` parser or another runtime dependency.
- Changing pre-commit snapshot semantics.

## Decisions

1. **Use Git-native inventory for Git repositories.** Artifact detection will obtain untracked, non-ignored paths through one repository-level Git query. This delegates ignore pattern semantics, including nested patterns and negations, to Git instead of extending the incomplete manual matcher. For non-Git directories, the existing filesystem traversal and ignore matcher remain the fallback. The artifact path query is bounded to one invocation per audit, independent of file count.

2. **Cache inventories per audit root.** A single audit-scoped tracked-file inventory will serve all rules that need tracked paths, with at most one tracked-file inventory query per audit. The cache will be created and discarded within one `executar_auditoria` call so repeated audits observe current state and results cannot leak between repositories.

3. **Keep the existing result contract.** The optimization changes collection strategy only. Result fields, configured severities, status calculation, exit codes, and report serialization remain unchanged.

4. **Treat generated local output as repository configuration.** `.opencode/node_modules/` and `graphify-out/` will be covered by the project's `.gitignore`, preventing local dependency and graph artifacts from being classified as unexpected artifacts. The auditor itself will not hard-code project-specific directories.

5. **Test at the repository boundary.** Tests will exercise real temporary Git repositories for tracked, ignored, and untracked paths, plus a non-Git temporary directory and a simulated Git command failure. A large-file-count regression test will instrument subprocess calls and assert at most one artifact inventory query plus one shared tracked inventory query, rather than relying only on microbenchmarks. CLI tests will cover text, JSON, SARIF, and exit codes `0`, `1`, and `2`.

## Risks / Trade-offs

- [Git output or Git availability differs across platforms] → Use machine-readable, null-delimited output where supported and retain the existing filesystem fallback for command failures.
- [The fallback matcher does not fully implement Git ignore semantics] → Restrict it to non-Git fallback paths and document Git as the authoritative path for Git repositories.
- [Inventory caching becomes stale during one audit] → Treat the working tree as an audit snapshot and scope cache lifetime to one `executar_auditoria` call.
- [Project `.gitignore` changes hide files users expected to inspect] → Ignore only generated local tooling output already identified as non-source artifacts; keep user-controlled source paths unaffected.
