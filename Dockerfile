# syntax=docker/dockerfile:1
# Node 26 LTS, pinned by digest; Dependabot keeps the digest current
FROM node:26-slim@sha256:e6bedef217677b276c591795e169840edd9096dbf13f29df8ef8d1856b8820bc AS assets
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends rsync \
    && rm -rf /var/lib/apt/lists/*

# npm ci installs exactly what package-lock.json records, and fails if the two disagree
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

COPY digital-land-frontend.config.json ./
COPY src/ ./src/
RUN mkdir -p application/static/stylesheets \
    && npm run postinstall

# the final stage is Python only: no node, no compilers, no git, no pip cache
FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Debian security fixes released since the base image was built; the pinned
# digest only changes when Dependabot bumps it
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/requirements.txt ./requirements/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r requirements/requirements.txt

# content, redirects and code are baked in and immutable at runtime
COPY application/ ./application/
COPY content/ ./content/
COPY redirects/ ./redirects/
COPY links/ ./links/
COPY --from=assets /app/application/static ./application/static

# fail the build on bad content or redirects
RUN python -m application.check

RUN useradd --system --no-create-home --uid 10001 app
USER 10001

EXPOSE 5050
# no control socket: the filesystem is read-only and nothing manages gunicorn at runtime
CMD ["gunicorn", "-b", "0.0.0.0:5050", "--worker-tmp-dir", "/dev/shm", "--no-control-socket", "application.wsgi:app"]
