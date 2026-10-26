**Not ready for customer handoff:** the exporter works for the supplied records, but the delivered CSV is stale, contradicting HANDOFF.md.

| Requirement | Status | Evidence |
|---|---|---|
| R1: Deliver both invoices with `id,net,tax` and 20% tax | `not_implemented` | `exports/invoices.csv:1` contains only `id,net` and `sample-1,100`. Fresh artifact check: **FAIL**. |
| R2: Update the exporter | `implemented_and_verified` | `exporter.py:5–6` adds `tax` and calculates `net * 0.2`. Executing it with in-memory output produced both records with taxes `20.0` and `10.0`: **PASS**. Filesystem output was not exercised. |

Verification used `python3 -B -c` with this executable body:

```python
import csv, io, json
from pathlib import Path
from unittest.mock import patch

rows = json.loads(Path("invoices.json").read_text())
expected = [["id", "net", "tax"]] + [
    [r["id"], str(r["net"]), str(r["net"] * 0.2)] for r in rows
]
def check(text):
    return list(csv.reader(io.StringIO(text))) == expected

print("R1 artifact:", "PASS" if check(
    Path("exports/invoices.csv").read_text()) else "FAIL")

class Capture(io.StringIO):
    def close(self): pass

out = Capture()
code = Path("exporter.py").read_text()
with patch.object(Path, "read_text", return_value=json.dumps(rows)), \
     patch.object(Path, "open", return_value=out):
    exec(compile(code, "exporter.py", "exec"), {})
print("R2 exporter:", "PASS" if check(out.getvalue()) else "FAIL")
```

Reviewed `f3d76a4..28794b3`; HEAD is `28794b359b590d899726b811d5517e407fbe8a27`. The range changes only `exporter.py`. Tracked files are clean; supplied `instructions/` files are untracked. Branch and workspace were left unchanged.

Remaining work: regenerate and verify `exports/invoices.csv` before handoff.