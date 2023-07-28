"""Meltano Cloud config CLI."""

from __future__ import annotations

import hashlib
import re
import typing as t
from dataclasses import asdict, dataclass

import click
import questionary

from meltano.cloud.api.client import MeltanoCloudClient, json
from meltano.cloud.api.config import (
    MeltanoCloudProjectAmbiguityError,
    NoMeltanoCloudProjectIDError,
)
from meltano.cloud.cli.base import (
    get_paginated,
    pass_context,
    print_limit_warning,
    run_async,
)

if t.TYPE_CHECKING:
    from meltano.cloud.cli.base import MeltanoCloudCLIContext

MAX_PAGE_SIZE = 250


@click.group("config")
def config() -> None:
    """Configure Meltano Cloud project settings and secrets."""


class ConfigCloudClient(MeltanoCloudClient):
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

    def _build_notification_url(self, key: str) -> str:
        """Helper function to build notification url.

        Args:
            key: The key to use in the url
        """
        key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
        try:
            return (
                f"{self.notifications_service_prefix}/"
                f"{self.config.tenant_resource_key}/"
                f"{key_hash}/notification"
                f"?entityId={self.config.internal_project_id}"
            )
        except (NoMeltanoCloudProjectIDError, MeltanoCloudProjectAmbiguityError):
            return (
                f"{self.notifications_service_prefix}/"
                f"{self.config.tenant_resource_key}/{key_hash}/notification"
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
            post_url = self._build_notification_url(input_string)
            return await self._json_request(
                "POST",
                post_url,
                json={
                    "notification": asdict(notification),
                },
            )

    async def update_notification_key(self, old_key: str, new_key: str):
        """Function to update the notification key.

        The notification key is hash of either webhook url or email

        Args:
            old_key: The old key to be changed
            new_key: The new key to be updated to
        """
        key_hash = hashlib.sha256(old_key.encode("utf-8")).hexdigest()
        async with self.authenticated():
            try:
                patch_url = (
                    f"{self.notifications_service_prefix}/"
                    f"{self.config.tenant_resource_key}/{key_hash}"
                    f"/notification/key?entityId={self.config.internal_project_id}"
                )
            except (NoMeltanoCloudProjectIDError, MeltanoCloudProjectAmbiguityError):
                patch_url = (
                    f"{self.notifications_service_prefix}/"
                    f"{self.config.tenant_resource_key}/{key_hash}/notification/key"
                )
            return await self._json_request(
                "PATCH",
                patch_url,
                json={
                    "new_key": new_key,
                },
            )

    async def delete_notification(self, key: str):
        """Function to delete notification by key.

        Args:
            key: The key of notification to be deleted
        """
        async with self.authenticated():
            delete_url = self._build_notification_url(key)
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


class NotificationTypeQuestionChoices(click.Option):
    """Click option that provides an interactive prompt for notification types."""

    def prompt_for_value(self, ctx: click.Context) -> t.Any:
        """Prompt the user to interactively select a Meltano Cloud notification type.

        Args:
            ctx: The Click context.

        Returns:
            The type of the notification
        """
        return questionary.select(
            message="",
            qmark="Choose notification type",
            choices=["webhook", "email"],
        ).unsafe_ask()  # Use Click's Ctrl-C handling instead of Questionary's


def validate_notification_input(
    value: str,
    regex: str,
    prompt_message: str,
    error_message: str,
) -> str:
    """Helper function to validate specific notification type input.

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
    """Helper function to validate email.

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
    """Helper function to validate url.

    Args:
        value: The value of the prompt

    Returns:
        Valid url
    """
    url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
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
    """Function to prompt if necessary and validate input for type.

    Args:
        value: The value to validated
        type: the type to validate against
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

    def type_cast_value(self, ctx: click.Context, value: list) -> list:
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
                raise click.BadParameter(f"Unable to parse given json: {item}")

        return filters


def validate_filter_dict(filter_dict: dict) -> None:
    """Helper function to validate filters dictionary against supported values.

    Args:
        filter_dict: The filter being validated
    """
    # For list of supported events check meltano/infra/common/models/meltano_models/models.py NotificationEventTypes
    NOTIFICATION_EVENTS_SET = {"all"}
    # For list of supported events check meltano/infra/common/models/meltano_models/models.py NotificationStatusfilters
    NOTIFICATION_STATUS_FILTERS_SET = {"failed", "cancelled", "succeeded"}

    if "events" in filter_dict:
        events_set = set(filter_dict["events"])
        if not events_set.issubset(NOTIFICATION_EVENTS_SET):
            raise click.BadParameter(
                f"Some events not supported. Supported events: {NOTIFICATION_EVENTS_SET}, events: {filter_dict['events']}",
            )

    if "status" in filter_dict:
        status_set = set(filter_dict["status"])
        if not status_set.issubset(NOTIFICATION_STATUS_FILTERS_SET):
            raise click.BadParameter(
                f"Some status not supported. Supported status: {NOTIFICATION_STATUS_FILTERS_SET}, status: {filter_dict['status']}",
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


@config.group()
def notification() -> None:
    """Configure Meltano Cloud notifications."""


@notification.group()
def set() -> None:
    """Commands for setting notification."""


def create_set_command(notification_type: t.Literal["webhook", "email"]):
    """Helper function create set commands for different notifications.

    Args:
        notification_type: The type of notification
    """

    @set.command(notification_type)
    @click.option(
        "--value",
        nargs=1,
        type=str,
        help=f"{notification_type} value to be used for notification",
    )
    @click.option(
        "--filter",
        cls=FilterList,
        multiple=True,
        help="The filters to add to notification.",
        default=[],
    )
    @pass_context
    @run_async
    async def set_notification(
        context: MeltanoCloudCLIContext,
        value: str | None,
        filter: list,
    ):
        """Function to set the notification of specific type.

        Args:
            context: The click context
            value: The value to set for the notification such as url or email
            filter: The list of filters to apply to the notification
        """
        validated_value = prompt_and_validate(
            value=value,
            notification_type=notification_type,
            prompt_message=f"Please provide a {notification_type} value",
            error_message=f"Invalid {notification_type} value",
        )
        if notification_type == "webhook":
            notification = WebhookNotificaton(
                type=str(notification_type),
                filters=filter,
                webhook_url=validated_value,
            )
        elif notification_type == "email":
            notification = EmailNotification(
                type=str(notification_type),
                filters=filter,
                email=validated_value,
            )

        async with ConfigCloudClient(config=context.config) as client:
            await client.put_notification(notification=notification)
            click.echo(f"Successfully created {notification_type} notification")
            # TODO: Implement https://github.com/meltano/infra/issues/1791
            # TODO: Add helpful message for ways for user to see notifications
        set_notification.__name__ = f"set_notification_{notification_type}"  # type: ignore[valid-type]
        return set_notification


create_set_command("webhook")
create_set_command("email")


@notification.group()
def update():
    """Notification group update command group."""


def create_update_command(notification_type: t.Literal["webhook", "email"]):
    """Helper function to create notification update commads.

    Args:
        notification_type: The notification type
    """

    @update.command(notification_type)
    @click.option(
        "--old",
        nargs=1,
        type=str,
        help=f"Old {notification_type} to be updated",
    )
    @click.option(
        "--new",
        nargs=1,
        type=str,
        help=f"New {notification_type} to be updated",
    )
    @pass_context
    @run_async
    async def update_notification(
        context: MeltanoCloudCLIContext,
        old: str | None,
        new: str | None,
    ):
        """Function to create update notification commands of specific type.

        Args:
            context: The click context
            old: The old value being updated
            new: The new value being set
        """
        old_key = prompt_and_validate(
            value=old,
            notification_type=notification_type,
            prompt_message=f"Please provide old {notification_type} value to update",
            error_message=f"Invalid {notification_type} value",
        )
        new_key = prompt_and_validate(
            value=new,
            notification_type=notification_type,
            prompt_message=f"Please provide new {notification_type} value to update to",
            error_message=f"Invalid {notification_type} value",
        )

        async with ConfigCloudClient(config=context.config) as client:
            await client.update_notification_key(old_key=old_key, new_key=new_key)
            click.echo(f"Successfully updated {notification_type} notification")

    update_notification.__name__ = f"update_notification_{type}"  # type: ignore[valid-type]
    return update_notification


create_update_command("webhook")
create_update_command("email")


@notification.group()
def delete() -> None:
    """Notification group delete command group."""


def create_delete_command(notification_type: t.Literal["webhook", "email"]):
    """Helper function to create delete commands for specific type.

    Args:
        notification_type: The type of notification
    """

    @delete.command(notification_type)
    @click.option(
        "--value",
        nargs=1,
        type=str,
        help=f"Old {notification_type} value to be deleted",
    )
    @pass_context
    @run_async
    async def delete_notification(
        context: MeltanoCloudCLIContext,
        value: str | None,
    ):
        """Function to create delete command for specific type.

        Args:
            context: The click context
            value: The value either email or url to delete
        """
        input_value = prompt_and_validate(
            value=value,
            notification_type=notification_type,
            prompt_message=f"Please provide a {notification_type} value to delete",
            error_message=f"Invalid {notification_type} value",
        )
        async with ConfigCloudClient(config=context.config) as client:
            await client.delete_notification(key=input_value)
            click.echo(f"Successfully deleted {notification_type} notification")

    delete_notification.__name__ = f"delete_notification_{type}"  # type: ignore[valid-type]

    return delete_notification


create_delete_command("email")
create_delete_command("webhook")
