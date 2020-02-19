import logging
from blinker import ANY
from flask import render_template, url_for
from flask_mail import Message

from meltano.api.mail import mail, MailService
from meltano.api.models.subscription import Subscription, SubscriptionEventType
from meltano.api.signals import PipelineSignals
from meltano.core.project import Project


class NotificationEvents:
    def __init__(self, project: Project, mail_service: MailService = None):
        self.project = project
        self.mail_service = mail_service or MailService(project)

    def init(self, app):
        self._app = app

        # wire the signal handlers
        PipelineSignals.completed.connect(self.handle_pipeline_completed, ANY)

    def handle_pipeline_completed(self, sender, **kwargs):
        """
        Handles the `First Run` pipeline email notification
        """

        if not kwargs["success"]:
            logging.debug(
                f"Not sending 'pipeline_first_run' because `{sender}` run has failed."
            )
            return

        messages = []
        job_id = sender["name"]
        instance_url = url_for(
            "root.default", path=f"data/schedule/{job_id}", _external=True
        )
        subscriptions = Subscription.query.filter_by(
            event_type=SubscriptionEventType.PIPELINE_FIRST_RUN,
            source_type="pipeline",
            source_id=job_id,
        ).all()
        html = render_template(
            "email/pipeline_first_run.html", pipeline=sender, instance_url=instance_url
        )

        sent_recipients = set()
        for subscription in subscriptions:
            # ensure it is not a duplicate mail
            if subscription.recipient in sent_recipients:
                continue

            msg = self.mail_service.create_message(
                subscription, subject="Your Meltano data source is ready!", html=html
            )
            sent_recipients.add(subscription.recipient)
            messages.append(msg)

        with mail.connect() as conn:
            for msg in messages:
                conn.send(msg)
