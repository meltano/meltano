from __future__ import annotations

import cProfile
import logging
import pstats
import time

from flask import g as global_app_ctx
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("meltano.api.sql")
logger.setLevel(logging.DEBUG)


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault("query_start_time", []).append(time.time())
    logger.debug(f"Start Query: {statement}")


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info["query_start_time"].pop(-1)
    logger.debug("Query Complete!")
    logger.debug(f"Total Time: {total}")


def begin_request_profile():
    global_app_ctx.pr = cProfile.Profile()
    global_app_ctx.pr.enable()


def print_request_profile(res):
    global_app_ctx.pr.disable()
    global_app_ctx.pr.create_stats()

    stats = pstats.Stats(global_app_ctx.pr)
    stats.sort_stats("cumulative").print_stats(0.1)

    return res


def init(app):
    app.before_request(begin_request_profile)
    app.after_request(print_request_profile)
