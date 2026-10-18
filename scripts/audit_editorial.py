#!/usr/bin/env python3
"""Conservative source-provenance audit. Never equates an accessible article with fact-checking."""
import datetime as dt
import json
from pathlib import Path
from urllib.parse import urlparse
import requests
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"data/feed.json"
OFFICIAL=("hpe.com","juniper.net","vmware.com","broadcom.com","nutanix.com","github.blog","github.com","openai.com","anthropic.com","blog.google","cloud.google.com","huggingface.co","nvidia.com","microsoft.com","ibm.com","meta.com","servicenow.com","cisa.gov","nist.gov")
def audit(story,session):
    url=story.get("source","")
    result={"level":"Needs review","source_status":"Unconfirmed source","claim_status":"Not independently validated","confidence":"Low","checked_at":dt.datetime.now(dt.timezone.utc).isoformat(),"evidence":[{"url":url,"kind":"RSS discovery"}] if url.startswith("https://") else [],"note":"Original announcement and factual claims not verified."}
    if not url.startswith("https://"):return result
    try:
        r=session.get(url,timeout=7,allow_redirects=True,headers={"User-Agent":"HybridRadarAudit/1.0"})
        host=(urlparse(r.url).hostname or "").lower()
        if r.ok and r.content and urlparse(r.url).scheme=="https":
            result["evidence"].append({"url":r.url,"kind":"Accessible source"})
            if any(host==d or host.endswith("."+d) for d in OFFICIAL):
                result.update(level="Vendor claim",source_status="Official-domain page accessible",confidence="Medium",note="Official source accessible; performance claims, factual accuracy and impact have not been independently validated.")
            else:
                result.update(source_status="Third-party source accessible",note="Article accessible; independent corroboration not established.")
        else:result["note"]="Source returned no accessible successful content."
    except requests.RequestException:result["note"]="Source request failed; still unverified."
    return result
def main():
    data=json.loads(PATH.read_text(encoding="utf-8"))
    stories=data.get("stories",[])
    with requests.Session() as session:
        for i,story in enumerate(stories):
            story["editorial"]=audit(story,session) if i<15 else {"level":"Needs review","source_status":"Not inspected","claim_status":"Not independently validated","confidence":"Low","checked_at":None,"evidence":[],"note":"Outside the top 15 automatic source checks."}
    data["editorial_audit"]={"method":"Source provenance and accessibility only; no independent fact-checking","count":min(15,len(stories)),"checked_at":dt.datetime.now(dt.timezone.utc).isoformat()}
    PATH.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
