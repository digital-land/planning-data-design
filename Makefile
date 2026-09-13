init::
	# pip-tools 7.5.3 breaks on pip>=26.1 (jazzband/pip-tools#2379); unpin once fixed upstream
	python -m pip install --upgrade "pip<26.1"
	python -m pip install pip-tools
	python -m piptools sync requirements/dev-requirements.txt requirements/requirements.txt
	python -m pre_commit install
	npm install

compile:
	python -m piptools compile requirements/dev-requirements.in
	python -m piptools compile requirements/requirements.in
	python -m piptools sync requirements/requirements.txt requirements/dev-requirements.txt

upgrade:
	python -m piptools compile --upgrade requirements/requirements.in
	python -m piptools compile --upgrade requirements/dev-requirements.in
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

DB_TABLES = answer change_log consideration consideration_tags note performance question tag

# restores data/latest_backup.dump into a fresh db container, then dumps
# each table to data/<table-name>.csv
export-csv:
	podman-compose down -v
	podman-compose up -d db
	until podman-compose exec -T db psql -U postgres -d planning-data-design -c "select 1 from consideration limit 1" >/dev/null 2>&1; do sleep 1; done
	for table in $(DB_TABLES); do \
		podman-compose exec -T db psql -U postgres -d planning-data-design -c "\copy public.$$table to stdout with csv header" > data/$$table.csv; \
	done
