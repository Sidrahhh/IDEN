import argparse
from pathlib import Path
from .core import run
from .utils import DEFAULT_STORAGE, DEFAULT_TIMEOUT_MS

def main():
    p = argparse.ArgumentParser(description="IdenHQ Challenge – Playwright Automation (Python)")
    p.add_argument("--base-url", default="https://hiring.idenhq.com/challenge",
                   help="Challenge URL (default: %(default)s)")
    p.add_argument("--username", default=None, help="Login username/email (or env IDEN_USERNAME)")
    p.add_argument("--password", default=None, help="Login password (or env IDEN_PASSWORD)")
    p.add_argument("--storage", default=str(DEFAULT_STORAGE), help="Path to storage_state JSON")
    p.add_argument("--output", default="products.json", help="Output JSON file")
    p.add_argument("--headless", default="true", choices=["true", "false"], help="Headless (default: true)")
    p.add_argument("--submit-url", default=None, help="Optional GitHub repo URL to submit on 'Submit Script' page")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_MS, help="Default element timeout in ms")

    ns = p.parse_args()

    run(
        base_url=ns.base_url,
        storage_state_path=Path(ns.storage),
        username=ns.username,
        password=ns.password,
        output_json=Path(ns.output),
        headless=(ns.headless.lower() == "true"),
        submit_url=ns.submit_url,
        default_timeout_ms=ns.timeout
    )
