## 1. Recommendation Taxonomy and Configuration Foundation

- [x] 1.1 Define recommendation taxonomy constants in `src/auditoria_higiene/core.py` (`REMOVE`, `ADD_TO_GITIGNORE`, `FIX_REFERENCE`, `UPDATE_DOCS`, `ADD_CI`, `ARCHIVE_CHANGE`, `SCOPE_PERMISSIONS`, `INVESTIGATE`, `ACCEPT_FALSE_POSITIVE`)
- [x] 1.2 Ensure every existing rule function emits a typed `recomendacao` field matching the taxonomy
- [x] 1.3 Add `fontes_semanticas` config section parsing in `carregar_configuracao()` with defaults (`openwiki: null`, `graphify: null`, `openspec: true`)
- [x] 1.4 Update `_avaliar_regra()` to register the new `repositorios_aninhados` rule dispatching (skeleton that logs "not implemented" until slice 3)
- [x] 1.5 Add `repositorios_aninhados` rule entry to `auditoria.yaml` template (severity: error, enabled: true)
- [x] 1.6 Write unit tests in `tests_package/test_auditoria_package.py` verifying all rules emit typed `recomendacao`

## 2. Semantic Evidence Module

- [x] 2.1 Create `src/auditoria_higiene/semantic.py` with `carregar_referencias_openspec(raiz)` extracting file paths from `openspec/specs/**/*.md` and `openspec/changes/**/*.md`
- [x] 2.2 Add `carregar_referencias_graphify(raiz)` to `semantic.py` extracting nodes with `source_location` from `graphify-out/graph.json` when present
- [x] 2.3 Add `montar_evidencias(raiz, config)` to `semantic.py` orchestrating OpenSpec + Graphify + OpenWiki sources into a path→evidence dict with in-memory cache
- [x] 2.4 Modify `_verificar_sem_referencia()` in `core.py` to call `montar_evidencias()` and skip files that appear in OpenSpec or Graphify evidence
- [x] 2.5 Modify `_verificar_documentacao()` in `core.py` to cross-check paths against semantic evidence sources before reporting stale references
- [x] 2.6 Write unit tests in `tests_package/` for `carregar_referencias_openspec` and `carregar_referencias_graphify` with fixture data

## 3. Nested Repository Detection

- [x] 3.1 Implement `_verificar_repositorios_aninhados()` in `core.py` detecting untracked directories containing `.git` via `git ls-files --others --directory`
- [x] 3.2 Add `.gitmodules` and `.gitignore` cross-check logic: submodule references → classify as intended, gitignore match → skip, neither → classify as accidental
- [x] 3.3 Cross-reference with semantic evidence: directories mentioned in OpenSpec changes → classify as planned, not surplus
- [x] 3.4 Emit finding with `recomendacao: remove` for accidental clones, `recomendacao: investigate` for ambiguous cases
- [x] 3.5 Update `_deve_reportar_artefato()` to exclude nested repos already handled by the new rule
- [x] 3.6 Write integration test verifying a nested `.git` directory without `.gitmodules` entry triggers `remove` not `add-to-gitignore`

## 4. Workflow Intent Evaluation

- [x] 4.1 Modify `_analisar_workflow()` in `core.py` to inspect `jobs.*.steps` for GitHub CLI (`gh issue`, `gh release`) and action references (`actions/github-script`, `actions/create-release`)
- [x] 4.2 Add `_permissao_justificada()` helper: `issues: write` justified when workflow has issue-management steps; `contents: write` justified when workflow has release-creation steps
- [x] 4.3 Modify `_reportar_permissoes_inseguras()` to call `_permissao_justificada()` before emitting findings; `permissoes_write_permitidas` config still applies as fallback
- [x] 4.4 Emit `recomendacao: accept-false-positive` for justified permissions, `recomendacao: scope-permissions` for unjustified ones
- [x] 4.5 Write integration test with a realistic GitHub Actions workflow fixture that uses `issues: write` alongside `gh issue` steps and verifies no finding is emitted

## 5. Agent Hygiene Flow Skill Update

- [x] 5.1 Update triage matrix in `.opencode/skills/agent-hygiene-flow/SKILL.md`: `artefatos_fora_gitignore` now distinguishes remove (accidental content) from add-to-gitignore (generated artifacts)
- [x] 5.2 Update triage matrix for `workflows_inseguros`: add accept-false-positive action for justified operational permissions
- [x] 5.3 Add `repositorios_aninhados` rule to triage matrix with severity error and remediation action remove
- [x] 5.4 Document the new remediation action taxonomy in the skill: remove, add-to-gitignore, fix-reference, update-documentation, add-ci-integration, archive-change, scope-permissions, pin-action-version, investigate, accept-false-positive

## 6. Regression Tests for Documented False Positives

- [x] 6.1 Add test fixture: directory `principal-tarefas-aleatorias/quiz/.git` simulating accidental clone → verify `recomendacao: remove`, no `.gitignore` recommendation
- [x] 6.2 Add test fixture: GitHub Actions workflow with `issues: write` + `gh issue create` step → verify no `workflows_inseguros` finding
- [x] 6.3 Add test fixture: file referenced in `openspec/specs/*/spec.md` but not in other tracked files → verify no `arquivos_sem_referencia` finding
- [x] 6.4 Add test fixture: directory planned in unarchived `openspec/changes/*/proposal.md` → verify no `artefatos_fora_gitignore` finding
- [x] 6.5 Run full test suite and verify no regressions on existing passing tests
