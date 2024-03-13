import os

from application.factory import create_app

app = create_app(os.getenv("FLASK_CONFIG") or "config.DevelopmentConfig")
