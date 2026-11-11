# Plan: checking outbound links

## Goal

Find broken outbound links, and see which domains the site depends on, without a costly or noisy check.

Today there are about 500 distinct external URLs across 75 domains. The largest are legislation.gov.uk, github.com, gov.uk and Google Docs and Drive.

## Principles

1. **Check only what changed or is stale.** Never re-check every link on every run.
2. **Be polite.** At most one request per domain per second, a few domains at a time, a clear `User-Agent`, `HEAD` first with `GET` as the fallback.
3. **Report, do not block.** A dead link is a pull request comment or an issue, not a failed build. Only a new domain or a malformed URL needs a human decision.
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

### 3. Domain report

`make links-report` writes `links/domains.md`: each domain, the number of links, an example page, and a status:

| Status | Meaning |
|---|---|
| `expected` | listed in `links/domains-allowed.csv` |
| `new` | not listed yet, needs review |
| `authenticated` | needs a login, so checks are skipped (Google Docs and Drive, SharePoint, Mural) |

`links/domains-allowed.csv` is owned by the content owners in `CODEOWNERS`. A new domain is a conscious, reviewed addition. This also shows who we depend on for content: third-party sites, shorteners and so on.

### 4. Check (networked, in `tools/check_links.py`)

State is kept in `links/status.csv`: `url,last_checked,status,last_ok,failures`.

Which URLs to check on each run:

- **Pull requests:** only new URLs from step 2. Usually none to a few.
- **Weekly scheduled run:** URLs never checked, then those not checked for 28 days, oldest first, capped at about 100 a run. All 500 are covered each month at about 100 requests a week.

Rules:

- Skip `authenticated` domains and `mailto:`. Report them as "not checked".
- Internal paths are already covered by `make check-content`.
- Follow up to 3 redirects. Record a permanent redirect (301 or 308) to a different URL as `moved`, with the new target, so it can be fixed.
- Treat 403, 429 and 5xx as `unclear`, not broken. Retry on the next run. Flag as broken only after 3 consecutive failures over at least 2 weeks, or a 404 or 410 twice.
- Timeouts of 10 seconds. Back off on 429, honouring `Retry-After`.

### 5. Reporting

- **Pull request:** a single comment listing new URLs, new domains and any new broken or moved links, using `gh`.
- **Weekly run:** open or update one GitHub issue, "Outbound link report", with broken links grouped by domain and by source page, and moved links with their suggested replacement. Close it when it is empty.
- The weekly run commits the updated `links/status.csv` to a `link-status` branch. It does not touch `main`, so content editors are not interrupted.

## CI

| Trigger | Runs | Network |
|---|---|---|
| Every push or pull request | extract, diff, domain report (`make links-report`) | none |
| Pull request that changes `content/` | check new URLs only, comment | a few requests |
| Weekly (cron) | check the stale batch, update the issue | about 100 requests |

The workflow has `contents: read` and `issues: write` only.

## Tests

- Extraction finds links in the body and in front matter.
- Domain classification and the allow-list.
- Status rules (404 versus 403, retry counts, redirects) against a fake HTTP server on `localhost`.
- Selection logic: new first, then stale, capped.

## Steps

Each step is one commit.

1. `application/links.py` and tests. Generate `links/links.csv`.
2. Domain report and the allow-list, seeded from today's 75 domains. Review the list for anything surprising.
3. `tools/check_links.py` with state, selection and status rules, plus tests.
4. Make targets (`links-report`, `check-links`) and CI workflow (pull request and weekly).
5. Pull request comment and the weekly issue.
6. Document in the README. Fix any broken links found by the first run.

## Open questions

1. **Authenticated domains.** Roughly 90 links go to Google Docs and Drive. They cannot be checked without a login. Accept that, or periodically check them by hand?
2. **Where to keep state.** A `link-status` branch, a committed `links/status.csv` on `main`, or the CI cache? The branch avoids noise on `main`, the cache is simplest but can expire.
3. **Cadence and cap.** Weekly with about 100 links is the proposal. Is monthly enough?
4. **Self-links.** There are 16 links to `design.planning.data.gov.uk` in content. Rewrite them as relative paths, which are cheaper and covered by `check-content`.
5. **Archive.** Should broken links be offered an Internet Archive snapshot as a replacement?
6. **Third-party dependency policy.** What should happen when a new domain appears: just review, or an owner sign-off?
