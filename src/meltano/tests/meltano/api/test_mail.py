from __future__ import annotations

import json

import pytest

from meltano.api.mail import MailService
from meltano.api.models.subscription import Subscription, SubscriptionEventType
from meltano.core.project_settings_service import ProjectSettingsService


class TestMailService:
    def test_get_unsubscribe_group(self, project):
        default_id = 12751
        custom_id = 42

        sub = Subscription()
        sub.event_type = SubscriptionEventType.PIPELINE_MANUAL_RUN

        settings = ProjectSettingsService(project)
        assert settings.get("mail.sendgrid_unsubscribe_group_id") == default_id

        # the default case
        service = MailService(project)

        assert service.get_unsubscribe_group(sub) == default_id

        # the custom case
        settings = ProjectSettingsService(project)
        settings.set("mail.sendgrid_unsubscribe_group_id", custom_id)
        assert settings.get("mail.sendgrid_unsubscribe_group_id") == custom_id

        custom_service = MailService(project)
        assert custom_service.get_unsubscribe_group(sub) == custom_id

    @pytest.mark.order(after="test_get_unsubscribe_group")
    def test_create_message(self, project):
        sub = Subscription()
        sub.event_type = SubscriptionEventType.PIPELINE_MANUAL_RUN
        sub.id = 42
        sub.recipient = "test@test.com"

        settings = ProjectSettingsService(project)
        settings.set("mail.sendgrid_unsubscribe_group_id", 1)

        service = MailService(project)
        message = service.create_message(sub)

        assert "test@test.com" in message.recipients

        decoded_headers = json.loads(message.extra_headers["X-SMTPAPI"])
        assert decoded_headers.get("asm_group_id") == 1
        assert decoded_headers.get("unique_args").get("subscription_id") == str(sub.id)
