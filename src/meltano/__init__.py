"""Meltano."""


from __future__ import annotations

# Managed by commitizen
__version__ = "2.20.0"

import asyncio
import platform

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy(),  # type: ignore[attr-defined]
    )
