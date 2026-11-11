"""Method restriction and response headers."""

from flask import abort, request

ALLOWED_METHODS = {"GET", "HEAD", "OPTIONS"}

HEADERS = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}


def init_security(app):
    @app.before_request
    def only_read():
        if request.method not in ALLOWED_METHODS:
            abort(405)

    @app.after_request
    def add_headers(response):
        for name, value in HEADERS.items():
            response.headers[name] = value
        return response
