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

ENV FLASK_CONFIG=application.config.DevelopmentConfig
ENV FLASK_APP=application.wsgi:app

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050
ENV FLASK_DEBUG=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ git libproj-dev proj-bin gdal-bin wget gnupg2  \
    && rm -rf /var/lib/apt/lists/*


RUN echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/postgresql.gpg

RUN apt-get update && \
    apt-get install -y postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*

COPY . .
COPY --from=assets /app/application/static ./application/static

RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/dev-requirements.txt

EXPOSE 5050

ENTRYPOINT ["./docker-entrypoint.sh"]
