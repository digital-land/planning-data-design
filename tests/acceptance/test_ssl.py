"""
SSL (http to https redirect) behaviour tests.

In deployed environments https is terminated at cloudfront and the load
balancer forwards plain http to the app, including its health checks on /.
The app must answer those requests rather than redirecting them to https,
otherwise health checks fail and real requests loop between the app and
cloudfront. Redirecting is still available via the HTTPS_REDIRECT setting.
"""

from application.config import Config
from application.factory import create_app


class HttpsRedirectConfig(Config):
    HTTPS_REDIRECT = True


def test_http_health_check_is_not_redirected_by_default():
    app = create_app("application.config.Config")

    response = app.test_client().get("/", base_url="http://localhost")

    assert response.status_code == 200


def test_http_is_redirected_to_https_when_enabled():
    app = create_app(HttpsRedirectConfig)

    response = app.test_client().get("/", base_url="http://localhost")

    assert response.status_code in (301, 302)
    assert response.location.startswith("https://")
