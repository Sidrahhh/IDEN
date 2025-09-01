import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import (
    sync_playwright, TimeoutError as PWTimeout, Page
)
from .utils import (
    log, sleep, get_env, try_fill, is_logged_in,
    DEFAULT_STORAGE, DEFAULT_TIMEOUT_MS, NAV_TIMEOUT_MS
)
from . import selectors as S

# ----------------------- Login & session -----------------------

def login_if_needed(page: Page, username: str, password: str) -> None:
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
    if is_logged_in(page):
        log("Session looks active; skipping login.")
        return

    log("No active session detected. Attempting login…")
    # If there is a login link/button, try clicking it
    for c in S.LOGIN_OPENERS:
        try:
            loc = page.locator(c)
            if loc.count() > 0:
                loc.first.click()
                break
        except Exception:
            continue

    ok_user = try_fill(page, S.USERNAME_FIELDS, username)
    ok_pass = try_fill(page, S.PASSWORD_FIELDS, password)
    if not ok_user or not ok_pass:
        raise RuntimeError("Could not locate login fields. Update selectors.")

    clicked = False
    for c in S.SUBMIT_BTNS:
        try:
            loc = page.locator(c)
            loc.first.wait_for(state="visible", timeout=2000)
            loc.first.click()
            clicked = True
            break
        except PWTimeout:
            continue
        except Exception:
            continue
    if not clicked:
        raise RuntimeError("Could not find a login submit button.")

    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
    if not is_logged_in(page):
        raise RuntimeError("Login failed (not authenticated after submit).")
    log("Login successful.")

# ----------------------- Hidden path nav -----------------------

def open_hidden_product_table(page: Page) -> None:
    log("Opening hidden product table path…")

    page.get_by_role("button", name="Open Options").wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
    page.get_by_role("button", name="Open Options").click()
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

    # Inventory tab
    try:
        page.get_by_role("tab", name="Inventory").wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        page.get_by_role("tab", name="Inventory").click()
    except PWTimeout:
        page.locator(S.INVENTORY_TAB_TEXT).first.click()
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

    # Access Detailed View
    try:
        page.get_by_role("button", name="Access Detailed View").wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        page.get_by_role("button", name="Access Detailed View").click()
    except PWTimeout:
        page.locator(S.ACCESS_DETAILED_BTN_T).first.click()
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

    # Show Full Product Table
    try:
        page.get_by_role("button", name="Show Full Product Table").wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)
        page.get_by_role("button", name="Show Full Product Table").click()
    except PWTimeout:
        page.locator(S.SHOW_FULL_TABLE_BTN_T).first.click()
    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

    log("Product table should now be visible.")

# ----------------------- Harvest helpers -----------------------

def _extract_table_once(page: Page) -> Tuple[List[str], List[Dict[str, Any]]]:
    table = page.locator(S.TABLE_SEL).first
    table.wait_for(state="visible", timeout=DEFAULT_TIMEOUT_MS)

    headers: List[str] = []
    ths = table.locator(S.THEAD_TH)
    if ths.count() == 0:
        ths = table.locator("tr").first.locator("th")
    for i in range(ths.count()):
        txt = ths.nth(i).inner_text().strip()
        headers.append(txt if txt else f"col_{i+1}")

    rows: List[Dict[str, Any]] = []
    body_rows = table.locator(S.TBODY_TR)
    for r in range(body_rows.count()):
        row = body_rows.nth(r)
        cells = row.locator("td")
        rec: Dict[str, Any] = {}
        for c in range(cells.count()):
            key = headers[c] if c < len(headers) else f"col_{c+1}"
            rec[key] = cells.nth(c).inner_text().strip()
        try:
            row_id = row.get_attribute("data-id")
            if row_id:
                rec["_row_id"] = row_id
        except Exception:
            pass
        rows.append(rec)

    return headers, rows

def _try_click_next(page: Page) -> bool:
    for sel in S.NEXT_CANDIDATES:
        try:
            btn = page.locator(sel)
            if btn.count() > 0:
                # ignore disabled buttons
                try:
                    if btn.first.get_attribute("disabled") is not None:
                        continue
                except Exception:
                    pass
                btn.first.click()
                page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
                sleep(0.3)
                return True
        except Exception:
            continue
    return False

