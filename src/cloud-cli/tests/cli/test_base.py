"""Test common cloud CLI functionality."""

from __future__ import annotations

from meltano.cloud.cli.base import LimitedResult, get_paginated, run_async


def test_get_paginated():
    async def paged_func(page_size: int, page_token: str, max_items: int):
        print(f"Ran with page_size={page_size}, page_token={page_token}")
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

    def test_case(max_items: int, limit: int, max_page_size: int) -> LimitedResult[int]:
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

        return results

    # Case: Page size, limit, and number of items all equal
    test_case(max_items=10, limit=10, max_page_size=10)

    # Case: Limit less than number of items, equal to page size
    test_case(max_items=11, limit=10, max_page_size=10)

    # Case: Limit greater than number of items
    test_case(max_items=5, limit=6, max_page_size=10)

    # Case: Limit less than number of items
    test_case(max_items=5, limit=4, max_page_size=10)

    # Case: Limit greater than number of items, multi-page
    test_case(max_items=15, limit=16, max_page_size=10)

    # Case: Limit less than number of items, multi-page
    test_case(max_items=15, limit=14, max_page_size=10)
