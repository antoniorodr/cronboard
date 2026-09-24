from cronboard.services.search_service import SearchService


async def test_find_matches() -> None:
    rows_data = [
        ["ID", "Expression", "Command", "Log Enabled", "Notifications Enabled"],
        ["1", "* * * * *", "echo hello", "True", "True"],
        ["2", "* * * * *", "echo foo", "True", "True"],
        ["3", "* * * * *", "echo foo", "True", "True"],
        ["4", "* * * * *", "echo bar", "True", "True"],
    ]
    query = "foo"
    matches = SearchService.find_matches(rows_data, query)
    assert matches == [2, 3]


async def test_highlight_text() -> None:
    text = "foo bar baz"
    query = "bar"
    highlighted_text = SearchService.highlight_text(text, query)
    assert "foo bar baz" in highlighted_text
