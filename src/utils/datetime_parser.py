"""
Function tool for the geocoding agent to format datetime strings
into full ISO 8601 with T separators required by the GeoCatalog STAC API.
"""

import re
from typing import Annotated

from pydantic import Field


_ISO_DATETIME = re.compile(r"\d{4}-\d{2}-\d{2}T")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _ensure_iso(date_str: str) -> str:
    """Add T00:00:00Z or T23:59:59Z to a bare YYYY-MM-DD date."""
    date_str = date_str.strip()
    if _ISO_DATETIME.match(date_str):
        return date_str  # already has T component
    if _ISO_DATE.match(date_str):
        return f"{date_str}T00:00:00Z"
    return date_str


def format_datetime(
    datetime_str: Annotated[
        str,
        Field(description="Datetime string or range resolved by the LLM, e.g. '2024-02-01/2024-02-28' or '2024-01-15'"),
    ],
) -> str:
    """
    Format a datetime string into full ISO 8601 with T separators.

    Takes the LLM-resolved datetime (e.g. '2024-02-01/2024-02-28')
    and ensures each part has the required T time component.

    Examples:
        '2024-02-01/2024-02-28' → '2024-02-01T00:00:00Z/2024-02-28T23:59:59Z'
        '2024-01-15' → '2024-01-15T00:00:00Z'
        '2024-02-01T00:00:00Z/2024-02-28T23:59:59Z' → unchanged

    Returns:
        ISO 8601 datetime string with T separators.
    """
    if "/" in datetime_str:
        parts = datetime_str.split("/", 1)
        start = _ensure_iso(parts[0])
        end = parts[1].strip()
        # For the end of a range, use end-of-day if no time component
        if _ISO_DATE.match(end) and not _ISO_DATETIME.match(end):
            end = f"{end}T23:59:59Z"
        else:
            end = _ensure_iso(end)
        return f"{start}/{end}"

    return _ensure_iso(datetime_str)
