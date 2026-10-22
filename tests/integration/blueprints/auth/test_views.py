"""
Integration tests for the GitHub sign in views in application/blueprints/auth/views.py.

Each view is called through the test client with its real dependencies: the
Authlib client registered in factory.py, the Flask session and the app config.
Only GitHub is faked, with responses, so these tests check what Authlib does
for us and catch an upgrade that changes it.

The state Authlib sends to GitHub is read from the redirect and sent back, as a
browser would, rather than from Authlib's session keys, which are internal.

TestConfig turns authentication off, which skips GitHub entirely, so these
tests use their own config with it turned on.
"""

import base64
from urllib.parse import parse_qs, urlsplit

import pytest
import responses
from authlib.integrations.base_client import MismatchingStateError

from application.config import TestConfig
from application.extensions import oauth
from application.factory import create_app

CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
REVOKE_URL = f"https://api.github.com/applications/{CLIENT_ID}/grant"

GITHUB_USER = {"login": "test-user", "email": "test-user@example.com"}


class AuthenticationOnConfig(TestConfig):
    AUTHENTICATION_ON = True
    GITHUB_CLIENT_ID = CLIENT_ID
    GITHUB_CLIENT_SECRET = CLIENT_SECRET


def membership_url(login):
    return f"https://api.github.com/orgs/digital-land/members/{login}"


@pytest.fixture(scope="module")
def auth_app():
    return create_app(AuthenticationOnConfig)


@pytest.fixture
def client(auth_app, monkeypatch):
    # Authlib keeps the client created by the first app in the test run, which
    # may have been built without credentials, so they are set on it directly
    # too, and put back after each test
    monkeypatch.setattr(oauth.github, "client_id", CLIENT_ID)
    monkeypatch.setattr(oauth.github, "client_secret", CLIENT_SECRET)
    return auth_app.test_client()


@pytest.fixture
def github():
    # each test adds the organisation membership reply it needs, and checks for
    # itself which calls were made, as not every test gets as far as the token
    with responses.RequestsMock(assert_all_requests_are_fired=False) as mock:
        mock.post(
            GITHUB_TOKEN_URL,
            json={
                "access_token": "test-access-token",
                "token_type": "bearer",
                "scope": "read:org,user:email",
            },
        )
        mock.get(GITHUB_USER_URL, json=GITHUB_USER)
        yield mock


def _start_login(client, next_url="/"):
    response = client.get("/auth/login", query_string={"next": next_url})
    return parse_qs(urlsplit(response.headers["Location"]).query)["state"][0]


def test_login_redirects_to_github_with_state(client):
    response = client.get("/auth/login")

    assert response.status_code == 302
    location = response.headers["Location"]
    assert location.startswith(GITHUB_AUTHORIZE_URL)
    query = parse_qs(urlsplit(location).query)
    assert query["client_id"] == [CLIENT_ID]
    assert query["response_type"] == ["code"]
    assert query["scope"] == ["user:email read:org"]
    assert query["redirect_uri"] == ["https://localhost/auth/authorize"]
    assert query["state"][0]


def test_authorize_signs_in_organisation_member(client, github):
    github.get(membership_url("test-user"), status=204)
    state = _start_login(client, next_url="/consideration/")

    response = client.get(
        "/auth/authorize", query_string={"code": "test-code", "state": state}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/consideration/"
    with client.session_transaction() as session:
        # the profile has no name so the login is used
        assert session["user"] == "test-user"

    token_request, user_request, membership_request = (
        call.request for call in github.calls
    )
    token_body = parse_qs(token_request.body)
    assert token_request.url == GITHUB_TOKEN_URL
    assert token_body["code"] == ["test-code"]
    assert token_body["redirect_uri"] == ["https://localhost/auth/authorize"]
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    assert token_request.headers["Authorization"] == f"Basic {credentials}"
    assert user_request.headers["Authorization"] == "Bearer test-access-token"
    assert membership_request.url == membership_url("test-user")
    assert membership_request.headers["Authorization"] == "Bearer test-access-token"


def test_authorize_refuses_non_member_and_revokes_grant(client, github):
    github.get(membership_url("test-user"), status=404)
    github.delete(REVOKE_URL, status=204)
    state = _start_login(client, next_url="/consideration/")

    response = client.get(
        "/auth/authorize", query_string={"code": "test-code", "state": state}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with client.session_transaction() as session:
        assert "user" not in session
        assert session["_flashes"] == [
            (
                "message",
                "You must be a member of the digital-land organisation to log in",
            )
        ]

    revoke_request = github.calls[-1].request
    assert revoke_request.method == "DELETE"
    assert urlsplit(revoke_request.url)._replace(query="").geturl() == REVOKE_URL
    assert parse_qs(urlsplit(revoke_request.url).query) == {
        "access_token": ["test-access-token"]
    }
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    assert revoke_request.headers["Authorization"] == f"Basic {credentials}"


@pytest.mark.parametrize(
    ("start_login", "sent_state"),
    [
        pytest.param(True, "not-the-real-state", id="state-from-a-different-login"),
        pytest.param(False, "some-state", id="no-login-started"),
        pytest.param(True, None, id="state-left-out"),
    ],
)
def test_authorize_rejects_mismatched_state(client, github, start_login, sent_state):
    # Authlib's protection against a forged sign in: the code must be refused
    # before it is exchanged for a token
    if start_login:
        _start_login(client)
    query = {"code": "test-code"}
    if sent_state is not None:
        query["state"] = sent_state

    with pytest.raises(MismatchingStateError):
        client.get("/auth/authorize", query_string=query)

    assert len(github.calls) == 0
    with client.session_transaction() as session:
        assert "user" not in session


@pytest.mark.parametrize(
    "next_url",
    [
        pytest.param("https://evil.example/", id="another-site"),
        pytest.param("//evil.example/", id="protocol-relative"),
        pytest.param("javascript:alert(1)", id="script"),
    ],
)
def test_authorize_ignores_unsafe_next_url(client, github, next_url):
    github.get(membership_url("test-user"), status=204)
    state = _start_login(client, next_url=next_url)

    response = client.get(
        "/auth/authorize", query_string={"code": "test-code", "state": state}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    with client.session_transaction() as session:
        assert session["user"] == "test-user"
