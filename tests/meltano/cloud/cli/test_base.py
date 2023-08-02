"""Test common cloud CLI functionality."""

from __future__ import annotations

import pytest

from meltano.cloud.cli.base import get_paginated
from meltano.core.utils import run_async


@pytest.mark.parametrize(
    ("max_items", "limit", "max_page_size"),
    (
        # Case: Page size, limit, and number of items all equal
        (10, 10, 10),
        # Case: Limit less than number of items, equal to page size
        (11, 10, 10),
        # Case: Limit greater than number of items
        (5, 6, 10),
        # Case: Limit less than number of items
        (5, 4, 10),
        # Case: Limit greater than number of items, multi-page
        (15, 16, 10),
        # Case: Limit less than number of items, multi-page
        (15, 14, 10),
    ),
)
def test_get_paginated(max_items: int, limit: int, max_page_size: int):
    async def paged_func(page_size: int, page_token: str, max_items: int):
        if not page_token:
            return {
                "results": list(range(min(page_size, max_items))),
                "pagination": {"next_page_token": str(page_size)}
                if max_items > page_size
                else None,
            }
        return {
            "results": list(
                range(int(page_token), min(int(page_token) + page_size, max_items)),
            ),
            "pagination": None,
        }

    results = run_async(get_paginated)(
        lambda page_size, page_token: paged_func(
            page_size,
            page_token,
            max_items=max_items,
        ),
        limit=limit,
        max_page_size=max_page_size,
    )
    assert results.items == list(range(min(limit, max_items)))
    assert results.truncated == (limit < max_items)
