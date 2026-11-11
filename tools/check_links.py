"""Check outbound links. Networked, so it is run by CI and never by the app.

    python -m tools.check_links --limit 100 --report links/report.md
    python -m tools.check_links --new-against base-links.csv --report report.md

Reports problems, never fails the build.
"""

import argparse
import http.client
import time
import urllib.error
import urllib.request
from collections import defaultdict, namedtuple
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from urllib.parse import urljoin, urlparse

from application import ROOT
from application.content import load_content
from application.links import (
    allowed_domains,
    domain,
    extract,
    new_urls,
    read_csv,
    write_csv,
)

USER_AGENT = (
    "planning-data-design-link-checker "
    "(+https://github.com/digital-land/planning-data-design)"
)
TIMEOUT = 10
MAX_REDIRECTS = 3
INTERVAL = 1.0  # seconds between requests to one domain
MAX_WAIT = 30  # longest Retry-After we honour
STALE_DAYS = 28
RETRY_DAYS = 6
GONE_FAILURES = 2
FAILURES = 3
FAILURE_DAYS = 14

SIGN_IN_HOSTS = {
    "accounts.google.com",
    "login.microsoftonline.com",
    "login.live.com",
    "login.microsoft.com",
}
SIGN_IN_SEGMENTS = {"login", "signin", "sign-in", "servicelogin"}
PROBLEMS = ("broken", "not_public", "moved", "failing")
STATUS_FIELDS = [
    "url",
    "last_checked",
    "status",
    "last_ok",
    "failures",
    "first_failed",
    "detail",
]
ARCHIVE = "https://webarchive.nationalarchives.gov.uk/ukgwa/*/"

Result = namedtuple("Result", "kind detail wait", defaults=("", 0))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def fetch(url, method):
    """One request, no cookies, no credentials. Returns (status or None, headers)."""
    request = urllib.request.Request(
        url, method=method, headers={"User-Agent": USER_AGENT}
    )
    try:
        with OPENER.open(request, timeout=TIMEOUT) as response:
            return response.status, response.headers
    except urllib.error.HTTPError as e:
        return e.code, e.headers
    except (urllib.error.URLError, OSError, ValueError, http.client.HTTPException) as e:
        return None, {"error": str(e)}


def request(url, fetch_fn):
    """HEAD first, then GET, as some servers handle HEAD badly."""
    status, headers = fetch_fn(url, "HEAD")
    if status is None or status >= 400:
        status, headers = fetch_fn(url, "GET")
    return status, headers


def is_sign_in(url):
    parts = urlparse(url)
    segments = {s.lower() for s in parts.path.split("/") if s}
    return (parts.hostname or "").lower() in SIGN_IN_HOSTS or bool(
        segments & SIGN_IN_SEGMENTS
    )


def same(a, b):
    return a.rstrip("/") == b.rstrip("/")


def check(url, fetch_fn=fetch):
    current, permanent = url, False
    for _ in range(MAX_REDIRECTS + 1):
        status, headers = request(current, fetch_fn)
        if status in (301, 302, 303, 307, 308):
            location = headers.get("Location")
            if not location:
                return Result("unclear", "redirect without a location")
            permanent = permanent or status in (301, 308)
            current = urljoin(current, location)
            if is_sign_in(current):
                return Result("not_public", f"redirects to sign in: {current}")
            continue
        if status is not None and 200 <= status < 300:
            if permanent and not same(current, url):
                return Result("moved", current)
            return Result("ok")
        if status in (401, 403):
            return Result("not_public", f"HTTP {status}")
        if status in (404, 410):
            return Result("gone", f"HTTP {status}")
        if status == 429:
            try:
                wait = min(int(headers.get("Retry-After", "")), MAX_WAIT)
            except ValueError:
                wait = INTERVAL * 5
            return Result("unclear", "HTTP 429", wait)
        return Result(
            "unclear", f"HTTP {status}" if status else headers.get("error", "")
        )
    return Result("unclear", "too many redirects")


def update(row, result, today):
    """New state row from the old one and a result."""
    row = dict(row or {"url": ""})
    failures = int(row.get("failures") or 0)
    row["last_checked"] = today.isoformat()
    row["detail"] = result.detail
    if result.kind in ("ok", "moved"):
        row.update(
            status=result.kind, last_ok=today.isoformat(), failures="0", first_failed=""
        )
        return row
    failures += 1
    first_failed = row.get("first_failed") or today.isoformat()
    row.update(failures=str(failures), first_failed=first_failed)
    if result.kind == "not_public":
        row["status"] = "not_public"
        return row
    days = (today - date.fromisoformat(first_failed)).days
    broken = (result.kind == "gone" and failures >= GONE_FAILURES) or (
        failures >= FAILURES and days >= FAILURE_DAYS
    )
    row["status"] = "broken" if broken else "failing"
    return row


