.PHONY: links links-report check-links server init compile upgrade black black-check flake8 lint bandit audit check-content test check build-css build-js build-assets copyjs assets assets-clobber

server:
	flask --app application.wsgi:app run --debug --port 5050

init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	python -m pre_commit install
	npm install

compile:
	python -m piptools compile --generate-hashes requirements/requirements.in
	python -m piptools compile --generate-hashes requirements/dev-requirements.in

upgrade:
	python -m piptools compile --upgrade --generate-hashes requirements/requirements.in
	python -m piptools compile --upgrade --generate-hashes requirements/dev-requirements.in

black:
	black application tests

black-check:
	black --check application tests

flake8:
	flake8 application tests

lint: black flake8

bandit:
	bandit -q -r application

audit:
	pip-audit --require-hashes -r requirements/requirements.txt

check-content:
	python -m application.check

# update links/links.csv and links/domains.md from the content (no network)
links links-report:
	python -m application.links

test:
	python -m pytest

# everything CI runs
check: black-check flake8 bandit audit check-content test

build-css:
	npm run nps build.stylesheets

build-js:
	npm run nps build.javascripts

build-assets: build-css build-js

copyjs:
	npm run copyjs

assets: build-assets copyjs

assets-clobber:
	rm -rf application/static/
	mkdir -p application/static
