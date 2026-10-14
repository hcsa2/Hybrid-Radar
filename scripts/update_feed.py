#!/usr/bin/env python3
"""RSS headlines for Hybrid Radar. Source reporting is not independently verified."""
import datetime as dt
import hashlib
import html
import json
import re
from pathlib import Path
import feedparser
import requests

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
 "HPE Software": "HPE Morpheus OpsRamp Zerto GreenLake Juniper",
 "Competitive": "VMware Broadcom Nutanix virtualization",
 "Opportunity": "Canada enterprise government AI infrastructure funding",
 "Security": "hybrid cloud cybersecurity vulnerability CISA",
 "Emerging": "private cloud startup funding open source",
 "AI & Cloud": "AI infrastructure Kubernetes GPU cloud",
 "Partners": "HPE Juniper channel partner enterprise",
}
KEYWORDS=("hpe","morpheus","opsramp","zerto","vmware","nutanix","quebec","canada","juniper","broadcom")
def clean(value):
    value=str(value or "")
    for _ in range(3):
        updated=html.unescape(value)
        if updated==value: break
        value=updated
    value=re.sub(r"<[^>]+>"," ",value).replace("\u00a0"," ")
    return re.sub(r"\s+"," ",value).strip()
def timestamp(entry):
    parsed=entry.get("published_parsed") or entry.get("updated_parsed")
    try: return dt.datetime(*parsed[:6],tzinfo=dt.timezone.utc) if parsed else None
    except (ValueError,TypeError): return None
def main():
    stories=[]; seen=set()
    for category, query in TOPICS.items():
        try:
            response=requests.get("https://news.google.com/rss/search",params={"q":query+" when:7d","hl":"en-US","gl":"US","ceid":"US:en"},timeout=25,headers={"User-Agent":"HybridRadar/1.1"})
            response.raise_for_status()
            entries=feedparser.parse(response.content).entries[:15]
        except requests.RequestException as e:
            print("RSS unavailable",category,str(e));continue
        for entry in entries:
            title=clean(entry.get("title")); url=str(entry.get("link",""))
            if not title or not url.startswith("https://"):continue
            key=re.sub(r"\W+","",title.casefold())[:140]
            if key in seen:continue
            seen.add(key)
            summary=clean(entry.get("summary"))
            if len(summary)<45 or title.casefold() in summary.casefold() or summary.casefold().startswith(re.sub(r"\\s*-\\s*[^-]+$", "", title).strip().casefold()):
                summary="Headline from a public RSS feed. Read the source for the reporting and context."
            date=timestamp(entry)
            score=min(5,3+sum(k in title.casefold() for k in KEYWORDS))
            stories.append({"id":hashlib.sha256(url.encode()).hexdigest()[:14],"cat":category,"title":title,"summary":summary[:330],
                "impact":"Review the source and evaluate relevance to customer architecture or partner discussions; this item is not independently analyzed.",
                "score":score,"region":"Global / North America lens","date":date.strftime("%Y-%m-%d") if date else "Date not confirmed",
                "source":url,"status":"RSS-discovered, unverified","_ts":date.timestamp() if date else 0})
    if not stories:
        print("No stories; keeping previous feed");return
    stories.sort(key=lambda s:(s["score"],s["_ts"]),reverse=True)
    for s in stories:s.pop("_ts")
    target=ROOT/"data"/"feed.json"
    target.write_text(json.dumps({"generated_at":dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),"stories":stories[:40]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Published",min(len(stories),40))
if __name__=="__main__":main()
