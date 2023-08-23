"""Meltano Cloud config CLI."""

from __future__ import annotations

import hashlib
import re
import typing as t
from dataclasses import asdict, dataclass

import click

from meltano.cloud.api.client import MeltanoCloudClient, json
from meltano.cloud.api.config import (
    MeltanoCloudProjectAmbiguityError,
    NoMeltanoCloudProjectIDError,
)
from meltano.cloud.api.types import CloudNotification
from meltano.cloud.cli.base import (
    LimitedResult,
    get_paginated,
    pass_context,
    print_formatted_list,
    print_limit_warning,
)
from meltano.core.utils import run_async

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

MAX_PAGE_SIZE = 250


@click.group("config")
def config() -> None:
    """Configure Meltano Cloud project settings and secrets."""


class ConfigCloudClient(MeltanoCloudClient):  # noqa: WPS214
    """Meltano Cloud config Client."""

    secrets_service_prefix = "/secrets/v1/"
    notifications_service_prefix = "/notifications/v1"

    @property
    def _tenant_prefix(self) -> str:
        return f"{self.config.tenant_resource_key}/{self.config.internal_project_id}/"

    async def list_items(
        self,
        page_size: int | None = None,
        page_token: str | None = None,
    ):
        """List Meltano Cloud config keys."""
        params: dict[str, t.Any] = {
            "page_size": page_size,
            "page_token": page_token,
        }
        async with self.authenticated():
            return await self._json_request(
                "GET",
                self.secrets_service_prefix + self._tenant_prefix,
                params=self.clean_params(params),
            )

    async def set_value(self, secret_name: str, secret_value: str):
        """Set Meltano Cloud config secret."""
        async with self.authenticated():
            return await self._json_request(
                "PUT",
                self.secrets_service_prefix + self._tenant_prefix,
                json={"name": secret_name, "value": secret_value},
            )

    async def delete(self, secret_name: str):
        """Delete Meltano Cloud config secret."""
        async with self.authenticated():
            return await self._json_request(
                "DELETE",
                self.secrets_service_prefix + self._tenant_prefix + secret_name,
            )

    def _build_notification_url(
        self,
        end_path: t.Literal["notification"] | t.Literal["notifications"],
        key: str | None = None,
    ) -> str:
        """Build a notification url.

        Args:
            key: The key to use in the url
        """
        url = (
            f"{self.notifications_service_prefix}/"
            f"{self.config.tenant_resource_key}/"
        )

        if key:
            key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
            url = f"{url}{key_hash}/"

        try:
            return f"{url}{end_path}?entity_id={self.config.internal_project_id}"
        except (NoMeltanoCloudProjectIDError, MeltanoCloudProjectAmbiguityError):
            return f"{url}{end_path}"

    async def list_notifications(
        self,
    ):
        """List notifications."""
        get_url = self._build_notification_url(end_path="notifications")

        async with self.authenticated():
            return await self._json_request(
                "GET",
                get_url,
            )

    async def put_notification(
        self,
        notification: WebhookNotificaton | EmailNotification,
    ):
        """Upsert notification.

        Args:
            notification: The notification to be upserted
        """
        if isinstance(notification, WebhookNotificaton):
            input_string = notification.webhook_url
        elif isinstance(notification, EmailNotification):
            input_string = notification.email
        else:
            raise TypeError("Invalid type")

        async with self.authenticated():
            post_url = self._build_notification_url(
                key=input_string,
                end_path="notification",
            )

            return await self._json_request(
                "POST",
                post_url,
                json={
                    "notification": asdict(notification),
                },
            )

    async def update_notification(
        self,
        recipient: str,
        new_key: str | None = None,
        status: str | None = None,
    ):
        """Update the notification key.

        The notification key is hash of either webhook url or email

        Args:
            recipient: The key of notification to be updated
            new_key: The new key to be updated to
            status: The new status to be updated to
        """
        async with self.authenticated():
            patch_url = self._build_notification_url(
                key=recipient,
                end_path="notification",
            )
            data = {}
            if new_key:
                data["new_key"] = new_key
            if status:
                data["status"] = status
            return await self._json_request(
                "PATCH",
                patch_url,
                json=data,
            )

    async def delete_notification(self, key: str):
        """Delete notification by key.

        Args:
            key: The key of notification to be deleted
        """
        async with self.authenticated():
            delete_url = self._build_notification_url(key=key, end_path="notification")
            return await self._json_request(
                "DELETE",
                delete_url,
            )


