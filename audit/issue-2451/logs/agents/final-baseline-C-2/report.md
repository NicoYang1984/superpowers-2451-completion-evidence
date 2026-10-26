**Not ready for customer handoff.** Fresh verification contradicts HANDOFF.md’s completion claim.

- **R1 — FAIL:** `exports/invoices.csv` contains only `sample-1` and columns `id,net`. It lacks the tax column and `sample-2`. This is an Important handoff blocker.
- **R2 — PASS:** Executing `exporter.py` with output captured in memory produced both invoices with `id,net,tax` and correct taxes of `20.0` and `10.0`.

Before handoff, regenerate and verify the delivered CSV. No sources or branch state were changed; no commits, integration, or cleanup were performed.

No recorded rulings or deferred minors were found.