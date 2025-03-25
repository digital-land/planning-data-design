#!/bin/sh
set -e
flask db upgrade
flask run --debug
