"""Browser checks for selectable data tables; run pytest with --integration."""

import os

import pytest
from rotunda.agent.dom_serializer import DOMSerializer
from rotunda.sync_api import NewContext, Rotunda


@pytest.mark.integration
def test_data_tables_are_selectable_without_layout_containers(
    request: pytest.FixtureRequest,
) -> None:
    """Expose whole data regions with real bounds while preserving layout links."""
    if not request.config.getoption("--integration"):
        pytest.skip("Pass --integration to run the real-browser table check.")

    # Mix explicit semantics with unmarked grids and common layout patterns;
    # nested headers must not promote their surrounding layout table.
    rows = "".join(
        f"<tr><td>September {day}</td><td>Sold</td></tr>" for day in (7, 14, 21)
    )
    html = f"""
        <table id="schedule"><caption>Schedule:</caption>{rows}</table>
        <table id="headers"><tr><th>Month</th><th>Total</th></tr>
            <tr><td>September</td><td>10</td></tr></table>
        <table id="scoped"><tr><td scope="row">September</td><td>10</td></tr></table>
        <table id="declared" role="table"><tr><td>September</td><td>10</td></tr></table>
        <table id="unmarked">{rows}</table>
        <table id="presentation" role="presentation"><caption>Layout</caption>{rows}
            <tr><td><a id="layout-link" href="#">Still clickable</a></td></tr></table>
        <table id="none" role="none"><caption>Layout</caption>{rows}</table>
        <table id="wrapper"><tr><td>Page layout</td><td>
            <table id="nested"><caption>Nested data</caption>{rows}</table>
        </td></tr></table>
        <table id="single"><tr><td>Page content</td></tr></table>
        <table id="short"><tr><td>Left</td><td>Right</td></tr></table>
        <table id="empty"><caption>Empty grid</caption><tr><td></td></tr></table>
        <table id="hidden" hidden><caption>Hidden</caption>{rows}</table>
        <table id="hidden-header"><tr><th hidden>Not visible</th></tr>
            <tr><td>Left</td><td>Right</td></tr></table>
        <table id="navigation">{
        "".join(
            '<tr><td><a href="#">Home</a></td><td><a href="#">About</a></td></tr>'
            for _ in range(3)
        )
    }</table>
        <table id="form">{
        "".join("<tr><td>Field</td><td><input></td></tr>" for _ in range(3))
    }</table>
        <table id="cards">{
        "".join(
            "<tr><td><h2>Card</h2>Content</td><td><h2>Card</h2>Content</td></tr>"
            for _ in range(3)
        )
    }</table>
        <table id="prose">{
        "".join(
            f"<tr><td>{'Long prose. ' * 30}</td><td>{'Long prose. ' * 30}</td></tr>"
            for _ in range(3)
        )
    }</table>
    """
    with Rotunda(
        headless=True, executable_path=os.environ.get("ROTUNDA_EXECUTABLE_PATH")
    ) as browser:
        page = NewContext(browser).new_page()
        page.set_content(html)
        serializer = DOMSerializer(max_items=200, max_text_length=400)
        snapshot = serializer.serialize(page)

        # The emitted table must resolve to the entire visible region, not a
        # heading or one link inside it. Layout descendants remain actionable.
        tables = {
            item.attributes["id"]: item
            for item in snapshot.items
            if item.tag == "table"
        }
        assert set(tables) == {
            "schedule",
            "headers",
            "scoped",
            "declared",
            "unmarked",
            "nested",
        }
        schedule = tables["schedule"]
        assert schedule.role == "table"
        assert "September 21" in schedule.text
        assert schedule.bounds is not None
        assert schedule.bounds.width > 0 and schedule.bounds.height > 0
        handle = serializer.resolve_locator(page, schedule.ref)
        assert handle.get_attribute("id") == "schedule"
        assert "September 21" in handle.inner_text()
        assert any(
            item.attributes.get("id") == "layout-link" for item in snapshot.items
        )
        assert not any(
            item.tag == "table"
            for item in DOMSerializer(include_content=False).serialize(page).items
        )
