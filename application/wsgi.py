import os

from application.factory import create_app

# default to production config so a missing FLASK_CONFIG never runs with
# development settings, local development sets it in .flaskenv
app = create_app(os.getenv("FLASK_CONFIG") or "application.config.Config")
