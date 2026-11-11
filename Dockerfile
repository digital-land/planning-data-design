# syntax=docker/dockerfile:1
FROM node:18-slim AS assets
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends rsync \
    && rm -rf /var/lib/apt/lists/*

COPY package.json package-lock.jso[n] ./
RUN npm install --ignore-scripts

COPY digital-land-frontend.config.json rollup.config.js ./
COPY src/ ./src/
RUN mkdir -p application/static/javascripts application/static/stylesheets \
    && npm run postinstall

# the final stage is Python only: no node, no compilers, no git, no pip cache
FROM python:3.12-slim@sha256:05a994d2344eb364cc186910f4fc8786a38215f39f00d0acc25bff33a08f4177
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements/requirements.txt ./requirements/requirements.txt
RUN pip install --no-cache-dir --require-hashes -r requirements/requirements.txt

# content, redirects and code are baked in and immutable at runtime
COPY application/ ./application/
COPY content/ ./content/
COPY redirects/ ./redirects/
COPY --from=assets /app/application/static ./application/static

# fail the build on bad content or redirects
RUN python -m application.check

RUN useradd --system --no-create-home --uid 10001 app
USER 10001

EXPOSE 5050
CMD ["gunicorn", "-b", "0.0.0.0:5050", "--worker-tmp-dir", "/dev/shm", "application.wsgi:app"]
