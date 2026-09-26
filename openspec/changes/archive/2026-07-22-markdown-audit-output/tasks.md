## 1. Markdown report generation

- [x] 1.1 Add the Markdown report format to the report selection contract while retaining text as the default.
- [x] 1.2 Implement Markdown rendering for status, severity groups, disabled rules, findings, evidence, and recommendations.
- [x] 1.3 Add coverage for successful, warning-only, failed, disabled-rule, deterministic-count, and sanitized Markdown reports.
- [x] 1.4 Verify Markdown escaping and omission of absent optional fields preserve the documented report structure.

## 2. Optional report file output

- [x] 2.1 Add the `--output` CLI option and route all supported formats through the selected destination.
- [x] 2.2 Preserve terminal output when `--output` is absent and preserve existing text, JSON, and SARIF content when it is present.
- [x] 2.3 Handle existing-file overwrite, missing parent directories, UTF-8 writing, and unwritable output paths with the documented stdout/stderr behavior and exit codes.
- [x] 2.4 Add CLI coverage for Markdown and existing formats written to files, default terminal output, overwrite behavior, UTF-8 content, and write failures.
- [x] 2.5 Update user documentation with Markdown and `--output` examples.
- [x] 2.6 Verify saved reports contain no unsanitized secret values and that output-path failures do not leave a success confirmation.