@config.group()
def env() -> None:
    """Configure Meltano Cloud environment variable secrets."""


@env.command("list")
@click.option(
    "--limit",
    required=False,
    type=int,
    default=10,
    help="The maximum number of history items to display.",
)
@pass_context
@run_async
async def list_items(
    context: MeltanoCloudCLIContext,
    limit: int,
) -> None:
    """List Meltano Cloud config items."""
    async with ConfigCloudClient(config=context.config) as client:
        results = await get_paginated(client.list_items, limit, MAX_PAGE_SIZE)

    for secret in results.items:
        click.echo(secret["name"])

    if results.truncated:
        print_limit_warning()


@env.command("set")
@click.option("--key", type=str, required=True)
@click.option("--value", type=str, required=True)
@pass_context
@run_async
async def set_value(
    context: MeltanoCloudCLIContext,
    key: str,
    value: str,
) -> None:
    """Create a new Meltano Cloud config item."""
    async with ConfigCloudClient(config=context.config) as client:
        await client.set_value(secret_name=key, secret_value=value)
        click.echo(f"Successfully set config item {key!r}.")


@env.command()
@click.argument("secret_name", type=str, required=True)
@pass_context
@run_async
async def delete_secret_name(
    context: MeltanoCloudCLIContext,
    secret_name,
) -> None:
    """Delete an existing Meltano Cloud config item."""
    async with ConfigCloudClient(config=context.config) as client:
        await client.delete(secret_name=secret_name)
        click.echo(f"Successfully deleted config item {secret_name!r}.")


def validate_notification_input(
    value: str,
    regex: str,
    prompt_message: str,
    error_message: str,
) -> str:
    """Validate specific notification type input.

    Args:
        value: The value to validate
        regex: The regex to test against
        prompt_message: The message to prompt user in case validation fails
        error_message: The message to display to user in case validation fails
    """
    try:
        if re.match(regex, value):
            return value
        raise ValueError(value)
    except ValueError:
        click.echo(error_message)
        prompt_value = click.prompt(prompt_message)
        return validate_notification_input(
            prompt_value,
            regex,
            prompt_message,
            error_message,
        )


def validate_email(
    value: str,
    prompt_message: str = "Please provide a valid email",
    error_message: str = "Value is not a valid email",
) -> str:
    """Validate an email.

    Args:
        value: The value of the prompt

    Returns:
        Valid email
    """
    email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return validate_notification_input(
        value=value,
        regex=email_regex,
        prompt_message=prompt_message,
        error_message=error_message,
    )


def validate_url(
    value: str,
    prompt_message: str = "Please provide a valid url",
    error_message: str = "Value is not a valid url",
) -> str:
    """Validate a url.

    Args:
        value: The value of the prompt

    Returns:
        Valid url
    """
    url_regex = (
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|"
        r"(?:%[0-9a-fA-F][0-9a-fA-F]))+"  # noqa: WPS360
    )
    return validate_notification_input(
        value=value,
        regex=url_regex,
        prompt_message=prompt_message,
        error_message=error_message,
    )


VALIDATE_FUNCTION_DICT = {"webhook": validate_url, "email": validate_email}


