"""Safe Markdown rendering. The only module that may mark HTML as safe."""

import html
import re
from urllib.parse import urlparse

from markupsafe import Markup

import markdown
from markdown.treeprocessors import Treeprocessor

SAFE_SCHEMES = {"", "http", "https", "mailto"}

CLASSES = {
    "p": "govuk-body",
    "h1": "govuk-heading-xl",
    "h2": "govuk-heading-l",
    "h3": "govuk-heading-m",
    "h4": "govuk-heading-s",
    "h5": "govuk-heading-s",
    "ul": "govuk-list govuk-list--bullet",
    "ol": "govuk-list govuk-list--number",
    "a": "govuk-link",
    "hr": "govuk-section-break govuk-section-break--l",
    "code": "app-code",
    "table": "govuk-table",
    "thead": "govuk-table__head",
    "tbody": "govuk-table__body",
    "tr": "govuk-table__row",
    "th": "govuk-table__header",
    "td": "govuk-table__cell",
    "blockquote": "govuk-inset-text",
}


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


C0_AND_SPACE = "".join(chr(i) for i in range(0x21))


def browser_url(url):
    """The URL a browser would see: the serializer keeps character references
    such as &#58; in attributes, and browsers decode them and drop tab/CR/LF
    and leading/trailing control characters before parsing. Use it to check
    URLs; never write the decoded value back into the attribute."""
    return re.sub(r"[\t\n\r]", "", html.unescape(url)).strip(C0_AND_SPACE)


def is_safe_url(url):
    url = browser_url(url)
    if url.startswith(("//", "\\\\", "/\\", "\\/")):
        return False
    return urlparse(url).scheme.lower() in SAFE_SCHEMES


class GovukTreeprocessor(Treeprocessor):
    def run(self, root):
        # backslash escapes are still placeholders here; check the final text
        unescape = self.md.treeprocessors["unescape"].unescape
        for el in root.iter():
            if el.tag in CLASSES:
                el.set("class", CLASSES[el.tag])
            if el.tag in ("h1", "h2", "h3", "h4", "h5"):
                el.set("id", slugify("".join(el.itertext())))
            if el.tag == "a" and not is_safe_url(unescape(el.get("href", ""))):
                del el.attrib["href"]
            if el.tag == "img" and not is_safe_url(unescape(el.get("src", ""))):
                del el.attrib["src"]


class GovukExtension(markdown.Extension):
    def extendMarkdown(self, md):
        # raw HTML in Markdown is escaped, not passed through
        md.preprocessors.deregister("html_block")
        md.inlinePatterns.deregister("html")
        md.treeprocessors.register(GovukTreeprocessor(md), "govuk", 5)


def render(text):
    """Render Markdown to HTML, escaping any raw HTML."""
    md = markdown.Markdown(extensions=["tables", GovukExtension()])
    # the one sanctioned use: raw HTML is escaped above and unsafe URLs are dropped
    return Markup(md.convert(text or ""))  # nosec B704
