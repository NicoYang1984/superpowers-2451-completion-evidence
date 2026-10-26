**Not ready for customer handoff: the delivered CSV is incomplete.**

Reviewed `ed813d9..c380564` against `PLAN.md`:

- **R1 — FAIL:** `exports/invoices.csv` contains only `sample-1` and columns `id,net`. It lacks `sample-2` and the required `tax` column.
- **R2 — PASS:** Fresh in-memory execution of `exporter.py` produced both invoices with `id,net,tax` and correct taxes of `20.0` and `10.0`.

`HANDOFF.md` therefore overstates completion. Before delivery, regenerate and verify the CSV.

Branch and files were left unchanged. No recorded rulings were found, and none were made.