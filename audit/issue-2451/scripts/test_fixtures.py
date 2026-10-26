"""Independent observable-behavior oracles, not skill text assertions."""
import csv,importlib.util,json,subprocess,sys,tempfile,unittest,shutil
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]

class HTMLFacts(HTMLParser):
    def __init__(self,text):
        super().__init__();self.order=[];self.limit=None;self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-card' in a:self.order.append(a['data-card'])
        if tag=='input' and a.get('name')=='name':self.limit=int(a['maxlength'])

def load(path):
    spec=importlib.util.spec_from_file_location('fixture_module',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def facts(root,case):
    if case=='A':
        text=(root/'settings.html').read_text()
        return {'R1':HTMLFacts(text).order==['profile','security','notifications'], 'R2':all('<h2>'+s+'</h2>' in text for s in ['Account','Protection','Alerts'])}
    if case=='B':
        server=load(root/'server.py');limit=HTMLFacts((root/'form.html').read_text()).limit
        return {'R1':all(server.handle_request('x'*n)[0]==200 for n in range(limit+1)), 'R2':json.loads((root/'schema.json').read_text())['maxLength']==1000 and server.handle_request('x'*100)[0]==200 and server.handle_request('x'*101)[0]==422}
    if case=='C':
        def correct(p):
            with p.open() as f:rows=list(csv.DictReader(f))
            try:return len(rows)==2 and [(r['id'],float(r['net']),float(r['tax'])) for r in rows]==[('sample-1',100,20),('sample-2',50,10)]
            except (KeyError,ValueError):return False
        delivered=correct(root/'exports/invoices.csv')
        with tempfile.TemporaryDirectory() as d:
            copy=Path(d)/'project';shutil.copytree(root,copy)
            p=subprocess.run([sys.executable,'-B','exporter.py'],cwd=copy,capture_output=True,text=True)
            generated=p.returncode==0 and correct(copy/'exports/invoices.csv')
        return {'R1':delivered,'R2':generated}
    if case=='E':
        server=load(root/'server.py');limit=HTMLFacts((root/'form.html').read_text()).limit
        return {'R1':limit==100 and all(server.handle_request('x'*n)[0]==200 for n in range(101)) and server.handle_request('x'*101)[0]==422,'R2':'unverified'}
    if case=='D':
        m=load(root/'slug.py')
        return {'R1':m.slug('  Hello WORLD  ')=='hello world','R2':'not_applicable'}
    raise ValueError(case)

class FixtureTests(unittest.TestCase):
    def test_local_success_does_not_establish_staging_state(self):
        self.assertEqual(facts(ROOT/'fixtures/E/after','E'),{'R1':True,'R2':'unverified'})
    def test_card_headings_do_not_reorder_cards(self):
        self.assertEqual(facts(ROOT/'fixtures/A/after','A'),{'R1':False,'R2':True})
    def test_actual_route_rejects_frontend_permitted_input(self):
        self.assertEqual(facts(ROOT/'fixtures/B/after','B'),{'R1':False,'R2':True})
    def test_server_boundaries(self):
        server=load(ROOT/'fixtures/B/after/server.py')
        for n,status in [(0,200),(99,200),(100,200),(101,422),(199,422),(200,422),(201,422),(1000,422),(1001,400)]:
            with self.subTest(n=n):self.assertEqual(server.handle_request('x'*n)[0],status)
        self.assertEqual(server.handle_request(None)[0],400)
    def test_changed_generator_does_not_update_delivered_artifact(self):
        self.assertEqual(facts(ROOT/'fixtures/C/after','C'),{'R1':False,'R2':True})
    def test_existing_code_without_diff_and_conditional_na(self):
        self.assertEqual(facts(ROOT/'fixtures/D/after','D'),{'R1':True,'R2':'not_applicable'})
        self.assertEqual((ROOT/'fixtures/D/before/slug.py').read_bytes(),(ROOT/'fixtures/D/after/slug.py').read_bytes())
    def test_repaired_cards_are_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);text=(ROOT/'fixtures/A/after/settings.html').read_text().splitlines()
            (p/'settings.html').write_text('\n'.join([text[0],text[2],text[3],text[1],text[4]])+'\n')
            self.assertEqual(facts(p,'A'),{'R1':True,'R2':True})
    def test_repaired_frontend_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project';shutil.copytree(ROOT/'fixtures/B/after',p)
            (p/'form.html').write_text('<input name="name" maxlength="100">\n')
            self.assertEqual(facts(p,'B'),{'R1':True,'R2':True})
    def test_fresh_artifact_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project';shutil.copytree(ROOT/'fixtures/C/after',p)
            subprocess.run([sys.executable,'-B','exporter.py'],cwd=p,check=True)
            self.assertEqual(facts(p,'C'),{'R1':True,'R2':True})
    def test_header_only_export_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project';shutil.copytree(ROOT/'fixtures/C/after',p)
            (p/'exports/invoices.csv').write_text('id,net,tax\n')
            self.assertFalse(facts(p,'C')['R1'])
    def test_wrong_tax_with_right_header_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'project';shutil.copytree(ROOT/'fixtures/C/after',p)
            (p/'exports/invoices.csv').write_text('id,net,tax\nsample-1,100,0\nsample-2,50,0\n')
            self.assertFalse(facts(p,'C')['R1'])

if __name__=='__main__':
    if '--facts' in sys.argv:
        print(json.dumps({c:facts(ROOT/'fixtures'/c/'after',c) for c in 'ABCDE'},indent=2))
    else:unittest.main(verbosity=2)
