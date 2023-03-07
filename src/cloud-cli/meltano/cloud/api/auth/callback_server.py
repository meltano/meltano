"""Minimal HTTP app for handling OAuth callbacks."""
from __future__ import annotations

import os

from flask import Flask, render_template, request

from meltano.cloud.api.config import MeltanoCloudConfig

APP = Flask(__name__)

CONFIG: MeltanoCloudConfig = MeltanoCloudConfig.find(
    config_path=os.environ.get("MELTANO_CLOUD_CONFIG_PATH")  # type: ignore
)


@APP.route("/")
def callback_page():
    """Serve the barebones page for localhost redirect.

    Returns:
        Rendered callback page.
    """
    return render_template("callback_page.html", port=CONFIG.auth_callback_port)


@APP.route("/tokens")
def handle_tokens():
    """Parse tokens from query params and write to config.

    Returns:
        Empty response with 204
    """
    args = request.args
    CONFIG.id_token = args["id_token"]
    CONFIG.access_token = args["access_token"]
    CONFIG.write_to_file()
    return "", 204


@APP.route("/logout")
def handle_logout():
    """Handle logout.

    Returns:
        Empty response with 204
    """
    CONFIG.id_token = None
    CONFIG.access_token = None
    CONFIG.write_to_file()
    return "", 204
