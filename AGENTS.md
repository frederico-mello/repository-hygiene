## Conventional Commits

All commit messages MUST follow the Conventional Commits format:

```
<type>(<optional-scope>): <description>
```

Breaking changes use `!` before `:`:

```
<type>(<optional-scope>)!: <description>
```

### Accepted Types

- `feat` — new feature (MINOR bump in semantic versioning)
- `fix` — bug fix (PATCH bump)
- `docs` — documentation only
- `style` — formatting, missing semicolons, etc. (no production code change)
- `refactor` — code restructuring (no functional change)
- `perf` — performance improvement
- `test` — adding/updating tests
- `chore` — maintenance, tooling, dependencies
- `ci` — CI/CD configuration
- `build` — build system or external dependencies

### Examples

```
feat: add user authentication
feat(auth): add OAuth2 support
fix(api): handle rate limiting correctly
docs: update README installation guide
feat!: drop Python 3.8 support
refactor(core): extract validation logic
```

### Scope

Scope is optional but encouraged for larger changes. Use the module or
component name in parentheses (e.g., `feat(auth):`, `fix(api):`).

### Breaking Changes

Add `!` after the type/scope to indicate a breaking change:

```
feat!: replace config format with YAML
feat(api)!: remove deprecated endpoints
```

The commit body should also include `BREAKING CHANGE:` for the changelog.
