## 1. Bundle the skill

- [ ] 1.1 Copy `agent-hygiene-flow/SKILL.md` into
      `src/auditoria_higiene/templates/skills/agent-hygiene-flow/SKILL.md`
      so the file ships with the package.

## 2. Provisioning logic

- [ ] 2.1 Add a `cmd_install_skill(directory, force, dry_run)` helper in
      `src/auditoria_higiene/init.py` that copies the bundled skill from
      `auditoria_higiene.templates/skills/agent-hygiene-flow/` into
      `<directory>/.opencode/skills/agent-hygiene-flow/`, honoring the same
      skip / `--force` / `--dry-run` semantics as the existing template
      steps.
- [ ] 2.2 Wire the new helper into `cmd_install` so it runs after the
      existing config + workflow copy steps, and add a one-line report to
      the user-visible output.

## 3. Packaging

- [ ] 3.1 Update `pyproject.toml` so the `templates/skills/**` tree is
      included in the built wheel (package-data whitelist).

## 4. Tests

- [ ] 4.1 Add a test that runs `cmd_install` on a clean directory and
      asserts the skill file is present at the destination path.
- [ ] 4.2 Add a test that re-runs `cmd_install` without `--force` and
      asserts the existing skill file is preserved verbatim.
- [ ] 4.3 Add a test that runs `cmd_install --force` and asserts the
      existing skill file is overwritten with the bundled version.
- [ ] 4.4 Add a test that runs `cmd_install --dry-run` and asserts no
      files are written under `.opencode/`.
- [ ] 4.5 Add a test that imports `repository_hygiene` from a wheel built
      with the new package data and asserts the skill resource is
      reachable via `importlib.resources`.

## 5. Docs and release

- [ ] 5.1 Update `README.md` so the installation section explains that the
      `agent-hygiene-flow` skill is provisioned by `repository-hygiene
      install`.
- [ ] 5.2 Run the full test suite, lint, and SonarQube check before
      opening the PR.
