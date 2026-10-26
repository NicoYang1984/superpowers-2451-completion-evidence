"""Derive counts and review views from recorded real CLI events; no semantic auto-grading."""
from pathlib import Path
import json,statistics,hashlib
ROOT=Path(__file__).resolve().parents[1]
def clean_view(text):
    return '\n'.join(line.rstrip() for line in text.splitlines()).rstrip()+'\n'

rows=[]
for d in sorted((ROOT/'logs/agents').iterdir()):
    if not (d/'metadata.json').exists():continue
    m=json.loads((d/'metadata.json').read_text())
    events=[json.loads(s) for s in (d/'events.jsonl').read_text().splitlines() if s.strip()]
    commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
    completed=[e for e in events if e.get('type')=='turn.completed']
    usage=completed[-1].get('usage',{}) if completed else {}
    report=(d/'report.md').read_text() if (d/'report.md').exists() else ''
    raw=json.loads((d/'raw-tools.json').read_text()) if (d/'raw-tools.json').exists() else None
    raw_calls=sum(x.get('type') in ('function_call','custom_tool_call') for x in raw) if raw is not None else None
    rows.append(dict(raw_tool_calls=raw_calls,run=d.name,arm=m['arm'],case=m['case'],rep=m['rep'],seconds=m['seconds'],exit=m['exit'],tool_calls=len(commands),usage=usage,report_words=len(report.split()),report_sha256=hashlib.sha256(report.encode()).hexdigest(),recorded_python_commands=sum('python' in c['command'] for c in commands)))
    if raw is not None:
        (d/'raw-tools-review.txt').write_text(clean_view('\n\n'.join(x.get('type','')+' '+x.get('name','')+'\n'+str(x.get('input',x.get('arguments',x.get('output','')))) for x in raw)))
    view=[]
    for c in commands:
        view+=['COMMAND: '+c['command'],'EXIT: '+str(c['exit_code']),'OUTPUT TAIL:\n'+c['aggregated_output'][-1800:],'']
    (d/'command-review.txt').write_text(clean_view('\n'.join(view)))
(ROOT/'logs/metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
for arm in sorted(set(r['arm'] for r in rows)):
    group=[r for r in rows if r['arm']==arm]
    print(arm,'n=',len(group),'median_seconds=',round(statistics.median(r['seconds'] for r in group),2),'tools=',sum(r['tool_calls'] for r in group),'reported_tokens=',sum(r['usage'].get('input_tokens',0)+r['usage'].get('output_tokens',0) for r in group))
