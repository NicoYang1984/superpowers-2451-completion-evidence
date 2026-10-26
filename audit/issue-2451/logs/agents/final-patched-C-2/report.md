**Not ready for customer handoff:** the exporter works for the supplied inputs, but the delivered CSV is stale.

Reviewed `aaa525f..83ef8ff`; HEAD is `83ef8ff78abda61372c6fd347128f0e4c7e29649`. Tracked files are unchanged; `instructions/` is untracked.

| Requirement | Status | Evidence |
|---|---|---|
| R1: Deliver both invoices with `id,net,tax` and 20% tax | `not_implemented` | `exports/invoices.csv:1` contains only `id,net` and `sample-1,100`. Verification returned **R1 FAIL**. The implementation range does not update this artifact. |
| R2: Update the exporter | `implemented_and_verified` | `exporter.py:5–6` adds the tax column and calculation. Executing it with output redirected to memory returned **R2 PASS**, producing both invoices with taxes `20.0` and `10.0`. |

Verification ran with `python3 -B -c` using this executable body:
```python
import io, runpy
from pathlib import Path
from unittest.mock import patch

class Buffer(io.StringIO):
    def close(self): pass

out = Buffer()
original = Path.open
with patch.object(Path, "open", lambda p, *a, **k:
                  out if a == ("w",) else original(p, *a, **k)):
    runpy.run_path("exporter.py")

expected = "id,net,tax\nsample-1,100,20.0\nsample-2,50,10.0\n"
assert out.getvalue().replace("\r\n", "\n") == expected
print("R2 PASS: generated both records with correct columns and tax")
actual = Path("exports/invoices.csv").read_text()
print("R1", "PASS" if actual == expected else "FAIL", repr(actual))
```

Remaining work: regenerate and verify `exports/invoices.csv` before delivery. No files were modified, and the branch was left as-is.