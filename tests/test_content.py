import pytest

from application import ROOT
from application.check import broken_links
from application.content import ContentError, load_content
from application.markdown import render
from application.redirects import Redirects


def write(tmp_path, name, text):
    file = tmp_path / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)


GOOD = "---\ntitle: T\ndescription: D\n---\nBody\n"


def test_all_content_loads_and_links_resolve():
    pages = load_content(ROOT / "content")
    assert broken_links(pages, Redirects.load(ROOT / "redirects")) == []


def test_every_content_url_is_200(app, client):
    for path in load_content(ROOT / "content"):
        assert client.get(path).status_code == 200, path


def test_url_comes_from_file_path(tmp_path):
    write(tmp_path, "index.md", GOOD)
    write(tmp_path, "a/index.md", GOOD)
    write(tmp_path, "a/b.md", GOOD)
    assert set(load_content(tmp_path)) == {"/", "/a", "/a/b"}


@pytest.mark.parametrize(
    "name,text",
    [
        ("Bad_Name.md", GOOD),
        ("x.md", "---\ntitle: T\ndescription: D\nextra: 1\n---\n"),
        ("x.md", "---\ntitle: T\n---\n"),
        ("x.md", "---\ntitle: T\ndescription: D\ntemplate: nope\n---\n"),
        ("x.md", "---\ntitle: T\ndescription: D\nstage: Backlog\n---\n"),
        (
            "x.md",
            "---\ntitle: T\ndescription: D\ntemplate: consideration\n"
            "github_discussion_number: abc\n---\n",
        ),
        (
            "x.md",
            "---\ntitle: T\ndescription: D\ntemplate: consideration\n"
            "legislation: {text: a, url: 'javascript:alert(1)'}\n---\n",
        ),
    ],
)
def test_bad_content_fails_at_load(tmp_path, name, text):
    write(tmp_path, "index.md", GOOD)
    write(tmp_path, name, text)
    with pytest.raises(ContentError):
        load_content(tmp_path)


def test_index_is_required(tmp_path):
    write(tmp_path, "x.md", GOOD)
    with pytest.raises(ContentError):
        load_content(tmp_path)


def test_duplicate_path_fails(tmp_path):
    write(tmp_path, "index.md", GOOD)
    write(tmp_path, "a.md", GOOD)
    write(tmp_path, "a/index.md", GOOD)
    with pytest.raises(ContentError):
        load_content(tmp_path)


def test_raw_html_is_escaped():
    html = str(render("<script>alert(1)</script>\n\n<b>x</b> and `<i>`"))
    assert "<script>" not in html
    assert "<b>" not in html
    assert "&lt;script&gt;" in html


def test_unsafe_links_are_dropped():
    html = str(render("[x](javascript:alert(1)) [y](//evil.example) [z](/ok)"))
    assert "javascript" not in html
    assert "evil.example" not in html
    assert 'href="/ok"' in html


@pytest.mark.parametrize(
    "url",
    [
        "javascript&#58;alert(1)",
        "javascript&#x3a;alert(1)",
        "javascript&colon;alert(1)",
        "java&Tab;script:alert(1)",
        "&#106;avascript:alert(1)",
        "&#1;javascript:alert(1)",
        "/\\evil.example",
        r"\\\\evil.example",  # Markdown unescapes this to \\evil.example
    ],
)
def test_encoded_unsafe_urls_are_dropped(url):
    html = str(render(f"[x]({url}) ![i]({url})"))
    assert "href" not in html
    assert "src" not in html


@pytest.mark.parametrize(
    "url",
    ["https://example.com/?a=1&amp;b=2", "mailto:a@example.com", "/ok#x", "page"],
)
def test_safe_urls_are_kept(url):
    assert "href=" in str(render(f"[x]({url})"))


def test_double_encoded_scheme_stays_inert():
    # kept, but the browser decodes it once to "javascript&#58;...", a relative path
    out = str(render("[x](javascript&amp;#58;alert(1))"))
    assert 'href="javascript&amp;#58;alert(1)"' in out


def test_markdown_gets_govuk_classes():
    html = str(render("# H\n\ntext [a](https://example.com)\n\n- one\n"))
    assert 'class="govuk-heading-xl"' in html
    assert 'class="govuk-body"' in html
    assert 'class="govuk-link"' in html
    assert "govuk-list--bullet" in html
