from functools import wraps

from werkzeug.routing import BaseConverter

from application.models import Stage


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app, redirect, request, session, url_for

        if current_app.config.get("AUTHENTICATION_ON", True):
            if session.get("user") is None:
                return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


class StageConverter(BaseConverter):

    def to_python(self, stage):
        stage = stage.upper()
        stage = stage.replace("-", "_")
        return Stage[stage]

    def to_url(self, stage):
        stage = stage.name.lower()
        stage = stage.replace("_", "-")
        return stage


def true_false_to_bool(s):
    if isinstance(s, bool):
        return s
    return s.lower() == "true"
