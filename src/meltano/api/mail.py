"""Basic `MailService` that sends notifications via the sendgrid API."""

from __future__ import annotations

from flask_mail import Mail, Message
from smtpapi import SMTPAPIHeader

from meltano.api.models.subscription import Subscription, SubscriptionEventType
from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService

mail = Mail()


class MailService:
    """Basic MailService that sends notifications via the sendgrid SMTPAPI."""

    def __init__(self, project: Project):
        """Initialize the MailService.

        Args:
            project: The project to use the MailService when referencing the project settings or project id.
        """
        self.project = project
        self._settings = ProjectSettingsService(self.project)

        self.project_id = self._settings.get("project_id")
        self.sendgrid_unsubscribe_group_id = self._settings.get(
            "mail.sendgrid_unsubscribe_group_id"
        )

    def get_unsubscribe_group(self, subscription: Subscription) -> int | None:
        """Get the unsubscribe group for the given subscription.

        Currently, the unsubscribe group is based on the event type, and only the SubscriptionEventType.PIPELINE_MANUAL_RUN
        even type is actually supported.

        Args:
            subscription: The subscription to get the unsubscribe group for.

        Returns:
            The unsubscribe group id or None if the event type is not supported.
        """
        event_type = SubscriptionEventType(subscription.event_type)
        if event_type == SubscriptionEventType.PIPELINE_MANUAL_RUN:
            return self.sendgrid_unsubscribe_group_id
        return None

    def create_message(self, subscription: Subscription, **kwargs) -> Message:
        """Create a message for the given subscription.

        Args:
            subscription: The subscription to create the message for.
            kwargs: Additional arguments to pass to the message constructor.

        Returns:
            The created message.
        """
        headers = SMTPAPIHeader()
        headers.set_unique_args(
            {
                "project_id": str(self.project_id),
                "subscription_id": str(subscription.id),
            }
        )

        unsubscribe_group = self.get_unsubscribe_group(subscription)
        if unsubscribe_group:
            headers.set_asm_group_id(int(unsubscribe_group))

        return Message(
            recipients=[subscription.recipient],
            extra_headers={"X-SMTPAPI": headers.json_string()},
            **kwargs,
        )
