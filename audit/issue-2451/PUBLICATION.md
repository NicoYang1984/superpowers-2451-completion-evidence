# Public archive and authoring disclosure

Publication preparation: 2026-10-26. This is a curated copy of existing experiments; no additional model experiment was run for publication.

## Scope and provenance

- Upstream base: `b58deb3b948d4c305feeac122700100419ee2777` (`dev`, Superpowers 7.0.1).
- Unchanged minimal production patch: `968c13faadad3de0a492580fe75db3f91620ad25`, three files / 61 additions.
- All final 30 session directories are included, plus the single collector diagnostic. Each final session has its prompt, original synthetic Git range, diff, report, metadata, CLI events, raw tool calls/results and fixture bundle. The before/after source trees and test scripts are included.
- Discovery history (40 sessions), the five V2 micro-tests, and connectivity probes are described in the evaluation but their raw archives remain local. They are not pooled into the published final comparison. Historical test logs are included; publication checks have separately named outputs.
- The local all-evidence commit is deliberately not an ancestor of the public branch. Its private path history is not published. Public history consists of upstream public history, the original minimal patch, and curated publication commits.
- The upstream README copy only normalizes trailing whitespace. The upstream copyright notice and full MIT text remain unchanged. Additional research code and text use the same MIT license.

## Sanitization

Only synthetic business records are used. The curated export excludes credentials/configuration files, personal sessions, unrelated project files, initial connector account data and third-party PR JSON dumps. Public tool records contain calls/results from the synthetic sessions, not full hidden reasoning or host session transcripts.

Private home prefixes become `/home/REDACTED`; historical `/private/tmp` prefixes become `/tmp`; system temporary folder paths become a generic temporary path. These are historical path placeholders and need replacing when replaying commands. OS usernames in directory listings become `REDACTED_USER`. No test result or numeric measurement was invented or changed. `logs/redaction-manifest.json` records the files changed by path substitution and their original/public SHA-256 hashes, before editorial publication updates. `scores.json` and `metrics.json` preserve `original_report_sha256` alongside the public `report_sha256`. Token counts, timings and word counts are the recorded original measurements, not measurements of the redacted copy. Git fixture bundles are unchanged and contain only allowlisted synthetic source files and synthetic author identities.

The publication checker tests bundle contents against the before/after fixtures, verifies recorded instruction hashes, checks all final reports/raw records are present and public report hashes match, checks citation bounds, and recomputes totals from scores and measurements. It does not independently validate the manual semantic grades. The initial suspected fabricated-execution finding was withdrawn after a collector defect was demonstrated; see `logs/red-observation.md` and `logs/agents/diagnostic-v2-A-1`.

## Agent and tools disclosure

The human partner requested an autonomous investigation, local candidate, real comparison and later a public technical archive and one issue comment. This is not the partner's original production incident. No independent human review or maintainer permission is asserted.

Experiments: Codex CLI `0.155.0-alpha.9`, model alias `gpt-6-astra`, medium reasoning, on macOS. Exact server model snapshot is unavailable. Each invocation uses `--ignore-user-config`, a read-only sandbox, full workflow/verification skill text supplied as fixture files, and built-in shell tools. This tests textual final-stage guidance, not installed Superpowers auto-triggering. The original study did not save an authoritative active-plugin inventory, so plugin isolation cannot be conclusively claimed from the CLI flag alone.

Publication: Codex desktop `26.915.31029` (build `9771`) with bundled CLI `0.155.0-alpha.9`; authoring agent is identified as GPT-6/Codex by its harness, with no exact server snapshot exposed. Tools used for publication: local Git/Python/shell, GitHub connector, Codex app tools, and unified-computer-use with the Codex in-app browser. No product plugin was used to implement the evidence contract. The session also exposes unrelated plugin capabilities; their installed/active status is not authoritatively inventoried by the available tool interface. This disclosure does not claim an isolated plugin-free desktop environment.

## Upstream status

Before publication, #2451 was open with zero comments. Current `dev` README, AGENTS.md and PR template were read again. Their rule forbids an uninvited agent-written PR fixing another person's issue; the permitted path is a report on the existing issue. No duplicate issue or upstream PR is part of this work. The publication is an independent experiment repository, not upstream endorsement. Formal PR consideration still needs a maintainer invitation, human review and human-written summary, plus stronger evidence in the original environment.
