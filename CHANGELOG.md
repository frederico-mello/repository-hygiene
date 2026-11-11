# CHANGELOG


## v1.1.2 (2026-11-11)

### Bug Fixes

- Remove unused cmd_update version parameter and dead update --version flag (python:S1172)
  ([#1135](https://github.com/frederico-mello/repository-hygiene/pull/1135),
  [`f8a8cc8`](https://github.com/frederico-mello/repository-hygiene/commit/f8a8cc80a2f6d0cab1e82a41174efcd95db5a34f))

Refs #1134

Co-authored-by: Claude Haiku 5.5 <noreply@anthropic.com>

### Chores

- **openspec**: Archive deduplicate-github-directory-literal
  ([`0802e2a`](https://github.com/frederico-mello/repository-hygiene/commit/0802e2a31e0f78dc6bf9f52de4a13f7839f1c142))

### Continuous Integration

- Point Mira callers at malformed-response fix [skip ci]
  ([`65ce784`](https://github.com/frederico-mello/repository-hygiene/commit/65ce784452837e9fafd971ceabb992135439b27d))

- Point routing helpers at malformed-response fix [skip ci]
  ([`b1cd565`](https://github.com/frederico-mello/repository-hygiene/commit/b1cd5652c6032bd9e02d56e915fc8599ba48f3ee))

- Prepare isolated review routing [skip ci]
  ([`ed8c5be`](https://github.com/frederico-mello/repository-hygiene/commit/ed8c5be2470f4c56daee4cc601b8ea3eeef4cc77))

- Prepare isolated review routing [skip ci]
  ([`1017647`](https://github.com/frederico-mello/repository-hygiene/commit/101764765c3ab8a29cf1e4932b2b0506b3c066ef))

- Prepare isolated review routing [skip ci]
  ([`1f30854`](https://github.com/frederico-mello/repository-hygiene/commit/1f308546db0afd77e77fd4b08fe15b85f7a3a63d))

- Prepare isolated review routing [skip ci]
  ([`3d78514`](https://github.com/frederico-mello/repository-hygiene/commit/3d78514f55c0610a745949cda6e2832ef76e7de7))

- Verify incomplete review handling [skip ci]
  ([`357518b`](https://github.com/frederico-mello/repository-hygiene/commit/357518b7c6b1696f2eb8ab93ddbe6d1f33b3a80c))

- **mira**: Move reviews to Claude Haiku 5.5 with GPT-6 Luna fallback
  ([`62dfd41`](https://github.com/frederico-mello/repository-hygiene/commit/62dfd410d33acf9186992f0001a2a79d446377e5))

Primary model is now anthropic/claude-haiku-5.5 (xhigh effort on the PR workflow, high on the push
  workflow) with openai/gpt-6-luna as the fallback. Reasoning effort is explicit in the effective
  config and the security pass stays on the review model.

- **mira**: Pin reusable workflows to the Haiku 5.5 revision
  ([`93bba81`](https://github.com/frederico-mello/repository-hygiene/commit/93bba814e9f82c0e3f69d618debe74769b586dd6))

- **mira**: Point callers at the OpenRouter provider commit 05edb475e84e
  ([`697ed2d`](https://github.com/frederico-mello/repository-hygiene/commit/697ed2d068c1f36f0a12ff9df017e677f6309815))

Both callers now forward the OPENROUTER_API_KEY secret to the reusable workflows.

- **mira**: Run reviews on OpenRouter (OPENROUTER_API_KEY)
  ([`05edb47`](https://github.com/frederico-mello/repository-hygiene/commit/05edb475e84e4172c0980ba36f2c92349fd7ef9a))

Switches both reusable workflows from the OpenCode Go (Zen) endpoint to OpenRouter: - base_url
  https://openrouter.ai/api/v1, api_key_env OPENROUTER_API_KEY - default models become vendor/model
  slugs (minimax/minimax-m3, qwen/qwen3.8-flash) - drops the Zen session-profile override
  (providers.json + MIRA_PROVIDERS_JSON_PATH) - secret interface renamed to OPENROUTER_API_KEY -
  quota classifier also recognises provider credit errors (insufficient credit / HTTP 402)


## v1.1.1 (2026-10-09)

### Bug Fixes

- Extract duplicated ".github" literal to a module constant
  ([#719](https://github.com/frederico-mello/repository-hygiene/pull/719),
  [`4e80ddc`](https://github.com/frederico-mello/repository-hygiene/commit/4e80ddc07156686c550aff466dd69a208ec7ce3a))

### Chores

- **openspec**: Archive agent-agnostic-provisioning + sync specs
  ([`55fb4d5`](https://github.com/frederico-mello/repository-hygiene/commit/55fb4d561d0b8e979364b08da70cc2cc74a8e757))

### Continuous Integration

- Require binary wheels in workflow pip installs
  ([`1ee4155`](https://github.com/frederico-mello/repository-hygiene/commit/1ee4155bd94d3a433c9285b25ef2934752120fa5))

- Trigger hygiene audit on all agent roots
  ([`9441d0c`](https://github.com/frederico-mello/repository-hygiene/commit/9441d0cdbbe2b9ed67168c2d906412f15e2bc795))

* ci: trigger hygiene audit on all agent roots

* ci: guard template and workflow trigger paths stay aligned

- Trigger hygiene audit on code and test paths
  ([`f3ce0b1`](https://github.com/frederico-mello/repository-hygiene/commit/f3ce0b17339f94701a43cd062114f9ebeaf41e1a))

### Documentation

- **changelog**: Adiciona secao v1.0.0 ausente
  ([`45c6c73`](https://github.com/frederico-mello/repository-hygiene/commit/45c6c734778f0bee65adc37145cdb723c9245ec1))

- **specs**: Write purpose placeholders left by archive
  ([`c77569f`](https://github.com/frederico-mello/repository-hygiene/commit/c77569f2bf4afdbff43504d8803a3126289fe0f8))

### Testing

- Scope package metadata assertions to this checkout
  ([`5ca3daa`](https://github.com/frederico-mello/repository-hygiene/commit/5ca3daa4720800a60ade42c68775e3cc273bf242))

- **snapshot**: Le a versao do pyproject em vez do literal 1.0.0
  ([`d5c6c97`](https://github.com/frederico-mello/repository-hygiene/commit/d5c6c97a6383120368f25e82b64b9048878f5094))


## v1.1.0 (2026-10-03)

### Chores

- **ci**: Bumpa o pin do reusable do Mira para o fix do gate partial
  ([`56f4582`](https://github.com/frederico-mello/repository-hygiene/commit/56f4582095218a7bdaa373bfbf6ad1858c9036b4))

- **ci**: Bumpa o pin do reusable do Mira para o fix do gate partial
  ([`4d5b252`](https://github.com/frederico-mello/repository-hygiene/commit/4d5b2529f936dde37ae2f828e6b1a1cf2ea85404))

- **deps**: Bump the github-actions group across 1 directory with 5 updates
  ([#658](https://github.com/frederico-mello/repository-hygiene/pull/658),
  [`65ecd98`](https://github.com/frederico-mello/repository-hygiene/commit/65ecd9890ac2ba232a57fb554857ff566fc0a8e0))

Bumps the github-actions group with 5 updates in the / directory:

| Package | From | To | | --- | --- | --- | |
  [actions/checkout](https://github.com/actions/checkout) | `4` | `7` | |
  [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) | `3.2.4` | `10.2.0` | |
  [actions/setup-python](https://github.com/actions/setup-python) | `5` | `7` | |
  [actions/github-script](https://github.com/actions/github-script) | `7` | `9` | |
  [actions/upload-artifact](https://github.com/actions/upload-artifact) | `4` | `7` |

Updates `actions/checkout` from 4 to 7 - [Release
  notes](https://github.com/actions/checkout/releases) -
  [Commits](https://github.com/actions/checkout/compare/v4...v7)

Updates `astral-sh/setup-uv` from 3.2.4 to 10.2.0 - [Release
  notes](https://github.com/astral-sh/setup-uv/releases) -
  [Commits](https://github.com/astral-sh/setup-uv/compare/caf0cab7a618c569241d31dcd442f54681755d39...c18668ad3cf93ea998bef934396af7bb5c839dc7)

Updates `actions/setup-python` from 5 to 7 - [Release
  notes](https://github.com/actions/setup-python/releases) -
  [Commits](https://github.com/actions/setup-python/compare/v5...v7)

Updates `actions/github-script` from 7 to 9 - [Release
  notes](https://github.com/actions/github-script/releases) -
  [Commits](https://github.com/actions/github-script/compare/v7...v9)

Updates `actions/upload-artifact` from 4 to 7 - [Release
  notes](https://github.com/actions/upload-artifact/releases) -
  [Commits](https://github.com/actions/upload-artifact/compare/v4...v7)

--- updated-dependencies: - dependency-name: actions/checkout dependency-version: '7'

dependency-type: direct:production

update-type: version-update:semver-major

dependency-group: github-actions

- dependency-name: astral-sh/setup-uv dependency-version: 10.2.0

- dependency-name: actions/setup-python dependency-version: '7'

- dependency-name: actions/github-script dependency-version: '9'

- dependency-name: actions/upload-artifact dependency-version: '7'

dependency-group: github-actions ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: frederico-mello <86882927+frederico-mello@users.noreply.github.com>

- **openspec**: Archive add-native-pre-commit-hook
  ([`9b62b49`](https://github.com/frederico-mello/repository-hygiene/commit/9b62b494bb7f47fbf362c791be719a22d80249cb))

- **openspec**: Descarta change reduzir-falsos-positivos-auditoria sem progresso
  ([`2d66154`](https://github.com/frederico-mello/repository-hygiene/commit/2d66154782a0f19f52f0f49b6ee385c7ebdc8dff))

### Continuous Integration

- Regenera requirements-ci.lock para py3.10 e repara configuracao do release
  ([`ca1ac64`](https://github.com/frederico-mello/repository-hygiene/commit/ca1ac645f3acc69322359876f2449bcd89b2467c))

Lock inclui exceptiongroup, tomli e typing-extensions com hashes porque o uv novo do setup-uv v10
  exige pin completo em --require-hashes e so falhava em py3.10; pyproject version_variable vira
  version_toml, chave correta da python-semantic-release 9 - antes a versao nunca era carimbada.

release.yml ganha --skip-existing para que pushes sem release novo nao falhem com arquivo ja
  publicado.

### Documentation

- **openspec**: Cria change agent-agnostic-provisioning
  ([`65ab9b8`](https://github.com/frederico-mello/repository-hygiene/commit/65ab9b8ee49567152aac081ef47a10057b8b9ece))

### Features

- **agents**: Multi-agent skill provisioning
  ([`145aa01`](https://github.com/frederico-mello/repository-hygiene/commit/145aa01821a552214e79923f493ec3ba5e331d50))

* feat(agents): multi-agent skill provisioning

* fix(agents): install skills before writing config


## v1.0.0 (2026-10-03)

### Chores

- **openspec**: Archive fix-mira-partial-gate-contradiction
  ([`bcac859`](https://github.com/frederico-mello/repository-hygiene/commit/bcac8597d6e0f34446cc92a119e7446d36364ef8))


## v0.9.7 (2026-10-03)

### Bug Fixes

- **mira**: Considera reviewed_files no veredito partial do gate
  ([#657](https://github.com/frederico-mello/repository-hygiene/pull/657),
  [`2c041d5`](https://github.com/frederico-mello/repository-hygiene/commit/2c041d5b34413e8fb167676ef518389600b99bdc))

O status 'partial' do gate ignorava reviewed_files, fazendo com que reviews limpas com payload
  recuperado ficassem presas em partial indefinidamente e o gate block-on-blocker reprovasses
  revisões honestas. O fix unifica o predicado 'covered' entre a seção news counting-as-covered e o
  veredito do gate, usando reviewed_files para distinguir "coberto por review limpa" de "realmente
  não coberto".

### Chores

- Alinhar uv.lock com pyproject 1.0.0 e ignorar .omp/
  ([`b42ed67`](https://github.com/frederico-mello/repository-hygiene/commit/b42ed676830ca4a00dea621ff6cb5a921f1a6818))

- **openspec**: Migrar changes/spec perdidas do workspace stray
  ([`686226a`](https://github.com/frederico-mello/repository-hygiene/commit/686226a538cd259dafc2cdf7ccf36786df5dcc21))

### Continuous Integration

- Fixa o reusable do Mira em SHA e habilita Dependabot
  ([`3454056`](https://github.com/frederico-mello/repository-hygiene/commit/3454056df6862338a9b56ac4777216f67b34d273))

A ref flutuante em @main expunha o secret encaminhado a qualquer push upstream. Dependabot abre o PR
  de bump para manter atualizado.

### Documentation

- **openspec**: Normalizar specs principais de delta para spec final (Purpose + Requirements)
  ([`06a7485`](https://github.com/frederico-mello/repository-hygiene/commit/06a74852a620f712eb89913d38ae924c2a1fe883))


## v0.9.6 (2026-09-24)

### Bug Fixes

- **mira**: Bare shellcheck directive — explanation text breaks parsing
  ([`7a5ddd0`](https://github.com/frederico-mello/repository-hygiene/commit/7a5ddd01b7ac777040084db6302924e63b1c273d))


## v0.9.5 (2026-09-24)

### Bug Fixes

- **mira**: Shellcheck directive needs '--', not em dash
  ([`17a7855`](https://github.com/frederico-mello/repository-hygiene/commit/17a78555f1042d62cee961f40f6a1d163cd553e3))


## v0.9.4 (2026-09-24)

### Bug Fixes

- **mira**: Revert quote on $range — it holds two SHAs, not one path
  ([`13cea50`](https://github.com/frederico-mello/repository-hygiene/commit/13cea5078997af8d34b8c25e0e659829fced3391))


## v0.9.3 (2026-09-24)

### Bug Fixes

- **mira**: Quote $range in git diff (shellcheck SC2086)
  ([`ee5f255`](https://github.com/frederico-mello/repository-hygiene/commit/ee5f25526fe7ebce29a119efc3ed4bbc98e4e2a2))


## v0.9.2 (2026-09-24)

### Bug Fixes

- **mira**: Recover prose-emitted payloads — chunk dropped with valid payload counts as covered
  ([`7c906e0`](https://github.com/frederico-mello/repository-hygiene/commit/7c906e0ef12b7b957af0a54a9d7a8b15cd618d04))

minimax-m3 degrades tool-call to prose intermittently on large outputs. Mira then prints the valid
  review JSON to stdout but marks the chunk as 'failed to parse, skipping', and the parser treated
  any dropped chunk as partial even when a complete payload (walkthrough, reviewed_files) was
  present — measured on a real run: 14 files walked, 0 comments, valid walkthrough, counted as
  partial 4 runs in a row.

Both parsers now merge every recoverable payload (dedupe on file+line+title) and only stay partial
  when a dropped chunk has no payload with walkthrough or findings. Validated against the real
  partial-run stdout plus synthetic multi-chunk/empty-payload cases.


## v0.9.1 (2026-09-23)

### Bug Fixes

- Skip git revert commits in conventional-commits audit
  ([#82](https://github.com/frederico-mello/repository-hygiene/pull/82),
  [`3c20a9b`](https://github.com/frederico-mello/repository-hygiene/commit/3c20a9b07398166fe3ad8e51a2af1b69179c8784))

Add subject-line prefix check before Conventional Commits regex validation in
  _mensagem_conventional. Revert commits auto-generated by git revert use this format and don't
  match the Conventional Commits pattern, producing false positives.

Merge commits were already excluded via commit c7c5af5e681112964c0f6ed8cd6ad3184a2c1f04 Author:
  semantic-release <semantic-release>

Date: Sat Jul 25 14:59:41 2026 +0000

chore(release): 0.5.0

commit f69f6d4fa522cd503e0460afbe51e922ee46920c Author: Frederico <fredericommello@gmail.com>

Date: Sat Jul 25 11:55:16 2026 -0300

fix: reduce cognitive complexity and validate file paths

- Extract `_processar_ref_doc` from `_verificar_refs_doc_em_arquivo` (16→15) - Extract
  `_subdir_contem_nome` and `_arquivo_contem_texto` from `_dir_mencionada_em_openspec` (20→15) - Add
  path validation in semantic.py before glob and file open to prevent path traversal
  (pythonsecurity:S8707)

commit ea00f886b274de56d332ef08ac7b7c669ae9f786 Author: Frederico <fredericommello@gmail.com>

Date: Sat Jul 25 07:46:55 2026 -0300

chore(openspec): arquivar change install-skill e sincronizar spec

commit 1257b1cb290c6280aaf4893f8d610a6fc6c7a989 Author: Frederico <fredericommello@gmail.com>

Date: Sat Jul 25 07:25:46 2026 -0300

chore: archive reconcile-hygiene-semantic-audit

commit 4852b7ba078d5d804f5e990c630c133b934b534f Author: Frederico <fredericommello@gmail.com>

Date: Sat Jul 25 07:25:16 2026 -0300

feat: semantic repository reconciliation audit

Add nested repo detection, workflow intent evaluation, semantic evidence cross-referencing with
  OpenSpec/Graphify, typed recommendation taxonomy, and updated agent-hygiene-flow skill.

- New: semantic-repository-reconciliation spec + semantic.py module - Modified:
  context-aware-audit-findings, agent-hygiene-flow, documentation-consistency specs - Core: taxonomy
  constants, nested repo rule, workflow permission justification - Tests: 32+ new tests across
  test_auditoria_package.py and test_semantic.py

commit 34213ccd441251a94c91dd6ff84fa7948f0f8765 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 22:04:23 2026 -0300

docs: reescrever README conciso — PT só, fluxo linear, aviso pip install

Remove duplicacao PT/EN (Instalacao + Installation & Execution). Remove instrucoes de venv
  redundantes. Adiciona aviso: apos pip install, executar repository-hygiene install . Reorganiza em
  fluxo linear: instalar → usar (init/audit/hook) → configurar. 336 → 160 linhas.

commit 5e2175273f9c09c13c718ef58da5af6b4ef156fe Author: semantic-release <semantic-release>

Date: Sat Jul 25 00:58:13 2026 +0000

chore(release): 0.4.0

commit edd2e7a8d78c15fcb31ed817b664a499cfe758e2 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:56:48 2026 -0300

feat(install): provisionar skill agent-hygiene-flow no alvo

Adiciona a skill OpenCode agent-hygiene-flow como package data e provisiona em
  .opencode/skills/agent-hygiene-flow/ durante o 'repository-hygiene install'. Reutiliza a semantica
  de skip/force/dry-run ja existente. A versao empacotada com o pacote fixa a versao da skill
  entregue.

commit 00ad30e4eaa076289701321af270db524ee658aa Author: semantic-release <semantic-release>

Date: Sat Jul 25 00:37:30 2026 +0000

chore(release): 0.3.0

commit d0fab712aa1bbc0b8f384626d491f8201cd22588 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:35:57 2026 -0300

refactor: parametrize hook validation tests to reduce duplication

commit c9ec30695136a14996bab3873e942b37df719b6e Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:33:31 2026 -0300

refactor: parametrize commit_check tests to reduce duplication

commit cc610e5f61fe599578115a22112256637dacab4e Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:26:50 2026 -0300

fix: pin repository-hygiene to exact version 0.2.0 for SonarQube

commit ae378a97c94659f6e51fc7275e0d2655202e3a18 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:25:00 2026 -0300

fix: use minimum version constraint for repository-hygiene

commit dcf82b46f3668eb9c4222242ea3fed3cbe3799f8 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:22:50 2026 -0300

fix: pin repository-hygiene to minimum version 0.3.0

commit 9c3a01037cf6bd5658c780751645eed689b46174 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:17:38 2026 -0300

fix: suppress S8544 - dynamic version by design

commit 473138f8e04fa9b4d4986362cc928e068fa70d1c Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:16:52 2026 -0300

fix: use exact versions for pip install

commit 0b38882da704ef0d194e583991d46ec2671bf41e Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:15:36 2026 -0300

fix: pin CI dependency versions for SonarQube

commit 449f47d50c48a3dc0612ad850146c55f439771b8 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:15:01 2026 -0300

fix: add --only-binary to workflow pip installs

commit f4102d51bfc59c7d3be691dcabf33167d050b6d7 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 21:11:06 2026 -0300

feat: version control and release automation

- Conventional Commits audit rule (commit_check.py + core.py integration) - commit-msg hook
  installed by default on --init - Dynamic workflow template (no hardcoded version) - Semantic
  release pipeline (.github/workflows/release.yml) - actionlint validation, CHANGELOG.md, AGENTS.md
  - 13/13 tasks complete, 140 tests passing

commit b4f95ab0f5429fad39283ff74813503bfa2ac9a3 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:55:57 2026 -0300

fix: resolve all remaining SonarCloud vulnerabilities

- Split uv pip install: --only-binary :all: + pinned pytest version - uv run --frozen locks all
  dependency versions - uvx/uv tool run with explicit ==0.2.0 version pin - All actions pinned to
  full commit SHA

commit 4dbb3dacccc395a53685da6f031b616e85a3b5ec Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:50:11 2026 -0300

fix: resolve SonarCloud security hotspots in CI workflow

- Pin actions/checkout and astral-sh/setup-uv to full SHA (HIGH) - Pin pytest version to 8.3.4
  (MEDIUM) - Pin uv tool install/run via --from <wheel> (MEDIUM)

commit f74e3425dab1f7b58f689881b34a5f43acbf3b34 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:45:52 2026 -0300

chore: ignore build artifacts

commit 2bbbeb30b1adff0585d48627bf59915140a20d5f Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:45:47 2026 -0300

fix: remove build artifacts from version control

commit b24fb572200f2c4bb0195735124b46335dc5953e Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:45:42 2026 -0300

fix: resolve Quality Gate and CI failures for PR #58

- Rewrite CLI to support subcommands (install/audit/update) with backward compat - Add cmd_install
  (dry-run support) and cmd_update to init.py - Fix CI workflow: use uv venv instead of --system,
  fix Windows glob - Fix README: wrong python -m path, add missing docs - Fix tests: version refs,
  help expectations, format flag - Fix pyproject.toml: deprecated license format - Keep backward
  compat: --init, --pre-commit, --install-hook still work

commit 1669e8987d42a44cccca38e0f437ab3123662310 Author: Frederico <fredericommello@gmail.com>

Date: Fri Jul 24 19:15:55 2026 -0300

fix: deduplicate git_repo fixture — extract to conftest.py

SonarCloud Quality Gate: 19.3% duplicated lines (threshold 3%). git_repo fixture was duplicated
  across test_auditoria_package.py and test_commit_check.py. Moved to shared conftest.py.

commit 52e01312a7d76ea33b33ef2c566522212a3c276d Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 19:14:47 2026 -0300

feat: robust-installation-path — suporte uvx, uv tool install, modulo Python

- Adiciona __main__.py para execucao via python -m auditoria_higiene - Documenta fluxos uvx, uv tool
  install, pip e modulo Python no README - Nova spec instalacao-cli-uv com cenarios para cada fluxo
  - Novo CI multiplataforma (ubuntu/windows/macos) testando uvx e uv tool install - Testes
  extensivos para todos os fluxos: entry point, modulo, uvx, uv tool - Testes de mascara de
  segredos, codigos de saida, config invalida, docs - Arquiva change instalacao-cli-com-uv

commit 52d5105952dc4c18ba3caa5941a36062ee9c5c12 Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 19:09:35 2026 -0300

feat: version-control-and-release — OpenSpec Plus 1.4.0 + commit check module

- Upgrade OpenSpec Plus de 1.3.0 para 1.4.0 - Adiciona regras mandatory no config.yaml para skills
  openspec-plus-* - Novo modulo commit_check.py: verifica se commits no branch principal seguem
  convencao (feat/fix/etc.) e referenciam issue - Testes para commit_check

commit b594142eecbfc72c9ce148ba5683f7f125337f47 Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 14:32:38 2026 -0300

fix: clarify git-wt as Worktrunk with AGENTS.md reference

commit f0acdbfd9029dec4600a034822b29c683d818b67 Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 14:29:33 2026 -0300

feat(openspec): sync agent-hygiene-flow delta spec to main specs

commit e8c36739997617828ef9c6f5486f96174809f83b Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 14:10:12 2026 -0300

feat(openspec): agent-hygiene-skill — 22/22 tasks complete

commit e2cc581610edef5b61352001f08a5cba14dda1ee Author: frederico-mello <fredericommello@gmail.com>

Date: Fri Jul 24 09:24:51 2026 -0300

chore(openspec-plus): bump to v1.4.0

- Update openspec/config.yaml with openspec-plus context and rules - Aligns with upstream
  sudokar/openspec-plus v1.4.0 - See CHANGELOG:
  https://github.com/sudokar/openspec-plus/releases/tag/v1.4.0

commit afd2a43f0c2c8b2fb82b5d17da1eba449ac5d4f0 Author: frederico-mello <fredericommello@gmail.com>

Date: Thu Jul 23 07:56:22 2026 -0300

docs: document remote installation

commit 3254d24da970d76b434824fe1ebf9bae6259e63c Author: Frederico <fredericommello@gmail.com>

Date: Wed Jul 22 19:52:22 2026 -0300

docs: reorganize README, align workflow template, add tests

commit c7d6b3108596d3ff2804e999731ef57705d2d018 Author: Frederico <fredericommello@gmail.com>

Date: Wed Jul 22 18:46:18 2026 -0300

fix(specs): add missing H1 title to publish-pypi-v020 spec

commit b30a4139d62fe7e83ded172b8f58c431a22abd5d Author: Frederico <fredericommello@gmail.com>

Date: Wed Jul 22 18:43:35 2026 -0300

fix: ignore auditoria-report.txt generated by CI

commit afd4420f156b6fd44bc7d8524f8f969c764d23bb Author: Frederico <fredericommello@gmail.com>

Date: Wed Jul 22 18:38:30 2026 -0300

feat: sync delta specs to main specs and archive completed changes

commit acfd4632af06842edcd0ee2327cfb5e854eae368 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:54:43 2026 -0300

fix: harden audit workflow

commit 79e48eff35401f3bc7d3245566597aea4ee76f97 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:49:31 2026 -0300

fix: resolve repository audit findings

commit b4025a5edf37aa7fa80731892bdd8cca488fe0e8 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:25:45 2026 -0300

fix: detect quoted documentation paths

commit 50edcb0218b51e8d0ae2475ad8431c951030d387 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:23:35 2026 -0300

fix: validate report output directory

commit 38c20b17eeca7b0de5f66824776868e88a12df69 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:20:40 2026 -0300

fix: address quality gate findings

commit 1ed8cf8e26522193408651c2b31c1afd2baed9e4 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 16:12:45 2026 -0300

feat: reduce audit false positives

commit c16844999919aaa7a3ec62d087a33c6b085fdac5 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 15:44:20 2026 -0300

docs: propose audit false-positive reduction

commit 2d87299d32aa40630ffa7cbc0ade66990671a3c4 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 15:30:08 2026 -0300

fix: mark validated report path sinks

commit de771ab0b70b3006a4922cba6a7c0ce71d83cb17 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 15:28:10 2026 -0300

fix: validate report output paths

commit 484a5c28c4387f7076c951b65d5e6adda265c64f Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 15:21:07 2026 -0300

fix: align agent report metadata

commit 26d2080ecaf1f98be900ea9634eed61ef7c6ab17 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 15:16:25 2026 -0300

feat: add agent audit reports

commit ffe3c295ba02556ac9882dc4f30d1736c53792c4 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 14:53:15 2026 -0300

docs: propose agent-friendly audit report

commit e1ac5e771d5550ca0465834062e11a33e2e64fa6 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 14:01:37 2026 -0300

fix: avoid scanning ignored directories

commit 08152edcebc7bb861703d942bb4b1b9e849fd113 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 13:56:06 2026 -0300

perf: scale artifact audit inventory

commit 7abcc2a9a99f85b215119861a2904cdb0f974325 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 13:28:09 2026 -0300

docs: propose scalable audit change

commit 0773b602c8f019e3deda0e5fe5eb44c7e8d2684c Author: frederico-mello <fredericommello@gmail.com>

commit 6294f4af3d92e27c47313dc83c74405995cbb0bb Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 13:05:20 2026 -0300

fix: close README test file

commit f078e2d33e28c8a053c6b95bb7f9a99a0a3f4230 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 12:56:19 2026 -0300

feat: bump to 0.2.0, update README, workflow, add tests

commit 1090dc5c15a1adfd6615cbaf80107ef683bcd2a0 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 12:48:16 2026 -0300

docs: propose PyPI 0.2.0 release

commit d4f55643c47869b779f24f1aa6626b56d5c82067 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 12:40:05 2026 -0300

fix: use repository-hygiene package name

commit 4fc6e84fb80b6735fc642d008316f6f88c536875 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 12:34:09 2026 -0300

fix: install package from git source

commit c2dbf5775e5f94e006df84971f1fd9be6174be9a Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 12:30:43 2026 -0300

docs: use uv commands in README

commit 23533b5ca4c933cd13359af0f9f0d232935ea9e6 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 11:22:36 2026 -0300

docs: sync README with current behavior

commit ac0b8e7f9e98aa518cb504b5eb1b2b422af37256 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 11:03:13 2026 -0300

fix: cache tracked files during audit

commit b1b9e80068a4fb735bbbc8a593776ff89d52a7c3 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 09:07:10 2026 -0300

fix: close remaining SonarCloud findings

commit 32b79a3c39ad2d33a0aa004dcc3825e6e92ec2f5 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 09:03:16 2026 -0300

fix: address SonarCloud security hotspots

commit 527dbb633330b247badbb63f756c4e0c5611af40 Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 08:57:28 2026 -0300

fix(snapshot): prevent path traversal via staged file paths

commit 21aabd25ce5257a16fde78c8fe89a204e11cc7fe Author: frederico-mello <fredericommello@gmail.com>

Date: Wed Jul 22 08:46:33 2026 -0300

fix: address Mira review feedback on pre-commit hook

commit b22a5268b15a2391a7731b8e2b3d8afce9959e10 Author: Frederico <fredericommello@gmail.com>

Date: Wed Jul 22 07:08:05 2026 -0300

feat: add native pre-commit hook with staged-only validation

commit 9703bdc20dd7245333186e849f0bdeabc5feb86a Author: frederico-mello <fredericommello@gmail.com>

Date: Tue Jul 21 16:39:02 2026 -0300

feat: initial release v0.1.0.


## v0.9.0 (2026-09-23)

### Features

- **openspec**: Version control release
  ([#103](https://github.com/frederico-mello/repository-hygiene/pull/103),
  [`5e29e39`](https://github.com/frederico-mello/repository-hygiene/commit/5e29e39a6dcc04867d337d72ba688df91dce6474))

* feat(openspec): version control release complete

* fix: reconcile release PR with main

* fix(ci): install local package in audit workflow

* fix(ci): run audit from local source

* fix(ci): pin local workflow test dependencies

* fix(ci): stabilize matrix and audit workflows

* fix(ci): pin wheels and use portable install shell

* fix(ci): use sonar-compatible binary pin syntax

* fix(ci): expose binary constraint to sonar

* fix(ci): use no-build for local wheel

* fix(ci): run matrix from pinned ephemeral environment

* fix(ci): declare pinned matrix requirements

* fix(ci): enforce hash-locked test environment

* fix(ci): lock external test dependencies only

* fix(ci): execute tests from activated venv


## v0.8.1 (2026-09-15)

### Bug Fixes

- **mira-ci**: Retry discarded chunks on push, and stop filing issues for partial
  ([`40fa8b2`](https://github.com/frederico-mello/repository-hygiene/commit/40fa8b240cae392bf8796bdac04268b5690cf617))

Two problems found while installing this across the fleet.

First, the push path had no retry, unlike the PR path. A discarded chunk is the harness losing the
  answer, not the model judging the diff, and on this path the same diff was measured producing
  findings on one run and silently nothing on the next. The first install therefore opened three
  issues whose entire content was 'review incomplete, 0 findings' on pushes that had nothing in
  them.

Second, partial reviews were opening issues. A partial review is a failure to review, not a finding,
  so it now warns and writes the step summary instead of filing an issue nobody should triage. Only
  status=ok can open or close the issue, so a partial never silently closes a real finding either.

Parser re-validated on five scenarios (ok, clean, partial, quota, no payload): the retry flag is set
  only on partial, and only a missing payload exits non-zero. actionlint clean.

### Continuous Integration

- **mira**: Revisar pushes diretos na branch default
  ([`7555883`](https://github.com/frederico-mello/repository-hygiene/commit/7555883737f5f0dc28d2d1902322ae3388f37e5c))

A revisao de PR nao ve commits empurrados direto para main. Este workflow revisa o diff do push e
  publica o resultado numa issue (abre/atualiza com achados, fecha quando o push esta limpo). Nao
  bloqueia o push.

- **mira**: Revisar pushes diretos na branch default
  ([`af8aa8e`](https://github.com/frederico-mello/repository-hygiene/commit/af8aa8e81bdf1987ede92f70048921e70b0df376))

A revisao de PR nao ve commits empurrados direto para main. Este workflow revisa o diff do push e
  publica o resultado numa issue (abre/atualiza com achados, fecha quando o push esta limpo). Nao
  bloqueia o push.

- **mira**: Revisar pushes diretos na branch default
  ([`bd9bf99`](https://github.com/frederico-mello/repository-hygiene/commit/bd9bf9943f7647149dd417cdf33f0bf032e4992c))

A revisao de PR nao ve commits empurrados direto para main. Este workflow revisa o diff do push e
  publica o resultado numa issue (abre/atualiza com achados, fecha quando o push esta limpo). Nao
  bloqueia o push.


## v0.8.0 (2026-09-15)

### Continuous Integration

- **mira**: Add the AI code-review caller
  ([`d5d8b26`](https://github.com/frederico-mello/repository-hygiene/commit/d5d8b26a508d3b5639e53f11c7b237751b9e6c92))

Calls the shared reusable workflow instead of carrying a copy:
  frederico-mello/repository-hygiene/.github/workflows/mira-review-reusable.yml@main

The reusable workflow owns the endpoint, credential, model, and fallback policy; .mira.yaml carries
  only this repo's review tuning and is merged over those defaults.

Needs the repo secret OPENCODE_GO_API_KEY (configured).

### Features

- **mira-ci**: Review direct pushes to the default branch
  ([`58f258e`](https://github.com/frederico-mello/repository-hygiene/commit/58f258ec28a18e91b494301347544875edb1f366))

Closes the gap the PR review cannot cover. On this account most commits go straight to main (6 of
  the last 8 in principal-tarefas-aleatorias, 4 of 8 in mundo-wumpus), and the PR-triggered workflow
  never sees them.

Design choices specific to this path: - uses `mira review --stdin` on the pushed diff, measured at
  ~8-20s versus 78-286s for `--pr`. No posting, no indexing, no PR pass, so it is cheap enough to
  run on every push. - never blocks the push (it already happened). It publishes evidence instead:
  one issue per repo with a marker, opened or updated on findings, closed when the latest push is
  clean. - skips pushes whose commits are all merges, since that content was reviewed in the origin
  PR, and skips diffs over max-diff-lines because a finding in a mass regeneration is an artifact of
  size rather than of the change. - carries the same honesty rules as the PR path: quota is reported
  as quota, discarded chunks report partial, and a missing payload fails the step.


## v0.7.1 (2026-09-15)

### Bug Fixes

- **mira-ci**: The retry never fired (verdict captured log output)
  ([`6c51fb9`](https://github.com/frederico-mello/repository-hygiene/commit/6c51fb997e780e799b2df2eb0a8dd5228a70de2a))

Caught in production on the first run of the retry code: the loop broke with 'attempt 1 verdict:
  partial' and still did not retry. Assigning $(python ...) captured the parser's whole stdout,
  which includes log lines besides the verdict, so the multi-line string never equalled 'partial'
  and the retry was silently dead code.

The parser now writes the verdict to its own one-line file and the loop reads that file. Verified
  directly: ok/failed/quota break, partial retries.


## v0.7.0 (2026-09-15)

### Features

- **mira-ci**: Retry once when a chunk is discarded
  ([`8e9007f`](https://github.com/frederico-mello/repository-hygiene/commit/8e9007fcc0913cf06cd73e30007669b5134d8fe0))

Measured on a real PR diff: the same model dropped a chunk on 2 of 5 runs, and the payload for a
  dropped chunk says 'No issues found.' — so the failure mode looks exactly like a clean review both
  to a human and to any naive check.

A discarded chunk is transient (the model answered in prose instead of calling the tool), so
  retrying once converts most incomplete reviews into full ones for the cost of one extra review.
  The parser moved into a file so the retry loop can reuse it verbatim, and the loop keys off the
  parser's verdict rather than Mira's exit code (which is 1 for both blockers and failures).

Also tightened the opt-in gate: a caller gating on blockers can no longer be satisfied by
  status=partial or status=quota. A merge gate that a review which never covered the diff can pass
  is not a gate.

Parser re-validated on seven scenarios; every step's bash syntax checked with bash -n.


## v0.6.2 (2026-09-15)

### Bug Fixes

- **mira-ci**: A discarded chunk is not a clean review
  ([`7ca7537`](https://github.com/frederico-mello/repository-hygiene/commit/7ca7537fb04f3dc7247fad6b9942381b96b64faf))

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
  ([`2bdafbf`](https://github.com/frederico-mello/repository-hygiene/commit/2bdafbffc8ee34a5215a609c1c0f23368b627214))

The caller was pinned to @ci/mira-reusable-workflow while the reusable workflow was under review.
  That branch was deleted in the squash merge of #521, so the caller resolved to a nonexistent ref
  and the run failed with ZERO jobs — the workflow could not even start.

Repos that received the caller after the merge already point at @main; this repo was the only one
  left on the dead branch, and it is the host of the workflow, so it was the natural place to
  notice.

### Chores

- **openspec**: Archive english-source-localization + sync specs
  ([`090dec2`](https://github.com/frederico-mello/repository-hygiene/commit/090dec213d766a1ebb277d85139ecead0f22d439))

Move change english-source-localization to openspec/changes/archive/. Sync delta specs: create new
  english-source-locale capability spec, apply MODIFIED+ADDED requirements to
  documentation-consistency spec.

### Continuous Integration

- **mira**: Reusable AI code-review workflow for all repos
  ([`991e64c`](https://github.com/frederico-mello/repository-hygiene/commit/991e64c25209110a561f2c39e81e796a9642b5b4))

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
  ([`bbf45e5`](https://github.com/frederico-mello/repository-hygiene/commit/bbf45e52b083b31c519df6a1b67ffb9b47a4376e))

- Implements change `` - Archived to openspec/changes/archive/


## v0.5.0 (2026-07-25)

### Bug Fixes

- Reduce cognitive complexity and validate file paths
  ([`f69f6d4`](https://github.com/frederico-mello/repository-hygiene/commit/f69f6d4fa522cd503e0460afbe51e922ee46920c))

- Extract `_processar_ref_doc` from `_verificar_refs_doc_em_arquivo` (16→15) - Extract
  `_subdir_contem_nome` and `_arquivo_contem_texto` from `_dir_mencionada_em_openspec` (20→15) - Add
  path validation in semantic.py before glob and file open to prevent path traversal
  (pythonsecurity:S8707)

### Chores

- Archive reconcile-hygiene-semantic-audit
  ([`1257b1c`](https://github.com/frederico-mello/repository-hygiene/commit/1257b1cb290c6280aaf4893f8d610a6fc6c7a989))

- Resolve merge conflict in openspec/config.yaml
  ([`8d9d0c0`](https://github.com/frederico-mello/repository-hygiene/commit/8d9d0c027c5c929af05e91b2659ee08b94031d9a))

- **openspec**: Arquivar change install-skill e sincronizar spec
  ([`ea00f88`](https://github.com/frederico-mello/repository-hygiene/commit/ea00f886b274de56d332ef08ac7b7c669ae9f786))

### Documentation

- Reescrever README conciso — PT só, fluxo linear, aviso pip install
  ([`34213cc`](https://github.com/frederico-mello/repository-hygiene/commit/34213ccd441251a94c91dd6ff84fa7948f0f8765))

Remove duplicacao PT/EN (Instalacao + Installation & Execution). Remove instrucoes de venv
  redundantes. Adiciona aviso: apos pip install, executar repository-hygiene install . Reorganiza em
  fluxo linear: instalar → usar (init/audit/hook) → configurar. 336 → 160 linhas.

### Features

- Semantic repository reconciliation audit
  ([`4852b7b`](https://github.com/frederico-mello/repository-hygiene/commit/4852b7ba078d5d804f5e990c630c133b934b534f))

Add nested repo detection, workflow intent evaluation, semantic evidence cross-referencing with
  OpenSpec/Graphify, typed recommendation taxonomy, and updated agent-hygiene-flow skill.

- New: semantic-repository-reconciliation spec + semantic.py module - Modified:
  context-aware-audit-findings, agent-hygiene-flow, documentation-consistency specs - Core: taxonomy
  constants, nested repo rule, workflow permission justification - Tests: 32+ new tests across
  test_auditoria_package.py and test_semantic.py


## v0.4.0 (2026-07-25)

### Features

- **install**: Provisionar skill agent-hygiene-flow no alvo
  ([`edd2e7a`](https://github.com/frederico-mello/repository-hygiene/commit/edd2e7a8d78c15fcb31ed817b664a499cfe758e2))

Adiciona a skill OpenCode agent-hygiene-flow como package data e provisiona em
  .opencode/skills/agent-hygiene-flow/ durante o 'repository-hygiene install'. Reutiliza a semantica
  de skip/force/dry-run ja existente. A versao empacotada com o pacote fixa a versao da skill
  entregue.


## v0.3.0 (2026-07-25)

### Bug Fixes

- Add --only-binary to workflow pip installs
  ([`449f47d`](https://github.com/frederico-mello/repository-hygiene/commit/449f47d50c48a3dc0612ad850146c55f439771b8))

- Address quality gate findings
  ([`38c20b1`](https://github.com/frederico-mello/repository-hygiene/commit/38c20b17eeca7b0de5f66824776868e88a12df69))

- Align agent report metadata
  ([`484a5c2`](https://github.com/frederico-mello/repository-hygiene/commit/484a5c28c4387f7076c951b65d5e6adda265c64f))

- Avoid scanning ignored directories
  ([`e1ac5e7`](https://github.com/frederico-mello/repository-hygiene/commit/e1ac5e771d5550ca0465834062e11a33e2e64fa6))

- Clarify git-wt as Worktrunk with AGENTS.md reference
  ([`b594142`](https://github.com/frederico-mello/repository-hygiene/commit/b594142eecbfc72c9ce148ba5683f7f125337f47))

- Deduplicate git_repo fixture — extract to conftest.py
  ([`1669e89`](https://github.com/frederico-mello/repository-hygiene/commit/1669e8987d42a44cccca38e0f437ab3123662310))

SonarCloud Quality Gate: 19.3% duplicated lines (threshold 3%). git_repo fixture was duplicated
  across test_auditoria_package.py and test_commit_check.py. Moved to shared conftest.py.

- Detect quoted documentation paths
  ([`b4025a5`](https://github.com/frederico-mello/repository-hygiene/commit/b4025a5edf37aa7fa80731892bdd8cca488fe0e8))

- Harden audit workflow
  ([`acfd463`](https://github.com/frederico-mello/repository-hygiene/commit/acfd4632af06842edcd0ee2327cfb5e854eae368))

- Ignore auditoria-report.txt generated by CI
  ([`b30a413`](https://github.com/frederico-mello/repository-hygiene/commit/b30a4139d62fe7e83ded172b8f58c431a22abd5d))

- Mark validated report path sinks
  ([`2d87299`](https://github.com/frederico-mello/repository-hygiene/commit/2d87299d32aa40630ffa7cbc0ade66990671a3c4))

- Pin CI dependency versions for SonarQube
  ([`0b38882`](https://github.com/frederico-mello/repository-hygiene/commit/0b38882da704ef0d194e583991d46ec2671bf41e))

- Pin repository-hygiene to exact version 0.2.0 for SonarQube
  ([`cc610e5`](https://github.com/frederico-mello/repository-hygiene/commit/cc610e5f61fe599578115a22112256637dacab4e))

- Pin repository-hygiene to minimum version 0.3.0
  ([`dcf82b4`](https://github.com/frederico-mello/repository-hygiene/commit/dcf82b46f3668eb9c4222242ea3fed3cbe3799f8))

- Remove build artifacts from version control
  ([`2bbbeb3`](https://github.com/frederico-mello/repository-hygiene/commit/2bbbeb30b1adff0585d48627bf59915140a20d5f))

- Resolve all remaining SonarCloud vulnerabilities
  ([`b4f95ab`](https://github.com/frederico-mello/repository-hygiene/commit/b4f95ab0f5429fad39283ff74813503bfa2ac9a3))

- Split uv pip install: --only-binary :all: + pinned pytest version - uv run --frozen locks all
  dependency versions - uvx/uv tool run with explicit ==0.2.0 version pin - All actions pinned to
  full commit SHA

- Resolve Quality Gate and CI failures for PR #58
  ([`b24fb57`](https://github.com/frederico-mello/repository-hygiene/commit/b24fb572200f2c4bb0195735124b46335dc5953e))

- Rewrite CLI to support subcommands (install/audit/update) with backward compat - Add cmd_install
  (dry-run support) and cmd_update to init.py - Fix CI workflow: use uv venv instead of --system,
  fix Windows glob - Fix README: wrong python -m path, add missing docs - Fix tests: version refs,
  help expectations, format flag - Fix pyproject.toml: deprecated license format - Keep backward
  compat: --init, --pre-commit, --install-hook still work

- Resolve repository audit findings
  ([`79e48ef`](https://github.com/frederico-mello/repository-hygiene/commit/79e48eff35401f3bc7d3245566597aea4ee76f97))

- Resolve SonarCloud security hotspots in CI workflow
  ([`4dbb3da`](https://github.com/frederico-mello/repository-hygiene/commit/4dbb3dacccc395a53685da6f031b616e85a3b5ec))

- Pin actions/checkout and astral-sh/setup-uv to full SHA (HIGH) - Pin pytest version to 8.3.4
  (MEDIUM) - Pin uv tool install/run via --from <wheel> (MEDIUM)

- Suppress S8544 - dynamic version by design
  ([`9c3a010`](https://github.com/frederico-mello/repository-hygiene/commit/9c3a01037cf6bd5658c780751645eed689b46174))

- Use exact versions for pip install
  ([`473138f`](https://github.com/frederico-mello/repository-hygiene/commit/473138f8e04fa9b4d4986362cc928e068fa70d1c))

- Use minimum version constraint for repository-hygiene
  ([`ae378a9`](https://github.com/frederico-mello/repository-hygiene/commit/ae378a97c94659f6e51fc7275e0d2655202e3a18))

- Validate report output directory
  ([`50edcb0`](https://github.com/frederico-mello/repository-hygiene/commit/50edcb0218b51e8d0ae2475ad8431c951030d387))

- Validate report output paths
  ([`de771ab`](https://github.com/frederico-mello/repository-hygiene/commit/de771ab0b70b3006a4922cba6a7c0ce71d83cb17))

- **specs**: Add missing H1 title to publish-pypi-v020 spec
  ([`c7d6b31`](https://github.com/frederico-mello/repository-hygiene/commit/c7d6b3108596d3ff2804e999731ef57705d2d018))

### Chores

- Ignore build artifacts
  ([`f74e342`](https://github.com/frederico-mello/repository-hygiene/commit/f74e3425dab1f7b58f689881b34a5f43acbf3b34))

- **openspec-plus**: Bump to v1.4.0
  ([`e2cc581`](https://github.com/frederico-mello/repository-hygiene/commit/e2cc581610edef5b61352001f08a5cba14dda1ee))

- Update openspec/config.yaml with openspec-plus context and rules - Aligns with upstream
  sudokar/openspec-plus v1.4.0 - See CHANGELOG:
  https://github.com/sudokar/openspec-plus/releases/tag/v1.4.0

### Documentation

- Document remote installation
  ([`afd2a43`](https://github.com/frederico-mello/repository-hygiene/commit/afd2a43f0c2c8b2fb82b5d17da1eba449ac5d4f0))

- Propose agent-friendly audit report
  ([`ffe3c29`](https://github.com/frederico-mello/repository-hygiene/commit/ffe3c295ba02556ac9882dc4f30d1736c53792c4))

- Propose audit false-positive reduction
  ([`c168449`](https://github.com/frederico-mello/repository-hygiene/commit/c16844999919aaa7a3ec62d087a33c6b085fdac5))

- Propose scalable audit change
  ([`0773b60`](https://github.com/frederico-mello/repository-hygiene/commit/0773b602c8f019e3deda0e5fe5eb44c7e8d2684c))

- Propose scalable audit change
  ([`7abcc2a`](https://github.com/frederico-mello/repository-hygiene/commit/7abcc2a9a99f85b215119861a2904cdb0f974325))

- Reorganize README, align workflow template, add tests
  ([`3254d24`](https://github.com/frederico-mello/repository-hygiene/commit/3254d24da970d76b434824fe1ebf9bae6259e63c))

### Features

- Add agent audit reports
  ([`26d2080`](https://github.com/frederico-mello/repository-hygiene/commit/26d2080ecaf1f98be900ea9634eed61ef7c6ab17))

- Reduce audit false positives
  ([`1ed8cf8`](https://github.com/frederico-mello/repository-hygiene/commit/1ed8cf8e26522193408651c2b31c1afd2baed9e4))

- Robust-installation-path — suporte uvx, uv tool install, modulo Python
  ([`52e0131`](https://github.com/frederico-mello/repository-hygiene/commit/52e01312a7d76ea33b33ef2c566522212a3c276d))

- Adiciona __main__.py para execucao via python -m auditoria_higiene - Documenta fluxos uvx, uv tool
  install, pip e modulo Python no README - Nova spec instalacao-cli-uv com cenarios para cada fluxo
  - Novo CI multiplataforma (ubuntu/windows/macos) testando uvx e uv tool install - Testes
  extensivos para todos os fluxos: entry point, modulo, uvx, uv tool - Testes de mascara de
  segredos, codigos de saida, config invalida, docs - Arquiva change instalacao-cli-com-uv

- Sync delta specs to main specs and archive completed changes
  ([`afd4420`](https://github.com/frederico-mello/repository-hygiene/commit/afd4420f156b6fd44bc7d8524f8f969c764d23bb))

- Version control and release automation
  ([`f4102d5`](https://github.com/frederico-mello/repository-hygiene/commit/f4102d51bfc59c7d3be691dcabf33167d050b6d7))

- Conventional Commits audit rule (commit_check.py + core.py integration) - commit-msg hook
  installed by default on --init - Dynamic workflow template (no hardcoded version) - Semantic
  release pipeline (.github/workflows/release.yml) - actionlint validation, CHANGELOG.md, AGENTS.md
  - 13/13 tasks complete, 140 tests passing

- Version-control-and-release — OpenSpec Plus 1.4.0 + commit check module
  ([`52d5105`](https://github.com/frederico-mello/repository-hygiene/commit/52d5105952dc4c18ba3caa5941a36062ee9c5c12))

- Upgrade OpenSpec Plus de 1.3.0 para 1.4.0 - Adiciona regras mandatory no config.yaml para skills
  openspec-plus-* - Novo modulo commit_check.py: verifica se commits no branch principal seguem
  convencao (feat/fix/etc.) e referenciam issue - Testes para commit_check

- **openspec**: Agent-hygiene-skill — 22/22 tasks complete
  ([`e8c3673`](https://github.com/frederico-mello/repository-hygiene/commit/e8c36739997617828ef9c6f5486f96174809f83b))

- **openspec**: Sync agent-hygiene-flow delta spec to main specs
  ([`f0acdbf`](https://github.com/frederico-mello/repository-hygiene/commit/f0acdbfd9029dec4600a034822b29c683d818b67))

### Performance Improvements

- Scale artifact audit inventory
  ([`08152ed`](https://github.com/frederico-mello/repository-hygiene/commit/08152edcebc7bb861703d942bb4b1b9e849fd113))

### Refactoring

- Parametrize commit_check tests to reduce duplication
  ([`c9ec306`](https://github.com/frederico-mello/repository-hygiene/commit/c9ec30695136a14996bab3873e942b37df719b6e))

- Parametrize hook validation tests to reduce duplication
  ([`d0fab71`](https://github.com/frederico-mello/repository-hygiene/commit/d0fab712aa1bbc0b8f384626d491f8201cd22588))


## v0.2.0 (2026-07-22)

### Bug Fixes

- Address Mira review feedback on pre-commit hook
  ([`21aabd2`](https://github.com/frederico-mello/repository-hygiene/commit/21aabd25ce5257a16fde78c8fe89a204e11cc7fe))

- Address SonarCloud security hotspots
  ([`32b79a3`](https://github.com/frederico-mello/repository-hygiene/commit/32b79a3c39ad2d33a0aa004dcc3825e6e92ec2f5))

- Cache tracked files during audit
  ([`ac0b8e7`](https://github.com/frederico-mello/repository-hygiene/commit/ac0b8e7f9e98aa518cb504b5eb1b2b422af37256))

- Close README test file
  ([`6294f4a`](https://github.com/frederico-mello/repository-hygiene/commit/6294f4af3d92e27c47313dc83c74405995cbb0bb))

- Close remaining SonarCloud findings
  ([`b1b9e80`](https://github.com/frederico-mello/repository-hygiene/commit/b1b9e80068a4fb735bbbc8a593776ff89d52a7c3))

- Install package from git source
  ([`4fc6e84`](https://github.com/frederico-mello/repository-hygiene/commit/4fc6e84fb80b6735fc642d008316f6f88c536875))

- Use repository-hygiene package name
  ([`d4f5564`](https://github.com/frederico-mello/repository-hygiene/commit/d4f55643c47869b779f24f1aa6626b56d5c82067))

- **snapshot**: Prevent path traversal via staged file paths
  ([`527dbb6`](https://github.com/frederico-mello/repository-hygiene/commit/527dbb633330b247badbb63f756c4e0c5611af40))

### Documentation

- Propose PyPI 0.2.0 release
  ([`1090dc5`](https://github.com/frederico-mello/repository-hygiene/commit/1090dc5c15a1adfd6615cbaf80107ef683bcd2a0))

- Sync README with current behavior
  ([`23533b5`](https://github.com/frederico-mello/repository-hygiene/commit/23533b5ca4c933cd13359af0f9f0d232935ea9e6))

- Use uv commands in README
  ([`c2dbf57`](https://github.com/frederico-mello/repository-hygiene/commit/c2dbf5775e5f94e006df84971f1fd9be6174be9a))

### Features

- Add native pre-commit hook with staged-only validation
  ([`b22a526`](https://github.com/frederico-mello/repository-hygiene/commit/b22a5268b15a2391a7731b8e2b3d8afce9959e10))

- Bump to 0.2.0, update README, workflow, add tests
  ([`f078e2d`](https://github.com/frederico-mello/repository-hygiene/commit/f078e2d33e28c8a053c6b95bb7f9a99a0a3f4230))

- Initial release v0.1.0
  ([`9703bdc`](https://github.com/frederico-mello/repository-hygiene/commit/9703bdc20dd7245333186e849f0bdeabc5feb86a))
