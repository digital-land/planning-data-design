# Plan: read-only static site

## Goal

Replace the current database-backed, authenticated app with the simplest Flask app that can serve the site's content, and that can be shown to be secure.

The app:

- serves HTML pages rendered from Markdown files in `content/`
- serves static CSS, JavaScript, CSV and image files
- accepts only `GET` and `HEAD`
- has no login, sessions, cookies, forms, database or outbound network connections

## Principles

1. **Less code is the security model.** Anything we do not ship cannot be attacked.
2. **Content is files.** Authors edit Markdown and CSV in git. Review happens in pull requests.
3. **Fail at build, not at request.** Validate all content and redirects when the app starts (and in CI). A request never touches the filesystem with user input.
4. **Modular.** Adding a page, section or redirect rule means adding a file, not editing Python.

## Out of scope

- Editing considerations through the web (this goes: edits become pull requests).
- Anything needing a user identity.
- A build step that generates HTML ("freezing"). We may add this later (see open questions).

## Target repository layout

```
content/
  index.md
  community.md
  cookies.md
  roadmap.md
  design-principles.md
  design-process.md
  project/
    index.md
    planning-applications/
      index.md
      members.md
      roadmap.md
      weeknotes.md
  consideration/
    index.md                 # list page, built from the data below
    <slug>.md                # one per consideration
    <slug>/stage-<stage>.md  # not needed
  help/
    os-declaration-options.md
data/
  glossary-of-tags.csv
  upcoming-events.yml
redirects/
  legacy-pages.csv           # old path, new path, status
  legacy-sections.csv        # prefix rules
application/
  __init__.py                # create_app()
  content.py                 # load and validate content at start-up
  redirects.py               # load and validate redirect files
  routes.py                  # the few routes
  markdown.py                # safe Markdown rendering
  templates/                 # layouts, components, page templates only
  static/                    # built CSS and JS
tests/
Dockerfile
Makefile
```

Everything under `data/` and `content/` is plain text.

## Content model

Each Markdown file has YAML front matter and a body.

```markdown
---
title: Site allocations
description: Areas identified as sites for housing, employment and other uses
template: consideration      # optional, default "page"
---
Body in Markdown.
```

- The URL is derived from the file path: `content/project/planning-applications/members.md` is `/project/planning-applications/members`. `index.md` is the directory path.
- Front matter is validated against a small schema (pydantic is already a dependency; consider plain dataclasses to drop it).
- Unknown front matter keys fail validation.
- Consideration files carry their structured fields in front matter: `stage`, `datasets`, `frequency_of_updates`, `legislation`, `useful_links`, `synonyms`, `tags`, `github_discussion_number`, `created`, `updated`.

### Migrating the database

Write a one-off script (`tmp/` or a throwaway branch, not shipped) that reads `data/*.csv` and writes `content/consideration/<slug>.md`. After migration, delete the CSVs it replaces.

| Current source | Becomes |
|---|---|
| `consideration.csv` | one Markdown file per consideration |
| `answer.csv`, `question.csv` | per-stage sections in each consideration file |
| `tag.csv`, `consideration_tags.csv` | `tags:` in front matter |
| `note.csv` | **decision needed** (see below) |
| `change_log.csv` | **decision needed**; probably `git log` instead |
| `performance.csv`, `planning-concerns-backlog.csv` | drop (routes already redirect to `/`) |
| `latest_backup.dump` | delete from the repository |

Do not publish by default: considerations with `public = f`, with `deleted_date` set, or with a `blocked_reason`. The migration script must apply the `public` and `deleted_date` filters, and list what it skipped for review.

## Routes

All routes are `GET` only.

| Path | Behaviour |
|---|---|
| `/` | `content/index.md` |
| `/<path>` | Look up `<path>` in the in-memory content index. 200 or 404. |
| `/consideration/` | List page, filters done in JavaScript or by per-stage pages |
| `/consideration/<slug>` | Consideration page |
| `/consideration/planning-considerations.csv` | Static CSV, generated at build time |
| `/static/...` | Flask static folder |
| anything in the redirect tables | 301 to the new path |

