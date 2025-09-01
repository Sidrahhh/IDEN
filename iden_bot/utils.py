import os, time
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv
from playwright.sync_api import Page, TimeoutError as PWTimeout

load_dotenv()

DEFAULT_STORAGE = Path("storage/iden_storage_state.json")
DEFAULT_TIMEOUT_MS = 15000
NAV_TIMEOUT_MS = 20000

def log(msg: str) -> None:
    print(f"[iden] {msg}")

def sleep(sec: float) -> None:
    time.sleep(sec)

def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name, default)
    return v

def try_fill(page: Page, selectors: List[str], value: str) -> bool:
    for sel in selectors:
        try:
            loc = page.locator(sel)
            loc.wait_for(state="visible", timeout=2000)
            loc.fill(value)
            return True
        except PWTimeout:
            continue
        except Exception:
            continue
    return False

def is_logged_in(page: Page) -> bool:
    """
    Heuristic: look for authenticated-only UI bits.
    """
    try:
        page.wait_for_selector("button:has-text('Open Options')", timeout=1500)
        return True
    except PWTimeout:
        pass
    try:
        page.wait_for_selector("text=Logout, Sign out, Profile, Account", timeout=1500)
        return True
    except PWTimeout:
        return False
