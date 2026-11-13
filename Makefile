.PHONY: links links-report check-links server init compile upgrade black black-check flake8 lint bandit audit semgrep check-content test check build-css build-assets assets assets-clobber

server:
	flask --app application.wsgi:app run --debug --port 5050

init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	python -m pre_commit install
	npm install

# lock files are compiled with uv (https://docs.astral.sh/uv/) for Python 3.13,
# matching the Dockerfile and CI; the command is recorded in each file's header
UV_COMPILE = uv pip compile --generate-hashes --python-version 3.13

compile:
	$(UV_COMPILE) requirements/requirements.in -o requirements/requirements.txt
	$(UV_COMPILE) requirements/dev-requirements.in -o requirements/dev-requirements.txt

upgrade:
	$(UV_COMPILE) --upgrade requirements/requirements.in -o requirements/requirements.txt
	$(UV_COMPILE) --upgrade requirements/dev-requirements.in -o requirements/dev-requirements.txt

black:
	black application tools tests

black-check:
	black --check application tools tests

flake8:
	flake8 application tools tests

lint: black flake8

bandit:
	bandit -q -r application

audit:
	pip-audit --require-hashes -r requirements/requirements.txt

# static analysis with Semgrep's own image (needs Docker), the repo mounted read-only.
# Rules come from the Semgrep registry at run time; --metrics=off sends no usage data.
SEMGREP_IMAGE = semgrep/semgrep:1.185.0@sha256:67518c174185a2043fdbed16c70631b79209499b3671178e7194379b48295a0d
SEMGREP_RULES = --config p/python --config p/flask --config p/secrets --config p/github-actions --config p/dockerfile

semgrep:
	docker run --rm -v "$(CURDIR):/src:ro" -w /src $(SEMGREP_IMAGE) \
		semgrep scan --metrics=off --disable-version-check --error $(SEMGREP_RULES)

check-content:
	python -m application.check

# check the next batch of links (network), update links/status.csv and write links/report.md
check-links:
	python -m tools.check_links --limit 100 --report links/report.md

# update links/links.csv and links/domains.md from the content (no network)
links links-report:
	python -m application.links

test:
	python -m pytest

# everything CI runs
check: black-check flake8 bandit audit semgrep check-content test

build-css:
	npm run nps build.stylesheets

# the site has no JavaScript; see "Adding JavaScript" in the README
build-assets: build-css

assets: build-assets

assets-clobber:
	rm -rf application/static/
	mkdir -p application/static
