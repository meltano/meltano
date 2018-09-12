#!/usr/bin/env python3
# TODO: convert this to alembic http://alembic.zzzcomputing.com/en/latest/
from .app import db
from .models import settings
#import backoff

# to get the desired UX we should wait for the db to be available
# @backoff.on_exception(backoff.expo,
#                       SOME SQL EXCEPTION
#                       max_time=60)
def create_db():
    db.create_all()
    db_settings = settings.Settings()
    db.session.add(db_settings)
    db.session.commit()


if __name__ == '__main__':
    create_db()
