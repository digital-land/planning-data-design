import csv
from flask import url_for
from playwright.sync_api import expect


def test_glossary_page(live_server, page):
    page.goto(url_for("main.glossary_of_tags"))

    expect(page.locator("h1")).to_contain_text("Glossary of tags")
    expect(page.locator("p.govuk-body-l")).to_contain_text(
        "These terms are defined for purpose of grouping related planning considerations. This will help you understand how they relate to planning considerations in the Data design service."
    )
    expect(page.locator("nav[aria-label='Content']")).to_exist()

def test_glossary_tags(live_server, page):
    page.goto(url_for("main.glossary_of_tags"))

    # Check if the glossary tags are present
    tags = csv.DictReader(
        open("data/glossary-of-tags.csv", encoding="utf-8")
    )

    expect(page.locator("nav[aria-label='Content'] a")).to_have_count(len(tags))
    expect(page.locator(".dl-glossary-tag")).to_have_count(len(tags))
    for tag in tags:
        tag_name = tag["name"]
        expect(page.locator(f".dl-glossary-tag#{tag_name} h3")).to_exist()
        expect(page.locator(f".dl-glossary-tag#{tag_name} p")).to_have_text(tag["definition"])
