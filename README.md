# Superpowers #2451 — completion evidence experiment

A reproducible, agent-assisted final-report-stage experiment for [obra/superpowers#2451](https://github.com/obra/superpowers/issues/2451). **This is an independent research archive, not an official Superpowers release or an accepted fix.**

The issue describes reports that restate a plan without checking the implementation: renamed settings headings reported as reordered cards, and a frontend limit checked against a schema while missing a stricter server business rule. The candidate connects both execution workflows' Finish steps to an explicit per-requirement evidence contract.

**The tested model did not reproduce the original false-completion behavior.** Both arms detected the seeded implementation gaps. The measured improvement is in final-report auditability, not demonstrated functional accuracy.

| Final comparison | Baseline | Patched |
|---|---:|---:|
| Fresh model sessions (5 cases × 3) | 15 | 15 |
| False functional completion claims | 0 | 0 |
| Unimplemented requirements identified | 9/9 | 9/9 |
| Strict report evidence completeness | 6/30 | 30/30 |
| False rejection of already-correct tasks | 0/3 | 0/3 |
| Mean runtime, seconds | 49.062 | 52.586 |
| Mean report words | 92.67 | 181.40 |

Same model alias `gpt-6-astra`, medium reasoning, Codex CLI `0.155.0-alpha.9`, macOS. Each arm has 10 SDD and 5 executing-plans sessions. Manual scoring was not blind or independently human-reviewed. Accepting a unique function name as a source locator raises baseline evidence completeness to 9/30. These correlated requirement rows are not independent tasks; 100% does not imply universal reliability. No full development lifecycle, plugin auto-triggering, original Claude/Windows environment, or official Quorum evaluation was tested.

Published technical feedback: [original issue comment](https://github.com/obra/superpowers/issues/2451#issuecomment-6413269117). No upstream PR was submitted.

## Review the contribution

- [Minimal patch commit](https://github.com/NicoYang1984/superpowers-2451-completion-evidence/commit/968c13faadad3de0a492580fe75db3f91620ad25): **3 production files, 61 added lines**, no new dependencies. [Portable patch](audit/issue-2451/fix.patch).
- [Method and scoring protocol](audit/issue-2451/PROTOCOL.md); [detailed results, costs and limitations](audit/issue-2451/EVALUATION.md) (Chinese).
- [Full technical report](audit/issue-2451/REPORT.md) (Chinese); [ground truth matrix](audit/issue-2451/EVIDENCE_MATRIX.md).
- [Final reports and tool evidence](audit/issue-2451/logs/agents); [per-requirement scores](audit/issue-2451/logs/scores.json); [numeric summary](audit/issue-2451/logs/summary.json).
- [Reproduction instructions](audit/issue-2451/REPRODUCTION.md); [publication scope, redaction and authoring disclosure](audit/issue-2451/PUBLICATION.md).

The shared contract maps Plan → Implementation → Diff → Verification → Report, with independent states `implemented_and_verified`, `implemented_but_unverified`, `not_implemented`, and `not_applicable`. Existing correct code may satisfy a requirement without a new diff. A diff proves a change, not correct behavior. Tests must cover the relevant validation layers; generated deliverables must be inspected separately from their generators. Unavailable verification remains explicit.

## Reproduce without calling a model

Requires Git and Python 3.9+; uses the Python standard library only. From this repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/test_fixtures.py
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/test_fixtures.py --facts
PYTHONDONTWRITEBYTECODE=1 python3 audit/issue-2451/scripts/verify_publication.py
```

The 11 fixture tests verify the seeded ground truth, not the efficacy of prose. The publication checker restores all 30 final fixture bundles into temporary directories, checks their sources/commits and recorded instruction hashes, and recomputes aggregate metrics from archived measurements. It does not rerun the model or treat path validity as semantic proof.

Cases: A heading-only UI changes; B frontend/schema/business limits 200/1000/100; C held-out stale CSV despite a correct exporter; D already-correct code with zero diff and a conditional N/A migration; E unavailable staging verification. A checks HTML structure, B invokes a local handler directly, C checks the delivered CSV and generator separately. No browser/HTTP/staging coverage is implied.

For an optional fresh model run, follow the reproduction document in a separate checkout. It consumes model usage; it is unnecessary for auditing the archived comparison. Historical logs are path-redacted, with original and public hashes preserved. CLI JSONL omitted some nested calls: final comparisons include raw tool records so missing JSONL events are not mistaken for fabricated execution.

## Provenance and contribution boundary

Based on upstream `dev` commit `b58deb3b948d4c305feeac122700100419ee2777`; the original patch commit is preserved. The public archive is a separate commit on top of that patch. Historical upstream files remain to support reproducibility; see [upstream README](README.upstream.md). No upstream PR has been opened, and no maintainer invitation or human diff approval is claimed.

Superpowers copyright (c) 2025 Jesse Vincent. The original [MIT License](LICENSE) is retained verbatim; the added patch and research material are also distributed under MIT. This experiment makes no claims about another product's capabilities.
