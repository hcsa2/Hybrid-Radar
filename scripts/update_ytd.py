#!/usr/bin/env python3
"""Build an indicative 2026-to-date news archive from public Google News RSS search results.
This is not a complete record of the year, and historical RSS availability varies.
"""
import datetime as dt
import hashlib
import json
import re
import time
from pathlib import Path
import requests
import feedparser
from update_feed import TOPICS, clean, timestamp

ROOT=Path(__file__).resolve().parents[1]
YEAR=2026
START=dt.date(YEAR,1,1)
END=min(dt.datetime.now(dt.timezone.utc).date(),dt.date(YEAR,12,31))
MAX_PER_MONTH_CATEGORY=12

def month_ranges():
    month=1
    while month<=END.month:
        start=dt.date(YEAR,month,1)
        stop=dt.date(YEAR+1,1,1) if month==12 else dt.date(YEAR,month+1,1)
        yield start,min(stop,END+dt.timedelta(days=1))
        month+=1

def main():
    session=requests.Session()
    stories=[]
    seen=set()
    attempted=0
    for start,stop in month_ranges():
        for category,query in TOPICS.items():
            attempted+=1
            search=f'{query} after:{start.isoformat()} before:{stop.isoformat()}'
            try:
                response=session.get("https://news.google.com/rss/search",
                    params={"q":search,"hl":"en-US","gl":"US","ceid":"US:en"},
                    headers={"User-Agent":"HybridRadar/1.2"},timeout=25)
                response.raise_for_status()
                entries=feedparser.parse(response.content).entries[:MAX_PER_MONTH_CATEGORY]
            except requests.RequestException as error:
                print("Unavailable",start,category,error)
                continue
            for entry in entries:
                title=clean(entry.get("title"))
                link=str(entry.get("link",""))
                published=timestamp(entry)
                if not title or not link.startswith("https://") or not published:continue
                date=published.date()
                if not START<=date<=END or not start<=date<stop:continue
                key=re.sub(r"\W+","",title.casefold())[:140]
                if key in seen:continue
                seen.add(key)
                summary=clean(entry.get("summary"))
                if len(summary)<45 or summary.casefold().startswith(re.sub(r"\s*-\s*[^-]+$","",title).strip().casefold()):
                    summary="Historical headline retrieved from a public RSS index. Read the original reporting for details."
                score=min(5,3+sum(k in title.casefold() for k in
                    ("hpe","morpheus","opsramp","zerto","vmware","nutanix","canada","quebec","juniper","broadcom")))
                stories.append({
                    "id":hashlib.sha256(link.encode()).hexdigest()[:14],
                    "title":title,"cat":category,"date":date.isoformat(),
                    "month":start.strftime("%B"),"source":link,
                    "summary":summary[:300],
                    "impact":"Historical context to research; relevance and factual details require source verification.",
                    "score":score,"region":"Global / North America lens",
                    "status":"Historical RSS discovery — not independently fact-checked",
                })
        print("Collected through",start.strftime("%B"),len(stories))
        time.sleep(0.3)
    stories.sort(key=lambda s:(s["date"],s["score"]),reverse=True)
    output={
        "year":YEAR,"generated_at":dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "coverage_start":START.isoformat(),"coverage_end":END.isoformat(),
        "methodology":"Select articles retrievable through public Google News RSS topic searches, month by month. Not exhaustive; publication dates and claims should be verified with primary sources.",
        "stories":stories[:650],
    }
    target=ROOT/"data"/"ytd.json"
    if not stories:
        print("No historical results. Keeping existing archive.");return
    target.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Saved",len(output["stories"]),"historical stories from",attempted,"searches")

if __name__=="__main__":main()
