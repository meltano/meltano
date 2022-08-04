from __future__ import annotations

import logging

from blinker import ANY
from flask import render_template, url_for

from meltano.api.mail import MailService, mail
from meltano.api.models.subscription import Subscription, SubscriptionEventType
from meltano.api.signals import PipelineSignals
from meltano.core.plugin import PluginType
from meltano.core.project import Project
from meltano.core.project_plugins_service import ProjectPluginsService

SUCCESS = True
FAILURE = False

logger = logging.getLogger(__name__)


class NotificationEvents:
    def __init__(
        self,
        project: Project,
        mail_service: MailService = None,
        plugins_service: ProjectPluginsService = None,
    ):
        self.project = project

        self.mail_service = mail_service or MailService(project)
        self.plugins_service = plugins_service or ProjectPluginsService(project)

    def init_app(self, app):
        # wire the signal handlers
        PipelineSignals.completed.connect(self.handle_pipeline_completed, ANY)

    def pipeline_data_source(self, schedule) -> str:
        """Return the Data Source name for a Pipeline."""
        return self.plugins_service.find_plugin(
            schedule.extractor, plugin_type=PluginType.EXTRACTORS
        ).label

    def pipeline_urls(self, schedule) -> str:
        """Return external URLs to different point of interests for a Pipeline."""
        plugin = self.plugins_service.find_plugin(
            schedule.extractor, plugin_type=PluginType.EXTRACTORS
        )
        return {
            "log": url_for(
                "root.default", path=f"data/schedule/{schedule.name}", _external=True
            ),
            "config": url_for(
                "root.default",
                path=f"data/extract/{schedule.extractor}",
                _external=True,
            ),
            "docs": plugin.docs,
        }

    def handle_pipeline_completed(self, schedule, success: bool = None):  # noqa: WPS210
        """Handle the `Manual Run` pipeline email notification."""
        if success is None:
            raise ValueError("'success' must be set.")

        state_id = schedule.name
        data_source = self.pipeline_data_source(schedule)

        subject, template = {
            SUCCESS: (
                f"Your {data_source} data is ready!",
                "email/pipeline_manual_run/success.html",
            ),
            FAILURE: (
                f"Your {data_source} extraction has failed!",
                "email/pipeline_manual_run/failure.html",
            ),
        }[success]
        html = render_template(
            template, data_source=data_source, urls=self.pipeline_urls(schedule)
        )

        subscriptions = Subscription.query.filter_by(
            event_type=SubscriptionEventType.PIPELINE_MANUAL_RUN,
            source_type="pipeline",
            source_id=state_id,
        ).all()
        logger.debug(
            f"Found {len(subscriptions)} subscriptions for source '{state_id}'."
        )

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
