from datetime import date

from application import ROOT
from application.content import load_content
from application.links import (
    allowed_domains,
    domain,
    extract,
    new_urls,
    problems,
    read_csv,
    report,
    stale,
    sync,
)

GOOD = "---\ntitle: T\ndescription: D\n{}---\n{}\n"


def pages_from(tmp_path, front="", body=""):
    (tmp_path / "index.md").write_text(GOOD.format(front, body))
    return load_content(tmp_path)


def test_extracts_body_and_front_matter_links(tmp_path):
    pages = pages_from(
        tmp_path,
        "template: consideration\nstage: Backlog\n"
        "legislation: {text: a, url: 'https://a.example/x#frag'}\n"
        "useful_links:\n- {text: b, url: 'https://b.example/'}\n",
        "[c](https://c.example/?a=1&b=2) [d](/relative) <https://e.example>",
    )
    assert list(extract(pages)) == [
        "https://a.example/x",
        "https://b.example/",
        "https://c.example/?a=1&b=2",
        "https://e.example",
    ]


def test_extracts_links_a_browser_would_follow(tmp_path):
    pages = pages_from(
        tmp_path,
        body="[a](HTTPS://a.example/) ![b](https://b.example/x.png) "
        "[c](ht&Tab;tps://c.example/) [d](https&#58;//d.example/) "
        'not a link: href="https://e.example/"',
    )
    assert {domain(url) for url in extract(pages)} == {
        "a.example",
        "b.example",
        "c.example",
        "d.example",
    }


def test_unlisted_domain_and_self_links_are_problems():
    found = {
        "https://ok.example/": ["a.md"],
        "https://new.example/": ["b.md"],
        "https://design.planning.data.gov.uk/x": ["c.md"],
    }
    out = problems(found, {"ok.example"})
    assert len(out) == 2
    assert "new.example" in out[0]
    assert "relative path" in out[1]


def test_sync_keeps_first_seen_and_detects_new():
    found = {"https://a.example/": [], "https://b.example/": []}
    existing = [
        {"url": "https://a.example/", "domain": "a.example", "first_seen": "2020-01-01"}
    ]
    assert new_urls(found, existing) == ["https://b.example/"]
    rows = sync(found, existing, today=date(2026, 1, 2))
    assert [r["first_seen"] for r in rows] == ["2020-01-01", "2026-01-02"]
    assert sync({}, existing) == []


def test_stale_detection(tmp_path):
    found = {"https://a.example/": ["content/x.md"]}
    (tmp_path / "domain.csv").write_text("domain,note\na.example,\n")
    (tmp_path / "links.csv").write_text("url,domain,first_seen\n")
    assert len(stale(found, tmp_path)) == 2


def test_committed_link_files_match_content():
    found = extract(load_content(ROOT / "content"))
    links = ROOT / "links"
    allowed = allowed_domains(read_csv(links / "domain.csv"))
    assert problems(found, allowed) == []
    assert stale(found, links) == []


def test_sharepoint_and_mural_are_not_listed():
    listed = allowed_domains(read_csv(ROOT / "links" / "domain.csv"))
    assert not {d for d in listed if "sharepoint" in d or "mural" in d}


def test_report_lists_each_domain():
    found = {
        "https://a.example/1": ["content/x.md"],
        "https://a.example/2": ["content/y.md"],
    }
    text = report(found, set())
    assert "| a.example | 2 | **no** |" in text
    assert domain("HTTPS://A.Example/x") == "a.example"


def test_url_with_space_is_a_problem():
    assert "space" in problems({"https://a.example/a b": ["x.md"]}, {"a.example"})[0]
