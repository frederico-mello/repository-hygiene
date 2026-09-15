# CHANGELOG


## v0.6.2 (2026-09-15)

### Bug Fixes

- **mira-ci**: A discarded chunk is not a clean review
  ([`d7d9c40`](https://github.com/frederico-mello/repository-hygiene/commit/d7d9c401b84296718cbb9215ad629d65d3a204c0))

Caught this on a live fleet run (repository-hygiene PR #103). The job went green reporting status=ok
  with 0 comments, while the log said:

mira.core.engine WARNING: Chunk 1/1 failed to parse, skipping: LLM response is not valid JSON (even
  after repair)

The model answered in prose instead of calling the tool, Mira dropped the entire chunk, and the run
  still exited 0 — so 'nothing found' was indistinguishable from 'never actually reviewed'. That is
  the same class of silent false-green this workflow exists to eliminate, and it survived my earlier
  fixes because I was only checking whether a payload existed, not whether the review covered the
  diff.

Zero comments now only reports ok when nothing was discarded. Otherwise the status is 'partial' and
  the step summary carries how many chunks were dropped plus an explicit note that the 0-comment
  result is incomplete, not clean.

Parser re-validated on seven scenarios: ok, failed, clean, warnings-only, quota,
  discarded-chunks-only, and partial-with-findings.


## v0.6.1 (2026-09-15)

### Bug Fixes

- **mira-ci**: Point this repo's caller at @main
  ([`e86b31f`](https://github.com/frederico-mello/repository-hygiene/commit/e86b31fa4ac6c7e82e85012607f117a329acb3f3))

The caller was pinned to @ci/mira-reusable-workflow while the reusable workflow was under review.
  That branch was deleted in the squash merge of #521, so the caller resolved to a nonexistent ref
  and the run failed with ZERO jobs — the workflow could not even start.

Repos that received the caller after the merge already point at @main; this repo was the only one
  left on the dead branch, and it is the host of the workflow, so it was the natural place to
  notice.

### Chores

- **openspec**: Archive english-source-localization + sync specs
  ([`755a4a8`](https://github.com/frederico-mello/repository-hygiene/commit/755a4a811e1527109089fa7e89b8adcc8c831a54))

Move change english-source-localization to openspec/changes/archive/. Sync delta specs: create new
  english-source-locale capability spec, apply MODIFIED+ADDED requirements to
  documentation-consistency spec.

### Continuous Integration

- **mira**: Reusable AI code-review workflow for all repos
  ([`0acb161`](https://github.com/frederico-mello/repository-hygiene/commit/0acb161f77adeb9dc1c926d792509810d9171850))

* ci(mira): reusable AI code-review workflow for all repos

Centralizes Mira (miracodeai/mira) PR review so every repo calls one workflow instead of carrying a
  copy.

Two things this encodes that the previous per-repo attempt (agente-suporte-ict) missed, both
  verified locally against the real endpoint:

- OpenCode Go (Zen) now rejects requests without an x-opencode-session header (HTTP 400
  MissingSessionID). Mira bundles only an openrouter provider profile, so the workflow generates
  providers.json and points MIRA_PROVIDERS_JSON_PATH at it, with a stable per-repo-per-PR session id
  for prompt-cache routing. - `mira review --config FILE` disables per-repo .mira.yaml
  auto-discovery, so passing a fixed deployment file would silently discard repo-local tuning. The
  workflow merges its defaults with the repo's .mira.yaml and passes the result, and refuses
  llm.base_url / llm.api_key_env from the repo file.

Advisory by default (blockers are reported, not enforced); callers opt into a merge gate with
  block-on-blocker: true.

* ci(mira): call the reusable workflow from this repo

Pins @ci/mira-reusable-workflow while the reusable workflow is under review; flip to @main once PR
  #521 merges. Also drops a .mira.yaml so the review behaviour for this repo is versioned alongside
  the code.

* fix(mira-ci): decide on the review payload, not on the exit code

Verified failure mode: Mira exits 1 for BOTH cases — sys.exit(1) when it finds blockers, and
  click.ClickException when the LLM call fails. Treating '>1 as failure' therefore let an
  operational failure pass as a clean review in advisory mode, which is exactly the silent failure
  that made the earlier per-repo workflow useless.

The step now runs with --output json, extracts the payload from the log-interleaved stdout (Mira
  logs to stdout, so warnings can precede or wrap the JSON), and fails loudly when no payload is
  present. Outputs status/comments/ blockers drive both the summary and the opt-in merge gate, so a
  gate can no longer be satisfied by a review that never ran.

Tested against four scenarios: interleaved logs + payload, no payload, clean review, warnings-only.

* fix(mira-ci): raise the LLM timeout and configure a fallback model

Root-caused the failure that produced 'LLM tool-call failed with <model>: ' with an EMPTY message.
  It is not a tool-calling or schema failure: httpx's TimeoutError stringifies to nothing, and
  Mira's error template puts the exception into the message slot. --verbose shows the real cause:

httpcore.http11 DEBUG: receive_response_headers.failed exception=ReadTimeout(TimeoutError())

Mira's default llm.request_timeout is 120s, which a slow endpoint exceeds on large tool-call
  payloads. A raw probe of the same endpoint with a tools array succeeds (finish_reason:
  tool_calls), which is what made the model look guilty.

- request_timeout: 300, max_retries: 5, retry_max_wait: 60 - fallback_model is now a workflow input
  (default minimax-m3), since the measured failure mode is intermittent, not deterministic - the
  summary reports which fallback is configured

Also noted for sizing: Mira sends a forced tool_choice first and re-sends with auto when the
  provider rejects it ('Model X rejected forced tool_choice'), so every call to such a provider
  costs two round trips.

* feat(mira-ci): report quota exhaustion distinctly from other failures

Hit this while measuring reliability: after ~20 consecutive reviews, every model started failing
  instantly with

HTTP 429 GoUsageLimitError: 5-hour usage limit reached. Resets in 3hr 57min.

OpenCode Go enforces per-model 5-hour and weekly windows, so a burst of PRs can exhaust the quota
  and every review then fails. That is a routine condition, not a code finding and not a broken
  reviewer, so the step now classifies it and the step summary says plainly that it is not a finding
  and to re-run after the window resets.

This also means reliability numbers measured in a burst are contaminated: the first model measured
  cleanly (minimax-m3, 5/5 payloads) while every model after the quota ran out failed 100%.
  Re-measure serially with quota headroom.

* fix(mira-ci): pick models by 5-hour budget, not just by quality

The --pr measurements are explained by OpenCode Go's documented per-model windows, which differ by
  ~20x:

minimax-m3 3,200 req/5h $60/mo qwen3.8-flash 5,400 req/5h $30/mo deepseek-v4-pro 1,050 req/5h $15/mo
  glm-5.3 220 req/5h $15/mo qwen3.8-max 160 req/5h $15/mo

A single review costs many calls: Mira sends a forced tool_choice, the provider rejects it, and Mira
  re-sends with auto, plus separate security and indexing passes. On the small-budget models a
  reliability sweep therefore exhausts the window after a handful of reviews — which is exactly the
  NOPAYLOAD pattern observed: the small-window models failed first, and the same model failed twice
  in a row rather than intermittently.

Defaults now favor budget headroom: minimax-m3 primary (3,200 req/5h) with qwen3.8-flash fallback
  (5,400 req/5h, different family so it is not exhausted alongside the primary).

* fix(mira-ci): pin the Mira install by commit SHA

SonarQube flagged githubactions:S8544 (MAJOR) at this line: 'Using dependencies without locking
  resolved versions is security-sensitive'. Fair finding — the install was pinned to a movable tag.

Resolved the tag to its commit and pinned that: v0.9.0 = 6410f596251ccc7df8 6fbf10234aff1a9225fa80
  (the tag is a lightweight ref straight to a commit, so no dereference needed). A tag can be
  repointed after review; a SHA cannot.

Note the tag/version drift this exposed: that SHA's tree reports mira 0.8.0, because
  pyproject/__init__ were not bumped for the v0.9.0 tag. The pin is accurate; the reported version
  is not.

* fix(mira-ci): quota exhaustion is a warning, not a failed check

The quota branch failed the step, which means every PR opened during a 5-hour window would show a
  red 'mira / review' check. A red X that is nobody's fault teaches people to ignore the check, and
  then the red X stops meaning anything when it IS their fault.

Quota now warns and exits 0. This is not a false green: status=quota is reported in the step
  summary, and a caller gating on blockers still cannot pass because the gate requires status ==
  'ok'. Real failures (no payload, not quota) still fail the step.

Parser re-validated on all five scenarios: ok/blockers, failed, clean, warnings-only, quota.

* fix(mira-ci): pin Mira inline so the pin is auditable

SonarCloud kept flagging S8544 on the install line even after the tag was resolved to a SHA, because
  the pin sat behind ${{ inputs.mira-ref }} — an analyzer cannot verify an indirection, and worse, a
  caller could pass a branch and silently defeat the pin that a reviewer approved.

The version is now a literal commit SHA on the install line and the mira-ref input is gone. Updating
  Mira means resolving the new tag and changing the SHA in a reviewed PR. This is deliberate
  friction: reviewers should see exactly which revision runs.

---------

Co-authored-by: Frederico Maciel de Mello <frederico.mello@unifesp.br>


## v0.6.0 (2026-07-26)

### Features

- English only localization
  ([`812e7e2`](https://github.com/frederico-mello/repository-hygiene/commit/812e7e2db4c5581b9ada4cd4ba43d413f93616bc))

- Implements change `` - Archived to openspec/changes/archive/


## v0.5.0 (2026-07-25)

### Bug Fixes

- Reduce cognitive complexity and validate file paths
  ([`c67cf2d`](https://github.com/frederico-mello/repository-hygiene/commit/c67cf2d776a2ec9a4d90eea4be7898a764684e73))

- Extract `_processar_ref_doc` from `_verificar_refs_doc_em_arquivo` (16→15) - Extract
  `_subdir_contem_nome` and `_arquivo_contem_texto` from `_dir_mencionada_em_openspec` (20→15) - Add
  path validation in semantic.py before glob and file open to prevent path traversal
  (pythonsecurity:S8707)

### Chores

- Archive reconcile-hygiene-semantic-audit
  ([`8e85923`](https://github.com/frederico-mello/repository-hygiene/commit/8e859238938d143685e288026e65cf06ef51b1c1))

- Resolve merge conflict in openspec/config.yaml
  ([`125b639`](https://github.com/frederico-mello/repository-hygiene/commit/125b639f42f4b0d75297c9ba6213c445080d352b))

- **openspec**: Arquivar change install-skill e sincronizar spec
  ([`1120bf6`](https://github.com/frederico-mello/repository-hygiene/commit/1120bf6464fb4385937a3fd594d5c9a9d25ec94e))

### Documentation

- Reescrever README conciso — PT só, fluxo linear, aviso pip install
  ([`f0dd747`](https://github.com/frederico-mello/repository-hygiene/commit/f0dd747c689a73221b79c12aae87afea368b7310))

Remove duplicacao PT/EN (Instalacao + Installation & Execution). Remove instrucoes de venv
  redundantes. Adiciona aviso: apos pip install, executar repository-hygiene install . Reorganiza em
  fluxo linear: instalar → usar (init/audit/hook) → configurar. 336 → 160 linhas.

### Features

- Semantic repository reconciliation audit
  ([`b00896b`](https://github.com/frederico-mello/repository-hygiene/commit/b00896bf5f9151dc28cf97b5360726cdaeb9b2ac))

Add nested repo detection, workflow intent evaluation, semantic evidence cross-referencing with
  OpenSpec/Graphify, typed recommendation taxonomy, and updated agent-hygiene-flow skill.

- New: semantic-repository-reconciliation spec + semantic.py module - Modified:
  context-aware-audit-findings, agent-hygiene-flow, documentation-consistency specs - Core: taxonomy
  constants, nested repo rule, workflow permission justification - Tests: 32+ new tests across
  test_auditoria_package.py and test_semantic.py


## v0.4.0 (2026-07-25)

### Features

- **install**: Provisionar skill agent-hygiene-flow no alvo
  ([`c554d6d`](https://github.com/frederico-mello/repository-hygiene/commit/c554d6da34317bd6fa688357818c271ab6484032))

Adiciona a skill OpenCode agent-hygiene-flow como package data e provisiona em
  .opencode/skills/agent-hygiene-flow/ durante o 'repository-hygiene install'. Reutiliza a semantica
  de skip/force/dry-run ja existente. A versao empacotada com o pacote fixa a versao da skill
  entregue.


## v0.3.0 (2026-07-25)

### Bug Fixes

- Add --only-binary to workflow pip installs
  ([`c87adbd`](https://github.com/frederico-mello/repository-hygiene/commit/c87adbd4d3f756d11526c7d8391e020fe06454ac))

- Address quality gate findings
  ([`51ccd5c`](https://github.com/frederico-mello/repository-hygiene/commit/51ccd5cc4c96bf90cf624419aeb02065821e5926))

- Align agent report metadata
  ([`d215edc`](https://github.com/frederico-mello/repository-hygiene/commit/d215edce657f89fa0f88a1339ae225c414c275f9))

- Avoid scanning ignored directories
  ([`d50bc2a`](https://github.com/frederico-mello/repository-hygiene/commit/d50bc2a81363d8ff260d2d947adf92c3e9430ca3))

- Clarify git-wt as Worktrunk with AGENTS.md reference
  ([`c183182`](https://github.com/frederico-mello/repository-hygiene/commit/c183182ec1f70b3e30900038139cbd7d5b43949d))

- Deduplicate git_repo fixture — extract to conftest.py
  ([`5463324`](https://github.com/frederico-mello/repository-hygiene/commit/5463324fb6bd05580a877165aead7fe4822fbaba))

SonarCloud Quality Gate: 19.3% duplicated lines (threshold 3%). git_repo fixture was duplicated
  across test_auditoria_package.py and test_commit_check.py. Moved to shared conftest.py.

- Detect quoted documentation paths
  ([`2d316f2`](https://github.com/frederico-mello/repository-hygiene/commit/2d316f2cb566033d1e3a13bae599ee8542a05a06))

- Harden audit workflow
  ([`bb735af`](https://github.com/frederico-mello/repository-hygiene/commit/bb735aff84e3589b21b0544856d67bedb4467f15))

- Ignore auditoria-report.txt generated by CI
  ([`e84a937`](https://github.com/frederico-mello/repository-hygiene/commit/e84a9374cd8fc82aceafdacf780103b49ba2d899))

- Mark validated report path sinks
  ([`cbc06b1`](https://github.com/frederico-mello/repository-hygiene/commit/cbc06b112fac378ced6a5806d7d798678c6876d4))

- Pin CI dependency versions for SonarQube
  ([`dd8aa48`](https://github.com/frederico-mello/repository-hygiene/commit/dd8aa4885cabb284b46e5eada3faa6d2aa7b62d7))

- Pin repository-hygiene to exact version 0.2.0 for SonarQube
  ([`eb074b2`](https://github.com/frederico-mello/repository-hygiene/commit/eb074b22fd0ec07ca6ed56124fe06ffeedfb027e))

- Pin repository-hygiene to minimum version 0.3.0
  ([`49cef22`](https://github.com/frederico-mello/repository-hygiene/commit/49cef220d6fae5f0990949dcb799acaad378f3e8))

- Remove build artifacts from version control
  ([`a115d75`](https://github.com/frederico-mello/repository-hygiene/commit/a115d75104c70ea53570648614cb3a97b839b9d7))

- Resolve all remaining SonarCloud vulnerabilities
  ([`905063c`](https://github.com/frederico-mello/repository-hygiene/commit/905063c6c5510f6807692520ba14ee8c1526ca27))

- Split uv pip install: --only-binary :all: + pinned pytest version - uv run --frozen locks all
  dependency versions - uvx/uv tool run with explicit ==0.2.0 version pin - All actions pinned to
  full commit SHA

- Resolve Quality Gate and CI failures for PR #58
  ([`0e75456`](https://github.com/frederico-mello/repository-hygiene/commit/0e754566a659f2622741e122edf14dfc07ba6d8b))

- Rewrite CLI to support subcommands (install/audit/update) with backward compat - Add cmd_install
  (dry-run support) and cmd_update to init.py - Fix CI workflow: use uv venv instead of --system,
  fix Windows glob - Fix README: wrong python -m path, add missing docs - Fix tests: version refs,
  help expectations, format flag - Fix pyproject.toml: deprecated license format - Keep backward
  compat: --init, --pre-commit, --install-hook still work

- Resolve repository audit findings
  ([`2323e5f`](https://github.com/frederico-mello/repository-hygiene/commit/2323e5f182d2d403aa06aed19aec54fbc9f8c197))

- Resolve SonarCloud security hotspots in CI workflow
  ([`56120ef`](https://github.com/frederico-mello/repository-hygiene/commit/56120ef5447c963643d16218b1bab231a7b601aa))

- Pin actions/checkout and astral-sh/setup-uv to full SHA (HIGH) - Pin pytest version to 8.3.4
  (MEDIUM) - Pin uv tool install/run via --from <wheel> (MEDIUM)

- Suppress S8544 - dynamic version by design
  ([`dc2c4b5`](https://github.com/frederico-mello/repository-hygiene/commit/dc2c4b5ed99a5a0dcc4e42431704d60d21742a8c))

- Use exact versions for pip install
  ([`066489b`](https://github.com/frederico-mello/repository-hygiene/commit/066489b6534ce10e10b275b1aaad7c9ebc4e3778))

- Use minimum version constraint for repository-hygiene
  ([`228fcff`](https://github.com/frederico-mello/repository-hygiene/commit/228fcff4286a94a7b3b4706726a4e5c7a9743b62))

- Validate report output directory
  ([`fdfe640`](https://github.com/frederico-mello/repository-hygiene/commit/fdfe640fbb14422d638f176f4c56292de6a4a3f0))

- Validate report output paths
  ([`1a3a89c`](https://github.com/frederico-mello/repository-hygiene/commit/1a3a89cc04b1dc4c330732fc9c072b3253a0f3da))

- **specs**: Add missing H1 title to publish-pypi-v020 spec
  ([`47665ab`](https://github.com/frederico-mello/repository-hygiene/commit/47665abe157e377a4c72c33cbe2004664ea81d05))

### Chores

- Ignore build artifacts
  ([`7b5e360`](https://github.com/frederico-mello/repository-hygiene/commit/7b5e3606f05f4920e2b19e559b815754af4b2f91))

- **openspec-plus**: Bump to v1.4.0
  ([`4613db4`](https://github.com/frederico-mello/repository-hygiene/commit/4613db48a528a43d776944fa5d5d528e5f16bd13))

- Update openspec/config.yaml with openspec-plus context and rules - Aligns with upstream
  sudokar/openspec-plus v1.4.0 - See CHANGELOG:
  https://github.com/sudokar/openspec-plus/releases/tag/v1.4.0

### Documentation

- Document remote installation
  ([`7f0c09c`](https://github.com/frederico-mello/repository-hygiene/commit/7f0c09c30cd973c2d86ad2c33946b1473db2b045))

- Propose agent-friendly audit report
  ([`08a2f52`](https://github.com/frederico-mello/repository-hygiene/commit/08a2f52d59f07243bbc772035f12cffce2573e34))

- Propose audit false-positive reduction
  ([`adb46cb`](https://github.com/frederico-mello/repository-hygiene/commit/adb46cbe4c58e03dc01abd73d531f4d1e0122702))

- Propose scalable audit change
  ([`083d6b4`](https://github.com/frederico-mello/repository-hygiene/commit/083d6b4eca409d87bf47ce17696ae6f26bf8b6c1))

- Propose scalable audit change
  ([`e675f7d`](https://github.com/frederico-mello/repository-hygiene/commit/e675f7d9b2fc5f6b6f330e394fd0b8a0eaa386f8))

- Reorganize README, align workflow template, add tests
  ([`1b620d0`](https://github.com/frederico-mello/repository-hygiene/commit/1b620d0df85847ddc6de00457e0d0bd41a083998))

### Features

- Add agent audit reports
  ([`e2e13e1`](https://github.com/frederico-mello/repository-hygiene/commit/e2e13e12f8f9788346c0b2b38b6c364104da34a8))

- Reduce audit false positives
  ([`6d3bc71`](https://github.com/frederico-mello/repository-hygiene/commit/6d3bc71607ddb02c22878ac62511006f2486a169))

- Robust-installation-path — suporte uvx, uv tool install, modulo Python
  ([`ef70377`](https://github.com/frederico-mello/repository-hygiene/commit/ef7037704e8daa75f3ffe897177b5fce3eab95aa))

- Adiciona __main__.py para execucao via python -m auditoria_higiene - Documenta fluxos uvx, uv tool
  install, pip e modulo Python no README - Nova spec instalacao-cli-uv com cenarios para cada fluxo
  - Novo CI multiplataforma (ubuntu/windows/macos) testando uvx e uv tool install - Testes
  extensivos para todos os fluxos: entry point, modulo, uvx, uv tool - Testes de mascara de
  segredos, codigos de saida, config invalida, docs - Arquiva change instalacao-cli-com-uv

- Sync delta specs to main specs and archive completed changes
  ([`004d0ce`](https://github.com/frederico-mello/repository-hygiene/commit/004d0ced702bb85dfb1624e4affd35a4181116db))

- Version control and release automation
  ([`ca3c777`](https://github.com/frederico-mello/repository-hygiene/commit/ca3c777f01592336cc74c10b7258eaf791f1c8f6))

- Conventional Commits audit rule (commit_check.py + core.py integration) - commit-msg hook
  installed by default on --init - Dynamic workflow template (no hardcoded version) - Semantic
  release pipeline (.github/workflows/release.yml) - actionlint validation, CHANGELOG.md, AGENTS.md
  - 13/13 tasks complete, 140 tests passing

- Version-control-and-release — OpenSpec Plus 1.4.0 + commit check module
  ([`b47ba8e`](https://github.com/frederico-mello/repository-hygiene/commit/b47ba8e8f382c47a6242a605c7851523224046a8))

- Upgrade OpenSpec Plus de 1.3.0 para 1.4.0 - Adiciona regras mandatory no config.yaml para skills
  openspec-plus-* - Novo modulo commit_check.py: verifica se commits no branch principal seguem
  convencao (feat/fix/etc.) e referenciam issue - Testes para commit_check

- **openspec**: Agent-hygiene-skill — 22/22 tasks complete
  ([`a09e614`](https://github.com/frederico-mello/repository-hygiene/commit/a09e61469132764f00e5f43245b1042afabd5796))

- **openspec**: Sync agent-hygiene-flow delta spec to main specs
  ([`3788b17`](https://github.com/frederico-mello/repository-hygiene/commit/3788b17a8891037c0fd5fe138da4ce1687f62825))

### Performance Improvements

- Scale artifact audit inventory
  ([`bdb6dc9`](https://github.com/frederico-mello/repository-hygiene/commit/bdb6dc996c2c52e1ca27a1cdc621dcb767fa0857))

### Refactoring

- Parametrize commit_check tests to reduce duplication
  ([`b1dff7b`](https://github.com/frederico-mello/repository-hygiene/commit/b1dff7bf183a85f365b348b55068006fea1b23fd))

- Parametrize hook validation tests to reduce duplication
  ([`d0c847a`](https://github.com/frederico-mello/repository-hygiene/commit/d0c847a6552ba6fd3db51a7f3720401dbc8239a0))


## v0.2.0 (2026-07-22)

### Bug Fixes

- Address Mira review feedback on pre-commit hook
  ([`4c6388e`](https://github.com/frederico-mello/repository-hygiene/commit/4c6388e6ff61f2bf5004c1474f6bba4209b9f0ce))

- Address SonarCloud security hotspots
  ([`bd10a97`](https://github.com/frederico-mello/repository-hygiene/commit/bd10a973dbc87833d416baf790827c569c8e5e77))

- Cache tracked files during audit
  ([`8cb9e6e`](https://github.com/frederico-mello/repository-hygiene/commit/8cb9e6e2d859ab4e460028dfe9b823b5fdd990a6))

- Close README test file
  ([`f5c1a9e`](https://github.com/frederico-mello/repository-hygiene/commit/f5c1a9e74d2c38430cfb6f40ed977b1a8ac39b89))

- Close remaining SonarCloud findings
  ([`789e312`](https://github.com/frederico-mello/repository-hygiene/commit/789e312c9c91f866d626bb60c17142b5fb496039))

- Install package from git source
  ([`0fa3877`](https://github.com/frederico-mello/repository-hygiene/commit/0fa3877e6c0f4eea5e64dba3eba046ccd954eadb))

- Use repository-hygiene package name
  ([`78dee7a`](https://github.com/frederico-mello/repository-hygiene/commit/78dee7a2b46e8070866ca019e9a511481d912586))

- **snapshot**: Prevent path traversal via staged file paths
  ([`3b2f899`](https://github.com/frederico-mello/repository-hygiene/commit/3b2f899de8583c5ba6206d76766bbfc62dd69e24))

### Documentation

- Propose PyPI 0.2.0 release
  ([`3dbeb74`](https://github.com/frederico-mello/repository-hygiene/commit/3dbeb744607a551284cfe55453bf2fe56640c311))

- Sync README with current behavior
  ([`365ea22`](https://github.com/frederico-mello/repository-hygiene/commit/365ea22f01172ed4f3b74f87ae6760b972647b0c))

- Use uv commands in README
  ([`0f76efe`](https://github.com/frederico-mello/repository-hygiene/commit/0f76efe7fc28643ed0c917893cc1cd81ff676bf1))

### Features

- Add native pre-commit hook with staged-only validation
  ([`c4cdf4a`](https://github.com/frederico-mello/repository-hygiene/commit/c4cdf4ab3f5a49cec2aa6b31115aa1c83ac43920))

- Bump to 0.2.0, update README, workflow, add tests
  ([`1cb0e47`](https://github.com/frederico-mello/repository-hygiene/commit/1cb0e477bdad09a1c4a335bc1404a1d9479c13c7))

- Initial release v0.1.0
  ([`3fbd500`](https://github.com/frederico-mello/repository-hygiene/commit/3fbd5008db6c0faa4a4fea47901de12b6ac7f7c9))