The content index is a dictionary built at start-up, mapping URL path to a parsed page. A request is a dictionary lookup, never `open(f"...{page}...")`. This removes path traversal as a class of bug, and fixes the current `/<string:page>` view, which builds a filesystem path from the URL.

## Redirects

Today redirects are spread across `main/views.py`: some are routes, some are a dictionary in `check_for_redirects`, one is a prefix rule (`/planning-consideration/...`).

Replace with data files in `redirects/`:

```csv
# redirects/legacy-pages.csv
from,to,status
/advisory-group,/project/planning-applications,301
/advisory-group/members,/project/planning-applications/members,301
/advisory-group/timeline,/project/planning-applications/roadmap,301
/what-we-are-working-on,/roadmap,301
/how-to-contribute-to-the-data-design-process,/community,301
/get-involved,/community,301
/get-involved-in-designing-data,/community,301
/how-to-help-develop-a-new-dataset,/design-process,301
/how-to-get-existing-datasets-on-to-planning-data-gov-uk,/design-process,301
/data-design-process,/design-process,301
/stage-count,/,301
/performance,/,301
/progress-report,/,301
```

```csv
# redirects/legacy-sections.csv
from_prefix,to_prefix,status
/planning-consideration,/consideration,301
```

Rules:

- One loader (`application/redirects.py`) reads every `redirects/*.csv`. Adding a file adds rules.
- Exact matches win over prefix rules.
- Query strings are preserved for prefix rules only.
- `to` must be a relative path starting with `/`. Absolute URLs and `//host` are rejected at start-up, so there is no open redirect.
- Start-up validation fails on: duplicate `from`, a redirect to a path that is neither content nor another redirect, and redirect chains or loops.
- A test asserts every old path in `PATHS.md` resolves to 200, a redirect or 404.

Check `/progress-report` and `/community`: `progress-report` currently renders a template and needs a decision (see open questions).

### Paths that currently need login: return 404

No route is registered for these, so Flask's own 404 applies:

- `/auth/*`
- `/admin/*`
- `/consideration/add`
- `/consideration/<slug>/` followed by any of: `edit`, `delete`, `edit-specification`, `add-schema`, `edit-estimated-size`, `add-synonym`, `prioritised`, `public`, `stage/change`, `os-declaration`, `edit-frequency`, `add-useful-link`, `edit-legislation`, `note`, `block`, and the `.../delete` routes
- `/consideration/<slug>/<stage>/<question>/...` (the questions blueprint)

Keep one test that asserts a sample of these return 404, and that `POST` to any path returns 405.

## Security

The aim is to be able to state, and test, each of these.

**Attack surface**

- No database, no `DATABASE_URL`, no SQL.
- No `SECRET_KEY`, no sessions, no cookies set by the server.
- No forms, so no CSRF protection is needed. Remove Flask-WTF.
- No OAuth, no GitHub API calls, no Sentry. Remove Authlib, PyGithub, sentry-sdk.
- No outbound network connections at runtime. Run the container with no egress in deployment, and test by importing the app with the network blocked.
- Methods restricted to `GET`, `HEAD` and `OPTIONS` through a single `before_request` check.

**Content**

- Markdown rendering is a single function. Raw HTML in Markdown is escaped or stripped (decide: escape everything, or allow a small allow-list through `nh3`/`bleach`). Default: escape.
- Content is trusted only as far as pull request review. Document this.
- Jinja autoescape stays on. A test fails the build if `|safe` or `Markup(` appears outside `application/markdown.py`.

**Response headers** (one `after_request` function)

