# Paths

## Current routes

The site is read-only. Every route is `GET` (and `HEAD`, `OPTIONS`).

| Path | Behaviour |
|---|---|
| `/` and `/<path>` | A page from `content/`, a redirect from `redirects/*.csv`, or 404 |
| `/consideration/planning-considerations.csv` | CSV generated from the consideration files at start-up |
| `/static/<path>` | Static files |

## Old paths (regression list)

Paths from the database-backed site, kept as a regression list. `tests/test_security.py` requests each one and expects a 200, a redirect, a 404 or a 410, never an error. Routes marked * needed login and are now 404 or redirect to the consideration page.

## Public pages (`main`)

| Path | Purpose |
|---|---|
| `/` | Home (also `tags` and `planning_consideration` register `/` under their prefixes) |
| `/cookies` | Cookies |
| `/advisory-group` | Advisory group |
| `/advisory-group/members` | Members |
| `/advisory-group/timeline` | Timeline |
| `/what-we-are-working-on` | Current work |
| `/planning-consideration[/<subpath>]` | Planning consideration pages |
| `/stage-count` | Considerations per stage |
| `/progress-report` | Progress report |
| `/performance` | Performance |
| `/get-involved-in-designing-data` | Get involved |
| `/community` | Community |
| `/tags/glossary` | Glossary of tags |
| `/<page>` | Markdown page from `application/templates/pages/<page>.md` (404 if missing) |

## Project (`project`)

| Path | Purpose |
|---|---|
| `/project` | Projects |
| `/project/planning-applications` | Planning applications project |
| `/project/planning-applications/members` | Members |
| `/project/planning-applications/roadmap` | Roadmap |
| `/project/planning-applications/weeknotes` | Weeknotes |

## Help (`help`, prefix `/help`)

| Path | Purpose |
|---|---|
| `/help/os-declaration-options` | Ordnance Survey declaration options |

## Auth (`auth`, prefix `/auth`)

| Path | Purpose |
|---|---|
| `/auth/login` | Log in (GitHub OAuth) |
| `/auth/authorize` | OAuth callback |
| `/auth/logout` | Log out |

## Considerations (`planning_consideration`, prefix `/consideration`)

| Path | Purpose |
|---|---|
| `/consideration/` | List |
| `/consideration/planning-considerations.csv` | CSV export |
| `/consideration/<slug>` | Detail |
| `/consideration/add` * | Add |
| `/consideration/<slug>/edit` * | Edit |
| `/consideration/<slug>/delete` * | Delete |
| `/consideration/<slug>/edit-specification` * | Edit specification |
| `/consideration/<slug>/add-schema` * | Add schema |
| `/consideration/<slug>/<attr_name>/<link_text>/delete` * | Delete link |
| `/consideration/<slug>/edit-estimated-size` * | Edit estimated size |
| `/consideration/<slug>/add-synonym` * | Add synonym |
| `/consideration/<slug>/synonym/<synonym>/delete` * | Delete synonym |
| `/consideration/<slug>/prioritised` * | Set prioritised |
| `/consideration/<slug>/public` * | Set public |
| `/consideration/<slug>/stage` | Stage |
| `/consideration/<slug>/stage/change` * | Change stage |
| `/consideration/<slug>/os-declaration` * | OS declaration |
| `/consideration/<slug>/edit-frequency` * | Edit frequency |
| `/consideration/<slug>/add-useful-link` * | Add useful link |
| `/consideration/<slug>/edit-legislation` * | Edit legislation |
| `/consideration/<slug>/note` * | Add note |
| `/consideration/<slug>/note/<note_id>` * | Edit note |
| `/consideration/<slug>/block` * | Block |
| `/consideration/<slug>/change-log` | Change log |

## Questions (`questions`, prefix `/consideration/<consideration_slug>/<stage>`)

| Path | Purpose |
|---|---|
| `…/<question_slug>/add-to-list` * | Add answer to list |
| `…/<question_slug>/delete-from-list/<position>` * | Delete answer from list |
| `…/<question_slug>/edit-answer/<position>` * | Edit answer |

## Tags admin (`tags`, prefix `/admin`)

| Path | Purpose |
|---|---|
| `/admin/tags`, `/admin/` | Tags list |
| `/admin/tags/add` * | Add tag |
| `/admin/tags/add-ajax` * | Add tag (AJAX, POST) |
| `/admin/<tag_id>/edit` * | Edit tag |
| `/admin/<consideration>/add` * | Add tag to consideration |