def _infinite_scroll_collect(page: Page, max_idle_cycles: int = 3) -> None:
    last = -1
    idle = 0
    table = page.locator(S.TABLE_SEL).first
    tbody = table.locator("tbody")
    while idle < max_idle_cycles:
        curr = tbody.locator("tr").count()
        idle = idle + 1 if curr == last else 0
        last = curr
        try:
            page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        except Exception:
            pass
        sleep(0.4)

def harvest_full_table(page: Page) -> List[Dict[str, Any]]:
    log("Harvesting table…")
    try:
        _infinite_scroll_collect(page)
    except Exception:
        pass

    all_records: List[Dict[str, Any]] = []
    seen = set()
    page_no = 1

    while True:
        headers, rows = _extract_table_once(page)
        for rec in rows:
            key = rec.get("_row_id") or tuple(rec.get(h, "") for h in headers)
            if key not in seen:
                seen.add(key)
                all_records.append(rec)
        log(f"Collected {len(rows)} rows from page {page_no} (total {len(all_records)}).")

        if not _try_click_next(page):
            break
        page_no += 1

    log(f"Done. Total rows collected: {len(all_records)}")
    return all_records

# ----------------------- Submit page -----------------------

def submit_repo_url(page: Page, repo_url: str) -> None:
    log("Navigating to 'Submit Script' page…")
    try:
        page.locator(S.SUBMIT_SCRIPT_LINK_R).first.click(timeout=DEFAULT_TIMEOUT_MS)
    except Exception:
        # try menu then link
        try:
            page.locator(S.MENU_BTN).first.click(timeout=2000)
            page.locator(S.SUBMIT_SCRIPT_LINK_R).first.click(timeout=DEFAULT_TIMEOUT_MS)
        except Exception as e:
            raise RuntimeError("Could not open 'Submit Script' page. Update navigation selectors.") from e

    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

    filled = False
    for sel in S.SUBMIT_INPUTS:
        try:
            field = page.locator(sel)
            field.first.wait_for(state="visible", timeout=2000)
            field.first.fill(repo_url)
            filled = True
            break
        except Exception:
            continue
    if not filled:
        raise RuntimeError("Could not find repository URL field on 'Submit Script' page.")

    try:
        page.locator(S.SUBMIT_BTN_R).first.click(timeout=DEFAULT_TIMEOUT_MS)
    except Exception:
        page.locator(S.SUBMIT_BTN_T).first.click()

    page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)
    log("Submission attempted (check UI confirmation).")

# ----------------------- Runner -----------------------

def run(base_url: str,
        storage_state_path: Path = DEFAULT_STORAGE,
        username: Optional[str] = None,
        password: Optional[str] = None,
        output_json: Path = Path("products.json"),
        headless: bool = True,
        submit_url: Optional[str] = None,
        default_timeout_ms: int = DEFAULT_TIMEOUT_MS) -> None:

    username = username or get_env("IDEN_USERNAME")
    password = password or get_env("IDEN_PASSWORD")
    if not username or not password:
        raise SystemExit("Missing credentials. Provide --username/--password or set IDEN_USERNAME/IDEN_PASSWORD.")

    storage_state_path.parent.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        ctx_kwargs = {}
        if storage_state_path.exists():
            log(f"Using existing session state: {storage_state_path}")
            ctx_kwargs["storage_state"] = str(storage_state_path)

        context = browser.new_context(**ctx_kwargs)
        page = context.new_page()
        page.set_default_timeout(default_timeout_ms)

        log(f"Opening {base_url} …")
        page.goto(base_url, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle", timeout=NAV_TIMEOUT_MS)

        login_if_needed(page, username, password)
        context.storage_state(path=str(storage_state_path))

        open_hidden_product_table(page)
        data = harvest_full_table(page)

        output_json.parent.mkdir(parents=True, exist_ok=True)
        with output_json.open("w", encoding="utf-8") as f:
            json.dump({"count": len(data), "products": data}, f, indent=2, ensure_ascii=False)
        log(f"Wrote JSON: {output_json}")

        if submit_url:
            submit_repo_url(page, submit_url)
            log(f"Submitted repo URL: {submit_url}")

        # persist session again
        context.storage_state(path=str(storage_state_path))
        context.close()
        browser.close()
        log("Done.")
