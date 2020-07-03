from enum import Enum
from flask_mail import Mail, Message
from smtpapi import SMTPAPIHeader

from meltano.core.project import Project
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.api.models.subscription import Subscription, SubscriptionEventType


mail = Mail()


# From `https://app.sendgrid.com` Meltano's account
class UnsubscribeGroup(int, Enum):
    ELT_NOTIFICATIONS = 12751


class MailService:
    EventTypeUnsubscribeGroup = {
        SubscriptionEventType.PIPELINE_MANUAL_RUN: UnsubscribeGroup.ELT_NOTIFICATIONS
    }

    def __init__(self, project: Project):
        self.project = project
        self.project_id = ProjectSettingsService(self.project).get("project_id")

    def get_unsubscribe_group(self, subscription) -> UnsubscribeGroup:
        try:
            event_type = SubscriptionEventType(subscription.event_type)
            return self.EventTypeUnsubscribeGroup[event_type]
        except:
            return None

    def create_message(self, subscription, **kwargs) -> Message:
        """
        Create the basic Message with the proper headers.

        Uses the SendGrid SMTPAPI.
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
            **kwargs
        )