def prompt_and_validate(
    value: str | None,
    notification_type: t.Literal["webhook", "email"],
    prompt_message: str = "Please provide valid value.",
    error_message: str = "Value is not valid",
) -> str:
    """Prompt if necessary and validate input for notification_type.

    Args:
        value: The value to validated
        notification_type: the notification_type to validate against
        prompt_message: The message to prompt user in case validation fails
        error_message: The message to display to user in case validation fails
    """
    input_value = (
        value
        if value
        else click.prompt(
            prompt_message,
            value_proc=VALIDATE_FUNCTION_DICT[notification_type],
        )
    )
    VALIDATE_FUNCTION_DICT[notification_type](
        value=input_value,
        prompt_message=prompt_message,
        error_message=error_message,
    )
    return input_value


class FilterList(click.Option):
    """Class for filters list for notifications."""

    def type_cast_value(self, _: click.Context, value: list) -> list:
        """Attempt to cast and validate filters parameter.

        Args:
            ctx: The click context
            value: Multiple filters list gathered via --filter flag
        """
        filters = []
        for item in value:
            try:
                filter_obj = json.loads(item)
                filter_list = (
                    filter_obj if isinstance(filter_obj, list) else [filter_obj]
                )
                for filter_dict in filter_list:
                    validate_filter_dict(filter_dict)
                filters.extend(filter_list)
            except json.JSONDecodeError:
                raise click.BadParameter(  # noqa: WPS469
                    f"Unable to parse given json: {item}",
                ) from None

        return filters


def validate_filter_dict(filter_dict: dict) -> None:
    """Validate filters dictionary against supported values.

    Args:
        filter_dict: The filter being validated
    """
    # For list of supported events and statuses
    # meltano/infra/common/models/meltano_models/models.py
    NOTIFICATION_EVENTS_SET = {"job_run"}
    NOTIFICATION_STATUS_FILTERS_SET = {"failed", "cancelled", "succeeded"}

    if "events" in filter_dict:
        # Since set() is a group for notificaiton need to set comprehension
        events_set = set(filter_dict["events"])
        if not events_set.issubset(NOTIFICATION_EVENTS_SET):
            raise click.BadParameter(
                "Some events not supported. "
                f"Supported events: {NOTIFICATION_EVENTS_SET}, "
                f"events: {filter_dict['events']}",
            )

    if "status" in filter_dict:
        status_set = set(filter_dict["status"])
        if not status_set.issubset(NOTIFICATION_STATUS_FILTERS_SET):
            raise click.BadParameter(
                "Some status not supported. "
                f"Supported status: {NOTIFICATION_STATUS_FILTERS_SET}, "
                f"status: {filter_dict['status']}",
            )


@dataclass
class WebhookNotificaton:
    """Dataclass for webhook notifications."""

    type: str
    filters: list
    webhook_url: str


@dataclass
class EmailNotification:
    """Dataclass for email notifications."""

    type: str
    filters: list
    email: str


def _format_notification(
    notification: CloudNotification,
) -> tuple[str, str, str, list | t.Literal["N/A"]]:
    def replace_empty_with_NA(item):
        """Replace empty list with N/A."""
        if isinstance(item, list) and not item:
            # If a an empty list return N/A
            return "N/A"
        return item

    filters = replace_empty_with_NA(notification["filters"])
    return (
        notification["recipient"],
        notification["type"],
        notification["status"],
        filters,
    )


@config.group()
def notification() -> None:
    """Configure Meltano Cloud notifications."""


