"""Validate content and redirects: python -m application.check"""

import re
import sys
from urllib.parse import unquote, urlparse

from application import ROOT, create_app
from application.content import load_content
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
    for problem in problems:
        print(problem)
    print(f"{len(pages)} pages checked, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
