"""Offline archive integrity and arithmetic; never invokes a model or grades prose."""
from pathlib import Path
import hashlib, json, re, statistics, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BASE = 'b58deb3b948d4c305feeac122700100419ee2777'
FIX = '968c13faadad3de0a492580fe75db3f91620ad25'
def git(cwd, *args):
    return subprocess.check_output(['git', '-C', str(cwd), *args], stderr=subprocess.PIPE)
def digest(data): return hashlib.sha256(data).hexdigest()
def load(path): return json.loads(path.read_text())
scores = load(ROOT/'logs/scores.json')
metrics = load(ROOT/'logs/metrics.json')
summary = load(ROOT/'logs/summary.json')
expected_runs = {f'final-{arm}-{case}-{rep}' for arm in ('baseline','patched') for case in 'ABCDE' for rep in range(1,4)}
assert {r['run'] for r in scores} == expected_runs and len(scores) == 30
assert {r['run'] for r in metrics} == expected_runs and len(metrics) == 30
citations = 0
for row in scores:
    d = ROOT/'logs/agents'/row['run']; m = load(d/'metadata.json')
    report = (d/'report.md').read_bytes(); raw = load(d/'raw-tools.json')
    assert m['exit'] == 0 and m['raw_tools_captured'] and raw
    assert digest(report) == row['report_sha256']
    metric = next(r for r in metrics if r['run'] == row['run'])
    assert digest(report) == metric['report_sha256']
    assert metric['raw_tool_calls'] == sum(x['type'] in ('function_call','custom_tool_call') for x in raw)
    assert metric['seconds'] == m['seconds']
    events = [json.loads(s) for s in (d/'events.jsonl').read_text().splitlines() if s.strip()]
    assert [e for e in events if e['type']=='turn.completed'][-1]['usage'] == metric['usage']
    for path, sha in m['skill_sha256'].items():
        ref = BASE if m['arm']=='final-baseline' else FIX
        assert digest(git(REPO,'show',ref+':'+path)) == sha
    for file,line in re.findall(r'((?:exports/)?[\w-]+\.(?:html|py|json|csv)):(\d+)',report.decode()):
        assert 1 <= int(line) <= len((ROOT/'fixtures'/m['case']/'after'/file).read_text().splitlines())
        citations += 1
    with tempfile.TemporaryDirectory(prefix='completion-archive-') as temp:
        subprocess.run(['git','clone','-q',str(d/'fixture.bundle'),temp],check=True,stderr=subprocess.PIPE)
        assert git(temp,'rev-parse','HEAD').decode().strip() == m['head']
        for ref, tree in [(m['base'],'before'),(m['head'],'after')]:
            fixture=ROOT/'fixtures'/m['case']
            expected={str(p.relative_to(fixture/tree)):p.read_bytes() for p in (fixture/tree).rglob('*') if p.is_file()}
            expected.update({n:(fixture/n).read_bytes() for n in ('PLAN.md','HANDOFF.md')})
            assert set(git(temp,'ls-tree','-r','--name-only',ref).decode().splitlines()) == set(expected)
            for name,data in expected.items(): assert git(temp,'show',ref+':'+name) == data
        assert git(temp,'diff',m['base'],m['head']) == (d/'diff.patch').read_bytes()
        identities=set(git(temp,'log','--all','--format=%an <%ae>%n%cn <%ce>').decode().splitlines())
        assert identities == {'Fixture <fixture@example.invalid>'}, identities
for arm in ('final-baseline','final-patched'):
    group=[r for r in metrics if r['arm']==arm]; grades=[s for s in scores if s['run'].startswith(arm+'-')]; s=summary[arm]
    assert s['runs']==len(group)==15
    assert s['false_functional_completion_claims']==sum(r['false_functional_completion_claims'] for r in grades)
    gaps=[r for r in grades if r['gap_identified'] is not None]
    assert s['gap_recall']==[sum(r['gap_identified'] for r in gaps),len(gaps)]
    assert s['evidence_complete']==[sum(sum(r['evidence_complete'].values()) for r in grades),sum(len(r['evidence_complete']) for r in grades)]
    assert sum(r['normal_task_false_rejection'] is True for r in grades)==0
    assert sum(r['normal_task_false_rejection'] is False for r in grades)==3
    assert sum(r['staging_honestly_unverified'] is True for r in grades)==3
    assert s['raw_top_level_tool_calls']==sum(r['raw_tool_calls'] for r in group)
    for key in ('input_tokens','cached_input_tokens','output_tokens'): assert s[key]==sum(r['usage'][key] for r in group)
    assert s['mean_seconds']==round(statistics.mean(r['seconds'] for r in group),3)
    assert s['median_seconds']==round(statistics.median(r['seconds'] for r in group),3)
    assert s['mean_report_words']==round(statistics.mean(r['report_words'] for r in group),2)
assert git(REPO,'diff',BASE,FIX,'--numstat').decode().splitlines() == [
'5\t0\tskills/executing-plans/SKILL.md',
'5\t0\tskills/subagent-driven-development/references/final-review.md',
'51\t0\tskills/verification-before-completion/references/completion-evidence.md']
assert not git(REPO,'diff',FIX,'--','skills')
assert git(REPO,'show',BASE+':LICENSE') == (REPO/'LICENSE').read_bytes()
print(json.dumps({'final_recordings':30,'restored_fixture_bundles':30,'citation_bounds_checked':citations,'summary_recomputed':True,'production_patch_unchanged':True,'license_unchanged':True,'scope':'Archive integrity and numeric aggregation only; no model rerun or independent semantic grading.'},indent=2))
