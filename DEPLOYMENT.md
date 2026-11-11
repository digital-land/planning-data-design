# Deployment

The image is built by `.github/workflows/deploy.yml` from the `Dockerfile`.

- Python only in the final stage. Content, redirects and code are baked in and immutable.
- Runs as a non-root user. Run with a read-only root filesystem, all capabilities dropped and no network egress (`compose.yml` shows the settings).
- Serves with gunicorn on port 5050. HTTPS is terminated by the platform.
- No environment variables are needed. There are no secrets.
- Health check: `GET /`.
- Bad content or redirects fail the image build (`python -m application.check`).

The old database-backed site is tagged `before-readonly`.
