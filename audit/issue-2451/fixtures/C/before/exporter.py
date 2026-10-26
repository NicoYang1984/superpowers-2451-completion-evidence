import csv,json
from pathlib import Path
rows=json.loads(Path("invoices.json").read_text())
with Path("exports/invoices.csv").open("w") as f:
    w=csv.DictWriter(f,fieldnames=["id","net"])
    w.writeheader();w.writerows(rows)
