# IdenHQ Challenge – Playwright Automation (Python)

Campus Recruitment '26 Challenge 

This repository contains a Python + Playwright solution that:

- reuses/saves a session
- logs in if needed
- follows the hidden path  
  **Open Options → Inventory (tab) → Access Detailed View → Show Full Product Table**
- harvests the entire product table (pagination *and/or* infinite scroll)
- exports to JSON
- optionally submits your GitHub repo URL on the **Submit Script** page

Target app: https://hiring.idenhq.com/challenge

---

## Quick start

> Python 3.10+ recommended. Run in a fresh virtualenv.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install --with-deps chromium
```

Set credentials (either via .env or environment variables):
```bash
cp .env.example .env
```
edit .env with your email/password for the challenge app

```bash
python -m iden_bot \
  --base-url https://hiring.idenhq.com/challenge \
  --output products.json \
  --headless true
```

CLI options:

--base-url     Challenge URL (default: https://hiring.idenhq.com/challenge)

--username     Login username/email (or env IDEN_USERNAME)

--password     Login password (or env IDEN_PASSWORD)

--storage      Path to storage_state JSON (default: storage/iden_storage_state.json)

--output       Output JSON file (default: products.json)

--headless     "true" or "false" (default: true)

--submit-url   Optional GitHub repository URL to submit on the "Submit Script" page

--timeout      Default element timeout in ms (default: 15000)




