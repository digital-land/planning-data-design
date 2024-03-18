# -*- coding: utf-8 -*-
import os

from flask import Flask
from flask.cli import load_dotenv

from application.models import *  # noqa

load_dotenv()


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 10

    register_blueprints(app)
    register_context_processors(app)
    register_templates(app)
    register_filters(app)
    register_extensions(app)
    register_commands(app)

    return app


def register_blueprints(app):
    from application.blueprints.auth.views import auth
    from application.blueprints.main.views import main

    app.register_blueprint(main)
    app.register_blueprint(auth)


def register_context_processors(app):
    """
    Add template context variables and functions
    """

    def base_context_processor():
        return {"assetPath": "/static"}

    app.context_processor(base_context_processor)


def register_filters(app):
    from application.filters import slugify_filter

    app.add_template_filter(slugify_filter, "slugify")


def register_extensions(app):
    from application.extensions import db, migrate, oauth

    db.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)

    from flask_sslify import SSLify

    sslify = SSLify(app)  # noqa

    # create the CSP for the app - until then leave commented out
    # talisman.init_app(app, content_security_policy=None)

    # if (
    #     app.get("AUTHENTICATION_ON") is not None
    #     and app.config["AUTHENTICATION_ON"] is True
    # ):
    #     oauth.register(
    #         name="github",
    #         client_id=app.config["GITHUB_CLIENT_ID"],
    #         client_secret=app.config["GITHUB_CLIENT_SECRET"],
    #         access_token_url="https://github.com/login/oauth/access_token",
    #         access_token_params=None,
    #         authorize_url="https://github.com/login/oauth/authorize",
    #         authorize_params=None,
    #         api_base_url="https://api.github.com/",
    #         client_kwargs={"scope": "user:email read:org"},
    #     )

    if os.environ.get("SENTRY_DSN") is not None:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=os.environ.get("SENTRY_DSN"), integrations=[FlaskIntegration()]
        )


def register_templates(app):
    """
    Register templates from packages
    """
    from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

    multi_loader = ChoiceLoader(
        [
            app.jinja_loader,
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "digital-land-frontend": PackageLoader("digital_land_frontend"),
                }
            ),
        ]
    )
    app.jinja_loader = multi_loader


def register_commands(app):
    from application.commands import consider_cli

    app.cli.add_command(consider_cli)
