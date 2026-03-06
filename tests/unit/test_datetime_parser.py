"""Tests for src.utils.datetime_parser — pure string transformation logic."""

import pytest

from src.utils.datetime_parser import format_datetime, _ensure_iso


class TestEnsureIso:
    """Tests for the _ensure_iso helper."""

    def test_bare_date_gets_midnight(self):
        assert _ensure_iso("2024-02-01") == "2024-02-01T00:00:00Z"

    def test_already_has_time_component(self):
        assert _ensure_iso("2024-02-01T12:00:00Z") == "2024-02-01T12:00:00Z"

    def test_strips_whitespace(self):
        assert _ensure_iso("  2024-02-01  ") == "2024-02-01T00:00:00Z"

    def test_non_date_string_returned_as_is(self):
        assert _ensure_iso("..") == ".."

    def test_empty_string_returned_as_is(self):
        assert _ensure_iso("") == ""


class TestFormatDatetime:
    """Tests for the main format_datetime function."""

    def test_single_bare_date(self):
        assert format_datetime("2024-01-15") == "2024-01-15T00:00:00Z"

    def test_single_date_with_time(self):
        assert format_datetime("2024-01-15T10:30:00Z") == "2024-01-15T10:30:00Z"

    def test_range_bare_dates(self):
        result = format_datetime("2024-02-01/2024-02-28")
        assert result == "2024-02-01T00:00:00Z/2024-02-28T23:59:59Z"

    def test_range_start_with_time_end_bare(self):
        result = format_datetime("2024-02-01T00:00:00Z/2024-02-28")
        assert result == "2024-02-01T00:00:00Z/2024-02-28T23:59:59Z"

    def test_range_both_have_time(self):
        result = format_datetime("2024-02-01T00:00:00Z/2024-02-28T23:59:59Z")
        assert result == "2024-02-01T00:00:00Z/2024-02-28T23:59:59Z"

    def test_range_with_spaces(self):
        result = format_datetime("2024-02-01 / 2024-02-28")
        assert result == "2024-02-01T00:00:00Z/2024-02-28T23:59:59Z"

    def test_range_end_gets_end_of_day(self):
        """End of range should get 23:59:59, not 00:00:00."""
        result = format_datetime("2024-01-01/2024-12-31")
        start, end = result.split("/")
        assert start.endswith("T00:00:00Z")
        assert end.endswith("T23:59:59Z")

    def test_range_start_bare_end_with_time(self):
        result = format_datetime("2024-02-01/2024-02-28T12:00:00Z")
        assert result == "2024-02-01T00:00:00Z/2024-02-28T12:00:00Z"