@notification.command(
    "list",
    help=(
        "List all configured project notifications.\n\n "
        "To set or list notifications for another project "
        "use 'meltano cloud project use'"
    ),
)
@click.option(
    "--format",
    "output_format",
    required=False,
    default="terminal",
    type=click.Choice(("terminal", "markdown", "json")),
    help="The output format to use.",
)
@pass_context
@run_async
async def list_notifications(
    context: MeltanoCloudCLIContext,
    output_format: str,
):
    """List all configured notifications.

    Args:
        context: The click context
    """
    async with ConfigCloudClient(config=context.config) as client:
        try:
            notifications = await client.list_notifications()
            if isinstance(notifications, list):
                print_notifications = LimitedResult(
                    items=notifications,
                )
                print_formatted_list(
                    print_notifications,
                    output_format,
                    _format_notification,
                    ("Recipient", "Type", "Status", "Filters"),
                    ("left", "left", "left", "left"),
                )
        except Exception as e:
            message = str(e) if str(e) else "Internal Server Error"
            raise click.ClickException(  # noqa: WPS469
                f"{message}. \n\n"
                "Please ensure you've correctly followed instructions at: "
                "https://docs.meltano.com/cloud/cloud-cli\n"
                "If the issue persists, "
                "we'd be happy to help at: https://meltano.com/slack",
            ) from None


@notification.group("set")
def notification_set() -> None:
    """Set a meltano cloud notification."""


def create_set_command(notification_type: t.Literal["webhook", "email"]):
    """Create set commands for different notifications.

    Args:
        notifcation_type: The type of notification
    """

    @notification_set.command(
        notification_type,
        help=f"Set a {notification_type} notification.",
    )
    @click.option(
        "--recipient",
        nargs=1,
        type=str,
        help=f"{notification_type} recipient to receive the notification.",
    )
    @click.option(
        "--filter",
        cls=FilterList,
        multiple=True,
        type=list,
        help="The filters to add to notification.",
        default=[],
    )
    @pass_context
    @run_async
    async def set_notification(
        context: MeltanoCloudCLIContext,
        recipient: str | None,
        filter: list,  # noqa: WPS125
    ):
        """Set the notification of specific type.

        Args:
            context: The click context
            recipient: The value to set for the notification such as url or email
            filter: The list of filters to apply to the notification
        """
        validated_recipient = prompt_and_validate(
            value=recipient,
            notification_type=notification_type,
            prompt_message=f"Please provide a {notification_type} value",
            error_message=f"Invalid {notification_type} value",
        )
        notification_to_set: t.Union[WebhookNotificaton, EmailNotification]
        if notification_type == "webhook":
            notification_to_set = WebhookNotificaton(
                type=str(notification_type),
                filters=filter,
                webhook_url=validated_recipient,
            )
        elif notification_type == "email":
            notification_to_set = EmailNotification(
                type=str(notification_type),
                filters=filter,
                email=validated_recipient,
            )

        async with ConfigCloudClient(config=context.config) as client:
            try:
                await client.put_notification(notification=notification_to_set)
                click.echo(
                    f"Successfully set {notification_type} "
                    f"notification for {validated_recipient}. ",
                )
                click.echo(
                    "To see all notifications, "
                    "run: meltano cloud config notification list",
                )
            except Exception as e:
                message = str(e) if str(e) else "Internal Server Error"
                raise click.ClickException(  # noqa: WPS469
                    f"{message}. \n\n"
                    "Please ensure you've correctly followed instructions at: "
                    "https://docs.meltano.com/cloud/cloud-cli\n"
                    "If the issue persists, "
                    "we'd be happy to help at: https://meltano.com/slack",
                ) from None
        set_notification.__name__ = (  # type: ignore[attr-defined]
            f"set_notification_{notification_type}"
        )
        return set_notification


create_set_command("webhook")
create_set_command("email")


@notification.group()
def update():
    """Update a meltano cloud notification."""


