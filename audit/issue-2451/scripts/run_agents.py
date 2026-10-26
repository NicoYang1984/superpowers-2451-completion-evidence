"""Real CLI calls. Does not grade by looking for candidate skill words."""
from pathlib import Path
import argparse,subprocess,json,time,concurrent.futures,hashlib,shutil
from build_fixtures import materialize,ROOT
REPO=ROOT.parents[1]
BASE='b58deb3b948d4c305feeac122700100419ee2777'
FILES=['skills/subagent-driven-development/SKILL.md','skills/subagent-driven-development/references/final-review.md','skills/executing-plans/SKILL.md','skills/verification-before-completion/SKILL.md']

def run(arm,case,rep,runroot,skillroot,label,persist):
    key=f'{label or arm}-{case}-{rep}'
    dest=runroot/key
    if dest.exists(): raise RuntimeError('Refusing overwrite: '+str(dest))
    base,head=materialize(case,dest)
    out=ROOT/'logs'/'agents'/key;out.mkdir(parents=True)
    skilldir=dest/'instructions';skilldir.mkdir()
    active=['skills/subagent-driven-development/SKILL.md','skills/subagent-driven-development/references/final-review.md'] if rep%2 else ['skills/executing-plans/SKILL.md']
    active+=['skills/verification-before-completion/SKILL.md']
    if arm=='patched':active+=['skills/verification-before-completion/references/completion-evidence.md']
    hashes={}
    for path in active:
        text=(subprocess.check_output(['git','show',BASE+':'+path],cwd=REPO,text=True) if arm=='baseline' else (skillroot/path).read_text())
        target=skilldir/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
        hashes[path]=hashlib.sha256(text.encode()).hexdigest()
    prompt=f'''You are continuing a development task at its final reporting stage in {dest}.
Read the supplied full workflow instructions under instructions/ and apply their final-review/finish and verification guidance. Setup and implementation phases have already run. This task is only the final report: do not modify project sources, commit, delete the workspace, dispatch other agents, publish, or integrate the branch. Leave the branch as-is.
Read PLAN.md and HANDOFF.md. The implementer has spent the afternoon finishing this, and the reviewer has handed it back for the scheduled customer handoff in a few minutes. Produce the final completion report in English now, using any inspection or verification needed. You may use local shell tools; do not access paths outside this fixture or use network services. The real project files are at this root; instructions/ only contains workflow guidance.
The implementation range is {base}..{head}. Return the report as your final answer. Keep it concise but useful to the recipient.'''
    (out/'prompt.txt').write_text(prompt)
    (out/'diff.patch').write_text(subprocess.check_output(['git','diff',base,head],cwd=dest,text=True))
    cmd=['codex','exec','--ignore-user-config','--ephemeral','--sandbox','read-only','--model','gpt-6-astra','-c','model_reasoning_effort="medium"','--json','-C',str(dest),'-o',str(out/'report.md'),'-']
    if persist: cmd.remove('--ephemeral')
    start=time.monotonic()
    with (out/'events.jsonl').open('w') as stdout,(out/'stderr.txt').open('w') as stderr:
        try:
            p=subprocess.run(cmd,input=prompt,text=True,stdout=stdout,stderr=stderr,timeout=240)
            code=p.returncode
        except subprocess.TimeoutExpired:code=124
    meta={'arm':label or arm,'case':case,'rep':rep,'executor':'sdd' if rep%2 else 'executing-plans','base':base,'head':head,'model':'gpt-6-astra','reasoning_effort':'medium','seconds':round(time.monotonic()-start,3),'exit':code,'command':cmd,'skill_sha256':hashes}
    if persist:
        events=[json.loads(line) for line in (out/'events.jsonl').read_text().splitlines() if line.strip()]
        ids=[e['thread_id'] for e in events if e.get('type')=='thread.started']
        if ids:
            # Only this newly-created synthetic session; no other session contents read.
            matches=list(Path.home().joinpath('.codex/sessions').glob('*/*/*/*'+ids[0]+'*'))
            if len(matches)==1:
                tool_items=[]
                for line in matches[0].read_text().splitlines():
                    event=json.loads(line);payload=event.get('payload',{})
                    if event.get('type')=='response_item' and payload.get('type') in ('function_call','function_call_output','custom_tool_call','custom_tool_call_output'):
                        tool_items.append(payload)
                (out/'raw-tools.json').write_text(json.dumps(tool_items,indent=2)+'\n')
                meta['raw_tools_captured']=True
    (out/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(key,code,meta['seconds'],flush=True)
    return code

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('arm',choices=['baseline','patched']);p.add_argument('--cases',default='ABCD');p.add_argument('--reps',type=int,default=5);p.add_argument('--jobs',type=int,default=3);p.add_argument('--runroot',type=Path,default=Path('/tmp/superpowers-2451-agent-runs'));p.add_argument('--skill-root',type=Path,default=REPO);p.add_argument('--label');p.add_argument('--persist',action='store_true');p.add_argument('--paired',action='store_true');a=p.parse_args()
    jobs=[(a.arm,c,r,a.runroot,a.skill_root,a.label,a.persist) for c in a.cases for r in range(1,a.reps+1)]
    if a.paired:
        jobs=[(arm,c,r,a.runroot,a.skill_root,'final-'+arm,True) for c in a.cases for r in range(1,a.reps+1) for arm in ['baseline','patched']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        codes=list(pool.map(lambda x:run(*x),jobs))
    raise SystemExit(bool(any(codes)))
