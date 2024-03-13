init::
	python -m pip install --upgrade pip
	python -m pip install pip-tools
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	python -m pre_commit install
	npm install

reqs:
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

upgrade:
	python -m piptools compile --upgrade requirements/dev-requirements.in
	python -m piptools compile --upgrade requirements/requirements.in
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

black:
	black application tests

black-check:
	black --check application tests

flake8:
	flake8 .

isort:
	isort --profile black .

lint: black flake8 isort

watch:
	npm run watch

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
