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

FROM python:3.10-slim
WORKDIR /code

# safe defaults for deployed environments, compose.yml overrides these for local development
ENV FLASK_CONFIG=application.config.Config
ENV FLASK_APP=application.wsgi:app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git libproj-dev proj-bin gdal-bin wget gnupg2  \
    && rm -rf /var/lib/apt/lists/*


RUN echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/postgresql.gpg

RUN apt-get update && \
    apt-get install -y postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/ ./requirements/
RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/dev-requirements.txt

# copy only what the app needs at runtime, node tooling (package.json,
# package-lock.json, src/ etc) stays in the assets stage
COPY docker-entrypoint.sh ./
COPY migrations/ ./migrations/
COPY data/glossary-of-tags.csv data/upcoming-events.yml ./data/
COPY application/ ./application/
COPY --from=assets /app/application/static ./application/static

EXPOSE 5050

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "-b", "0.0.0.0:5050", "application.wsgi:app"]