def age(row, today):
    return (today - date.fromisoformat(row["last_checked"])).days


def select(urls, rows, today, limit):
    """Never checked first, then failing ones due a retry, then the stalest."""
    state = {r["url"]: r for r in rows if r.get("last_checked")}
    never = [u for u in urls if u not in state]
    retry = sorted(
        (
            u
            for u in urls
            if u in state
            and state[u]["status"] in ("failing", "not_public")
            and age(state[u], today) >= RETRY_DAYS
        ),
        key=lambda u: state[u]["last_checked"],
    )
    stale = sorted(
        (
            u
            for u in urls
            if u in state and u not in retry and age(state[u], today) >= STALE_DAYS
        ),
        key=lambda u: state[u]["last_checked"],
    )
    return (never + retry + stale)[:limit]


def run(urls, rows, today, check_fn=check, sleep=time.sleep, workers=4):
    """Check urls, one at a time per domain. Returns the updated state rows."""
    by_domain = defaultdict(list)
    for url in urls:
        by_domain[domain(url)].append(url)
    state = {r["url"]: r for r in rows}

    def one_domain(items):
        out = {}
        for i, url in enumerate(items):
            if i:
                sleep(INTERVAL)
            try:
                result = check_fn(url)
            except Exception as e:  # one bad link must not stop the run
                result = Result("unclear", f"{type(e).__name__}: {e}")
            out[url] = update(state.get(url, {"url": url}), result, today)
            if result.wait:
                sleep(result.wait)
        return out

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done in pool.map(one_domain, by_domain.values()):
            state.update(done)
    return state


def build_report(found, state, include=None, new=(), new_domains=()):
    """Markdown report, empty when there is nothing to say."""
    rows = [
        r
        for r in state.values()
        if r["url"] in found
        and r["status"] in PROBLEMS
        and (include is None or r["url"] in include)
    ]
    if not rows and not new and not new_domains:
        return ""
    lines = ["# Outbound link report", ""]
    if new:
        lines += [f"## New links ({len(new)})", ""] + [f"- {u}" for u in new] + [""]
    if new_domains:
        lines += ["## New domains, add to `links/domain.csv` if wanted", ""]
        lines += [f"- {d}" for d in sorted(new_domains)] + [""]
    titles = {
        "broken": "Broken",
        "not_public": "Not public (needs a sign in)",
        "moved": "Moved (permanent redirect)",
        "failing": "Failing, will be retried",
    }
    for status in PROBLEMS:
        group = sorted(
            (r for r in rows if r["status"] == status),
            key=lambda r: (domain(r["url"]), r["url"]),
        )
        if not group:
            continue
        lines += [f"## {titles[status]} ({len(group)})", ""]
        if status == "not_public":
            lines += [
                "A 403 can also mean the site refuses automated checks. "
                "Open those links in a private browser window to confirm.",
                "",
            ]
        current = None
        for row in group:
            host = domain(row["url"])
            if host != current:
                current = host
                lines += [f"### {host}", ""]
            lines.append(f"- {row['url']}")
            if row["detail"]:
                lines.append(f"  - {row['detail']}")
            if status == "moved":
                lines.append(f"  - replace with {row['detail']}")
            if status == "broken" and host.endswith(".gov.uk"):
                lines.append(f"  - web archive: {ARCHIVE}{row['url']}")
            for source in found[row["url"]]:
                lines.append(f"  - used in `{source.split('content/')[-1]}`")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--status", default=str(ROOT / "links" / "status.csv"))
    parser.add_argument("--report")
    parser.add_argument("--new-against", help="links.csv from the base branch")
    args = parser.parse_args(argv)

    today = date.today()
    found = extract(load_content(ROOT / "content"))
    rows = read_csv(args.status)
    include = new = new_domains = None
    if args.new_against:
        base = read_csv(args.new_against)
        new = new_urls(found, base)
        known = {r["domain"] for r in base} | allowed_domains(
            read_csv(ROOT / "links" / "domain.csv")
        )
        new_domains = {domain(u) for u in new} - known
        urls = include = new
    else:
        urls = select(list(found), rows, today, args.limit)
    state = run(urls, rows, today)
    if not args.new_against:
        kept = [state[u] for u in sorted(state) if u in found]
        write_csv(args.status, STATUS_FIELDS, kept)
    report = build_report(found, state, include, new or (), new_domains or ())
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report)
    print(f"checked {len(urls)} links")
    print(report or "no problems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
