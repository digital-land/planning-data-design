from flask import url_for
from playwright.sync_api import expect


def test_visit_main_pages(live_server, page):
    page.goto(url_for("main.index", _external=True))
    page.get_by_role("link", name="Design process").click()
    expect(page.locator("h1")).to_contain_text("Data design process")


def test_add_and_update_planning_consideration(live_server, page):
    page.goto(url_for("planning_consideration.considerations", _external=True))
    page.get_by_role("link", name="+Add planning consideration").click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").fill("This is a test consideration")
    page.get_by_label("Github discussion number").click()
    page.get_by_label("Github discussion number").fill("22")
    page.get_by_label("Description").click()
    page.get_by_label("Description").fill("This is the description")
    page.get_by_role("button", name="Create").click()
    expect(
        page.locator("#details").get_by_text("This is a test consideration")
    ).to_be_visible()
    expect(page.get_by_text("This is the description")).to_be_visible()
    expect(page.get_by_role("link", name="22")).to_be_visible()

    page.locator("#details").get_by_role(
        "link", name="Change planning consideration name"
    ).click()
    page.get_by_label("Name").click()
    page.get_by_label("Name").fill("This is a test consideration that is being updated")
    page.get_by_role("button", name="Save changes").click()
    expect(
        page.locator("#details").get_by_text("This is a test consideration")
    ).to_be_visible()

    page.locator("#details").get_by_text("This is a test consideration").click()
    page.get_by_role("link", name="Change planning consideration description").click()
    page.get_by_label("Description").click()
    page.get_by_label("Description").fill(
        "This is the description that has been updated"
    )
    page.get_by_role("button", name="Save changes").click()
    expect(page.get_by_text("This is the description that")).to_be_visible()

    page.get_by_role("link", name="Add link to applicable schemas").click()
    page.get_by_label("Dataset schema URL").click()
    page.get_by_label("Dataset schema URL").fill(
        "https://github.com/digital-land/specification/blob/main/content/dataset/ancient-woodland.md"
    )
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_role("link", name="ancient-woodland")).to_be_visible()
    assert (
        page.get_by_role("link", name="ancient-woodland").get_attribute("href")
        == "https://github.com/digital-land/specification/blob/main/content/dataset/ancient-woodland.md"
    )
    expect(page.get_by_role("link", name="Remove")).to_be_visible()

    # need to add tests to handle different states of specification row

    # page.get_by_role("link", name="Remove").click()
    # expect(
    #     page.locator("#data-related dl div")
    #     .filter(has_text="Schemas Add link to")
    #     .get_by_role("definition")
    #     .first
    # ).to_be_visible()

    page.get_by_role("link", name="Change expected number of").click()
    page.get_by_label("Expected number of records").click()
    page.get_by_label("Expected number of records").fill("10000")
    page.get_by_role("button", name="Save changes").click()
    expect(page.get_by_text("10,000")).to_be_visible()
    page.get_by_role("link", name="Change frequency of updates").click()
    page.get_by_label("Annually").check()
    page.get_by_role("button", name="Save").click()
    expect(page.locator("#data-related")).to_contain_text("Annually")
    page.get_by_role("link", name="Change frequency of updates").click()
    page.get_by_label("Daily").check()
    page.get_by_role("button", name="Save").click()
    expect(page.locator("#data-related")).to_contain_text("Daily")

    page.get_by_role("link", name="Change planning consideration stage").click()
    page.get_by_label("Research").check()
    page.get_by_role("button", name="Update").click()
    expect(page.locator("#details")).to_contain_text("Research")
    page.locator("dd").filter(
        has_text="Change planning consideration prioritisation"
    ).get_by_role("link").click()
    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Set prioritisation").click()
    expect(page.locator("#details")).to_contain_text("True")
    page.locator("dd").filter(
        has_text="Change planning consideration public status"
    ).get_by_role("link").click()
    page.get_by_label("No").check()
    page.get_by_role("button", name="Set").click()
    expect(page.locator("#details")).to_contain_text("False")
    page.locator("dd").filter(
        has_text="Change planning consideration public status"
    ).get_by_role("link").click()
    page.get_by_label("Yes").check()
    page.get_by_role("button", name="Set").click()
    expect(page.locator("#details")).to_contain_text("True")

    page.get_by_role("link", name="+Add note").click()
    page.get_by_label("Note").click()
    page.get_by_label("Note").fill(
        "This is a test of a note that should appear on the page."
    )
    page.get_by_role("button", name="Save note").click()
    expect(page.locator("#notes")).to_contain_text(
        "This is a test of a note that should appear on the page."
    )


def test_add_answer_backlog_questions(live_server, page, questions):

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
