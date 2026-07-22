## 1. Fast artifact audit for large repositories

- [x] 1.1 Replace per-file artifact Git checks with repository-level detection of untracked, non-ignored paths while preserving finding fields and configured severity
- [x] 1.2 Reuse tracked-file inventory across enabled rules within one audit execution without leaking inventory between roots
- [x] 1.3 Add temporary-Git-repository coverage for tracked files, ignored directories, untracked files, and large untracked trees after the inventory implementation is complete
- [x] 1.4 Instrument Git interactions and verify a repository containing thousands of ignored and unignored files uses at most one artifact inventory query plus one shared tracked inventory query
- [x] 1.5 Run two audits against the same root with a changed working tree and verify the second result does not use stale inventory

## 2. Generated output remains outside routine audit scope

- [x] 2.1 Extend project ignore configuration with `.opencode/node_modules/` and `graphify-out/`
- [x] 2.2 Add regression coverage proving those ignored generated directories do not produce artifact findings while unignored files still do
- [x] 2.3 Run the normal CLI in text, JSON, and SARIF modes against the project and verify clean, error, and configuration-failure exit codes remain `0`, `1`, and `2`

## 3. Non-Git compatibility remains functional

- [x] 3.1 Preserve filesystem fallback when Git is unavailable or the target directory is not a repository
- [x] 3.2 Add non-Git audit coverage and simulated Git-command-failure coverage for artifact detection and existing rule execution
- [x] 3.3 Verify fallback failures are converted into normal audit results rather than unhandled exceptions
