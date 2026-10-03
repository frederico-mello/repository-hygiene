## 1. Multi-Destination Skill Provisioning

- [x] 1.1 Add a single source of truth for supported agent roots (`.opencode`, `.kilocode`, `.kilo`, `.omp`, `.hermes`) shared by `init.py` and `core.py`.
- [x] 1.2 Make `_instalar_skills` and `_dry_run_msg_skills` provision/report every selected destination, defaulting to the agent roots present in the target repository with `.opencode` fallback, evaluated per destination.
- [x] 1.3 Add the `--agents` CLI option to `install`/`install-skill` (comma-separated selection) and surface the full destination list in `--dry-run` output.
- [x] 1.4 Extend `tests_package/test_install_skill.py` for multi-destination provisioning, explicit selection, per-destination skip, forced overwrite, and dry-run listing every destination.

## 2. Audit Scope Covers Agent Directories

- [x] 2.1 Extend `_em_diretorio_ruidoso_referencias` in `core.py` with `commands/` and `skills/openspec-` prefixes for the five agent roots, plus `.kilocode/workflows/`.
- [x] 2.2 Extend `_eh_diretorio_fonte` in `core.py` to accept the five agent roots instead of only `src/`, `.github/`, `.opencode/`, `openspec/`.
- [x] 2.3 Add tests proving files under agent directories are not reported as untracked artifacts and that reference enforcement is skipped only in command/openspec-skill paths, while the `agent-hygiene-flow` skill stays enforced.

## 3. Workflow Template Triggers

- [x] 3.1 Add the five agent roots to the `push` and `pull_request` path filters in `templates/workflow.yml`.
- [x] 3.2 Add a template test asserting every supported agent root appears in both trigger lists.

## 4. Documentation And Verification

- [x] 4.1 Update `README.md` skill and workflow documentation for multi-agent provisioning and the `--agents` option.
- [x] 4.2 Run the complete test suite and `openspec validate agent-agnostic-provisioning` before implementation is considered complete.
