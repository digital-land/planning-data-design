"""
Security regression tests.

Guards against previously found vulnerabilities coming back:

- user supplied values (urls, consideration names) rendered unescaped in
  flash messages, allowing cross site scripting
- the docker image defaulting to development settings, i.e. the flask dev
  server with the interactive debugger and csrf protection turned off

The docker tests read the Dockerfile and entrypoint rather than building the
image, so they check what the image is configured to run by default.
"""

import re
from pathlib import Path

import pytest
from markupsafe import Markup
from wtforms import ValidationError

from application.extensions import db
from application.factory import create_app
from application.forms import DeleteForm
from application.models import Consideration, Stage

PROJECT_ROOT = Path(__file__).resolve().parents[2]
XSS_PAYLOAD = "<img src=x onerror=alert(document.domain)>"
ESCAPED_XSS_PAYLOAD = "&lt;img src=x onerror=alert(document.domain)&gt;"


def _dockerfile_env(name):
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()
    match = re.search(rf"^ENV {name}=(\S+)", dockerfile, re.MULTILINE)
    return match.group(1) if match else None


def test_unknown_consideration_slug_is_escaped_in_flash_message(client):
    response = client.get(
        "/consideration/%3Cimg%20src=x%20onerror=alert(document.domain)%3E",
        follow_redirects=True,
    )

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert XSS_PAYLOAD not in page
    assert ESCAPED_XSS_PAYLOAD in page
    # the rest of the message is still rendered as html
    assert "<span class='govuk-!-font-weight-bold'>" in page


def test_duplicate_consideration_message_escapes_name(app, monkeypatch):
    from application.blueprints.planning_consideration import forms

    flashed = []
    monkeypatch.setattr(forms, "flash", flashed.append)

    with app.app_context():
        existing = Consideration(
            name=XSS_PAYLOAD, slug="xss-name-test", stage=Stage.BACKLOG
        )
        db.session.add(existing)
        db.session.commit()

        class NameField:
            data = "xss name test"

        try:
            with app.test_request_context("/consideration/add"):
                with pytest.raises(ValidationError):
                    forms.unique_name_validator(None, NameField())
        finally:
            db.session.delete(existing)
            db.session.commit()

    assert len(flashed) == 1
    assert isinstance(flashed[0], Markup)
    assert XSS_PAYLOAD not in flashed[0]
    assert ESCAPED_XSS_PAYLOAD in flashed[0]


def test_image_does_not_set_flask_debug():
    assert _dockerfile_env("FLASK_DEBUG") is None


def test_image_runs_gunicorn_not_the_flask_dev_server():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text()
    entrypoint = (PROJECT_ROOT / "docker-entrypoint.sh").read_text()

    assert re.search(r'^CMD \["gunicorn"', dockerfile, re.MULTILINE)
    assert "flask run" not in entrypoint
    assert "--debug" not in entrypoint


def test_image_default_config_is_not_debug_and_enforces_csrf():
    config_name = _dockerfile_env("FLASK_CONFIG")
    assert config_name == "application.config.Config"

    app = create_app(config_name)
    assert app.debug is False
    assert app.testing is False

    # a form posted without a csrf token must be rejected
    with app.test_request_context(method="POST", data={"confirm": "True"}):
        form = DeleteForm()
        assert form.validate() is False
        assert "csrf_token" in form.errors
