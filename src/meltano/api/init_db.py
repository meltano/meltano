#!/usr/bin/env python3
# TODO: convert this to alembic http://alembic.zzzcomputing.com/en/latest/
import backoff
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from meltano.api.models import *
from meltano.core.job import *
from meltano.core.plugin.setting import *
from meltano.core.db import SystemMetadata


# to get the desired UX we should wait for the db to be available
@backoff.on_exception(backoff.expo, OperationalError, max_time=60)
def create_db():
    engine = create_engine("sqlite:///meltano.db")
    SystemMetadata.create_all(engine)


if __name__ == "__main__":
    create_db()
