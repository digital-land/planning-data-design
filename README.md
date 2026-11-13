# Designing planning and housing data

A read-only website built from Markdown and CSV files in this repository.

The app serves pages from `content/`, static files from `application/static/`, and redirects from `redirects/`. It accepts only `GET`, `HEAD` and `OPTIONS`. It has no database, login, sessions, cookies, forms or outbound network connections.

## Adding or changing content

Edit or add a Markdown file in `content/` and open a pull request.

The URL comes from the file path. `content/project/index.md` is `/project`.

```markdown
---
title: Site allocations
description: Areas identified as sites for housing, employment and other uses
---
Body in Markdown.
```

- `title` and `description` are required. Unknown keys fail validation.
- `template` is optional: `page` (default), `home`, `consideration` or `consideration-list`.
- Raw HTML in Markdown is escaped, not rendered.
- Considerations are files in `content/consideration/`. Their extra front matter keys are listed in `application/content.py`.

Moved or removed pages go in `redirects/*.csv`:

| File header | Use |
|---|---|
| `from,to,status` | one path to another (`410` with an empty `to` for removed pages) |
| `from_prefix,to_prefix,status` | a section to a section, keeping the query string |
| `section,status` | pages below `<section>/<slug>/` go to `<section>/<slug>` |

## Running

```sh
make init
make server      # http://localhost:5050
make check       # lint, bandit, pip-audit, semgrep, content checks and tests
make semgrep     # static analysis on its own (runs Semgrep's Docker image)
```

Dependencies are listed in `requirements/*.in` and locked with hashes in `requirements/*.txt`. To change them, edit the `.in` file and run `make compile`, or `make upgrade` to move everything to the latest versions. Both need [uv](https://docs.astral.sh/uv/) (`brew install uv` or `pipx install uv`). Dependabot proposes updates weekly, a week after each release.

`make check-content` validates front matter, redirects (no loops, chains, open redirects or dead targets) and internal links. It also runs when the container is built.

CSS and images are built by npm (`make assets`) and are not committed.

### Adding JavaScript

The site has no JavaScript: every page works as plain HTML and CSS. If a feature really needs it:

1. Put the source in `src/javascripts/` and add a `rollup.config.js` that writes to `application/static/javascripts/`.
2. Add `npm run nps build.javascripts` to `postinstall` in `package.json` and to `make build-assets`, so local and Docker builds include it.
3. Load it from `application/templates/base.html` with `<script type="module" src="/static/javascripts/...">`. The Content-Security-Policy (`default-src 'self'`) blocks inline `<script>` blocks and `on...=` attributes, so keep all code in files. For GOV.UK Frontend components, import `initAll` from `govuk-frontend`.

## Outbound links

Every external link in the content is listed in `links/links.csv`, and every linked domain must be listed in `links/domain.csv`.

- After adding or removing a link, run `make links` to update `links/links.csv` and `links/domains.md`. `make check-content` fails if they are out of date, if a domain is not listed, if a URL contains a space, or if a link uses an absolute `design.planning.data.gov.uk` address (use a relative path).
- Linked pages must be public. SharePoint and Mural are not in the domain list because their pages need a sign in.
- `make check-links` checks the next batch of about 100 links (network) and updates `links/status.csv`. CI runs it weekly and keeps one "Outbound link report" issue up to date. Pull requests that change content check only their new links and comment with the result.
- Broken, moved and not-public links are reported, never fixed automatically. Some sites return 403 to automated checks, so check those by hand.

See `notes/LINKS.md` for the design.

## Security

See `notes/READONLY.md`. In short:

- Content is trusted only as far as pull request review. `CODEOWNERS` separates content and code review.
- Responses carry a strict Content Security Policy (`default-src 'self'`) and other headers, set in `application/security.py`.
- Tests check the route table, methods, headers, imports and the absence of `|safe` and `Markup(` outside `application/markdown.py`.

## Deployment

See `DEPLOYMENT.md`.
