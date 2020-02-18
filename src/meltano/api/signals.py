import logging
from blinker import ANY
from flask import render_template, url_for
from flask_mail import Message
from flask.signals import Namespace

from meltano.core.project import Project
from meltano.core.job import Job
from meltano.core.job.finder import JobFinder
from meltano.api.mail import mail
from meltano.api.models import db
from meltano.api.models.subscription import Subscription


pipeline = Namespace()
pipeline_completed = pipeline.signal("completed")


class PipelineSignals:
    @classmethod
    def on_completed(self, session, pipeline, success: bool):
        job_finder = JobFinder(pipeline["name"])
        jobs = job_finder.successful(session).all()

        pipeline_completed.send(pipeline, success=success, first_run=len(jobs) <= 1)


class NotificationHandlers:
    def init(self, app):
        self._app = app

        # wire the signal handlers
        pipeline_completed.connect(self.handle_pipeline_completed, ANY)

    def handle_pipeline_completed(self, sender, **kwargs):
        """
        Handles the `First Run` pipeline email notification
        """

        if not kwargs["success"]:
            logging.debug(
                f"Not sending 'pipeline_first_run' because `{sender}` run has failed."
            )
            return

        if not kwargs["first_run"]:
            logging.debug(
                f"Not sending 'pipeline_first_run' because `{sender}` has already ran."
            )
            return

        messages = []
        job_id = sender["name"]
        instance_url = url_for(
            "root.default", path=f"data/schedule/{job_id}", _external=True
        )
        subscriptions = Subscription.query.filter_by(
            event_type="pipeline_first_run", source_type="pipeline", source_id=job_id
        ).all()
        html = render_template(
            "email/pipeline_first_run.html", pipeline=sender, instance_url=instance_url
        )

        for subscription in subscriptions:
            msg = Message(
                subject="Your Meltano data source is ready!",
                html=html,
                recipients=[subscription.recipient],
            )
            messages.append(msg)

        with mail.connect() as conn:
            for msg in messages:
                conn.send(msg)
