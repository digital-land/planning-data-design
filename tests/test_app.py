from flask import url_for
from playwright.sync_api import expect


def test_add_consideration(live_server, page, questions):

    page.goto(url_for("planning_consideration.considerations", _external=True))
    page.get_by_role("link", name="+Add planning consideration").click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").fill("Test consideration")
    page.get_by_label("Description").click()
    page.get_by_label("Description").fill(
        "This is a test of a public planning consideration"
    )
    page.get_by_role("button", name="Create").click()

    expect(page.locator("#details").get_by_text("Test consideration")).to_be_visible()
    expect(page.get_by_text("This is a test of a public")).to_be_visible()
    expect(page.get_by_role("link", name="Backlog")).to_be_visible()
    expect(page.get_by_role("link", name="Screen")).to_be_visible()
    expect(page.get_by_role("link", name="Research")).to_be_visible()

    page.get_by_role("link", name="Backlog").click()
    page.get_by_role("link", name="Answer all").click()
    expect(page.get_by_role("heading", name="Who asked for 'Test")).to_be_visible()
    page.locator("#input").click()
    page.locator("#input").fill("Someone")
    page.get_by_role("button", name="Save and continue").click()

    expect(
        page.get_by_role("heading", name="What is the driver for the")
    ).to_be_visible()
    page.get_by_label("National policy change").check()
    page.get_by_role("button", name="Save and continue").click()

    expect(
        page.get_by_role("heading", name="Which 2024 focus area does")
    ).to_be_visible()
    page.get_by_label("Modern planning software").check()
    page.get_by_role("button", name="Save and continue").click()
    expect(page.get_by_text("Someone")).to_be_visible()
    expect(page.get_by_text("National policy change")).to_be_visible()
    expect(page.get_by_text("Modern planning software")).to_be_visible()
    page.get_by_role("link", name="Go back to Test consideration summary").click()
