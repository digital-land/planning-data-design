from bs4 import BeautifulSoup
from markdown import markdown
from markupsafe import Markup
from slugify import slugify


def slugify_filter(s):
    if not isinstance(s, str):
        return s
    return slugify(s)


def deslugify_filter(s):
    if not isinstance(s, str):
        return s
    return s.replace("-", " ").capitalize()


def map_to_tag_class_filter(s):
    stage_to_class = {
        "Backlog": "govuk-tag--grey",
        "On the platform": "govuk-tag--green",
        "Archived": "govuk-tag--orange",
    }
    if s in stage_to_class.keys():
        return stage_to_class[s]
    return "govuk-tag--blue"


def choice_to_list_filter(s):
    return s.split(";")


def render_markdown_filter(text, gov_attributes=True, make_safe=True):
    if text is None:
        return ""
    soup = BeautifulSoup(markdown(text), "html.parser")
    if gov_attributes:
        _add_html_attrs(soup)
    if make_safe:
        return Markup(soup)
    else:
        return soup


def _add_html_attrs(soup):
    for tag in soup.select("p"):
        tag["class"] = "govuk-body"
    for tag in soup.select("h1, h2, h3, h4, h5"):
        # sets the id to a 'slugified' version of the text content
        tag["id"] = slugify(tag.getText())
    for tag in soup.select("h1"):
        tag["class"] = "govuk-heading-xl"
    for tag in soup.select("h2"):
        tag["class"] = "govuk-heading-l"
    for tag in soup.select("h3"):
        tag["class"] = "govuk-heading-m"
    for tag in soup.select("h4"):
        tag["class"] = "govuk-heading-s"
    for tag in soup.select("ul"):
        tag["class"] = "govuk-list govuk-list--bullet"
    for tag in soup.select("a"):
        tag["class"] = "govuk-link"
    for tag in soup.select("ol"):
        tag["class"] = "govuk-list govuk-list--number"
    for tag in soup.select("hr"):
        tag["class"] = "govuk-section-break govuk-section-break--l"
    for tag in soup.select("code"):
        tag["class"] = "app-code"


def short_date_filter(date):
    if date is None:
        return ""
    return date.strftime("%d %B %Y")


def date_time_filter(date):
    if date is None:
        return ""
    return date.strftime("%Y-%m-%d %H:%M:%S")


def date_time_12_hours_filter(date):
    if date is None:
        return ""
    return date.strftime("%Y-%m-%d %I:%M %p")


def start_case_filter(s):
    return s[0].upper() + s[1:] if s else s

