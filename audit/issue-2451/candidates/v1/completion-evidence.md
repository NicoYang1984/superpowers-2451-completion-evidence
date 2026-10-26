# Completion Evidence

At the end of a plan, produce the completion report from inspected work:
plan → implementation → diff → verification → report.

Re-read the plan and its acceptance requirements. Inspect the current code
and deliverables, the full implementation range from the branch's starting
commit to HEAD, and any uncommitted or untracked work. Record the revision
and working-tree state being reported. A plan, completion ledger, or review
verdict identifies claims to check; it is not evidence that they are true.

## Required report content

Include one row or bullet per requirement, with these fields:

- **Requirement:** the plan requirement being accounted for; split compound
  requirements when their outcomes differ.
- **Status:** one of:
  - `implemented_and_verified`: inspected implementation and relevant
    verification establish the requested behavior or deliverable.
  - `implemented_but_unverified`: implementation is present, but the required
    verification is missing, blocked, or inconclusive. Name what remains
    unknown; do not imply it passed.
  - `not_implemented`: the requested behavior or deliverable is missing or
    contradicts the requirement, even if related code changed or tests pass.
  - `not_applicable`: the requirement's condition does not apply. State the
    condition and the evidence for that decision; difficulty is not a reason.
- **Implementation evidence:** inspected `file:line` or deliverable location
  and the relevant change in the recorded revision range. If existing code
  already meets the requirement, cite and verify that code; no new diff is
  needed. If the implementation cannot be inspected, state that uncertainty
  rather than asserting it exists or is absent.
- **Verification evidence:** the actual command or runtime check, observed
  result, and its scope. Include enough detail to repeat it, or a durable
  location containing those details. For missing verification, name the gap.

Match evidence to the claim. A diff proves a change, not correct behavior;
a passing test proves only what it exercises. For behavior spanning layers,
trace the exercised path through each relevant layer and name which ones
were checked. Inspect the actual delivered artifact as well as its producer.

Write the summary from this map. Only `implemented_and_verified` rows support
unqualified completion claims. Surface the other statuses and remaining
work explicitly; a clean review does not erase them. Preserve the map and
the evidence it cites in the final response or a durable, human-reachable
artifact before workspace cleanup; links into deleted scratch do not count.
