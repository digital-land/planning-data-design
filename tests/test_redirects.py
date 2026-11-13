import pytest

from application import ROOT
from application.content import load_content
from application.redirects import RedirectError, Redirects

PAGES = load_content(ROOT / "content")


def load(tmp_path, **files):
    for name, text in files.items():
        (tmp_path / f"{name}.csv").write_text(text)
    return Redirects.load(tmp_path)


def test_every_redirect_resolves_in_one_hop(client):
    redirects = Redirects.load(ROOT / "redirects")
    for source, (target, status) in redirects.pages.items():
        response = client.get(source)
        assert response.status_code == status, source
        if status != 410:
            assert response.headers["Location"] == target
            assert client.get(target).status_code == 200, source


def test_prefix_keeps_query_string(client):
    response = client.get("/planning-consideration/article-4-directions?a=b")
    assert response.status_code == 301
    assert response.headers["Location"] == "/consideration/article-4-directions?a=b"


@pytest.mark.parametrize(
    "rest",
    [
        "//evil.example",
        "/\\evil.example",
        "/%2F%2Fevil.example",
        "/%5Cevil.example",
        "/../x",
        "/%2e%2e/x",
        "/./x",
    ],
)
def test_prefix_remainder_cannot_change_destination(client, rest):
    assert client.get(f"/planning-consideration{rest}").status_code == 404


@pytest.mark.parametrize("target", ["/", "/new/"])
def test_prefix_to_root_stays_on_site(tmp_path, target):
    r = load(tmp_path, a=f"from_prefix,to_prefix,status\n/old,{target},301\n")
    base = target.rstrip("/")
    assert r.resolve("/old", "", {}) == (base or "/", 301)
    assert r.resolve("/old/ok", "a=b", {}) == (f"{base}/ok?a=b", 301)
    assert r.resolve("/old//evil.example", "", {}) is None
    assert r.resolve("/old/\\evil.example", "", {}) is None


def test_exact_match_keeps_no_query_string(client):
    response = client.get("/advisory-group?a=b")
    assert response.headers["Location"] == "/project/planning-applications"


def test_subpages_redirect_to_consideration(client):
    for sub in ["edit", "stage-research/", "research/risks/edit-answer/0", "note"]:
        response = client.get(f"/consideration/article-4-directions/{sub}")
        assert response.status_code == 301, sub
        assert response.headers["Location"] == "/consideration/article-4-directions"


def test_subpages_of_unknown_consideration_are_404(client):
    assert client.get("/consideration/nope/edit").status_code == 404


@pytest.mark.parametrize(
    "target", ["https://evil.example/", "//evil.example", "evil", "/\\evil.example"]
)
def test_open_redirects_rejected(tmp_path, target):
    with pytest.raises(RedirectError):
        load(tmp_path, a=f"from,to,status\n/x,{target},301\n")


def test_duplicate_from_rejected(tmp_path):
    with pytest.raises(RedirectError):
        load(tmp_path, a="from,to,status\n/x,/,301\n/x,/community,301\n")


def test_chain_rejected(tmp_path):
    r = load(tmp_path, a="from,to,status\n/x,/y,301\n/y,/community,301\n")
    with pytest.raises(RedirectError):
        r.validate(PAGES)


def test_redirect_to_missing_page_rejected(tmp_path):
    r = load(tmp_path, a="from,to,status\n/x,/missing,301\n")
    with pytest.raises(RedirectError):
        r.validate(PAGES)


def test_redirect_from_content_page_rejected(tmp_path):
    r = load(tmp_path, a="from,to,status\n/community,/,301\n")
    with pytest.raises(RedirectError):
        r.validate(PAGES)


def test_bad_status_and_header_rejected(tmp_path):
    with pytest.raises(RedirectError):
        load(tmp_path, a="from,to,status\n/x,/,200\n")
    with pytest.raises(RedirectError):
        load(tmp_path, b="a,b\n1,2\n")
