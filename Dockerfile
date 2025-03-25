# syntax=docker/dockerfile:1
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
    wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update && \
    apt-get install -y postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/dev-requirements.txt
EXPOSE 5050

ENTRYPOINT ["./docker-entrypoint.sh"]
