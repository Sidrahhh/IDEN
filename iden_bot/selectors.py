"""
Central place for selectors so they're easy to tweak if the UI changes.
Prefer accessible roles when possible, with text fallbacks.
"""

OPEN_OPTIONS_BTN       = "role=button[name='Open Options']"                # get_by_role("button", name="Open Options")
INVENTORY_TAB_ROLE     = "role=tab[name='Inventory']"
INVENTORY_TAB_TEXT     = "text=Inventory"

ACCESS_DETAILED_BTN_R  = "role=button[name='Access Detailed View']"
ACCESS_DETAILED_BTN_T  = "button:has-text('Access Detailed View')"

SHOW_FULL_TABLE_BTN_R  = "role=button[name='Show Full Product Table']"
SHOW_FULL_TABLE_BTN_T  = "button:has-text('Show Full Product Table')"

SUBMIT_SCRIPT_LINK_R   = "role=link[name='Submit Script']"
MENU_BTN               = "role=button[name='Menu']"

# Login form fallbacks
LOGIN_OPENERS = [
    "text=Log in",
    "text=Login",
    "role=button[name='Login']",
    "a:has-text('Login')",
    "a:has-text('Sign in')",
    "text=Sign in"
]

USERNAME_FIELDS = [
    "input[name='email']",
    "input[name='username']",
    "input[type='email']",
    "input[autocomplete='username']",
    "label:has-text('Email') >> .. >> input",
    "label:has-text('Username') >> .. >> input",
]

PASSWORD_FIELDS = [
    "input[name='password']",
    "input[type='password']",
    "input[autocomplete='current-password']",
    "label:has-text('Password') >> .. >> input",
]

SUBMIT_BTNS = [
    "button:has-text('Sign in')",
    "button:has-text('Log in')",
    "button[type='submit']",
    "input[type='submit']",
    "role=button[name='Sign in']",
    "role=button[name='Login']",
]

# Table
TABLE_SEL = "table"
THEAD_TH  = "thead tr th"
TBODY_TR  = "tbody tr"

# Pagination
NEXT_CANDIDATES = [
    "button:has-text('Next'):not([disabled])",
    "a:has-text('Next')",
    "[aria-label='Next']:not([disabled])",
    ".pagination >> text=Next"
]

# Submit page input
SUBMIT_INPUTS = [
    "input[name='repository']",
    "input[name='repo']",
    "input[placeholder*='GitHub']",
    "label:has-text('GitHub') >> .. >> input",
    "label:has-text('Repository') >> .. >> input",
]

SUBMIT_BTN_R = "role=button[name='Submit']"
SUBMIT_BTN_T = "button:has-text('Submit')"
