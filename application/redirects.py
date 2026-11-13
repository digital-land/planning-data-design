"""Load and validate redirect rules from redirects/*.csv.

Three kinds of file, told apart by their header:

    from,to,status                    exact path to path (or to nothing for 410)
    from_prefix,to_prefix,status      prefix to prefix, query string kept
    section,status                    pages below <section>/<slug>/ go to <section>/<slug>
"""

import csv
from pathlib import Path

PAGE_STATUSES = {301, 302, 307, 308, 410}
GONE = 410
HEADERS = {
    ("from", "to", "status"): "pages",
    ("from_prefix", "to_prefix", "status"): "prefixes",
    ("section", "status"): "sections",
}


class RedirectError(Exception):
    pass


def _check_path(where, value):
    if not value.startswith("/") or value.startswith("//") or "\\" in value:
        raise RedirectError(f"{where}: {value!r} must be a path starting with /")


def _status(where, value):
    try:
        status = int(value)
    except ValueError:
        raise RedirectError(f"{where}: invalid status {value!r}")
    if status not in PAGE_STATUSES:
        raise RedirectError(f"{where}: status {status} not allowed")
    return status


def _under(path, prefix):
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


def _join(target, rest):
    """target + the rest of the request path, or None if rest could change
    where the redirect goes. Without this a to_prefix of "/" turns
    /old//evil.example into //evil.example, a redirect to another site."""
    if "//" in rest or "\\" in rest or {".", ".."} & set(rest.split("/")):
        return None
    return (target.rstrip("/") + rest) or "/"


class Redirects:
    def __init__(self):
        self.pages = {}
        self.prefixes = []
        self.sections = []

    @classmethod
    def load(cls, directory):
        self = cls()
        for file in sorted(Path(directory).glob("*.csv")):
            with open(file, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                kind = HEADERS.get(tuple(reader.fieldnames or ()))
                if kind is None:
                    raise RedirectError(f"{file}: unrecognised header")
                for n, row in enumerate(reader, start=2):
                    getattr(self, "_add_" + kind)(f"{file}:{n}", row)
        self.prefixes.sort(key=lambda r: -len(r[0]))
        return self

    def _add_pages(self, where, row):
        source, target = row["from"], row["to"]
        _check_path(where, source)
        status = _status(where, row["status"])
        if source in self.pages:
            raise RedirectError(f"{where}: duplicate from {source}")
        if status == GONE:
            if target:
                raise RedirectError(f"{where}: 410 must not have a destination")
        else:
            _check_path(where, target)
        self.pages[source] = (target, status)

    def _add_prefixes(self, where, row):
        source, target = row["from_prefix"], row["to_prefix"]
        _check_path(where, source)
        _check_path(where, target)
        self.prefixes.append((source, target, _status(where, row["status"])))

    def _add_sections(self, where, row):
        _check_path(where, row["section"])
        self.sections.append((row["section"], _status(where, row["status"])))

    def validate(self, pages, extra_paths=()):
        """Every redirect must land on content in one hop, with no loops."""
        known = set(pages) | set(extra_paths)
        for source, (target, status) in self.pages.items():
            if source in known:
                raise RedirectError(f"{source} is both content and a redirect")
            if status == GONE:
                continue
            if target in self.pages:
                raise RedirectError(f"{source}: chain, {target} is also a redirect")
            if target not in known:
                raise RedirectError(f"{source}: {target} is not a page")
        for source, target, _ in self.prefixes:
            if source in known:
                raise RedirectError(f"{source} is both content and a redirect")
            if not any(_under(p, target) for p in known):
                raise RedirectError(f"{source}: nothing exists under {target}")
        for section, _ in self.sections:
            if not any(_under(p, section) for p in known):
                raise RedirectError(f"nothing exists under {section}")

    def resolve(self, path, query, pages):
        """Return (location, status) or None. location is None for 410."""
        path = path if path == "/" else path.rstrip("/")
        if path in self.pages:
            target, status = self.pages[path]
            return (target or None), status
        for source, target, status in self.prefixes:
            if _under(path, source):
                location = _join(target, path[len(source.rstrip("/")) :])
                if location is None:
                    return None
                return (location + ("?" + query if query else ""), status)
        for section, status in self.sections:
            parts = path[len(section) :].strip("/").split("/")
            if _under(path, section) and len(parts) > 1:
                parent = f"{section}/{parts[0]}"
                if parent in pages:
                    return parent, status
        return None
