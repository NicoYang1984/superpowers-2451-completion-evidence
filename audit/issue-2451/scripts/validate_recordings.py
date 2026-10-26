"""Deterministic integrity checks, not a semantic judge of completion prose."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[1]
BASE='b58deb3b948d4c305feeac122700100419ee2777'
errors=[];checked=0;citations=0;live_checked=0;live_unavailable=[]
for arm in ['baseline','patched']:
 for case in 'ABCDE':
  for rep in range(1,4):
   key=f'final-{arm}-{case}-{rep}';d=ROOT/'logs/agents'/key
   try:
    m=json.loads((d/'metadata.json').read_text());report=(d/'report.md').read_text();raw=json.loads((d/'raw-tools.json').read_text())
    assert m['exit']==0 and report.strip() and raw and m.get('raw_tools_captured'), 'incomplete recording'
    for path,digest in m['skill_sha256'].items():
     text=subprocess.check_output(['git','show',BASE+':'+path],cwd=REPO) if arm=='baseline' else (REPO/path).read_bytes()
     assert hashlib.sha256(text).hexdigest()==digest,'skill changed during run: '+path
    for file,line in re.findall(r'((?:exports/)?[\w-]+\.(?:html|py|json|csv)):(\d+)',report):
     p=ROOT/'fixtures'/case/'after'/file
     assert p.exists() and 1<=int(line)<=len(p.read_text().splitlines()),'invalid citation '+file+':'+line
     citations+=1
    # Check only the exact synthetic directory named by this recorded invocation.
    cmd=m['command'];runroot=Path(cmd[cmd.index('-C')+1])
    if runroot.exists():
     live_checked+=1
     for p in (ROOT/'fixtures'/case/'after').rglob('*'):
      if p.is_file(): assert (runroot/p.relative_to(ROOT/'fixtures'/case/'after')).read_bytes()==p.read_bytes(),'fixture mutated'
     assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=runroot,text=True).strip()==m['head'],'HEAD changed'
    else: live_unavailable.append(key)
    checked+=1
   except Exception as e:errors.append(key+': '+str(e))
result={'recordings_checked':checked,'live_source_checks':live_checked,'live_source_unavailable':live_unavailable,'citations_in_bounds':citations,'errors':errors,'scope':'Integrity only; semantic grading is in scores.json and EVALUATION.md'}
print(json.dumps(result,indent=2));sys.exit(bool(errors))
