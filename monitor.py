#!/usr/bin/env python3
"""
Job Alert Monitor — checks 19 company career APIs every hour via GitHub Actions.
Sends email when new Data Engineer / AI Engineer roles are posted.
State tracked in seen_jobs.json (committed back to repo each run).
"""

import json
import os
import re
import smtplib
import requests
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from companies import COMPANIES, KEYWORDS

STATE_FILE = Path(__file__).parent / "seen_jobs.json"
TIMEOUT = 15
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


@dataclass
class Job:
    id: str
    title: str
    company: str
    location: str
    url: str


# ── Keyword filter ─────────────────────────────────────────────────────────────

def matches(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in KEYWORDS)


# ── Fetchers ───────────────────────────────────────────────────────────────────

def fetch_greenhouse(company: dict) -> list[Job]:
    token, name = company["token"], company["name"]
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    try:
        data = requests.get(url, headers=HEADERS, timeout=TIMEOUT).json()
        return [
            Job(str(j["id"]), j["title"], name,
                j.get("location", {}).get("name", ""),
                j.get("absolute_url", ""))
            for j in data.get("jobs", []) if matches(j.get("title", ""))
        ]
    except Exception as e:
        print(f"  [{name}] greenhouse error: {e}")
        return []


def fetch_ashby(company: dict) -> list[Job]:
    token, name = company["token"], company["name"]
    url = f"https://api.ashbyhq.com/posting-api/job-board/{token}"
    try:
        data = requests.get(url, headers=HEADERS, timeout=TIMEOUT).json()
        return [
            Job(j["id"], j["title"], name,
                j.get("location", "") or j.get("locationName", ""),
                j.get("jobUrl", ""))
            for j in data.get("jobs", [])
            if matches(j.get("title", "")) and j.get("isListed", True)
        ]
    except Exception as e:
        print(f"  [{name}] ashby error: {e}")
        return []


def fetch_lever(company: dict) -> list[Job]:
    token, name = company["token"], company["name"]
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    try:
        data = requests.get(url, headers=HEADERS, timeout=TIMEOUT).json()
        return [
            Job(j["id"], j["text"], name,
                j.get("categories", {}).get("location", ""),
                j.get("hostedUrl", ""))
            for j in data if matches(j.get("text", ""))
        ]
    except Exception as e:
        print(f"  [{name}] lever error: {e}")
        return []


def fetch_custom_citi(company: dict) -> list[Job]:
    """Scrape Citi jobs page, deduplicate by href."""
    name, url = company["name"], company["url"]
    try:
        from bs4 import BeautifulSoup
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        seen_hrefs: set[str] = set()
        jobs: list[Job] = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/job/" not in href:
                continue
            if href in seen_hrefs:
                continue
            title = a.get_text(strip=True)
            if not title or not matches(title):
                continue
            seen_hrefs.add(href)
            full_url = href if href.startswith("http") else f"https://jobs.citi.com{href}"
            job_id = href.split("/")[-1] or href
            jobs.append(Job(job_id, title[:120], name, "", full_url))
        return jobs
    except Exception as e:
        print(f"  [{name}] custom error: {e}")
        return []


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "ashby": fetch_ashby,
    "lever": fetch_lever,
    "custom_citi": fetch_custom_citi,
}


# ── State ──────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ── Email ──────────────────────────────────────────────────────────────────────

def send_email(new_jobs: list[Job]) -> None:
    sender   = os.environ.get("ALERT_EMAIL_FROM")
    password = os.environ.get("ALERT_EMAIL_PASSWORD")
    recipient = os.environ.get("ALERT_EMAIL_TO")

    if not all([sender, password, recipient]):
        print("\n── No email credentials. New jobs found ──")
        for j in new_jobs:
            print(f"  [{j.company}] {j.title}" + (f" | {j.location}" if j.location else ""))
            print(f"  {j.url}")
        return

    lines = [f"Found {len(new_jobs)} new role(s) matching your profile:\n"]
    for j in new_jobs:
        lines += [f"🏢 {j.company}", f"   📌 {j.title}"]
        if j.location:
            lines.append(f"   📍 {j.location}")
        lines += [f"   🔗 {j.url}", ""]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚨 {len(new_jobs)} new job(s) — {', '.join(sorted({j.company for j in new_jobs}))}"
    msg["From"]    = sender
    msg["To"]      = recipient
    msg.attach(MIMEText("\n".join(lines), "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(sender, password)
            s.sendmail(sender, recipient, msg.as_string())
        print(f"Email sent — {len(new_jobs)} new jobs across "
              f"{len({j.company for j in new_jobs})} companies.")
    except Exception as e:
        print(f"Email failed: {e}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    state     = load_state()
    new_jobs: list[Job] = []

    for company in COMPANIES:
        name    = company["name"]
        fetcher = FETCHERS.get(company["type"])
        if not fetcher:
            print(f"  [{name}] unknown type: {company['type']}")
            continue

        jobs  = fetcher(company)
        seen  = set(state.get(name, []))
        fresh = [j for j in jobs if j.id not in seen]

        if fresh:
            print(f"  [{name}] ✓ {len(fresh)} NEW  (total matched: {len(jobs)})")
            new_jobs.extend(fresh)
        else:
            print(f"  [{name}] — {len(jobs)} matched, none new")

        if jobs:
            state[name] = sorted(seen | {j.id for j in jobs})

    save_state(state)

    if new_jobs:
        send_email(new_jobs)
    else:
        print("\nNo new jobs this run.")


if __name__ == "__main__":
    main()
