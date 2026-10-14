#!/usr/bin/env python3
"""Fetch public RSS news headlines. Does not verify underlying reporting."""
import datetime, hashlib, json, re, time
from pathlib import Path
import requests, feedparser
ROOT=Path(__file__).resolve().parents[1]
TOPICS={
 "HPE Software":"HPE Morpheus OpsRamp Zerto GreenLake Juniper",
 "Competitive":"VMware Broadcom Nutanix virtualization",
 "Opportunity":"Canada enterprise government AI infrastructure funding",
 "Security":"hybrid cloud cybersecurity vulnerability CISA",
 "Emerging":"private cloud startup funding open source",
 "AI & Cloud":"AI infrastructure Kubernetes GPU cloud",
 "Partners":"HPE Juniper channel partner enterprise"
}
def clean(s):
 return re.sub(r"\s+"," ",re.sub(r"<[^>]*>"," ",s or "")).strip()
def fetch():
 news=[];seen=set()
 for cat,q in TOPICS.items():
  try:
   url="https://news.google.com/rss/search"
   res=requests.get(url,params={"q":q+" when:7d","hl":"en-US","gl":"US","ceid":"US:en"},headers={"User-Agent":"HybridRadarNews/1.0"},timeout=25)
   res.raise_for_status()
   entries=feedparser.parse(res.content).entries[:15]
  except Exception as e:
   print("Fetch unavailable:",cat,str(e));continue
  for item in entries:
   title=clean(item.get("title",""));link=item.get("link","")
   if not title or not link:continue
   key=re.sub(r"\W","",title.lower())[:110]
   if key in seen:continue
   seen.add(key)
   hits=sum(word in title.lower() for word in ("hpe","morpheus","opsramp","zerto","vmware","nutanix","quebec","canada","juniper","broadcom"))
   news.append({"id":hashlib.sha256(link.encode()).hexdigest()[:14],"cat":cat,"title":title,
    "summary":clean(item.get("summary",""))[:330] or "Read the linked source for the underlying reporting.",
    "impact":"Evaluate potential implications for hybrid-cloud architecture, customer needs or partner discussions. Verify the source before taking action.",
    "score":min(5,3+hits),"region":"Global / North America lens",
    "date":item.get("published","Date not supplied"),"source":link,
    "status":"RSS-discovered; source content not independently verified"})
 return sorted(news,key=lambda x:(x["score"],x["date"]),reverse=True)[:40]
if __name__=="__main__":
 target=ROOT/"data"/"feed.json";stories=fetch()
 if not stories:
  print("No results; retaining previous feed");quit()
 target.write_text(json.dumps({"generated_at":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),"stories":stories},ensure_ascii=False,indent=2)+"\n")
 print("Saved",len(stories),"stories")