def create_update_command(notification_type: t.Literal["webhook", "email"]):
    """Create notification update commads.

    Args:
        type: The notification type
    """

    @update.command(
        notification_type,
        help=f"Update {notification_type} notification.",
    )
    @click.option(
        "--recipient",
        nargs=1,
        type=str,
        help=f"{notification_type} recipient notification to be updated",
    )
    @click.option(
        "--new",
        nargs=1,
        type=str,
        help=f"New {notification_type} recipient value",
    )
    @click.option(
        "--status",
        nargs=1,
        type=click.Choice(["active", "inactive"]),
        help="Notification status",
    )
    @pass_context
    @run_async
    async def update_notification(
        context: MeltanoCloudCLIContext,
        recipient: str,
        new: str | None,
        status: str | None,
    ):
        """Create update notification commands of specific type.

        Args:
            context: The click context
            recipient: The recipient of notification to be updated
            new: The new recipient value
        """
        if not new and not status:
            click.echo(
                "Nothing to update. Please provide either --new or --status "
                "option to update the notification\n",
            )
            return

        update_recipient = prompt_and_validate(
            value=recipient,
            notification_type=notification_type,
            prompt_message=(
                f"Please provide old {notification_type} "
                "recipient for notification to be updated"
            ),
            error_message=f"Invalid {notification_type} recipient",
        )

        new_key = None
        if new:
            new_key = prompt_and_validate(
                value=new,
                notification_type=notification_type,
                prompt_message=(
                    f"Please provide new {notification_type} recipient to update to"
                ),
                error_message=f"Invalid {notification_type} recipient",
            )

        async with ConfigCloudClient(config=context.config) as client:
            try:
                await client.update_notification(
                    recipient=update_recipient,
                    new_key=new_key,
                    status=status,
                )
                click.echo(f"Successfully updated {notification_type} notification")
            except Exception as e:
                message = str(e) if str(e) else "Internal Server Error"
                raise click.ClickException(  # noqa: WPS469
                    f"{message}. \n\n"
                    "Please ensure you've correctly followed instructions at: "
                    "https://docs.meltano.com/cloud/cloud-cli\n"
                    "If the issue persists, "
                    "we'd be happy to help at: https://meltano.com/slack",
                ) from None

    update_notification.__name__ = (  # type: ignore[attr-defined]
        f"update_notification_{notification_type}"
    )
    return update_notification


create_update_command("webhook")
create_update_command("email")


@notification.group()
def delete() -> None:
    """Delete a meltano cloud notification."""


def create_delete_command(notification_type: t.Literal["webhook", "email"]):
    """Create delete commands for specific type.

    Args:
        type: The type of notification
    """

    @delete.command(
        notification_type,
        help=f"Delete {notification_type} notification",
    )
    @click.option(
        "--recipient",
        nargs=1,
        type=str,
        help=f"{notification_type} recipient to delete notification for",
    )
    @pass_context
    @run_async
    async def delete_notification(
        context: MeltanoCloudCLIContext,
        recipient: str | None,
    ):
        """Delete specific notification type.

        Args:
            context: The click context
            recipient: The recipient for notification
        """
        input_value = prompt_and_validate(
            value=recipient,
            notification_type=notification_type,
            prompt_message=(
                f"Please provide a valid {notification_type} "
                "from the 'recipient' column "
                "from `meltano cloud config notification list`"
            ),
            error_message=(
                f"Invalid {notification_type}. "
                f"Please provide a valid {notification_type} "
                "from the 'recipient' column "
                "from `meltano cloud config notification list`"
            ),
        )
        async with ConfigCloudClient(config=context.config) as client:
            try:
                await client.delete_notification(key=input_value)
                click.echo(
                    f"Successfully deleted {notification_type} "
                    f"notification for {input_value}",
                )
            except Exception as e:
                message = str(e) if str(e) else "Internal Server Error"
                raise click.ClickException(  # noqa: WPS469
                    f"{message}. \n\n"
                    "Please ensure you've correctly followed instructions at: "
                    "https://docs.meltano.com/cloud/cloud-cli\n"
                    "If the issue persists, "
                    "we'd be happy to help at: https://meltano.com/slack",
                ) from None

    delete_notification.__name__ = (  # type: ignore[attr-defined]
        f"delete_notification_{notification_type}"
    )
    return delete_notification


create_delete_command("email")
create_delete_command("webhook")
