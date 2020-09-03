import logging
from datetime import datetime

from flask import Blueprint
from flask_login import current_user
from meltano.api.security import block_if_api_auth_required, users


VERSION = 1


class APIBlueprint(Blueprint):
    @property
    def api_version():
        return f"v{VERSION}"

    @classmethod
    def url_prefix(cls, name, version=VERSION):
        return f"/api/v{version}/{name}"

    def __init__(self, name, *args, require_authentication=True, **kwargs):
        # make sure the `url_prefix` is set
        url_prefix = kwargs.pop("url_prefix", self.url_prefix(name))

        super().__init__(name, *args, url_prefix=url_prefix, **kwargs)

        if require_authentication:
            self.before_request(self.__class__.auth_filter)

    @block_if_api_auth_required
    def auth_filter():
        logging.debug(f"Authenticated as {current_user}")

        current_user.last_activity_at = datetime.utcnow()
        users.db.session.commit()
