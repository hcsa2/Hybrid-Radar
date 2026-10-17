#!/usr/bin/env python3
"""Produce a structured, source-linked weekly RSS digest (not independently fact-checked)."""
import datetime
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/"data"/"feed.json").read_text(encoding="utf-8"))
stories=data.get("stories",[])
today=datetime.datetime.now(datetime.timezone.utc).date()
selected=[]
seen=set()
for s in stories:
    if s.get("id") in seen:continue
    seen.add(s.get("id"))
    try:published=datetime.date.fromisoformat(s.get("date",""))
    except ValueError:continue
    if (today-published).days < 0 or (today-published).days > 7:continue
    selected.append(s)
    if len(selected)==10:break
questions=[
 "Which upcoming virtualization renewals create a modernization opportunity?",
 "Which AI workloads need private deployment, observability or runtime governance?",
 "Which partners could help deliver a discovery workshop next week?"
]
lines=["HYBRID RADAR WEEKLY — "+today.isoformat(),"North America first | Global technology intelligence",""]
for i,s in enumerate(selected,1):
    lines.extend([str(i)+". "+s.get("title",""),"Date: "+s.get("date","")+" | "+s.get("cat",""),"Relevance: "+str(s.get("score",3))+"/5",s.get("summary",""),"Presales angle: "+s.get("impact",""),"Source: "+s.get("source",""),""])
lines.extend(["DISCOVERY QUESTIONS",*questions,"","Editorial note: selected public RSS headlines; original reporting and claims have not been independently verified."])
out={"date":today.isoformat(),"stories":selected,"questions":questions,"methodology":"Selected public RSS headlines from the available seven-day feed, not a comprehensive or independently verified research report.","text":"\n".join(lines)}
(ROOT/"data"/"weekly.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
