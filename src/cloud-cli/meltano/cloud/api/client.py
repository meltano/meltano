"""Meltano Cloud service client."""

from __future__ import annotations

import sys

if sys.version_info <= (3, 8):
    from cached_property import cached_property
else:
    from functools import cached_property

import typing as t
from contextlib import contextmanager

import requests

from meltano.cloud.api.auth import MeltanoCloudAuth
from meltano.cloud.api.config import MeltanoCloudConfig


class MeltanoCloudClient:
    """Client for interacting with Meltano Cloud API."""

    def __init__(self):
        """Initialize the MeltanoCloudClient."""
        self.config = MeltanoCloudConfig.find()
        self.auth = MeltanoCloudAuth()
        self.base_url = self.config.base_url

    @cached_property
    def session(self) -> requests.Session:
        """Return a session for use in making requests.

        Returns:
            A requests.Session
        """
        return requests.Session()

    @contextmanager
    def authenticated(self) -> t.Iterator[None]:
        """Provide context for API calls which require authentication.

        Yields:
            None
        """
        if not self.auth.logged_in():
            self.auth.login()
        self.session.headers.update(self.auth.get_auth_header())
        yield
