from http import HTTPStatus

import requests
from flask import Blueprint, current_app, flash, redirect, request, session, url_for
from is_safe_url import is_safe_url

from application.extensions import oauth

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.get("/login")
def login():
    session["next"] = _make_next_url_safe(request.args.get("next", "/"))
    auth_url = url_for("auth.authorize", _external=True)
    return oauth.github.authorize_redirect(auth_url)


@auth.get("/authorize")
def authorize():
    next_url = session.pop("next", None)
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get("user", token=token)
    resp.raise_for_status()
    user_profile = resp.json()
    if user_profile:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token['access_token']}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        # check if user is a member of digitial-land org - if they are the members endpoint
        # will return status code 204
        # https://docs.github.com/en/rest/orgs/members?apiVersion=2022-11-28#check-organization-membership-for-a-user
        url = (
            f"https://api.github.com/orgs/digital-land/members/{user_profile['login']}"
        )
        resp = requests.get(url, headers=headers)
        if resp.status_code == HTTPStatus.NO_CONTENT:
            session["user"] = user_profile
            next_url = _make_next_url_safe(next_url)
            return redirect(next_url)
        else:
            client_id = current_app.config["GITHUB_CLIENT_ID"]
            client_secret = current_app.config["GITHUB_CLIENT_SECRET"]
            params = {"access_token": token["access_token"]}
            headers = {"X-GitHub-Api-Version": "2022-11-28"}
            resp = requests.delete(
                f"https://api.github.com/applications/{client_id}/grant",
                headers=headers,
                params=params,
                auth=(client_id, client_secret),
            )
            flash("You must be a member of the digital-land organisation to log in")
            return redirect(url_for("main.index"))
    else:
        flash("You must be a member of the digital-land organisation to log in")
        return redirect(url_for("main.index"))


@auth.get("/logout")
def logout():
    session.pop("user", None)
    session.pop("next", None)
    return redirect(url_for("main.index"))


def _make_next_url_safe(next_url):
    if next_url is None:
        return url_for("main.index")
    if not is_safe_url(next_url, current_app.config.get("SAFE_URLS", {})):
        return url_for("main.index")
    return next_url
