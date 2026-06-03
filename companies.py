KEYWORDS = [
    "data engineer",
    "analytics engineer",
    "data platform",
    "ai data",
    "data infrastructure",
    "platform engineer",
    "ml engineer",
    "ai engineer",
    "machine learning engineer",
]

# ── Verified working companies ─────────────────────────────────────────────────
COMPANIES = [
    # ── Greenhouse ────────────────────────────────────────────────────────────
    {"name": "Stripe",          "type": "greenhouse", "token": "stripe"},
    {"name": "Anthropic",       "type": "greenhouse", "token": "anthropic"},
    {"name": "Scale AI",        "type": "greenhouse", "token": "scaleai"},
    {"name": "Affirm",          "type": "greenhouse", "token": "affirm"},
    {"name": "Marqeta",         "type": "greenhouse", "token": "marqeta"},
    {"name": "Brex",            "type": "greenhouse", "token": "brex"},
    {"name": "Toast",           "type": "greenhouse", "token": "toast"},
    {"name": "Block / Square",  "type": "greenhouse", "token": "block"},
    {"name": "Garner",          "type": "greenhouse", "token": "garnerhealth"},
    {"name": "Perpay",          "type": "greenhouse", "token": "perpay"},
    {"name": "ComplyAdvantage", "type": "greenhouse", "token": "complyadvantage"},
    {"name": "Relativity",      "type": "greenhouse", "token": "relativity"},
    # ── Ashby ─────────────────────────────────────────────────────────────────
    {"name": "Vanta",           "type": "ashby", "token": "vanta"},
    {"name": "Drata",           "type": "ashby", "token": "drata"},
    {"name": "Cohere",          "type": "ashby", "token": "cohere"},
    # ── Lever ─────────────────────────────────────────────────────────────────
    {"name": "Palantir",        "type": "lever", "token": "palantir"},
    {"name": "Plaid",           "type": "lever", "token": "plaid"},
    # ── Custom HTML scrape ────────────────────────────────────────────────────
    {
        "name": "Citi",
        "type": "custom_citi",
        "url": "https://jobs.citi.com/search-jobs/data%20engineer/287/1",
    },
]

# ── Manual check list (Workday / anti-bot) ────────────────────────────────────
# These block programmatic access. Check manually once a week:
#   Capital One  → https://capitalone.wd1.myworkdayjobs.com/Capital_One
#   JPMorgan     → https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001
#   Goldman Sachs→ https://www.goldmansachs.com/careers/search
#   Visa         → https://jobs.visa.com
#   Bloomberg    → https://careers.bloomberg.com
#   Fidelity     → https://jobs.fidelity.com
#   Booz Allen   → https://careers.boozallen.com
#   Morgan Stanley → https://morganstanley.tal.net
#   Leidos       → https://careers.leidos.com
#   Innovaccer   → https://innovaccer.com/careers
