from __future__ import annotations

import json
import logging
import os
from collections import Counter
from copy import deepcopy
from http import HTTPStatus
from typing import Any, Mapping

import pytest
import requests
from requests.adapters import BaseAdapter

from meltano.core.hub.client import MeltanoHubService
from meltano.core.plugin.base import PluginType

logging.basicConfig(level=logging.INFO)

PYTEST_BACKEND = os.getenv("PYTEST_BACKEND", "sqlite")

pytest_plugins = [
    "fixtures.db",
    "fixtures.fs",
    "fixtures.core",
    "fixtures.api",
    "fixtures.cli",
    "fixtures.docker",
]

if PYTEST_BACKEND == "sqlite":
    pytest_plugins.append("fixtures.db.sqlite")
elif PYTEST_BACKEND == "postgresql":
    pytest_plugins.append("fixtures.db.postgresql")
elif PYTEST_BACKEND == "mssql":
    pytest_plugins.append("fixtures.db.mssql")
else:
    raise Exception(f"Unsuported backend: {PYTEST_BACKEND}.")

BACKEND = ["sqlite", "postgresql", "mssql", "mysql"]


def pytest_runtest_setup(item):
    backend_marker = item.get_closest_marker("backend")

    # currently, there is no distinction between the SYSTEM database
    # and the WAREHOUSE database at the test level.
    # There is only one database used for the tests, and it serves
    # both as SYSTEM and WAREHOUSE.
    if backend_marker and backend_marker.args[0] != PYTEST_BACKEND:
        pytest.skip()


@pytest.fixture(scope="session")
def concurrency():
    return {
        "threads": int(os.getenv("PYTEST_CONCURRENCY_THREADS", 8)),
        "processes": int(os.getenv("PYTEST_CONCURRENCY_PROCESSES", 8)),
        "cases": int(os.getenv("PYTEST_CONCURRENCY_CASES", 64)),  # noqa: WPS432
    }


class MockAdapter(BaseAdapter):
    RETURN_500 = {
        "/extractors/this-returns-500--original": {"error": "Server error"},
    }

    def _process_discovery(self, api_url: str, discovery: dict) -> dict:
        hub = {}
        for plugin_type in PluginType:
            index_key = f"/{plugin_type}/index"
            hub[index_key] = {}
            for plugin in discovery.get(plugin_type, []):
                plugin_name = plugin["name"]
                hub[index_key][plugin_name] = {}
                hub[index_key][plugin_name]["variants"] = {}
                default_variant = None

                variants = plugin.pop("variants", [])

                for variant in variants:
                    variant_name = variant["name"]

                    if not default_variant or variant.get("default", False):
                        default_variant = variant_name

                    hub[index_key][plugin_name]["variants"][variant_name] = {
                        "ref": f"{api_url}/plugins/{plugin_type}/{plugin_name}--{variant_name}"
                    }

                    plugin_key = f"/{plugin_type}/{plugin_name}--{variant_name}"
                    hub[plugin_key] = {
                        **plugin,
                        **variant,
                        "name": plugin_name,
                        "label": plugin.get("label"),
                        "namespace": plugin["namespace"],
                        "variant": variant_name,
                    }

                if not variants:
                    variant_name = plugin.get("variant", "original")
                    default_variant = variant_name

                    hub[index_key][plugin_name]["variants"][variant_name] = {
                        "ref": f"{api_url}/plugins/{plugin_type}/{plugin_name}--{variant_name}"
                    }

                    plugin_key = f"/{plugin_type}/{plugin_name}--{variant_name}"
                    hub[plugin_key] = {
                        **plugin,
                        "name": plugin_name,
                        "namespace": plugin["namespace"],
                        "variant": variant_name,
                        "settings": plugin.get("settings", []),
                        "commands": plugin.get("commands", {}),
                        "docs": plugin.get("docs"),
                        "repo": plugin.get("repo"),
                        "pip_url": plugin.get("pip_url"),
                    }

                    if "dialect" in plugin:
                        hub[plugin_key]["dialect"] = plugin["dialect"]  # noqa: WPS529

                hub[index_key][plugin_name][
                    "logo_url"
                ] = f"https://mock.meltano.com/{plugin_name}.png"
                hub[index_key][plugin_name]["default_variant"] = default_variant

        return hub

    def __init__(self, api_url: str, discovery: dict) -> None:
        """Create a mock HTTP adapter for the Hub.

        Args:
            api_url: The base URL of the Hub.
            discovery: A parsed discovery.yml file.
        """
        super().__init__()
        self.api_url = api_url
        self.count = Counter()
        self._mapping = self._process_discovery(api_url, deepcopy(discovery))

        # Special cases
        self._mapping["/extractors/index"]["this-returns-500"] = {
            "default_variant": "original",
            "logo_url": "https://mock.meltano.com/this-returns-500.png",
            "variants": {
                "original": {
                    "ref": f"{api_url}/plugins/extractors/this-returns-500--original"
                }
            },
        }

    def send(
        self,
        request: requests.PreparedRequest,
        stream: bool = False,
        timeout: float | tuple[float, float] | tuple[float, None] | None = None,
        verify: bool | str = True,
        cert: Any | None = None,
        proxies: Mapping[str, str] | None = None,
    ):
        _, endpoint = request.path_url.split("/meltano/api/v1/plugins")

        response = requests.Response()
        response.request = request
        response.url = request.url

        response_500 = self.RETURN_500.get(endpoint)
        if response_500:
            response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
            response.reason = "Internal Server Error"
            response._content = json.dumps(response_500).encode()
            return response

        try:
            data = self._mapping[endpoint]
        except KeyError:
            response.status_code = HTTPStatus.NOT_FOUND
            response._content = b""
            return response

        self.count[endpoint] += 1
        response.status_code = HTTPStatus.OK
        response._content = json.dumps(data).encode()
        return response


@pytest.fixture(scope="class")
def meltano_hub_service(project, discovery):
    hub = MeltanoHubService(project)
    hub.session.mount(hub.hub_api_url, MockAdapter(hub.hub_api_url, discovery))
    return hub


@pytest.fixture(scope="class")
def hub_endpoints(meltano_hub_service):
    adapter = meltano_hub_service.session.adapters[meltano_hub_service.hub_api_url]
    return adapter._mapping


@pytest.fixture(scope="function")
def hub_request_counter(meltano_hub_service: MeltanoHubService):
    counter: Counter = meltano_hub_service.session.get_adapter(
        meltano_hub_service.hub_api_url
    ).count
    counter.clear()
    return counter
