
# ROTCHAIN Auto Starter (No-Treo-Máy)

This repo lets you run your airdrop/ref farming **automatically on GitHub Actions** so you don't have to keep your phone or PC on.

## What it does
- Runs every 30 minutes (cron) on GitHub's servers.
- Loads your private keys (from a GitHub Secret) and loops through them.
- Reads your campaign definitions in `config/campaigns.yaml`.
- Prints progress logs and writes a daily report to the Actions artifacts.

> ⚠️ This is a starter. It does not contain integrations for specific campaigns. You (or I) can add them in `farmer.py` where indicated.

---

## Quick Start (10–15 mins)

### 0) Create a PRIVATE GitHub repository
- Name: `rotchain-auto`
- Make sure it's **Private**.

### 1) Upload the contents of this zip
Upload everything (keep folder structure).

### 2) Add your wallet keys securely
- Open your CSV file `rotchain_wallets_500_private_keys.csv`.
- **Base64-encode** its content (one simple way: https://www.base64encode.org/ ).
- In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**
  - Name: `WALLETS_CSV`
  - Value: (paste the base64 string)

Optional secrets:
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` — to send you progress reports.
- `CAMPAIGNS_YAML` — if you prefer to store `config/campaigns.yaml` as a secret (recommended).

### 3) Customize campaigns
- Edit `config/campaigns.yaml` to list which campaigns to run.
- Each campaign has a `name` and `actions` to simulate. Replace with your real logic later.

### 4) Done — it runs automatically
- The Action runs every 30 minutes.
- Check progress: **Actions → rotchain-farmer → latest run → logs**.
- A daily report file is saved as an artifact you can download.

---

## Where to add real campaign logic?
Open `farmer.py` and look for `# TODO: IMPLEMENT CAMPAIGN LOGIC HERE`.
You can insert your requests/automation for specific sites or on-chain calls.
(For on-chain, prefer using Alchemy/Ankr free RPC endpoints and avoid rate limits.)

## Security Notes
- **Never commit raw private keys or CSV** to the repo.
- Use GitHub **Secrets** only.
- This starter only loads keys to iterate accounts — you control the logic that signs/uses them.

## Support
Ping me in chat with your repo link (no secrets!), and I’ll help wire in a real campaign.
