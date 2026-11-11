import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from tools import check_links as cl
from tools.check_links import Result, build_report, check, run, select, update

TODAY = date(2026, 6, 1)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self):
        path = self.path
        if path == "/ok":
            self.send_response(200)
        elif path == "/moved":
            self.send_response(301)
            self.send_header("Location", "/ok")
        elif path == "/temp":
            self.send_response(302)
            self.send_header("Location", "/ok")
        elif path == "/sign-in-redirect":
            self.send_response(302)
            self.send_header("Location", "/accounts/login?next=x")
        elif path == "/loop":
            self.send_response(302)
            self.send_header("Location", "/loop")
        elif path == "/gone":
            self.send_response(404)
        elif path == "/private":
            self.send_response(403)
        elif path == "/unauthorised":
            self.send_response(401)
        elif path == "/limited":
            self.send_response(429)
            self.send_header("Retry-After", "3")
        elif path == "/error":
            self.send_response(503)
        elif path == "/no-head":
            self.send_response(405 if self.command == "HEAD" else 200)
        else:
            self.send_response(404)
        self.send_header("Content-Length", "0")
        self.end_headers()

    do_GET = do_HEAD = respond


@pytest.fixture(scope="module")
def base():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()


@pytest.mark.parametrize(
    "path,kind",
    [
        ("/ok", "ok"),
        ("/no-head", "ok"),
        ("/temp", "ok"),
        ("/moved", "moved"),
        ("/gone", "gone"),
        ("/private", "not_public"),
        ("/unauthorised", "not_public"),
        ("/sign-in-redirect", "not_public"),
        ("/limited", "unclear"),
        ("/error", "unclear"),
        ("/loop", "unclear"),
    ],
)
def test_check(base, path, kind):
    assert check(base + path).kind == kind


def test_check_details(base):
    assert check(base + "/moved").detail == base + "/ok"
    assert check(base + "/limited").wait == 3


def test_connection_failure_is_unclear():
    assert check("http://127.0.0.1:1/").kind == "unclear"


def test_ok_resets_failures():
    row = {
        "url": "u",
        "failures": "2",
        "first_failed": "2026-01-01",
        "status": "failing",
    }
    row = update(row, Result("ok"), TODAY)
    assert (row["status"], row["failures"], row["first_failed"]) == ("ok", "0", "")


def test_not_public_is_immediate():
    assert (
        update(None, Result("not_public", "HTTP 403"), TODAY)["status"] == "not_public"
    )


def test_gone_needs_two_failures():
    row = update(None, Result("gone"), TODAY)
    assert row["status"] == "failing"
    assert update(row, Result("gone"), TODAY + timedelta(days=7))["status"] == "broken"


def test_unclear_needs_three_failures_over_two_weeks():
    row = None
    for week in range(3):
        row = update(row, Result("unclear"), TODAY + timedelta(days=week * 3))
    assert row["status"] == "failing"  # 3 failures, only 6 days
    row = update(row, Result("unclear"), TODAY + timedelta(days=15))
    assert row["status"] == "broken"


def row(url, status, days_ago):
    return {
        "url": url,
        "status": status,
        "last_checked": (TODAY - timedelta(days=days_ago)).isoformat(),
    }


def test_select_order_and_cap():
    urls = ["new1", "fresh", "stale-old", "stale-older", "retry", "new2"]
    rows = [
        row("fresh", "ok", 1),
        row("stale-old", "ok", 30),
        row("stale-older", "ok", 90),
        row("retry", "failing", 7),
    ]
    assert select(urls, rows, TODAY, 100) == [
        "new1",
        "new2",
        "retry",
        "stale-older",
        "stale-old",
    ]
    assert select(urls, rows, TODAY, 3) == ["new1", "new2", "retry"]


def test_failing_recently_checked_is_not_retried_early():
    assert select(["a"], [row("a", "failing", 2)], TODAY, 10) == []


def test_run_is_polite_per_domain():
    calls, sleeps = [], []

    def fake(url):
        calls.append(url)
        return Result("ok")

    state = run(
        ["https://a.example/1", "https://a.example/2", "https://b.example/1"],
        [],
        TODAY,
        check_fn=fake,
        sleep=sleeps.append,
        workers=1,
    )
    assert len(calls) == 3
    assert sleeps == [cl.INTERVAL]  # only between two requests to a.example
    assert state["https://a.example/1"]["status"] == "ok"


def test_run_honours_retry_after():
    sleeps = []
    run(
        ["https://a.example/1"],
        [],
        TODAY,
        check_fn=lambda u: Result("unclear", "HTTP 429", 3),
        sleep=sleeps.append,
    )
    assert sleeps == [3]


def test_report_groups_and_suggests():
    found = {
        "https://www.gov.uk/gone": ["content/a.md"],
        "https://x.example/moved": ["content/b.md"],
        "https://y.example/ok": ["content/c.md"],
    }
    state = {
        "https://www.gov.uk/gone": {
            **row("https://www.gov.uk/gone", "broken", 0),
            "detail": "HTTP 404",
        },
        "https://x.example/moved": {
            **row("https://x.example/moved", "moved", 0),
            "detail": "https://x.example/new",
        },
        "https://y.example/ok": {**row("https://y.example/ok", "ok", 0), "detail": ""},
    }
    text = build_report(
        found, state, new=["https://y.example/ok"], new_domains={"y.example"}
    )
    assert "## Broken (1)" in text
    assert "webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/gone" in text
    assert "replace with https://x.example/new" in text
    assert "used in `a.md`" in text
    assert "## New domains" in text
    assert "https://y.example/ok" in text


def test_report_empty_when_nothing_wrong():
    found = {"https://y.example/ok": ["content/c.md"]}
    state = {
        "https://y.example/ok": {**row("https://y.example/ok", "ok", 0), "detail": ""}
    }
    assert build_report(found, state) == ""
