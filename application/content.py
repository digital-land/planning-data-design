"""Load and validate content at start-up. A request never touches the filesystem."""

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import frontmatter

from application.markdown import is_safe_url, render

STEM = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TEMPLATES = {"page", "home", "consideration", "consideration-list"}
BASE_KEYS = {"title", "description", "template"}
CONSIDERATION_KEYS = {
    "stage",
    "datasets",
    "frequency_of_updates",
    "legislation",
    "specification",
    "useful_links",
    "synonyms",
    "tags",
    "github_discussion_number",
    "created",
    "updated",
}


class ContentError(Exception):
    pass


@dataclass
class Page:
    path: str
    title: str
    description: str
    template: str
    html: str
    meta: dict = field(default_factory=dict)
    source: str = ""

    @property
    def slug(self):
        return self.path.rstrip("/").rsplit("/", 1)[-1]


def _str_list(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _link(value):
    return (
        isinstance(value, dict)
        and set(value) == {"text", "url"}
        and all(isinstance(v, str) and v for v in value.values())
        and is_safe_url(value["url"])
    )


def _links(value):
    return isinstance(value, list) and all(_link(v) for v in value)


CHECKS = {
    "stage": lambda v: isinstance(v, str),
    "datasets": _str_list,
    "frequency_of_updates": lambda v: isinstance(v, str),
    "legislation": _link,
    "specification": _link,
    "useful_links": _links,
    "synonyms": _str_list,
    "tags": _str_list,
    "github_discussion_number": lambda v: isinstance(v, int),
    "created": lambda v: isinstance(v, date),
    "updated": lambda v: isinstance(v, date),
}


def url_path(root, file):
    parts = list(file.relative_to(root).with_suffix("").parts)
    if parts[-1] == "index":
        parts.pop()
    for part in parts:
        if not STEM.match(part):
            raise ContentError(f"{file}: invalid file or directory name {part!r}")
    return "/" + "/".join(parts)


def parse(root, file):
    path = url_path(root, file)
    post = frontmatter.load(file)
    meta = dict(post.metadata)
    template = meta.get("template", "page")
    if template not in TEMPLATES:
        raise ContentError(f"{file}: unknown template {template!r}")
    allowed = BASE_KEYS | (CONSIDERATION_KEYS if template == "consideration" else set())
    unknown = set(meta) - allowed
    if unknown:
        raise ContentError(f"{file}: unknown front matter {sorted(unknown)}")
    for key in ("title", "description"):
        if not isinstance(meta.get(key), str) or not meta[key].strip():
            raise ContentError(f"{file}: {key} is required")
    for key, check in CHECKS.items():
        if key in meta and not check(meta[key]):
            raise ContentError(f"{file}: invalid value for {key}")
    extra = {k: v for k, v in meta.items() if k not in BASE_KEYS}
    return Page(
        path=path,
        title=meta["title"],
        description=meta["description"],
        template=template,
        html=render(post.content),
        meta=extra,
        source=str(file),
    )


def load_content(root):
    """Return {url path: Page}. Raises ContentError on any problem."""
    root = Path(root)
    pages = {}
    for file in sorted(root.rglob("*.md")):
        page = parse(root, file)
        if page.path in pages:
            raise ContentError(f"{file}: duplicate path {page.path}")
        pages[page.path] = page
    if "/" not in pages:
        raise ContentError("content/index.md is required")
    return pages


def breadcrumbs(pages, path):
    """Ancestors of path that exist as pages, as (title, href), excluding the home page."""
    crumbs = []
    parts = path.strip("/").split("/")[:-1]
    for i in range(1, len(parts) + 1):
        ancestor = "/" + "/".join(parts[:i])
        if ancestor in pages:
            crumbs.append((pages[ancestor].title, ancestor))
    return crumbs
