"""Services for logging into managed Meltano."""
from __future__ import annotations

import json

import requests


class LoginService:
    """Common code for login providers."""

    def __init__(self) -> None:
        """Make a new login service."""
        pass


class GithubLoginService(LoginService):
    """Login service using Github Device Flow Auth.

    See: https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow
    """

    def __init__(self) -> None:
        """Make a new github login service."""
        super().__init__()
        self.code_url = "https://github.com/login/device/code"

    def request_codes(self) -> json:
        """Request a user auth code from the github API.

        Returns:
            A json object with user auth code and details
        """
        resp = requests.post(
            self.code_url,
            params={"client_id": "Iv1.93c2c054fa168eb2"},
            headers={"Accept": "application/json"},
        )
        return resp.json()
