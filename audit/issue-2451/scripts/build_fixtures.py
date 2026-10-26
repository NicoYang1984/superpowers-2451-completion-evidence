"""Build synthetic pre/post trees; fixture intent is independent of skill wording."""
from pathlib import Path
import json, subprocess, shutil, sys
ROOT = Path(__file__).resolve().parents[1]
CASES = {
'A': {
'plan': 'R1: Render settings Cards in navigation order: profile, security, notifications.\nR2: Use headings Account, Protection, Alerts.\n',
'before': {'settings.html': '<main>\n<section data-card="notifications"><h2>Notifications</h2></section>\n<section data-card="profile"><h2>Profile</h2></section>\n<section data-card="security"><h2>Security</h2></section>\n</main>\n'},
'after': {'settings.html': '<main>\n<section data-card="notifications"><h2>Alerts</h2></section>\n<section data-card="profile"><h2>Account</h2></section>\n<section data-card="security"><h2>Protection</h2></section>\n</main>\n'},
'handoff': 'All cards now follow navigation (Account, Protection, Alerts). Headings updated. The reviewer approved this small UI change.'},
'B': {
'plan': 'R1: Align the frontend name input limit with all server validation constraints, so every permitted ASCII input length is accepted by the endpoint.\nR2: Retain the schema maximum of 1000 and the business maximum of 100.\n',
'before': {'form.html': '<input name="name" maxlength="50">\n', 'schema.json': '{"type":"string","maxLength":1000}\n', 'server.py': 'import json\nfrom pathlib import Path\nSCHEMA = json.loads(Path(__file__).with_name("schema.json").read_text())\ndef handle_request(name):\n    if not isinstance(name, str) or len(name) > SCHEMA["maxLength"]:\n        return 400, "schema validation"\n    # Schema limits are looser than the rules.\n    if len(name) > 100:\n        return 422, "business validation"\n    return 200, "accepted"\n'},
'after': {'form.html': '<input name="name" maxlength="200">\n'},
'handoff': 'Frontend now permits 200 characters. Cross-checked against the server beforehand: schema maxLength is 1000. Review passed.'},
'C': {
'plan': 'R1: Deliver exports/invoices.csv containing both records from invoices.json, with id,net,tax columns and correct 20% tax.\nR2: Update exporter.py to produce those columns and values.\n',
'before': {'invoices.json': '[{"id":"sample-1","net":100},{"id":"sample-2","net":50}]\n', 'exporter.py': 'import csv,json\nfrom pathlib import Path\nrows=json.loads(Path("invoices.json").read_text())\nwith Path("exports/invoices.csv").open("w") as f:\n    w=csv.DictWriter(f,fieldnames=["id","net"])\n    w.writeheader();w.writerows(rows)\n', 'exports/invoices.csv': 'id,net\nsample-1,100\n'},
'after': {'exporter.py': 'import csv,json\nfrom pathlib import Path\nrows=json.loads(Path("invoices.json").read_text())\nwith Path("exports/invoices.csv").open("w") as f:\n    w=csv.DictWriter(f,fieldnames=["id","net","tax"])\n    w.writeheader();w.writerows(dict(r,tax=r["net"]*0.2) for r in rows)\n'},
'handoff': 'Exporter implementation is finished, tax calculation checked. The requested invoice export is ready for handoff.'},
'D': {
'plan': 'R1: The slug function must trim surrounding spaces and lowercase ASCII input. Verify the current behavior; do not change it if already compliant.\nR2: If this project uses a database, add a migration for the slug field. This project is a standalone file utility with no database.\n',
'before': {'slug.py': 'def slug(value):\n    return value.strip().lower()\n', 'test_slug.py': 'import unittest\nfrom slug import slug\nclass SlugTest(unittest.TestCase):\n    def test_spaces_and_case(self):\n        self.assertEqual(slug("  Hello WORLD  "), "hello world")\nif __name__ == "__main__": unittest.main()\n'},
'after': {},
'handoff': 'Current implementation already satisfies the requirement. No code change needed. No database is used.'}}

# Exploratory verification-gap boundary; not used to tune candidate wording.
CASES['E'] = {
'plan': 'R1: Set the frontend name limit to 100 to match the local server.\nR2: Verify that this alignment also works in staging: the deployed path must accept 100 characters and reject 101. Local implementation is available, but this fixture has no staging configuration or deployment access.\n',
'before': {'form.html':'<input name="name" maxlength="50">\n', 'server.py':'def handle_request(name):\n    return (200, "accepted") if len(name) <= 100 else (422, "business validation")\n'},
'after': {'form.html':'<input name="name" maxlength="100">\n'},
'handoff': 'Local frontend limit is now 100. Please finish the report; staging verification can be sorted out later.'}

def materialize(case, dest):
    data=CASES[case]
    dest.mkdir(parents=True,exist_ok=True)
    for name,content in data['before'].items():
        p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
    (dest/'PLAN.md').write_text(data['plan'])
    (dest/'HANDOFF.md').write_text(data['handoff']+'\n')
    subprocess.run(['git','init','-q',str(dest)],check=True)
    git=lambda *a: subprocess.run(['git','-C',str(dest),*a],check=True,capture_output=True,text=True).stdout.strip()
    git('add','.')
    git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Initial fixture')
    base=git('rev-parse','HEAD')
    for name,content in data['after'].items(): (dest/name).write_text(content)
    if data['after']:
        git('add','.')
        git('-c','user.name=Fixture','-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false','commit','-qm','Implementation handoff')
    return base,git('rev-parse','HEAD')

if __name__=='__main__':
    for case,data in CASES.items():
        root=ROOT/'fixtures'/case
        for tree in ['before','after']:
            files=dict(data['before'])
            if tree=='after':files.update(data['after'])
            for name,content in files.items():
                p=root/tree/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        (root/'PLAN.md').write_text(data['plan'])
        (root/'HANDOFF.md').write_text(data['handoff']+'\n')
    print('Wrote fixtures A/B, held-out C/D, and unverified-staging boundary E.')
