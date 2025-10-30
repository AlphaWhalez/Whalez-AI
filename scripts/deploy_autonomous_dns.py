import os, uuid, json, time

try:
    import requests
except Exception:
    requests = None

ZONE_ID = os.getenv("CLOUDFLARE_ZONE_ID", "").strip()
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
DRY_RUN = os.getenv("DRY_RUN", "1").strip()
BASE_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"

def sanity_check():
    if DRY_RUN not in ("0", "1"):
        raise SystemExit("DRY_RUN must be '0' or '1'. Default is safe '1'.")
    if DRY_RUN == "0":
        missing = [k for k,v in (
            ("CLOUDFLARE_ZONE_ID", ZONE_ID),
            ("CLOUDFLARE_ACCOUNT_ID", ACCOUNT_ID),
            ("CLOUDFLARE_API_TOKEN", API_TOKEN)) if not v]
        if missing:
            raise SystemExit(f"Missing env vars: {', '.join(missing)}")

def generate_subdomain():
    return f"ai-{uuid.uuid4().hex[:6]}"

def build_payload(name, ip="127.0.0.1"):
    return {"type":"A","name":name,"content":ip,"ttl":120,"proxied":False}

def create_dns_record(payload):
    if DRY_RUN == "1":
        sim = {"simulated":True,"payload":payload,"ok":True}
        print(json.dumps(sim,indent=2)); return sim
    if not requests: raise RuntimeError("requests not installed for live run")
    headers={"Authorization":f"Bearer {API_TOKEN}","Content-Type":"application/json"}
    r=requests.post(BASE_URL,headers=headers,json=payload,timeout=15)
    return r.json()

def main():
    print("=== deploy_autonomous_dns.py ===")
    sanity_check()
    sub=generate_subdomain()
    root=os.getenv("ROOT_DOMAIN","deltaalpha-trade-pro.com")
    fqdn=f"{sub}.{root}"
    payload=build_payload(fqdn)
    result=create_dns_record(payload)
    print("Result:",json.dumps(result,indent=2))
    audit="/tmp/whalez_audit"; os.makedirs(audit,exist_ok=True)
    fn=f"{audit}/dns_{sub}_{int(time.time())}.json"
    open(fn,"w").write(json.dumps({"fqdn":fqdn,"result":result},indent=2))
    print("Audit log saved:",fn)

if __name__=="__main__":
    main()
