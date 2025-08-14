
import os, json, datetime

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts} UTC] {msg}")

def save_report(results):
    os.makedirs("reports", exist_ok=True)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d")
    path = os.path.join("reports", f"report_{ts}.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    log(f"Saved report: {path}")
