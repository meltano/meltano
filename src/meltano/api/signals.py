from flask.signals import Namespace


class PipelineSignals:
    __namespace__ = Namespace()
    completed = __namespace__.signal("completed")

    @classmethod
    def on_complete(cls, pipeline, success: bool):
        cls.completed.send(pipeline, success=success)
