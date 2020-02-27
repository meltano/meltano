import logging
from blinker import ANY
from flask import render_template, url_for
from flask_mail import Message

from meltano.api.mail import mail, MailService
from meltano.api.models.subscription import Subscription, SubscriptionEventType
from meltano.api.signals import PipelineSignals
from meltano.core.project import Project
from meltano.core.plugin import PluginType, Plugin
from meltano.core.plugin_discovery_service import PluginDiscoveryService


SUCCESS = True
FAILURE = False

logger = logging.getLogger(__name__)


class NotificationEvents:
    def __init__(
        self,
        project: Project,
        mail_service: MailService = None,
        plugin_discovery_service: PluginDiscoveryService = None,
    ):
        self.project = project
        self.mail_service = mail_service or MailService(project)
        self.plugin_discovery_service = (
            plugin_discovery_service or PluginDiscoveryService(project)
        )

    def init_app(self, app):
        # wire the signal handlers
        PipelineSignals.completed.connect(self.handle_pipeline_completed, ANY)

    def pipeline_data_source(self, pipeline) -> str:
        """
        Returns the Data Source name for a Pipeline
        """

        plugin = self.plugin_discovery_service.find_plugin(
            PluginType.EXTRACTORS, pipeline["extractor"]
        )
        return plugin.label

    def pipeline_urls(self, pipeline) -> str:
        """
        Return external URLs to different point of interests for a Pipeline.
        """

        plugin = self.plugin_discovery_service.find_plugin(
            PluginType.EXTRACTORS, pipeline["extractor"]
        )

        return {
            "log": url_for(
                "root.default", path=f"data/schedule/{pipeline['name']}", _external=True
            ),
            "config": url_for(
                "root.default",
                path=f"data/extract/{pipeline['extractor']}",
                _external=True,
            ),
            "docs": plugin.docs,
        }

    def handle_pipeline_completed(self, sender, success: bool = None):
        """
        Handles the `Manual Run` pipeline email notification
        """
        if success is None:
            raise ValueError("'success' must be set.")

        job_id = sender["name"]
        data_source = self.pipeline_data_source(sender)

        status_subject_template = {
            SUCCESS: (
                f"Your {data_source} data is ready!",
                "email/pipeline_manual_run/success.html",
            ),
            FAILURE: (
                f"Your {data_source} extraction has failed!",
                "email/pipeline_manual_run/failure.html",
            ),
        }
        subject, template = status_subject_template[success]
        html = render_template(
            template, data_source=data_source, urls=self.pipeline_urls(sender)
        )

        subscriptions = Subscription.query.filter_by(
            event_type=SubscriptionEventType.PIPELINE_MANUAL_RUN,
            source_type="pipeline",
            source_id=job_id,
        ).all()
        logger.debug(f"Found {len(subscriptions)} subscriptions for source '{job_id}'.")

        messages = set()
        sent_recipients = set()
        for subscription in subscriptions:
            # ensure it is not a duplicate mail
            if subscription.recipient in sent_recipients:
                logger.debug(
                    f"Skipping duplicate notification for recipient '{subscription.recipient}'."
                )
                continue

            msg = self.mail_service.create_message(
                subscription, subject=subject, html=html
            )
            sent_recipients.add(subscription.recipient)
            messages.add(msg)

        with mail.connect() as conn:
            for msg in messages:
                conn.send(msg)
                logger.debug(f"Notification sent to '{msg.recipients}'.")
