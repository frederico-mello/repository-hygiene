## Why

After `pip install repository-hygiene` in a target repository, the OpenCode
skill `agent-hygiene-flow` is not available there. Users must manually copy it
from another repo, which is friction-prone and causes version drift between the
skill and the Python tool that powers it. The skill is the documented entry
point for the agent to run the hygiene remediation flow, so its absence breaks
the out-of-the-box experience for every new repo that adopts the package.

## What Changes

- Ship the `agent-hygiene-flow` skill inside the Python distribution so it
  travels with the package version users install.
- Extend the `install` flow so that, after it runs in a target repo, the
  `agent-hygiene-flow` skill is available to the agent in that repo.
- Apply the same skip-or-overwrite semantics that `install` already uses for
  its other files, so the new step is consistent with existing user
  expectations.

## Non-Goals

- No new top-level CLI subcommand is introduced; the skill provisioning is
  reached through the existing `install` flow.
- No removal or "uninstall" flow for the skill.
- No automatic re-sync of an already-provisioned skill when the package is
  upgraded; the user must opt into overwrite with the existing `--force` flag.
- No changes to the OpenCode runtime, its global config, or skills owned by
  other repositories.
- No new release / publication workflow for the package.

## Capabilities

### New Capabilities

- `skill-provisioning`: makes the `agent-hygiene-flow` skill available to the
  agent in the target repository as part of the existing `install` flow. The
  capability is responsible for delivering the skill files into the location
  where OpenCode loads them, and for honoring the install flow's skip /
  overwrite / dry-run semantics.

### Modified Capabilities

(none)

## Impact

- Affected area: the `install` user-facing flow of the CLI.
- Affected area: the Python distribution's payload (a new skill artifact
  ships with the package).
- Affected area: the test suite (new coverage for the new behavior).
