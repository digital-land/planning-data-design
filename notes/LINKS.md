# Plan: checking outbound links

## Goal

Find broken outbound links, and see which domains the site depends on, without a costly or noisy check.

Today there are about 500 distinct external URLs across 75 domains. The largest are legislation.gov.uk, github.com, gov.uk and Google Docs and Drive.

Every linked page must be public. A link that needs a login is a problem to fix, not a link to skip.

## Principles

1. **Check only what changed or is stale.** Never re-check every link on every run.
2. **Be polite.** At most one request per domain per second, a few domains at a time, a clear `User-Agent`, `HEAD` first with `GET` as the fallback.
3. **Report, do not block.** A dead link is a pull request comment or an issue, not a failed build. Only an unlisted domain, a malformed URL or an absolute link to our own site fails `make check-content`.
4. **Not part of the app.** The checker is a dev tool in `tools/`, run by CI. The app stays free of outbound connections, and the existing import test still covers `application/`.

## Pieces

### 1. Extract (offline, in `make check-content`)

Add `application/links.py`: walk the front matter and rendered HTML for every `http(s)` URL and return `{url: [source files]}`. This reuses the content loader, so it sees links in front matter (`useful_links`, `legislation`, `specification`) as well as in the body.

Output a sorted, committed file `links/links.csv`: `url,domain,first_seen`.

### 2. Detect new links and domains (offline, fast)

Compare the extracted URLs with `links/links.csv`:

- **New URL:** add it, with today's date as `first_seen`.
- **New domain:** also listed in the pull request comment for review.
- **Removed URL:** drop it.

Because `links.csv` is committed, a pull request diff shows exactly which links and domains it adds.

### 3. Domain list and report

`links/domain.csv` lists every domain the content may link to. It is owned by the content owners in `CODEOWNERS`.

**Every linked domain must be in `links/domain.csv`.** `make check-content` fails on a link to a domain that is not listed, so adding a third-party dependency is always a reviewed change. Seed the file from today's 75 domains and review it for anything surprising (shorteners, personal sites).

`make links-report` writes `links/domains.md`: each domain, the number of links, an example page, and whether it is listed.

Rules for non-public hosts:

- `docs.google.com` and `drive.google.com` are allowed only when the linked file is public. The check flags any that need a sign-in.
- SharePoint (`sharepoint.com`) and Mural (`app.mural.co`) are not allowed unless the link is public. They are not listed by default, so a link to them fails the domain check.

### 4. Check (networked, in `tools/check_links.py`)

State is kept in `links/status.csv` on `main`: `url,last_checked,status,last_ok,failures`.

Which URLs to check on each run:

- **Pull requests:** only new URLs from step 2. Usually none to a few.
- **Weekly scheduled run:** URLs never checked, then those not checked for 28 days, oldest first, capped at about 100 a run. All 500 are covered each month at about 100 requests a week.

Rules:

- Skip `mailto:`.
- **Check that each page is public.** Request without cookies or credentials. A 401, a 403 or a redirect to a sign-in page (for example `accounts.google.com`, `login.microsoftonline.com`) is reported as `not public`, which is a problem to fix, not an unclear result. Google Docs and Drive links are checked like any other.
- Internal paths are already covered by `make check-content`.
- Follow up to 3 redirects. Record a permanent redirect (301 or 308) to a different URL as `moved`, with the new target, so it can be fixed.
- For a broken link where a snapshot is appropriate (for example a withdrawn gov.uk page), suggest the National Archives web archive (`webarchive.nationalarchives.gov.uk`) as a replacement in the report. Never rewrite a link automatically.
- Treat 429 and 5xx as `unclear`, not broken (403 and 401 are `not public`, see above). Retry on the next run. Flag as broken only after 3 consecutive failures over at least 2 weeks, or a 404 or 410 twice.
- Timeouts of 10 seconds. Back off on 429, honouring `Retry-After`.

### 5. Reporting

- **Pull request:** a single comment listing new URLs, new domains and any new broken or moved links, using `gh`.
- **Weekly run:** open or update one GitHub issue, "Outbound link report", with broken links grouped by domain and by source page, and moved links with their suggested replacement. Close it when it is empty.
- The weekly run commits the updated `links/status.csv` to `main` as a bot. If `main` is protected, it opens a pull request instead.
- Self-links: absolute links to `design.planning.data.gov.uk` fail `make check-content`. Write them as relative paths, which are cheaper and already covered by the internal link check. Rewrite the 16 existing ones as part of step 1.

## CI

| Trigger | Runs | Network |
|---|---|---|
| Every push or pull request | extract, diff, domain report (`make links-report`) | none |
| Pull request that changes `content/` | check new URLs only, comment | a few requests |
| Weekly (cron) | check the stale batch (about 100), update the issue and `links/status.csv` | about 100 requests |

The pull request workflow has `contents: read` and `pull-requests: write`. The weekly workflow also has `issues: write` and `contents: write` to commit `links/status.csv`.

## Tests

- Extraction finds links in the body and in front matter.
- The domain list: an unlisted domain, and absolute self-links, fail.
- Public check: sign-in redirects, 401 and 403 are `not public`.
- Status rules (404 versus 403, retry counts, redirects) against a fake HTTP server on `localhost`.
- Selection logic: new first, then stale, capped.

## Steps

Each step is one commit.

1. `application/links.py` and tests. Generate `links/links.csv`. Rewrite self-links as relative paths.
2. `links/domain.csv`, seeded from today's 75 domains, the check in `make check-content` and the domain report. Review the list, and remove or fix SharePoint and Mural links.
3. `tools/check_links.py` with state, selection and status rules, plus tests.
4. Make targets (`links-report`, `check-links`) and CI workflow (pull request and weekly).
5. Pull request comment, the weekly issue and the web archive suggestions.
6. Document in the README. Fix any broken or non-public links found by the first run.
