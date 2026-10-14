#!/usr/bin/env python3
import json,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
stories=json.loads((ROOT/"data"/"feed.json").read_text()).get("stories",[])
lines=["HYBRID CLOUD WEEKLY — "+datetime.date.today().isoformat(),"North America first | Global intelligence","","THIS WEEK'S AVAILABLE SIGNALS"]
if not stories:lines.append("No news has been collected yet.")
for i,s in enumerate(stories[:10],1):
 lines.extend(["",str(i)+". "+s["title"],"Category: "+s["cat"]+" | Relevance: "+str(s["score"])+"/5",s["summary"],"Presales angle: "+s["impact"],"Source: "+s["source"]])
lines.extend(["","AI MODEL & DEVELOPER TOOL WATCH","Review Frontier AI, Open Models, AI Dev Tools and Agent Testing categories in the daily feed for model releases, Hugging Face updates and evaluation harnesses.","","THREE DISCOVERY QUESTIONS","1. What virtualization renewals or migrations are approaching?","2. Where do customers need improved observability, cyber resilience or automation?","3. Which partners could support an architecture review?","","Editorial note: This is a digest of the latest RSS feed, not a fully researched seven-day retrospective. Verify primary sources."])
(ROOT/"data"/"weekly.json").write_text(json.dumps({"date":datetime.date.today().isoformat(),"text":"\n".join(lines)},ensure_ascii=False,indent=2)+"\n")
