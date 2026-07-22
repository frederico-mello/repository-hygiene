## Context

The README currently documents the audit command and its formats, but the first-use setup and file-output workflow are implicit. The change is documentation-only and must preserve the existing command behavior and examples.

## Goals / Non-Goals

**Goals:**

- Make first-use setup discoverable.
- Show shell redirection examples for each supported report format.
- Explain exit codes in the context of saved reports.

**Non-Goals:**

- Adding a report-output option to the CLI.
- Changing report contents, formats, or exit-code behavior.
- Adding new configuration rules or workflow behavior.

## Decisions

- Extend the existing README usage section rather than create separate documentation. This keeps the complete command workflow in the location users already consult.
- Use shell redirection (`>`) in examples because the CLI already writes reports to standard output and no runtime change is required.
- Show `install` before `audit` in the first-use flow because the default audit depends on `auditoria.yaml`.
- Keep text, JSON, and SARIF examples explicit so users can choose an artifact suitable for humans, automation, or code-scanning integrations.

## Risks / Trade-offs

- [Users may confuse report files with configuration files] -> Label configuration and generated report examples separately.
- [Shell redirection can hide command failure if users only inspect the file] -> Document exit codes and state that findings still return exit code `1`.
