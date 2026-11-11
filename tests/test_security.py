import ast
import re

import pytest

from application import ROOT, security

APP_DIR = ROOT / "application"
SAMPLE = "article-4-directions"


def paths_from_notes():
    text = (ROOT / "notes" / "PATHS.md").read_text()
    paths = set()
    for line in text.splitlines():
        match = re.match(r"\|\s*`([^`]+)`", line)
        if match:
            for raw in match.group(1).split(", "):
                raw = raw.replace("[/<subpath>]", "")
                raw = re.sub(r"<consideration_slug>|<slug>", SAMPLE, raw)
                raw = re.sub(r"<[^>]+>", "x", raw).replace("…", f"/{SAMPLE}/x")
                if raw.startswith("/"):
                    paths.add(raw)
    return sorted(paths)


@pytest.mark.parametrize("path", paths_from_notes())
def test_every_old_path_is_200_redirect_404_or_410(client, path):
    assert client.get(path).status_code in (200, 301, 302, 404, 410), path


@pytest.mark.parametrize(
    "path",
    [
        "/auth/login",
        "/auth/authorize",
        "/auth/logout",
        "/admin/tags",
        "/admin/tags/add",
        "/consideration/add",
        "/nothing-here",
    ],
)
def test_login_only_paths_are_404(client, path):
    assert client.get(path).status_code == 404


@pytest.mark.parametrize("method", ["post", "put", "delete", "patch"])
@pytest.mark.parametrize(
    "path", ["/", "/community", "/consideration/add", "/auth/login"]
)
def test_write_methods_are_405(client, method, path):
    assert getattr(client, method)(path).status_code == 405


def test_head_and_options_allowed(client):
    assert client.head("/").status_code == 200
    assert client.options("/").status_code == 200


def test_headers_on_every_response(client):
    for path in [
        "/",
        "/community",
        "/nope",
        "/advisory-group",
        "/static/x",
        "/help/os-declaration-options",
    ]:
        response = client.get(path)
        for name, value in security.HEADERS.items():
            assert response.headers[name] == value, (path, name)
    assert client.post("/").headers["X-Content-Type-Options"] == "nosniff"


def test_no_cookies_set(client):
    assert "Set-Cookie" not in client.get("/").headers


def test_only_expected_routes(app):
    rules = {
        (r.rule, tuple(sorted(r.methods - {"HEAD", "OPTIONS"})))
        for r in app.url_map.iter_rules()
    }
    assert rules == {
        ("/", ("GET",)),
        ("/<path:path>", ("GET",)),
        ("/consideration/planning-considerations.csv", ("GET",)),
        ("/static/<path:filename>", ("GET",)),
    }


def test_no_secret_key_or_sessions(app):
    assert not app.config.get("SECRET_KEY")
    assert not app.config.get("DATABASE_URL")


FORBIDDEN = {
    "sqlalchemy",
    "requests",
    "urllib.request",
    "socket",
    "smtplib",
    "authlib",
    "http.client",
    "httpx",
    "psycopg2",
}


def test_app_imports_nothing_that_talks_to_the_network():
    for file in APP_DIR.rglob("*.py"):
        for node in ast.walk(ast.parse(file.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for name in names:
                assert not any(
                    name == f or name.startswith(f + ".") for f in FORBIDDEN
                ), (file, name)


def test_no_unsafe_markup_outside_markdown_module():
    for file in list(APP_DIR.rglob("*.py")) + list(
        (APP_DIR / "templates").rglob("*.html")
    ):
        if file.name == "markdown.py":
            continue
        text = file.read_text()
        assert "|safe" not in text.replace(" ", ""), file
        assert "Markup(" not in text, file


def test_templates_have_no_inline_script_or_style():
    for file in (APP_DIR / "templates").rglob("*.html"):
        text = file.read_text()
        assert "<script" not in text, file
        assert "<style" not in text, file
        assert " style=" not in text, file
