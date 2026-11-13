"""Validate content and redirects: python -m application.check"""

import re
import sys
from urllib.parse import unquote, urlparse

from application import ROOT, create_app
from application.content import load_content
from application.links import (
    LINKS_DIR,
    allowed_domains,
    extract,
)
from application.links import problems as domain_problems
from application.links import (
    read_csv,
    stale,
)
from application.redirects import Redirects
from application.routes import GENERATED_PATHS

HREF = re.compile(r'(?:href|src)="(/[^"]*)"')


def broken_links(pages, redirects, static_dir=ROOT / "application" / "static"):
    problems = []
    for page in pages.values():
        for link in HREF.findall(str(page.html)):
            path = unquote(urlparse(link).path)
            if path.startswith("/static/"):
                if not (static_dir / path[len("/static/") :]).is_file():
                    problems.append(f"{page.source}: missing file {path}")
            elif (
                (path.rstrip("/") or "/") not in pages
                and not redirects.resolve(path, "", pages)
                and path not in GENERATED_PATHS
            ):
                problems.append(f"{page.source}: broken link {path}")
    return problems


def main():
    create_app()  # raises on bad front matter, bad redirects
    pages = load_content(ROOT / "content")
    problems = broken_links(pages, Redirects.load(ROOT / "redirects"))
    found = extract(pages)
    links = ROOT / LINKS_DIR
    allowed = allowed_domains(read_csv(links / "domain.csv"))
    problems_ = problems + domain_problems(found, allowed) + stale(found, links)
    for problem in problems_:
        print(problem)
    print(
        f"{len(pages)} pages and {len(found)} links checked, {len(problems_)} problems"
    )
    return 1 if problems_ else 0


if __name__ == "__main__":
    sys.exit(main())
