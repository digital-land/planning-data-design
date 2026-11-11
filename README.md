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
make check       # lint, bandit, pip-audit, content checks and tests
```

`make check-content` validates front matter, redirects (no loops, chains, open redirects or dead targets) and internal links. It also runs when the container is built.

CSS and images are built by npm (`make assets`) and are not committed.

## Security

See `notes/READONLY.md`. In short:

- Content is trusted only as far as pull request review. `CODEOWNERS` separates content and code review.
- Responses carry a strict Content Security Policy (`default-src 'self'`) and other headers, set in `application/security.py`.
- Tests check the route table, methods, headers, imports and the absence of `|safe` and `Markup(` outside `application/markdown.py`.

## Deployment

See `DEPLOYMENT.md`.
