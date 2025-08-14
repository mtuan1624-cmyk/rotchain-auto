
import os, csv, io, base64, datetime, json
from utils.log import log, save_report

def load_wallets_from_secret():
    b64 = os.environ.get("WALLETS_CSV", "").strip()
    if not b64:
        raise RuntimeError("Missing GitHub Secret WALLETS_CSV (base64 of rotchain_wallets_500_private_keys.csv)")
    data = base64.b64decode(b64).decode("utf-8", errors="ignore")
    rows = list(csv.DictReader(io.StringIO(data)))
    # Expect columns: index, private_key_hex
    wallets = [{"index": r.get("index"), "pk": r.get("private_key_hex")} for r in rows if r.get("private_key_hex")]
    return wallets

def load_campaigns():
    yml_secret = os.environ.get("CAMPAIGNS_YAML", "").strip()
    if yml_secret:
        text = yml_secret
    else:
        with open("config/campaigns.yaml", "r", encoding="utf-8") as f:
            text = f.read()
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML not installed. Add 'pip install pyyaml' in workflow.")
    doc = yaml.safe_load(text) or {}
    return doc.get("campaigns", [])

def run_step(wallet, campaign_name, step):
    # TODO: IMPLEMENT CAMPAIGN LOGIC HERE
    # This is where you'd add real HTTP/API/on-chain actions.
    # For now we just simulate the action and return a result record.
    return {"wallet": wallet["index"], "campaign": campaign_name, "step": step, "status": "ok"}

def run():
    wallets = load_wallets_from_secret()
    campaigns = load_campaigns()
    log(f"Loaded {len(wallets)} wallets")
    log(f"Loaded {len(campaigns)} campaigns")

    results = []
    for c in campaigns:
        name = c.get("name", "unknown")
        steps = c.get("steps", [])
        for w in wallets:
            for step in steps:
                res = run_step(w, name, step)
                results.append(res)
        log(f"Completed campaign: {name} for {len(wallets)} wallets x {len(steps)} steps")

    # Save daily report
    save_report(results)
    log("All done.")

if __name__ == "__main__":
    run()
