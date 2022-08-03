from __future__ import annotations

from flask.signals import Namespace


class PipelineSignals:
    __namespace__ = Namespace()
    completed = __namespace__.signal("completed")

    @classmethod
    def on_complete(cls, schedule, success: bool):
        cls.completed.send(schedule, success=success)
