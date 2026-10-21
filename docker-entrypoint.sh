#!/bin/sh
set -e
flask db upgrade
# run the image's CMD (gunicorn by default), exec so it receives stop signals
exec "$@"
