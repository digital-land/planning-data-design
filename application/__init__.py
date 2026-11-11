from pathlib import Path

from flask import Flask

from application.content import breadcrumbs, load_content
from application.redirects import Redirects
from application.routes import GENERATED_PATHS, register_routes
from application.security import init_security

ROOT = Path(__file__).resolve().parent.parent

SITE_NAME = "Designing planning and housing data"
PLATFORM_URL = "https://www.planning.data.gov.uk"
DISCUSSIONS_URL = "https://github.com/digital-land/data-standards-backlog/discussions"
NAVIGATION = [
    ("/design-principles", "Design principles"),
    ("/consideration", "Considerations"),
]


def create_app(content_dir=ROOT / "content", redirects_dir=ROOT / "redirects"):
    """Build the app. Any content or redirect problem raises here, not at request time."""
    app = Flask(__name__)
    pages = load_content(content_dir)
    redirects = Redirects.load(redirects_dir)
    redirects.validate(pages, extra_paths=GENERATED_PATHS)

    @app.context_processor
    def site():
        return {
            "site_name": SITE_NAME,
            "navigation": NAVIGATION,
            "platform_url": PLATFORM_URL,
            "discussions_url": DISCUSSIONS_URL,
        }

    init_security(app)
    register_routes(app, pages, redirects)
    return app