- `Content-Security-Policy: default-src 'self'` (no inline scripts, no third-party origins; move any inline script into `static/`)
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy` denying all features
- `Strict-Transport-Security` (HTTPS is terminated by the platform; set it in the app too)
- Replace `flask-sslify` and `flask-talisman` with these headers, or keep Talisman only if it is the smaller change.

**Dependencies**

- Runtime: Flask, Markdown, python-frontmatter, `govuk-frontend-jinja`, `digital-land-frontend` (templates only), gunicorn. Check whether `digital-land-frontend` can be reduced to its compiled CSS and JS, which would remove a git dependency.
- Remove: SQLAlchemy, Flask-Migrate, psycopg2, alembic-postgresql-enum, Authlib, PyGithub, Flask-WTF, flask-sslify, flask-debugtoolbar, sentry-sdk, is-safe-url, beautifulsoup4 (if unused), pydantic (if replaced).
- Pin with hashes (`pip-compile --generate-hashes`) and run `pip-audit` in CI.
- Dependabot or Renovate for updates.

**Container**

- Slim base image, pinned by digest.
- Drop `gcc`, `g++`, `git`, `gdal`, `proj`, `wget`, `gnupg2`, `postgresql-client`. None are needed to serve files.
- Multi-stage build: assets stage (node) builds CSS and JS, final stage is Python only, with no node, no `pip` cache.
- Run as a non-root user, read-only root filesystem, no capabilities.
- Gunicorn in production. Remove `flask run --debug` and `FLASK_DEBUG=1` from the image, and `flask db upgrade` from `Procfile` and `docker-entrypoint.sh`.
- Content is copied into the image at build time and is immutable at runtime.

**Verification (the "provable" part)**

CI runs, and fails on any of:

1. Content and redirect validation (`make check-content`).
2. Tests: every content URL returns 200; every redirect resolves to 200 in one hop; all auth-only paths return 404; `POST`, `PUT`, `DELETE` return 405; security headers present on every response.
3. A test that walks `app.url_map` and asserts it contains only the expected rules.
4. A test that fails if the app package imports `sqlalchemy`, `requests`, `urllib.request`, `socket`, `smtplib` or `authlib`.
5. `pip-audit`, `bandit`, `black --check`, `flake8`.
6. Optionally, an OWASP ZAP baseline scan against the built container.

## Separate content repository

Would a separate content repository be more secure? Somewhat, but not by much, and it adds moving parts. Start with one repository and split later.

### What a split gives

- **Separate permissions.** Editors get write access to content only. Only code owners can change the app.
- **Smaller app repository.** It holds code and tests only.
- **Different review rules.** Content changes can have lighter review than code changes.

### Why the gain is limited

- **Single-repository alternative.** `CODEOWNERS` plus branch protection gives most of the same separation. Content owners approve `content/**` and `redirects/**`. Code owners approve everything else. Nobody can merge unreviewed.
- **The real boundary is deployment.** If merging content triggers a deploy, content editors can effectively change what runs. The access control only matters if deploying is a separate, gated action.
- **Content is untrusted input either way.** It is rendered into HTML, so a malicious editor could try script injection through Markdown. The defences belong to the app (escaped raw HTML, CSP, no `|safe`), not the repository.
- **Extra risks.** The app depends on a second repository at build time, so we need version pinning, a content-to-app compatibility check, and a way to stop broken content being deployed.

### How to split safely

1. The app Dockerfile pulls content at a pinned commit SHA or tag, never `main`.
2. The content repository's CI runs the same validator as the app (front matter schema, links, redirects). The validator lives in the app repository and is installed as a pinned dependency or container. Bad content never reaches a deploy.
3. A deploy is a pull request in the app repository that bumps the content SHA. Editors can merge content, but only deployers can publish it.
4. Content is baked into the image at build time. Nothing is fetched at runtime, so there are still no outbound network connections.

### Decision

- Keep one repository for the refactor.
- Use `CODEOWNERS` from the start.
- Keep `content/` a clean seam: the loader takes its directory from one setting, so splitting later is a mechanical change.
- Split when there are editors who should not be able to change code, or when content changes much more often than code.

## Steps

Each step is one commit and leaves the tests green.

1. **Branch and baseline.** Tag the current state as `pre-readonly`. Record every path in `PATHS.md` with its current status code (a script that requests each path), to use as the regression list.
2. **Add `content/` and the loader.** `content.py`, front matter schema, start-up validation, tests. Move existing `application/templates/pages/*.md` to `content/`.
3. **Single page route.** Serve `content/` through the in-memory index, replacing `/<string:page>`. Add the page template.
4. **Redirects module.** Create `redirects/*.csv` and `redirects.py`. Remove the redirect routes and `check_for_redirects` from `main/views.py`. Add validation tests.
5. **Project and help pages.** Convert `project` and `help` blueprints to Markdown under `content/project/` and `content/help/`.
6. **Migrate considerations.** Write and run the one-off export. Review the output, especially skipped records. Add `content/consideration/`.
7. **Consideration templates.** Render list and detail pages from content. Replace the filters with client-side filtering or pre-built per-filter pages (decide in review). Generate `planning-considerations.csv` at build time.
8. **Remove write paths.** Delete the `auth`, `tags` (admin), `questions` blueprints and all `*-form.html`, `delete.html`, `block-form.html`, `note-form.html`, `questiontypes/`, `macros/` templates. Delete `forms.py`, `question_sets.py`, `commands.py`, `models.py`, `extensions.py`, `services/` (check `EventService` first; it may be replaced by reading `upcoming-events.yml`).
9. **Remove the database.** Delete `migrations/`, `restore-init.sh`, `compose.yml` database service, `latest_backup.dump`, CSVs now in `content/`. Strip `config.py` to a handful of settings.
10. **Security headers and method restriction.**
11. **Dependencies.** Cut `requirements/` down; pin with hashes.
12. **Container.** New slim Dockerfile; remove `Dockerfile.assets` if redundant; non-root and read-only.
13. **CI checks.** Add the verification tests and `pip-audit`.
14. **Docs.** Rewrite `README.md`, replace `REPLATFORM.md` with a short deployment note, update `PATHS.md`.
15. **Cut over.** Deploy alongside the old site, compare the regression list, switch DNS.

## Open questions

1. **Notes (`note.csv`, 470 rows).** Are these public? They may be internal. Default: drop.
2. **Change log (`change_log.csv`, 2,880 rows).** Drop, publish as a single CSV, or rely on git history? The `/consideration/<slug>/change-log` page is currently public.
3. **Non-public considerations.** Confirm that `public = f` means "do not publish".
4. **`/progress-report`.** Public today and renders from the database. Drop with a redirect to `/`, or generate at build time?
5. **Consideration list filtering.** Client-side JavaScript over an embedded JSON file, or static pages per stage and tag? The first is simpler to build; the second works without JavaScript (GOV.UK progressive enhancement).
6. **Freezing later.** If the content stays small, a build step that writes HTML to `public/` would let us serve with any static host and remove Flask from production. Keep `create_app()` free of anything that would prevent that.
7. **Cookies page and banner.** With no analytics and no cookies set, can the banner and `/cookies` page go? `/cookies` would need a redirect or a short "we do not use cookies" page.
8. **Markdown raw HTML.** Escape everything, or allow a small allow-list?
9. **`digital-land-frontend`.** Keep as a Python package for templates, or vendor the compiled assets?
10. **Python version.** `runtime.txt` and the Dockerfile say 3.10, which reaches end of life in October 2026. Move to a supported version as part of step 12.
11. **Editing workflow.** Who edits content now? Is "pull request on GitHub" acceptable for all authors, or do we need a docs-style editor later?
12. **Separate content repository.** Agree the decision above, and who owns `CODEOWNERS` for `content/**`.
