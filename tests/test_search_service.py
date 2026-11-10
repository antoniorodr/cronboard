"""Unit tests for SearchService.find_matches."""

from cronboard.services.search_service import SearchService

ROWS = [
    ("backup_job", "* * * * *", "echo hi", "x", "y", "z", "w", "Active"),
    ("deploy_job", "0 * * * *", "echo bye", "x", "y", "z", "w", "Paused"),
]


def test_find_matches_lowercase_query():
    assert SearchService.find_matches(ROWS, "backup") == [0]


def test_find_matches_mixed_case_query():
    """Search must be case-insensitive: the service lowercases the
    haystack, so it must lowercase the query too instead of relying on
    every caller to do it first."""
    assert SearchService.find_matches(ROWS, "Backup") == [0]
    assert SearchService.find_matches(ROWS, "BACKUP_JOB") == [0]


def test_find_matches_no_match():
    assert SearchService.find_matches(ROWS, "nope") == []
