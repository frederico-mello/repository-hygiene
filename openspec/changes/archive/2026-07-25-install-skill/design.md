## Context

`repository-hygiene` is a Python package that ships hygiene tooling for Git
repositories. It already bundles `auditoria.yaml`, `commit-msg`, `pre-commit`,
and `workflow.yml` as package data under `src/auditoria_higiene/templates/`,
and the `install` subcommand writes those files into the target repo using
the importlib.resources accessor.

The OpenCode skill `agent-hygiene-flow` lives in
`auditoria-higiene/.opencode/skills/agent-hygiene-flow/SKILL.md` and is the
documented entry point for the agent-driven hygiene remediation flow. Today
the skill is not packaged: users who install `repository-hygiene` in another
repo have to copy `SKILL.md` by hand, which bypasses the package's version
pinning and breaks the "out of the box" expectation.

The change is small and self-contained: bundle the skill in package data
(alongside the existing templates) and have the `install` subcommand copy it
into `<repo>/.opencode/skills/agent-hygiene-flow/` using the same skip /
overwrite / dry-run semantics already used for the other template files.

## Goals / Non-Goals

**Goals:**
- Bundle the `agent-hygiene-flow` skill files inside the Python distribution
  so they travel with the package version.
- Make the `install` subcommand provision the skill into the target repo.
- Reuse the existing install semantics (skip, `--force`, `--dry-run`) so the
  skill provisioning is invisible to the user except in the report.

**Non-Goals:**
- No new CLI subcommand (skill is reached via existing `install` flow).
- No removal / uninstall flow.
- No version-check or auto-sync of an already-provisioned skill.
- No changes to OpenCode, its global config, or other repos' skills.

## Decisions

- **Package data location:** place the bundled skill at
  `src/auditoria_higiene/templates/skills/agent-hygiene-flow/SKILL.md` so it
  mirrors the existing `templates/` layout and is picked up by the same
  MANIFEST / `package-data` rule.
  - Alternative considered: a new top-level `skills/` package alongside
    `templates/`. Rejected because it splits the file-distribution surface
    into two places and forces callers to learn two resource paths.
- **Resource accessor:** `importlib.resources.files(
  "auditoria_higiene.templates")` joins the existing `auditoria_higiene`
  resource walk used elsewhere in the codebase. The new skill files are
  reachable as `templates_root / "skills" / "agent-hygiene-flow" / "SKILL.md"`.
- **Single-skill MVP:** the implementation ships exactly one skill,
  `agent-hygiene-flow`. A future change can add more by dropping files under
  `templates/skills/<name>/`; the copy walker discovers them generically.
- **Reuse `cmd_install`:** the skill copy step is appended at the end of the
  existing `cmd_install` (init.py) so it inherits the same operating
  directory, `--force`, and `--dry-run` semantics. No new CLI flags.
- **Skip on existing:** the same `cmd_install` already approaches existing
  files as "report and skip" with `--force` opt-in. The skill step follows
  the same pattern, with the destination being the directory
  `<repo>/.opencode/skills/agent-hygiene-flow/` instead of a single file.
- **Reporting:** the user-visible report gains a line such as
  `Skill instalado: .opencode/skills/agent-hygiene-flow/` so the user knows
  the skill shipped; no separate verbosity level.

## Risks / Trade-offs

- [Risk] Path safety: copying into a path under `.opencode/` requires using
  the existing `caminho_seguro` helper to avoid traversal. → Mitigation: pass
  the destination through `caminho_seguro` like the other template steps.
- [Risk] Filesystem permissions on `.opencode/` may be restricted in some
  workflows. → Mitigation: surface the OSError from the existing install
  pipeline, which already exits with code 2 on FS errors.
- [Risk] Bundle drift: the bundled skill can diverge from the version in the
  developing repo. → Mitigation: the bundle file is the single source of
  truth; updating the skill is a normal code change in this repo and ships
  with the next release. Document this in the design to set expectations.
- [Risk] Larger install footprint: adding a multi-KB file to the wheel. →
  Mitigation: the skill is small (~8 KB) and the wheel already includes
  several templates; the added weight is negligible.
