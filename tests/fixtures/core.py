from __future__ import annotations

import datetime
import itertools
import logging
import os
import shutil
import typing as t
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
import structlog

from fixtures.utils import cd, tmp_project
from meltano.core.behavior.canonical import Canonical
from meltano.core.elt_context import ELTContextBuilder
from meltano.core.environment_service import EnvironmentService
from meltano.core.job import Job, Payload, State
from meltano.core.job_state import JobState
from meltano.core.locked_definition_service import LockedDefinitionService
from meltano.core.logging.formatters import get_default_foreign_pre_chain
from meltano.core.logging.job_logging_service import JobLoggingService
from meltano.core.plugin import PluginType
from meltano.core.plugin.settings_service import PluginSettingsService
from meltano.core.plugin_install_service import PluginInstallService
from meltano.core.plugin_invoker import invoker_factory
from meltano.core.project import Project
from meltano.core.project_add_service import ProjectAddService
from meltano.core.project_files import ProjectFiles
from meltano.core.project_init_service import ProjectInitService
from meltano.core.project_plugins_service import PluginAlreadyAddedException
from meltano.core.project_settings_service import ProjectSettingsService
from meltano.core.schedule_service import ScheduleAlreadyExistsError, ScheduleService
from meltano.core.state_service import StateService
from meltano.core.task_sets_service import TaskSetsService
from meltano.core.utils import merge

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from requests.adapters import BaseAdapter

    from meltano.core.plugin.project_plugin import ProjectPlugin

current_dir = Path(__file__).parent


@pytest.fixture(scope="class")
def discovery():
    return {
        PluginType.EXTRACTORS: [
            {
                "name": "tap-that-needs-custom-python",
                "namespace": "tap_that_needs_custom_python",
                "variants": [
                    {
                        "name": "meltano",
                        "original": True,
                        "pip_url": "tap-that-needs-custom-python",
                    },
                ],
            },
            {
                "name": "tap-google-analytics",
                "label": "Google Analytics",
                "description": "App and website analytics platform hosted by Google",
                "namespace": "tap_google_analytics",
                "variants": [
                    {
                        "name": "meltanolabs",
                        "docs": "https://hub.meltano.com/extractors/google-analytics.html",
                        "repo": "https://github.com/MeltanoLabs/tap-google-analytics",
                        "pip_url": "git+https://github.com/MeltanoLabs/tap-google-analytics.git",
                        "capabilities": ["catalog", "discover", "state"],
                        "settings_group_validation": [
                            ["key_file_location", "view_id", "start_date"],
                            ["client_secrets", "view_id", "start_date"],
                            [
                                "oauth_credentials.client_id",
                                "oauth_credentials.client_secret",
                                "oauth_credentials.access_token",
                                "oauth_credentials.refresh_token",
                                "view_id",
                                "start_date",
                            ],
                        ],
                        "settings": [
                            {
                                "name": "key_file_location",
                                "kind": "file",
                                "description": "A file that contains the Google Analytics client secrets json.",  # noqa: E501
                                "value": "$MELTANO_PROJECT_ROOT/client_secrets.json",
                                "label": "Client Secrets File Location",
                                "placeholder": "Ex. client_secrets.json",
                            },
                            {
                                "name": "client_secrets",
                                "description": "An object that contains the Google Analytics client secrets.",  # noqa: E501
                                "kind": "object",
                                "label": "Client Secrets JSON",
                                "placeholder": "Ex. client_secrets.json",
                            },
                            {
                                "name": "oauth_credentials.client_id",
                                "description": "The Google Analytics oauth client ID.",
                                "sensitive": True,
                                "label": "OAuth Client ID",
                            },
                            {
                                "name": "oauth_credentials.client_secret",
                                "description": "The Google Analytics oauth client secret.",  # noqa: E501
                                "sensitive": True,
                                "label": "OAuth Client Secret",
                            },
                            {
                                "name": "oauth_credentials.access_token",
                                "description": "The Google Analytics oauth access token.",  # noqa: E501
                                "sensitive": True,
                                "label": "OAuth Access Token",
                            },
                            {
                                "name": "oauth_credentials.refresh_token",
                                "sensitive": True,
                                "description": "The Google Analytics oauth refresh token.",  # noqa: E501
                                "label": "OAuth Refresh Token",
                            },
                            {
                                "name": "view_id",
                                "description": "The ID for the view to fetch data from.",  # noqa: E501
                                "label": "View ID",
                                "placeholder": "Ex. 198343027",
                            },
                            {
                                "name": "reports",
                                "description": "The reports definition of which fields to retrieve from the view.",  # noqa: E501
                                "label": "Reports",
                                "placeholder": "Ex. my_report_definition.json",
                            },
                            {
                                "name": "start_date",
                                "label": "Start Date",
                                "kind": "date_iso8601",
                                "description": "This property determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "label": "End Date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "hidden": True,
                        "docs": "https://hub.meltano.com/extractors/google-analytics.html",
                        "repo": "https://gitlab.com/meltano/tap-google-analytics",
                        "pip_url": "git+https://gitlab.com/meltano/tap-google-analytics.git",
                        "capabilities": ["catalog", "discover"],
                        "settings_group_validation": [
                            ["key_file_location", "view_id", "start_date"],
                            [
                                "oauth_credentials.client_id",
                                "oauth_credentials.client_secret",
                                "oauth_credentials.access_token",
                                "oauth_credentials.refresh_token",
                                "view_id",
                                "start_date",
                            ],
                        ],
                        "settings": [
                            {
                                "name": "key_file_location",
                                "kind": "file",
                                "value": "$MELTANO_PROJECT_ROOT/client_secrets.json",
                                "label": "Client Secrets",
                                "placeholder": "Ex. client_secrets.json",
                            },
                            {
                                "name": "oauth_credentials.client_id",
                                "sensitive": True,
                                "label": "OAuth Client ID",
                            },
                            {
                                "name": "oauth_credentials.client_secret",
                                "sensitive": True,
                                "label": "OAuth Client Secret",
                            },
                            {
                                "name": "oauth_credentials.access_token",
                                "sensitive": True,
                                "label": "OAuth Access Token",
                            },
                            {
                                "name": "oauth_credentials.refresh_token",
                                "sensitive": True,
                                "label": "OAuth Refresh Token",
                            },
                            {
                                "name": "view_id",
                                "label": "View ID",
                                "placeholder": "Ex. 198343027",
                            },
                            {
                                "name": "reports",
                                "label": "Reports",
                                "placeholder": "Ex. my_report_definition.json",
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "This property determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "tap-facebook",
                "label": "Facebook Ads",
                "description": "Advertising Platform",
                "namespace": "tap_facebook",
                "variants": [
                    {
                        "name": "singer-io",
                        "docs": "https://hub.meltano.com/extractors/facebook.html",
                        "repo": "https://github.com/singer-io/tap-facebook",
                        "pip_url": "git+https://github.com/singer-io/tap-facebook.git",
                        "capabilities": ["properties", "discover", "state"],
                        "settings_group_validation": [
                            ["account_id", "access_token", "start_date"],
                        ],
                        "settings": [
                            {
                                "name": "account_id",
                                "label": "Account ID",
                                "placeholder": "Ex. 123456789012345",
                                "description": "Your Facebook Ads Account ID",
                            },
                            {
                                "name": "access_token",
                                "label": "Access Token",
                                "placeholder": "Ex. *****************",
                                "description": "User Token generated by Facebook OAuth handshake",  # noqa: E501
                                "kind": "oauth",
                                "oauth": {"provider": "facebook"},
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                            {
                                "name": "insights_buffer_days",
                                "kind": "integer",
                                "value": 0,
                                "label": "Ads Insights Buffer Days",
                                "description": "How many Days before the Start Date to fetch Ads Insights for",  # noqa: E501
                            },
                            {
                                "name": "include_deleted",
                                "kind": "boolean",
                                "label": "Include Deleted Objects",
                                "description": "Determines if it should include deleted objects or not.",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "hidden": True,
                        "repo": "https://gitlab.com/meltano/tap-facebook",
                        "pip_url": "git+https://gitlab.com/meltano/tap-facebook.git",
                        "capabilities": ["properties", "discover", "state"],
                        "settings_group_validation": [
                            ["account_id", "access_token", "start_date"],
                        ],
                        "settings": [
                            {
                                "name": "account_id",
                                "label": "Account ID",
                                "placeholder": "Ex. 123456789012345",
                                "description": "Your Facebook Ads Account ID",
                            },
                            {
                                "name": "access_token",
                                "label": "Access Token",
                                "placeholder": "Ex. *****************",
                                "description": "User Token generated by Facebook OAuth handshake",  # noqa: E501
                                "kind": "oauth",
                                "oauth": {"provider": "facebook"},
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                            {
                                "name": "insights_buffer_days",
                                "kind": "integer",
                                "value": 0,
                                "label": "Ads Insights Buffer Days",
                                "description": "How many Days before the Start Date to fetch Ads Insights for",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "tap-adwords",
                "label": "Google Ads",
                "description": "Advertising Platform",
                "namespace": "tap_adwords",
                "variants": [
                    {
                        "name": "singer-io",
                        "docs": "https://hub.meltano.com/extractors/adwords.html",
                        "repo": "https://github.com/singer-io/tap-adwords",
                        "pip_url": "git+https://github.com/singer-io/tap-adwords.git",
                        "capabilities": ["properties", "discover", "state"],
                        "select": [
                            "campaigns.*",
                            "ad_groups.*",
                            "ads.*",
                            "accounts.*",
                            "KEYWORDS_PERFORMANCE_REPORT.customerID",
                            "KEYWORDS_PERFORMANCE_REPORT.account",
                            "KEYWORDS_PERFORMANCE_REPORT.currency",
                            "KEYWORDS_PERFORMANCE_REPORT.timeZone",
                            "KEYWORDS_PERFORMANCE_REPORT.clientName",
                            "KEYWORDS_PERFORMANCE_REPORT.campaign",
                            "KEYWORDS_PERFORMANCE_REPORT.campaignID",
                            "KEYWORDS_PERFORMANCE_REPORT.campaignState",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroup",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroupID",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroupState",
                            "KEYWORDS_PERFORMANCE_REPORT.day",
                            "KEYWORDS_PERFORMANCE_REPORT.network",
                            "KEYWORDS_PERFORMANCE_REPORT.device",
                            "KEYWORDS_PERFORMANCE_REPORT.clicks",
                            "KEYWORDS_PERFORMANCE_REPORT.cost",
                            "KEYWORDS_PERFORMANCE_REPORT.impressions",
                            "KEYWORDS_PERFORMANCE_REPORT.interactions",
                            "KEYWORDS_PERFORMANCE_REPORT.engagements",
                            "KEYWORDS_PERFORMANCE_REPORT.conversions",
                            "KEYWORDS_PERFORMANCE_REPORT.allConv",
                            "KEYWORDS_PERFORMANCE_REPORT.views",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableImpressions",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableCost",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailClicksToWebsite",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailSaves",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailForwards",
                            "KEYWORDS_PERFORMANCE_REPORT.keywordID",
                            "KEYWORDS_PERFORMANCE_REPORT.keyword",
                            "KEYWORDS_PERFORMANCE_REPORT.keywordState",
                            "KEYWORDS_PERFORMANCE_REPORT.criterionServingStatus",
                            "KEYWORDS_PERFORMANCE_REPORT.destinationURL",
                            "KEYWORDS_PERFORMANCE_REPORT.matchType",
                            "KEYWORDS_PERFORMANCE_REPORT.topOfPageCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.firstPageCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.imprAbsTop",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewAvgCPM",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableCTR",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableImprImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableImprMeasurableImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.allConvRate",
                            "KEYWORDS_PERFORMANCE_REPORT.allConvValue",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCost",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPE",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPM",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPV",
                            "KEYWORDS_PERFORMANCE_REPORT.avgPosition",
                            "KEYWORDS_PERFORMANCE_REPORT.convRate",
                            "KEYWORDS_PERFORMANCE_REPORT.totalConvValue",
                            "KEYWORDS_PERFORMANCE_REPORT.costAllConv",
                            "KEYWORDS_PERFORMANCE_REPORT.costConv",
                            "KEYWORDS_PERFORMANCE_REPORT.costConvCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.crossDeviceConv",
                            "KEYWORDS_PERFORMANCE_REPORT.ctr",
                            "KEYWORDS_PERFORMANCE_REPORT.conversionsCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.convValueCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.engagementRate",
                            "KEYWORDS_PERFORMANCE_REPORT.interactionRate",
                            "KEYWORDS_PERFORMANCE_REPORT.interactionTypes",
                            "KEYWORDS_PERFORMANCE_REPORT.imprTop",
                            "KEYWORDS_PERFORMANCE_REPORT.valueAllConv",
                            "KEYWORDS_PERFORMANCE_REPORT.valueConv",
                            "KEYWORDS_PERFORMANCE_REPORT.valueConvCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo100",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo25",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo50",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo75",
                            "KEYWORDS_PERFORMANCE_REPORT.viewRate",
                            "KEYWORDS_PERFORMANCE_REPORT.viewThroughConv",
                            "KEYWORDS_PERFORMANCE_REPORT.searchAbsTopIS",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostAbsTopISBudget",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostTopISBudget",
                            "KEYWORDS_PERFORMANCE_REPORT.searchExactMatchIS",
                            "KEYWORDS_PERFORMANCE_REPORT.searchImprShare",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostAbsTopISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostTopISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchTopIS",
                            "AD_PERFORMANCE_REPORT.customerID",
                            "AD_PERFORMANCE_REPORT.account",
                            "AD_PERFORMANCE_REPORT.currency",
                            "AD_PERFORMANCE_REPORT.timeZone",
                            "AD_PERFORMANCE_REPORT.clientName",
                            "AD_PERFORMANCE_REPORT.campaign",
                            "AD_PERFORMANCE_REPORT.campaignID",
                            "AD_PERFORMANCE_REPORT.campaignState",
                            "AD_PERFORMANCE_REPORT.adGroup",
                            "AD_PERFORMANCE_REPORT.adGroupID",
                            "AD_PERFORMANCE_REPORT.adGroupState",
                            "AD_PERFORMANCE_REPORT.day",
                            "AD_PERFORMANCE_REPORT.network",
                            "AD_PERFORMANCE_REPORT.device",
                            "AD_PERFORMANCE_REPORT.clicks",
                            "AD_PERFORMANCE_REPORT.cost",
                            "AD_PERFORMANCE_REPORT.impressions",
                            "AD_PERFORMANCE_REPORT.interactions",
                            "AD_PERFORMANCE_REPORT.engagements",
                            "AD_PERFORMANCE_REPORT.conversions",
                            "AD_PERFORMANCE_REPORT.allConv",
                            "AD_PERFORMANCE_REPORT.views",
                            "AD_PERFORMANCE_REPORT.activeViewViewableImpressions",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableImpr",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableCost",
                            "AD_PERFORMANCE_REPORT.gmailClicksToWebsite",
                            "AD_PERFORMANCE_REPORT.gmailSaves",
                            "AD_PERFORMANCE_REPORT.gmailForwards",
                            "AD_PERFORMANCE_REPORT.adID",
                            "AD_PERFORMANCE_REPORT.adState",
                            "AD_PERFORMANCE_REPORT.approvalStatus",
                            "AD_PERFORMANCE_REPORT.adType",
                            "AD_PERFORMANCE_REPORT.adStrength",
                            "AD_PERFORMANCE_REPORT.autoAppliedAdSuggestion",
                            "AD_PERFORMANCE_REPORT.ad",
                            "AD_PERFORMANCE_REPORT.descriptionLine1",
                            "AD_PERFORMANCE_REPORT.descriptionLine2",
                            "AD_PERFORMANCE_REPORT.finalURL",
                            "AD_PERFORMANCE_REPORT.displayURL",
                            "AD_PERFORMANCE_REPORT.description",
                            "AD_PERFORMANCE_REPORT.headline1",
                            "AD_PERFORMANCE_REPORT.headline2",
                            "AD_PERFORMANCE_REPORT.path1",
                            "AD_PERFORMANCE_REPORT.businessName",
                            "AD_PERFORMANCE_REPORT.callToActionTextResponsive",
                            "AD_PERFORMANCE_REPORT.shortHeadline",
                            "AD_PERFORMANCE_REPORT.longHeadline",
                            "AD_PERFORMANCE_REPORT.promotionTextResponsive",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdPath1",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdHeadlines",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdDescriptions",
                            "AD_PERFORMANCE_REPORT.gmailAdBusinessName",
                            "AD_PERFORMANCE_REPORT.gmailAdHeadline",
                            "AD_PERFORMANCE_REPORT.gmailAdDescription",
                            "AD_PERFORMANCE_REPORT.imageAdName",
                            "AD_PERFORMANCE_REPORT.businessNameMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.longHeadlineMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.headlinesMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.callToActionTextMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.promotionTextMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.imprAbsTop",
                            "AD_PERFORMANCE_REPORT.activeViewAvgCPM",
                            "AD_PERFORMANCE_REPORT.activeViewViewableCTR",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableImprImpr",
                            "AD_PERFORMANCE_REPORT.activeViewViewableImprMeasurableImpr",
                            "AD_PERFORMANCE_REPORT.allConvRate",
                            "AD_PERFORMANCE_REPORT.allConvValue",
                            "AD_PERFORMANCE_REPORT.avgCost",
                            "AD_PERFORMANCE_REPORT.avgCPC",
                            "AD_PERFORMANCE_REPORT.avgCPE",
                            "AD_PERFORMANCE_REPORT.avgCPM",
                            "AD_PERFORMANCE_REPORT.avgCPV",
                            "AD_PERFORMANCE_REPORT.avgPosition",
                            "AD_PERFORMANCE_REPORT.convRate",
                            "AD_PERFORMANCE_REPORT.totalConvValue",
                            "AD_PERFORMANCE_REPORT.costAllConv",
                            "AD_PERFORMANCE_REPORT.costConv",
                            "AD_PERFORMANCE_REPORT.costConvCurrentModel",
                            "AD_PERFORMANCE_REPORT.crossDeviceConv",
                            "AD_PERFORMANCE_REPORT.ctr",
                            "AD_PERFORMANCE_REPORT.conversionsCurrentModel",
                            "AD_PERFORMANCE_REPORT.convValueCurrentModel",
                            "AD_PERFORMANCE_REPORT.engagementRate",
                            "AD_PERFORMANCE_REPORT.interactionRate",
                            "AD_PERFORMANCE_REPORT.interactionTypes",
                            "AD_PERFORMANCE_REPORT.imprTop",
                            "AD_PERFORMANCE_REPORT.valueAllConv",
                            "AD_PERFORMANCE_REPORT.valueConv",
                            "AD_PERFORMANCE_REPORT.valueConvCurrentModel",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo100",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo25",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo50",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo75",
                            "AD_PERFORMANCE_REPORT.viewRate",
                            "AD_PERFORMANCE_REPORT.viewThroughConv",
                        ],
                        "settings_group_validation": [
                            [
                                "developer_token",
                                "oauth_client_id",
                                "oauth_client_secret",
                                "refresh_token",
                                "user_agent",
                                "customer_ids",
                                "start_date",
                            ],
                        ],
                        "settings": [
                            {
                                "name": "developer_token",
                                "sensitive": True,
                                "label": "Developer Token",
                                "description": "Your Developer Token for Google AdWord Application",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "oauth_client_id",
                                "sensitive": True,
                                "label": "OAuth Client ID",
                                "description": "Your Google OAuth Client ID",
                                "placeholder": "Ex. 123456789012345.apps.googleusercontent.com",  # noqa: E501
                            },
                            {
                                "name": "oauth_client_secret",
                                "sensitive": True,
                                "label": "OAuth Client Secret",
                                "description": "Your Google OAuth Client Secret",
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "refresh_token",
                                "kind": "oauth",
                                "oauth": {"provider": "google-adwords"},
                                "label": "Access Token",
                                "description": "The Refresh Token generated through the OAuth flow run using your OAuth Client and your Developer Token",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "customer_ids",
                                "label": "Account ID(s)",
                                "placeholder": "Ex. 1234567890,1234567891,1234567892",
                                "description": "A comma-separated list of Ad Account IDs to replicate data from",  # noqa: E501
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                            {
                                "name": "user_agent",
                                "value": "tap-adwords via Meltano",
                                "label": "User Agent for your OAuth Client",
                                "placeholder": "Ex. tap-adwords via Meltano <user@example.com>",  # noqa: E501
                                "description": "The User Agent for your OAuth Client (used in requests made to the AdWords API)",  # noqa: E501
                            },
                            {
                                "name": "conversion_window_days",
                                "kind": "integer",
                                "value": 0,
                                "label": "Conversion Window Days",
                                "description": "How many Days before the Start Date to fetch data for Performance Reports",  # noqa: E501
                            },
                            {
                                "name": "primary_keys",
                                "kind": "object",
                                "value": {
                                    "KEYWORDS_PERFORMANCE_REPORT": [
                                        "customerID",
                                        "campaignID",
                                        "adGroupID",
                                        "keywordID",
                                        "day",
                                        "network",
                                        "device",
                                    ],
                                    "AD_PERFORMANCE_REPORT": [
                                        "customerID",
                                        "campaignID",
                                        "adGroupID",
                                        "adID",
                                        "day",
                                        "network",
                                        "device",
                                    ],
                                },
                                "label": "Primary Keys",
                                "description": "Primary Keys for the selected Entities (Streams)",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "hidden": True,
                        "repo": "https://gitlab.com/meltano/tap-adwords",
                        "pip_url": "git+https://gitlab.com/meltano/tap-adwords.git",
                        "capabilities": ["properties", "discover", "state"],
                        "select": [
                            "campaigns.*",
                            "ad_groups.*",
                            "ads.*",
                            "accounts.*",
                            "KEYWORDS_PERFORMANCE_REPORT.customerID",
                            "KEYWORDS_PERFORMANCE_REPORT.account",
                            "KEYWORDS_PERFORMANCE_REPORT.currency",
                            "KEYWORDS_PERFORMANCE_REPORT.timeZone",
                            "KEYWORDS_PERFORMANCE_REPORT.clientName",
                            "KEYWORDS_PERFORMANCE_REPORT.campaign",
                            "KEYWORDS_PERFORMANCE_REPORT.campaignID",
                            "KEYWORDS_PERFORMANCE_REPORT.campaignState",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroup",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroupID",
                            "KEYWORDS_PERFORMANCE_REPORT.adGroupState",
                            "KEYWORDS_PERFORMANCE_REPORT.day",
                            "KEYWORDS_PERFORMANCE_REPORT.network",
                            "KEYWORDS_PERFORMANCE_REPORT.device",
                            "KEYWORDS_PERFORMANCE_REPORT.clicks",
                            "KEYWORDS_PERFORMANCE_REPORT.cost",
                            "KEYWORDS_PERFORMANCE_REPORT.impressions",
                            "KEYWORDS_PERFORMANCE_REPORT.interactions",
                            "KEYWORDS_PERFORMANCE_REPORT.engagements",
                            "KEYWORDS_PERFORMANCE_REPORT.conversions",
                            "KEYWORDS_PERFORMANCE_REPORT.allConv",
                            "KEYWORDS_PERFORMANCE_REPORT.views",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableImpressions",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableCost",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailClicksToWebsite",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailSaves",
                            "KEYWORDS_PERFORMANCE_REPORT.gmailForwards",
                            "KEYWORDS_PERFORMANCE_REPORT.keywordID",
                            "KEYWORDS_PERFORMANCE_REPORT.keyword",
                            "KEYWORDS_PERFORMANCE_REPORT.keywordState",
                            "KEYWORDS_PERFORMANCE_REPORT.criterionServingStatus",
                            "KEYWORDS_PERFORMANCE_REPORT.destinationURL",
                            "KEYWORDS_PERFORMANCE_REPORT.matchType",
                            "KEYWORDS_PERFORMANCE_REPORT.topOfPageCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.firstPageCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.imprAbsTop",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewAvgCPM",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableCTR",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewMeasurableImprImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.activeViewViewableImprMeasurableImpr",
                            "KEYWORDS_PERFORMANCE_REPORT.allConvRate",
                            "KEYWORDS_PERFORMANCE_REPORT.allConvValue",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCost",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPC",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPE",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPM",
                            "KEYWORDS_PERFORMANCE_REPORT.avgCPV",
                            "KEYWORDS_PERFORMANCE_REPORT.avgPosition",
                            "KEYWORDS_PERFORMANCE_REPORT.convRate",
                            "KEYWORDS_PERFORMANCE_REPORT.totalConvValue",
                            "KEYWORDS_PERFORMANCE_REPORT.costAllConv",
                            "KEYWORDS_PERFORMANCE_REPORT.costConv",
                            "KEYWORDS_PERFORMANCE_REPORT.costConvCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.crossDeviceConv",
                            "KEYWORDS_PERFORMANCE_REPORT.ctr",
                            "KEYWORDS_PERFORMANCE_REPORT.conversionsCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.convValueCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.engagementRate",
                            "KEYWORDS_PERFORMANCE_REPORT.interactionRate",
                            "KEYWORDS_PERFORMANCE_REPORT.interactionTypes",
                            "KEYWORDS_PERFORMANCE_REPORT.imprTop",
                            "KEYWORDS_PERFORMANCE_REPORT.valueAllConv",
                            "KEYWORDS_PERFORMANCE_REPORT.valueConv",
                            "KEYWORDS_PERFORMANCE_REPORT.valueConvCurrentModel",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo100",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo25",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo50",
                            "KEYWORDS_PERFORMANCE_REPORT.videoPlayedTo75",
                            "KEYWORDS_PERFORMANCE_REPORT.viewRate",
                            "KEYWORDS_PERFORMANCE_REPORT.viewThroughConv",
                            "KEYWORDS_PERFORMANCE_REPORT.searchAbsTopIS",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostAbsTopISBudget",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostTopISBudget",
                            "KEYWORDS_PERFORMANCE_REPORT.searchExactMatchIS",
                            "KEYWORDS_PERFORMANCE_REPORT.searchImprShare",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostAbsTopISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchLostTopISRank",
                            "KEYWORDS_PERFORMANCE_REPORT.searchTopIS",
                            "AD_PERFORMANCE_REPORT.customerID",
                            "AD_PERFORMANCE_REPORT.account",
                            "AD_PERFORMANCE_REPORT.currency",
                            "AD_PERFORMANCE_REPORT.timeZone",
                            "AD_PERFORMANCE_REPORT.clientName",
                            "AD_PERFORMANCE_REPORT.campaign",
                            "AD_PERFORMANCE_REPORT.campaignID",
                            "AD_PERFORMANCE_REPORT.campaignState",
                            "AD_PERFORMANCE_REPORT.adGroup",
                            "AD_PERFORMANCE_REPORT.adGroupID",
                            "AD_PERFORMANCE_REPORT.adGroupState",
                            "AD_PERFORMANCE_REPORT.day",
                            "AD_PERFORMANCE_REPORT.network",
                            "AD_PERFORMANCE_REPORT.device",
                            "AD_PERFORMANCE_REPORT.clicks",
                            "AD_PERFORMANCE_REPORT.cost",
                            "AD_PERFORMANCE_REPORT.impressions",
                            "AD_PERFORMANCE_REPORT.interactions",
                            "AD_PERFORMANCE_REPORT.engagements",
                            "AD_PERFORMANCE_REPORT.conversions",
                            "AD_PERFORMANCE_REPORT.allConv",
                            "AD_PERFORMANCE_REPORT.views",
                            "AD_PERFORMANCE_REPORT.activeViewViewableImpressions",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableImpr",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableCost",
                            "AD_PERFORMANCE_REPORT.gmailClicksToWebsite",
                            "AD_PERFORMANCE_REPORT.gmailSaves",
                            "AD_PERFORMANCE_REPORT.gmailForwards",
                            "AD_PERFORMANCE_REPORT.adID",
                            "AD_PERFORMANCE_REPORT.adState",
                            "AD_PERFORMANCE_REPORT.approvalStatus",
                            "AD_PERFORMANCE_REPORT.adType",
                            "AD_PERFORMANCE_REPORT.adStrength",
                            "AD_PERFORMANCE_REPORT.autoAppliedAdSuggestion",
                            "AD_PERFORMANCE_REPORT.ad",
                            "AD_PERFORMANCE_REPORT.descriptionLine1",
                            "AD_PERFORMANCE_REPORT.descriptionLine2",
                            "AD_PERFORMANCE_REPORT.finalURL",
                            "AD_PERFORMANCE_REPORT.displayURL",
                            "AD_PERFORMANCE_REPORT.description",
                            "AD_PERFORMANCE_REPORT.headline1",
                            "AD_PERFORMANCE_REPORT.headline2",
                            "AD_PERFORMANCE_REPORT.path1",
                            "AD_PERFORMANCE_REPORT.businessName",
                            "AD_PERFORMANCE_REPORT.callToActionTextResponsive",
                            "AD_PERFORMANCE_REPORT.shortHeadline",
                            "AD_PERFORMANCE_REPORT.longHeadline",
                            "AD_PERFORMANCE_REPORT.promotionTextResponsive",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdPath1",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdHeadlines",
                            "AD_PERFORMANCE_REPORT.responsiveSearchAdDescriptions",
                            "AD_PERFORMANCE_REPORT.gmailAdBusinessName",
                            "AD_PERFORMANCE_REPORT.gmailAdHeadline",
                            "AD_PERFORMANCE_REPORT.gmailAdDescription",
                            "AD_PERFORMANCE_REPORT.imageAdName",
                            "AD_PERFORMANCE_REPORT.businessNameMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.longHeadlineMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.headlinesMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.callToActionTextMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.promotionTextMultiAssetResponsiveDisplay",
                            "AD_PERFORMANCE_REPORT.imprAbsTop",
                            "AD_PERFORMANCE_REPORT.activeViewAvgCPM",
                            "AD_PERFORMANCE_REPORT.activeViewViewableCTR",
                            "AD_PERFORMANCE_REPORT.activeViewMeasurableImprImpr",
                            "AD_PERFORMANCE_REPORT.activeViewViewableImprMeasurableImpr",
                            "AD_PERFORMANCE_REPORT.allConvRate",
                            "AD_PERFORMANCE_REPORT.allConvValue",
                            "AD_PERFORMANCE_REPORT.avgCost",
                            "AD_PERFORMANCE_REPORT.avgCPC",
                            "AD_PERFORMANCE_REPORT.avgCPE",
                            "AD_PERFORMANCE_REPORT.avgCPM",
                            "AD_PERFORMANCE_REPORT.avgCPV",
                            "AD_PERFORMANCE_REPORT.avgPosition",
                            "AD_PERFORMANCE_REPORT.convRate",
                            "AD_PERFORMANCE_REPORT.totalConvValue",
                            "AD_PERFORMANCE_REPORT.costAllConv",
                            "AD_PERFORMANCE_REPORT.costConv",
                            "AD_PERFORMANCE_REPORT.costConvCurrentModel",
                            "AD_PERFORMANCE_REPORT.crossDeviceConv",
                            "AD_PERFORMANCE_REPORT.ctr",
                            "AD_PERFORMANCE_REPORT.conversionsCurrentModel",
                            "AD_PERFORMANCE_REPORT.convValueCurrentModel",
                            "AD_PERFORMANCE_REPORT.engagementRate",
                            "AD_PERFORMANCE_REPORT.interactionRate",
                            "AD_PERFORMANCE_REPORT.interactionTypes",
                            "AD_PERFORMANCE_REPORT.imprTop",
                            "AD_PERFORMANCE_REPORT.valueAllConv",
                            "AD_PERFORMANCE_REPORT.valueConv",
                            "AD_PERFORMANCE_REPORT.valueConvCurrentModel",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo100",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo25",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo50",
                            "AD_PERFORMANCE_REPORT.videoPlayedTo75",
                            "AD_PERFORMANCE_REPORT.viewRate",
                            "AD_PERFORMANCE_REPORT.viewThroughConv",
                        ],
                        "settings_group_validation": [
                            [
                                "developer_token",
                                "oauth_client_id",
                                "oauth_client_secret",
                                "refresh_token",
                                "user_agent",
                                "customer_ids",
                                "start_date",
                            ],
                        ],
                        "settings": [
                            {
                                "name": "developer_token",
                                "sensitive": True,
                                "label": "Developer Token",
                                "description": "Your Developer Token for Google AdWord Application",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "oauth_client_id",
                                "sensitive": True,
                                "label": "OAuth Client ID",
                                "description": "Your Google OAuth Client ID",
                                "placeholder": "Ex. 123456789012345.apps.googleusercontent.com",  # noqa: E501
                            },
                            {
                                "name": "oauth_client_secret",
                                "sensitive": True,
                                "label": "OAuth Client Secret",
                                "description": "Your Google OAuth Client Secret",
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "refresh_token",
                                "kind": "oauth",
                                "oauth": {"provider": "google-adwords"},
                                "label": "Access Token",
                                "description": "The Refresh Token generated through the OAuth flow run using your OAuth Client and your Developer Token",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "customer_ids",
                                "label": "Account ID(s)",
                                "placeholder": "Ex. 1234567890,1234567891,1234567892",
                                "description": "A comma-separated list of Ad Account IDs to replicate data from",  # noqa: E501
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                            {
                                "name": "end_date",
                                "kind": "date_iso8601",
                                "description": "Date up to when historical data will be extracted.",  # noqa: E501
                            },
                            {
                                "name": "user_agent",
                                "value": "tap-adwords via Meltano",
                                "label": "User Agent for your OAuth Client",
                                "placeholder": "Ex. tap-adwords via Meltano <user@example.com>",  # noqa: E501
                                "description": "The User Agent for your OAuth Client (used in requests made to the AdWords API)",  # noqa: E501
                            },
                            {
                                "name": "conversion_window_days",
                                "kind": "integer",
                                "value": 0,
                                "label": "Conversion Window Days",
                                "description": "How many Days before the Start Date to fetch data for Performance Reports",  # noqa: E501
                            },
                            {
                                "name": "primary_keys",
                                "kind": "object",
                                "value": {
                                    "KEYWORDS_PERFORMANCE_REPORT": [
                                        "customerID",
                                        "campaignID",
                                        "adGroupID",
                                        "keywordID",
                                        "day",
                                        "network",
                                        "device",
                                    ],
                                    "AD_PERFORMANCE_REPORT": [
                                        "customerID",
                                        "campaignID",
                                        "adGroupID",
                                        "adID",
                                        "day",
                                        "network",
                                        "device",
                                    ],
                                },
                                "label": "Primary Keys",
                                "description": "Primary Keys for the selected Entities (Streams)",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "tap-carbon-intensity",
                "label": "Carbon Emissions Intensity",
                "description": "National Grid ESO's Carbon Emissions Intensity API",
                "namespace": "tap_carbon_intensity",
                "variants": [
                    {
                        "name": "meltano",
                        "hidden": True,
                        "repo": "https://gitlab.com/meltano/tap-carbon-intensity",
                        "pip_url": "git+https://gitlab.com/meltano/tap-carbon-intensity.git",
                        "capabilities": ["discover"],
                    },
                ],
            },
            {
                "name": "tap-gitlab",
                "label": "GitLab",
                "description": "Single application for the entire DevOps lifecycle",
                "namespace": "tap_gitlab",
                "variants": [
                    {
                        "name": "meltanolabs",
                        "docs": "https://hub.meltano.com/extractors/gitlab.html",
                        "repo": "https://github.com/MeltanoLabs/tap-gitlab",
                        "pip_url": "git+https://github.com/MeltanoLabs/tap-gitlab.git",
                        "capabilities": ["catalog", "discover", "state"],
                        "settings_group_validation": [
                            ["api_url", "groups", "start_date"],
                            ["api_url", "projects", "start_date"],
                        ],
                        "settings": [
                            {
                                "name": "api_url",
                                "label": "GitLab Instance",
                                "value": "https://gitlab.com",
                                "description": "GitLab API/instance URL. When an API path is omitted, `/api/v4/` is assumed.",  # noqa: E501
                            },
                            {
                                "name": "private_token",
                                "sensitive": True,
                                "value": "",
                                "label": "Access Token",
                                "description": "GitLab personal access token or other API token.",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "groups",
                                "value": "",
                                "label": "Groups",
                                "description": "Space-separated names of groups to extract data from. Leave empty and provide a project name if you'd like to pull data from a project in a personal user namespace.",  # noqa: E501
                                "placeholder": "Ex. my-organization",
                            },
                            {
                                "name": "projects",
                                "value": "",
                                "label": "Project",
                                "description": "Space-separated `namespace/project` paths of projects to extract data from. Leave empty and provide a group name to extract data from all group projects.",  # noqa: E501
                                "placeholder": "Ex. my-organization/project-1",
                            },
                            {
                                "name": "ultimate_license",
                                "kind": "boolean",
                                "value": False,
                                "description": "Enable to pull in extra data (like Epics, Epic Issues and other entities) only available to GitLab Ultimate and GitLab.com Gold accounts.",  # noqa: E501
                            },
                            {
                                "name": "fetch_merge_request_commits",
                                "kind": "boolean",
                                "value": False,
                                "description": "For each Merge Request, also fetch the MR's commits and create the join table `merge_request_commits` with the Merge Request and related Commit IDs. This can slow down extraction considerably because of the many API calls required.",  # noqa: E501
                            },
                            {
                                "name": "fetch_pipelines_extended",
                                "kind": "boolean",
                                "value": False,
                                "description": "For every Pipeline, also fetch extended details of each of these pipelines. This can slow down extraction considerably because of the many API calls required.",  # noqa: E501
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "hidden": True,
                        "repo": "https://gitlab.com/meltano/tap-gitlab",
                        "pip_url": "git+https://gitlab.com/meltano/tap-gitlab.git",
                        "capabilities": ["catalog", "discover", "state"],
                        "settings_group_validation": [
                            ["api_url", "groups", "start_date"],
                            ["api_url", "projects", "start_date"],
                        ],
                        "settings": [
                            {
                                "name": "api_url",
                                "label": "GitLab Instance",
                                "value": "https://gitlab.com",
                                "description": "GitLab API/instance URL. When an API path is omitted, `/api/v4/` is assumed.",  # noqa: E501
                            },
                            {
                                "name": "private_token",
                                "sensitive": True,
                                "value": "",
                                "label": "Access Token",
                                "description": "GitLab personal access token or other API token.",  # noqa: E501
                                "placeholder": "Ex. *****************",
                            },
                            {
                                "name": "groups",
                                "value": "",
                                "label": "Groups",
                                "description": "Space-separated names of groups to extract data from. Leave empty and provide a project name if you'd like to pull data from a project in a personal user namespace.",  # noqa: E501
                                "placeholder": "Ex. my-organization",
                            },
                            {
                                "name": "projects",
                                "value": "",
                                "label": "Project",
                                "description": "Space-separated `namespace/project` paths of projects to extract data from. Leave empty and provide a group name to extract data from all group projects.",  # noqa: E501
                                "placeholder": "Ex. my-organization/project-1",
                            },
                            {
                                "name": "ultimate_license",
                                "kind": "boolean",
                                "value": False,
                                "description": "Enable to pull in extra data (like Epics, Epic Issues and other entities) only available to GitLab Ultimate and GitLab.com Gold accounts.",  # noqa: E501
                            },
                            {
                                "name": "fetch_merge_request_commits",
                                "kind": "boolean",
                                "value": False,
                                "description": "For each Merge Request, also fetch the MR's commits and create the join table `merge_request_commits` with the Merge Request and related Commit IDs. This can slow down extraction considerably because of the many API calls required.",  # noqa: E501
                            },
                            {
                                "name": "fetch_pipelines_extended",
                                "kind": "boolean",
                                "value": False,
                                "description": "For every Pipeline, also fetch extended details of each of these pipelines. This can slow down extraction considerably because of the many API calls required.",  # noqa: E501
                            },
                            {
                                "name": "start_date",
                                "kind": "date_iso8601",
                                "description": "Determines how much historical data will be extracted. Please be aware that the larger the time period and amount of data, the longer the initial extraction can be expected to take.",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "tap-mock",
                "label": "Mock",
                "namespace": "tap_mock",
                "variants": [
                    {
                        "name": "meltano",
                        "pip_url": "tap-mock",
                        "executable": "tap-mock",
                        "capabilities": ["discover", "catalog", "state"],
                        "settings": [
                            {"name": "test", "value": "mock"},
                            {"name": "start_date"},
                            {"name": "secure", "sensitive": True},
                            {"name": "port", "kind": "integer", "value": 5000},
                            {"name": "list", "kind": "array", "value": []},
                            {
                                "name": "object",
                                "aliases": ["data"],
                                "kind": "object",
                                "value": {"nested": "from_default"},
                            },
                            {
                                "name": "hidden",
                                "kind": "integer",
                                "value": 42,
                                "hidden": True,
                            },
                            {"name": "boolean", "kind": "boolean"},
                            {"name": "auth.username"},
                            {"name": "auth.password", "sensitive": True},
                            {
                                "name": "aliased",
                                "kind": "string",
                                "aliases": ["aliased_1", "aliased_2", "aliased_3"],
                            },
                            {"name": "stacked_env_var", "kind": "string"},
                        ],
                        "commands": {
                            "cmd": {
                                "args": "cmd meltano",
                                "description": "a description of cmd",
                            },
                            "cmd-variant": "cmd-variant meltano",
                            "test": {
                                "args": "--test",
                                "description": "Run tests",
                            },
                            "test_extra": {
                                "args": "test_extra",
                                "description": "Run extra tests",
                                "executable": "test-extra",
                            },
                        },
                    },
                    {
                        "name": "singer-io",
                        "original": True,
                        "deprecated": True,
                        "pip_url": "singer-tap-mock",
                    },
                ],
            },
            {
                "name": "tap-mock-noinstall",
                "label": "Mock",
                "namespace": "tap_mock_noinstall",
                "variants": [
                    {
                        "name": "meltano",
                        "executable": "tap-mock-noinstall",
                        "capabilities": ["discover", "catalog", "state"],
                        "settings": [
                            {"name": "test", "value": "mock"},
                            {"name": "start_date"},
                        ],
                    },
                ],
            },
        ],
        PluginType.LOADERS: [
            {
                "name": "target-sqlite",
                "label": "SQLite",
                "description": "SQLite database loader",
                "namespace": "target_sqlite",
                "variants": [
                    {
                        "name": "meltanolabs",
                        "docs": "https://hub.meltano.com/loaders/sqlite.html",
                        "repo": "https://github.com/MeltanoLabs/target-sqlite",
                        "pip_url": "git+https://github.com/MeltanoLabs/target-sqlite.git",
                        "dialect": "sqlite",
                        "settings_group_validation": [["batch_size"]],
                        "settings": [
                            {
                                "name": "database",
                                "label": "Database Name",
                                "description": "Name of the SQLite database file to be used or created, relative to the project root. The `.db` extension is optional and will be added automatically when omitted.",  # noqa: E501
                                "value": "warehouse",
                            },
                            {
                                "name": "batch_size",
                                "label": "Batch Size",
                                "kind": "integer",
                                "value": 50,
                                "description": "How many records are sent to SQLite at a time?",  # noqa: E501
                            },
                            {
                                "name": "timestamp_column",
                                "label": "Timestamp Column",
                                "value": "__loaded_at",
                                "description": "Name of the column used for recording the timestamp when Data are loaded to SQLite.",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "hidden": True,
                        "repo": "https://gitlab.com/meltano/target-sqlite",
                        "pip_url": "git+https://gitlab.com/meltano/target-sqlite.git",
                        "dialect": "sqlite",
                        "settings_group_validation": [["batch_size"]],
                        "settings": [
                            {
                                "name": "database",
                                "label": "Database Name",
                                "description": "Name of the SQLite database file to be used or created, relative to the project root. The `.db` extension is optional and will be added automatically when omitted.",  # noqa: E501
                                "value": "warehouse",
                            },
                            {
                                "name": "batch_size",
                                "kind": "integer",
                                "value": 50,
                                "description": "How many records are sent to SQLite at a time?",  # noqa: E501
                            },
                            {
                                "name": "timestamp_column",
                                "value": "__loaded_at",
                                "description": "Name of the column used for recording the timestamp when Data are loaded to SQLite.",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "target-csv",
                "label": "Comma Separated Values (CSV)",
                "description": "CSV loader",
                "namespace": "target_csv",
                "variants": [
                    {
                        "name": "hotgluexyz",
                        "docs": "https://hub.meltano.com/loaders/csv.html",
                        "repo": "https://github.com/hotgluexyz/target-csv",
                        "pip_url": "git+https://github.com/hotgluexyz/target-csv.git@0.3.3",
                        "settings": [
                            {
                                "name": "destination_path",
                                "description": 'Sets the destination path the CSV files are written to, relative to the project root. The directory needs to exist already, it will not be created automatically. To write CSV files to the project root, set an empty string (`""`).',  # noqa: E501
                                "value": "output",
                            },
                            {
                                "name": "delimiter",
                                "kind": "options",
                                "options": [
                                    {"label": "Comma (,)", "value": ","},
                                    {"label": "Tab (  )", "value": "\\t"},
                                    {"label": "Semi-colon (;)", "value": ";"},
                                    {"label": "Pipe (|)", "value": "|"},
                                ],
                                "value": ",",
                                "description": "A one-character string used to separate fields. It defaults to a comma (,).",  # noqa: E501
                            },
                            {
                                "name": "quotechar",
                                "kind": "options",
                                "options": [
                                    {"label": "Single Quote (')", "value": "'"},
                                    {"label": 'Double Quote (")', "value": '"'},
                                ],
                                "value": "'",
                                "description": "A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to single quote (').",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "singer-io",
                        "docs": "https://hub.meltano.com/loaders/csv.html",
                        "repo": "https://github.com/singer-io/target-csv",
                        "pip_url": "target-csv",
                        "settings": [
                            {
                                "name": "destination_path",
                                "description": 'Sets the destination path the CSV files are written to, relative to the project root. The directory needs to exist already, it will not be created automatically. To write CSV files to the project root, set an empty string (`""`).',  # noqa: E501
                                "value": "output",
                            },
                            {
                                "name": "delimiter",
                                "kind": "options",
                                "options": [
                                    {"label": "Comma (,)", "value": ","},
                                    {"label": "Tab (  )", "value": "\\t"},
                                    {"label": "Semi-colon (;)", "value": ";"},
                                    {"label": "Pipe (|)", "value": "|"},
                                ],
                                "value": ",",
                                "description": "A one-character string used to separate fields. It defaults to a comma (,).",  # noqa: E501
                            },
                            {
                                "name": "quotechar",
                                "kind": "options",
                                "options": [
                                    {"label": "Single Quote (')", "value": "'"},
                                    {"label": 'Double Quote (")', "value": '"'},
                                ],
                                "value": "'",
                                "description": "A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to single quote (').",  # noqa: E501
                            },
                        ],
                    },
                ],
            },
            {
                "name": "target-postgres",
                "label": "PostgreSQL",
                "description": "PostgreSQL database loader",
                "namespace": "target_postgres",
                "dialect": "postgres",
                "variants": [
                    {
                        "name": "transferwise",
                        "docs": "https://hub.meltano.com/loaders/postgres.html",
                        "repo": "https://github.com/transferwise/pipelinewise-target-postgres",
                        "pip_url": "pipelinewise-target-postgres",
                        "settings_group_validation": [
                            [
                                "host",
                                "port",
                                "user",
                                "password",
                                "dbname",
                                "default_target_schema",
                            ],
                        ],
                        "settings": [
                            {
                                "name": "host",
                                "value": "localhost",
                                "description": "PostgreSQL host",
                                "label": "Host",
                            },
                            {
                                "name": "port",
                                "kind": "integer",
                                "value": 5432,
                                "description": "PostgreSQL port",
                                "label": "Port",
                            },
                            {
                                "name": "user",
                                "description": "PostgreSQL user",
                                "label": "User",
                            },
                            {
                                "name": "password",
                                "sensitive": True,
                                "description": "PostgreSQL password",
                                "label": "Password",
                            },
                            {
                                "name": "dbname",
                                "description": "PostgreSQL database name",
                                "label": "Database Name",
                            },
                            {
                                "name": "ssl",
                                "kind": "boolean",
                                "value": False,
                                "value_post_processor": "stringify",
                                "label": "SSL",
                            },
                            {
                                "name": "default_target_schema",
                                "aliases": ["schema"],
                                "env": "TARGET_POSTGRES_SCHEMA",
                                "value": "$MELTANO_EXTRACT__LOAD_SCHEMA",
                                "description": "Name of the schema where the tables will be created. If `schema_mapping` is not defined then every stream sent by the tap is loaded into this schema.",  # noqa: E501
                                "label": "Default Target Schema",
                            },
                            {
                                "name": "batch_size_rows",
                                "kind": "integer",
                                "value": 100000,
                                "description": "Maximum number of rows in each batch. At the end of each batch, the rows in the batch are loaded into Postgres.",  # noqa: E501
                                "label": "Batch Size Rows",
                            },
                            {
                                "name": "flush_all_streams",
                                "kind": "boolean",
                                "value": False,
                                "description": "Flush and load every stream into Postgres when one batch is full. Warning: This may trigger the COPY command to use files with low number of records.",  # noqa: E501
                                "label": "Flush All Streams",
                            },
                            {
                                "name": "parallelism",
                                "kind": "integer",
                                "value": 0,
                                "description": "The number of threads used to flush tables. 0 will create a thread for each stream, up to parallelism_max. -1 will create a thread for each CPU core. Any other positive number will create that number of threads, up to parallelism_max.",  # noqa: E501
                                "label": "Parallelism",
                            },
                            {
                                "name": "parallelism_max",
                                "kind": "integer",
                                "value": 16,
                                "description": "Max number of parallel threads to use when flushing tables.",  # noqa: E501
                                "label": "Max Parallelism",
                            },
                            {
                                "name": "default_target_schema_select_permission",
                                "description": "Grant USAGE privilege on newly created schemas and grant SELECT privilege on newly created tables to a specific role or a list of roles. If `schema_mapping` is not defined then every stream sent by the tap is granted accordingly.",  # noqa: E501
                                "label": "Default Target Schema Select Permission",
                            },
                            {
                                "name": "schema_mapping",
                                "kind": "object",
                                "description": "Useful if you want to load multiple streams from one tap to multiple Postgres schemas.\nIf the tap sends the `stream_id` in `<schema_name>-<table_name>` format then this option overwrites the `default_target_schema` value. Note, that using `schema_mapping` you can overwrite the `default_target_schema_select_permission` value to grant SELECT permissions to different groups per schemas or optionally you can create indices automatically for the replicated tables.\n",  # noqa: E501
                                "label": "Schema Mapping",
                            },
                            {
                                "name": "add_metadata_columns",
                                "kind": "boolean",
                                "value": False,
                                "description": "Metadata columns add extra row level information about data ingestions, (i.e. when was the row read in source, when was inserted or deleted in postgres etc.) Metadata columns are creating automatically by adding extra columns to the tables with a column prefix `_SDC_`. The column names are following the stitch naming conventions documented at https://www.stitchdata.com/docs/data-structure/integration-schemas#sdc-columns. Enabling metadata columns will flag the deleted rows by setting the `_SDC_DELETED_AT` metadata column. Without the `add_metadata_columns` option the deleted rows from singer taps will not be recongisable in Postgres.",  # noqa: E501
                                "label": "Add Metadata Columns",
                            },
                            {
                                "name": "hard_delete",
                                "kind": "boolean",
                                "value": False,
                                "description": "When `hard_delete` option is true then DELETE SQL commands will be performed in Postgres to delete rows in tables. It's achieved by continuously checking the `_SDC_DELETED_AT` metadata column sent by the singer tap. Due to deleting rows requires metadata columns, `hard_delete` option automatically enables the `add_metadata_columns` option as well.",  # noqa: E501
                                "label": "Hard Delete",
                            },
                            {
                                "name": "data_flattening_max_level",
                                "kind": "integer",
                                "value": 0,
                                "description": "Object type RECORD items from taps can be transformed to flattened columns by creating columns automatically. When value is 0 (default) then flattening functionality is turned off.",  # noqa: E501
                                "label": "Data Flattening Max Level",
                            },
                            {
                                "name": "primary_key_required",
                                "kind": "boolean",
                                "value": True,
                                "description": "Log based and Incremental replications on tables with no Primary Key cause duplicates when merging UPDATE events. When set to true, stop loading data if no Primary Key is defined.",  # noqa: E501
                                "label": "Primary Key Required",
                            },
                            {
                                "name": "validate_records",
                                "kind": "boolean",
                                "value": False,
                                "description": "Validate every single record message to the corresponding JSON schema. This option is disabled by default and invalid RECORD messages will fail only at load time by Postgres. Enabling this option will detect invalid records earlier but could cause performance degradation.",  # noqa: E501
                                "label": "Validate Records",
                            },
                            {
                                "name": "temp_dir",
                                "description": "(Default: platform-dependent) Directory of temporary CSV files with RECORD messages.",  # noqa: E501
                                "label": "Temporary Directory",
                            },
                        ],
                    },
                    {
                        "name": "datamill-co",
                        "docs": "https://hub.meltano.com/loaders/postgres--datamill-co.html",
                        "repo": "https://github.com/datamill-co/target-postgres",
                        "pip_url": "singer-target-postgres",
                        "settings_group_validation": [
                            [
                                "postgres_host",
                                "postgres_port",
                                "postgres_database",
                                "postgres_username",
                                "postgres_password",
                                "postgres_schema",
                            ],
                        ],
                        "settings": [
                            {"name": "postgres_host", "value": "localhost"},
                            {"name": "postgres_port", "kind": "integer", "value": 5432},
                            {"name": "postgres_database"},
                            {"name": "postgres_username"},
                            {"name": "postgres_password", "sensitive": True},
                            {
                                "name": "postgres_schema",
                                "aliases": ["schema"],
                                "value": "$MELTANO_EXTRACT__LOAD_SCHEMA",
                            },
                            {
                                "name": "postgres_sslmode",
                                "value": "prefer",
                                "description": "Refer to the libpq docs for more information about SSL: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS",  # noqa: E501
                            },
                            {
                                "name": "postgres_sslcert",
                                "value": "~/.postgresql/postgresql.crt",
                                "description": "Only used if a SSL request w/ a client certificate is being made",  # noqa: E501
                            },
                            {
                                "name": "postgres_sslkey",
                                "value": "~/.postgresql/postgresql.key",
                                "description": "Only used if a SSL request w/ a client certificate is being made",  # noqa: E501
                            },
                            {
                                "name": "postgres_sslrootcert",
                                "value": "~/.postgresql/root.crt",
                                "description": "Used for authentication of a server SSL certificate",  # noqa: E501
                            },
                            {
                                "name": "postgres_sslcrl",
                                "value": "~/.postgresql/root.crl",
                                "description": "Used for authentication of a server SSL certificate",  # noqa: E501
                            },
                            {
                                "name": "invalid_records_detect",
                                "kind": "boolean",
                                "value": True,
                                "description": "Include `false` in your config to disable `target-postgres` from crashing on invalid records",  # noqa: E501
                            },
                            {
                                "name": "invalid_records_threshold",
                                "kind": "integer",
                                "value": 0,
                                "description": "Include a positive value `n` in your config to allow for `target-postgres` to encounter at most `n` invalid records per stream before giving up.",  # noqa: E501
                            },
                            {
                                "name": "disable_collection",
                                "kind": "boolean",
                                "value": False,
                                "description": "Include `true` in your config to disable Singer Usage Logging: https://github.com/datamill-co/target-postgres#usage-logging",  # noqa: E501
                            },
                            {
                                "name": "logging_level",
                                "kind": "options",
                                "value": "INFO",
                                "options": [
                                    {"label": "Debug", "value": "DEBUG"},
                                    {"label": "Info", "value": "INFO"},
                                    {"label": "Warning", "value": "WARNING"},
                                    {"label": "Error", "value": "ERROR"},
                                    {"label": "Critical", "value": "CRITICAL"},
                                ],
                                "description": "The level for logging. Set to `DEBUG` to get things like queries executed, timing of those queries, etc.",  # noqa: E501
                            },
                            {
                                "name": "persist_empty_tables",
                                "kind": "boolean",
                                "value": False,
                                "description": "Whether the Target should create tables which have no records present in Remote.",  # noqa: E501
                            },
                            {
                                "name": "max_batch_rows",
                                "kind": "integer",
                                "value": 200000,
                                "description": "The maximum number of rows to buffer in memory before writing to the destination table in Postgres",  # noqa: E501
                            },
                            {
                                "name": "max_buffer_size",
                                "kind": "integer",
                                "value": 104857600,
                                "description": "The maximum number of bytes to buffer in memory before writing to the destination table in Postgres. Default: 100MB in bytes",  # noqa: E501
                            },
                            {
                                "name": "batch_detection_threshold",
                                "kind": "integer",
                                "description": "How often, in rows received, to count the buffered rows and bytes to check if a flush is necessary. There's a slight performance penalty to checking the buffered records count or bytesize, so this controls how often this is polled in order to mitigate the penalty. This value is usually not necessary to set as the default is dynamically adjusted to check reasonably often.",  # noqa: E501
                            },
                            {
                                "name": "state_support",
                                "kind": "boolean",
                                "value": True,
                                "description": "Whether the Target should emit `STATE` messages to stdout for further consumption. In this mode, which is on by default, STATE messages are buffered in memory until all the records that occurred before them are flushed according to the batch flushing schedule the target is configured with.",  # noqa: E501
                            },
                            {
                                "name": "add_upsert_indexes",
                                "kind": "boolean",
                                "value": True,
                                "description": "Whether the Target should create column indexes on the important columns used during data loading. These indexes will make data loading slightly slower but the deduplication phase much faster. Defaults to on for better baseline performance.",  # noqa: E501
                            },
                            {
                                "name": "before_run_sql",
                                "description": "Raw SQL statement(s) to execute as soon as the connection to Postgres is opened by the target. Useful for setup like `SET ROLE` or other connection state that is important.",  # noqa: E501
                            },
                            {
                                "name": "after_run_sql",
                                "description": "Raw SQL statement(s) to execute as soon as the connection to Postgres is opened by the target. Useful for setup like `SET ROLE` or other connection state that is important.",  # noqa: E501
                            },
                        ],
                    },
                    {
                        "name": "meltano",
                        "original": True,
                        "docs": "https://hub.meltano.com/loaders/postgres--meltano.html",
                        "repo": "https://github.com/meltano/target-postgres",
                        "pip_url": "git+https://github.com/meltano/target-postgres.git",
                        "settings_group_validation": [
                            ["url", "schema"],
                            ["user", "password", "host", "port", "dbname", "schema"],
                        ],
                        "settings": [
                            {
                                "name": "user",
                                "aliases": ["username"],
                                "value": "warehouse",
                            },
                            {
                                "name": "password",
                                "sensitive": True,
                                "value": "warehouse",
                            },
                            {
                                "name": "host",
                                "aliases": ["address"],
                                "value": "localhost",
                            },
                            {"name": "port", "kind": "integer", "value": 5502},
                            {
                                "name": "dbname",
                                "aliases": ["database"],
                                "label": "Database Name",
                                "value": "warehouse",
                            },
                            {
                                "name": "url",
                                "label": "URL",
                                "description": "Lets you set `user`, `password`, `host`, `port`, and `dbname` in one go using a `postgresql://` URI. Takes precedence over the other settings when set.",  # noqa: E501
                            },
                            {
                                "name": "schema",
                                "value": "$MELTANO_EXTRACT__LOAD_SCHEMA",
                            },
                        ],
                    },
                ],
            },
            {
                "name": "target-mock",
                "namespace": "mock",
                "pip_url": "target-mock",
                "settings": [
                    {
                        "name": "schema",
                        "env": "MOCKED_SCHEMA",
                    },
                ],
            },
        ],
        PluginType.TRANSFORMS: [
            {
                "name": "tap-mock-transform",
                "namespace": "tap_mock",
                "pip_url": "tap-mock-transform",
                "package_name": "dbt_mock",
            },
            {
                "name": "tap-google-analytics",
                "namespace": "tap_google_analytics",
                "variant": "meltano",
                "repo": "https://gitlab.com/meltano/dbt-tap-google-analytics",
                "pip_url": "https://gitlab.com/meltano/dbt-tap-google-analytics.git@config-version-2",
                "vars": {
                    "schema": "{{ env_var('DBT_SOURCE_SCHEMA', 'tap_google_analytics') }}",  # noqa: E501
                },
            },
        ],
        PluginType.ORCHESTRATORS: [
            {
                "name": "airflow",
                "namespace": "airflow",
                "docs": "https://docs.meltano.com/guide/orchestration",
                "repo": "https://github.com/apache/airflow",
                "pip_url": "apache-airflow==2.10.5 --constraint https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-${MELTANO__PYTHON_VERSION}.txt",
                "settings": [
                    {
                        "name": "core.dags_folder",
                        "value": "$MELTANO_PROJECT_ROOT/orchestrate/dags",
                        "env": "AIRFLOW__CORE__DAGS_FOLDER",
                    },
                    {
                        "name": "core.plugins_folder",
                        "value": "$MELTANO_PROJECT_ROOT/orchestrate/plugins",
                        "env": "AIRFLOW__CORE__PLUGINS_FOLDER",
                    },
                    {
                        "name": "core.sql_alchemy_conn",
                        "value": "sqlite:///$MELTANO_PROJECT_ROOT/.meltano/orchestrators/airflow/airflow.db",
                        "env": "AIRFLOW__CORE__SQL_ALCHEMY_CONN",
                    },
                    {
                        "name": "core.load_examples",
                        "value": False,
                        "env": "AIRFLOW__CORE__LOAD_EXAMPLES",
                    },
                    {
                        "name": "core.dags_are_paused_at_creation",
                        "env": "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION",
                        "value": False,
                    },
                ],
                "requires": {"files": [{"name": "airflow", "variant": "meltano"}]},
            },
            {
                "name": "orchestrator-mock",
                "namespace": "pytest",
                "pip_url": "orchestrator-mock",
            },
        ],
        PluginType.TRANSFORMERS: [
            {
                "name": "dbt",
                "label": "dbt",
                "namespace": "dbt",
                "docs": "https://docs.meltano.com/guide/transformation",
                "repo": "https://github.com/dbt-labs/dbt-core",
                "pip_url": "dbt-core~=1.9.0 dbt-postgres~=1.9.0 dbt-duckdb~=1.9.0 dbt-redshift~=1.9.0 dbt-snowflake~=1.9.0 dbt-bigquery~=1.9.0",  # noqa: E501
                "variant": "dbt-labs",
                "requires": {"files": [{"name": "dbt", "variant": "meltano"}]},
                "settings": [
                    {
                        "name": "project_dir",
                        "label": "Project Directory",
                        "value": "$MELTANO_PROJECT_ROOT/transform",
                    },
                    {
                        "name": "profiles_dir",
                        "label": "Profiles Directory",
                        "env": "DBT_PROFILES_DIR",
                        "value": "$MELTANO_PROJECT_ROOT/transform/profile",
                    },
                    {
                        "name": "target",
                        "label": "Target",
                        "value": "$MELTANO_LOAD__DIALECT",
                    },
                    {
                        "name": "source_schema",
                        "label": "Source Schema",
                        "value": "$MELTANO_EXTRACT__DEFAULT_TARGET_SCHEMA",
                    },
                    {
                        "name": "target_schema",
                        "label": "Target Schema",
                        "value": "analytics",
                    },
                    {
                        "name": "models",
                        "label": "Models",
                        "value": "$MELTANO_TRANSFORM__PACKAGE_NAME $MELTANO_EXTRACTOR_NAMESPACE my_meltano_project",  # noqa: E501
                    },
                ],
                "commands": {
                    "clean": {
                        "args": "clean",
                        "description": "Delete all folders in the clean-targets list (usually the dbt_modules and target directories.)",  # noqa: E501
                    },
                    "compile": {
                        "args": "compile --models $DBT_MODELS",
                        "description": "Generates executable SQL from source model, test, and analysis files. Compiled SQL files are written to the target/ directory.",  # noqa: E501
                    },
                    "deps": {
                        "args": "deps",
                        "description": "Pull the most recent version of the dependencies listed in packages.yml",  # noqa: E501
                    },
                    "run": {
                        "args": "run --models $DBT_MODELS",
                        "description": "Compile SQL and execute against the current target database.",  # noqa: E501
                    },
                    "seed": {
                        "args": "seed",
                        "description": "Load data from csv files into your data warehouse.",  # noqa: E501
                    },
                    "snapshot": {
                        "args": "snapshot",
                        "description": "Execute snapshots defined in your project.",
                    },
                    "test": {
                        "args": "test",
                        "description": "Runs tests on data in deployed models.",
                    },
                },
            },
            {
                "name": "transformer-mock",
                "namespace": "transformer_mock",
                "pip_url": "transformer-mock",
                "requires": {
                    "files": [
                        {
                            "name": "files-transformer-mock",
                            "variant": "meltano",
                        },
                    ],
                },
            },
        ],
        PluginType.UTILITIES: [
            {
                "name": "superset",
                "namespace": "superset",
                "label": "Superset",
                "description": "A modern, enterprise-ready business intelligence web application.",  # noqa: E501
                "docs": "https://docs.meltano.com/guide/analysis",
                "repo": "https://github.com/apache/superset",
                "variant": "apache",
                "pip_url": "apache-superset==1.5.0 markupsafe==2.0.1",
                "settings": [
                    {"name": "ui.bind_host", "value": "0.0.0.0"},  # noqa: S104
                    {"name": "ui.port", "value": 8088},
                    {"name": "ui.timeout", "value": 60},
                    {"name": "ui.workers", "value": 4},
                    {
                        "name": "SQLALCHEMY_DATABASE_URI",
                        "value": "sqlite:///$MELTANO_PROJECT_ROOT/.meltano/utilities/superset/superset.db",
                    },
                    {
                        "name": "SECRET_KEY",
                        "sensitive": True,
                        "value": "thisisnotapropersecretkey",
                    },
                ],
                "commands": {
                    "ui": {
                        "executable": "gunicorn",
                        "args": "--bind $SUPERSET_UI_BIND_HOST:$SUPERSET_UI_PORT --timeout $SUPERSET_UI_TIMEOUT --workers $SUPERSET_UI_WORKERS superset.app:create_app()",  # noqa: E501
                        "description": "Start the Superset UI. Will be available on the configured `ui.bind_host` and `ui.port`, which default to `http://localhost:4000`",  # noqa: E501
                    },
                    "create-admin": {
                        "args": "fab create-admin",
                        "description": "Create an admin user.",
                    },
                    "load_examples": {
                        "args": "load_examples",
                        "description": "Load examples.",
                    },
                },
                "logo_url": "/assets/logos/utilities/superset.png",
            },
            {
                "name": "utility-mock",
                "namespace": "utility_mock",
                "pip_url": "utility-mock",
                "executable": "utility-mock",
                "commands": {
                    "cmd": {
                        "args": "--option $ENV_VAR_ARG",
                        "description": "description of utility command",
                    },
                    "alternate-exec": {
                        "args": "--option $ENV_VAR_ARG",
                        "executable": "other-utility",
                    },
                    "containerized": {
                        "args": "",
                        "container_spec": {
                            "image": "mock-utils/mock",
                            "ports": {
                                "5000": "5000",
                            },
                            "volumes": ["$MELTANO_PROJECT_ROOT/example/:/usr/app/"],
                        },
                    },
                },
            },
        ],
        PluginType.MAPPERS: [
            {
                "name": "mapper-mock",
                "namespace": "mapper_mock",
                "variants": [
                    {
                        "name": "meltano",
                        "executable": "mapper-mock-cmd",
                        "pip_url": "mapper-mock",
                        "package_name": "mapper-mock",
                    },
                    {
                        "name": "alternative",
                        "executable": "mapper-mock-alt",
                        "pip_url": "mapper-mock-alt",
                        "package_name": "mapper-mock-alt",
                    },
                ],
            },
        ],
        PluginType.FILES: [
            {
                "name": "dbt",
                "variant": "meltano",
                "namespace": "dbt",
                "repo": "https://gitlab.com/meltano/files-dbt",
                "pip_url": "git+https://gitlab.com/meltano/files-dbt.git@3120-deprecate-env-aliases-config-v2",
            },
            {
                "name": "docker-compose",
                "variant": "meltano",
                "namespace": "docker_compose",
                "repo": "https://gitlab.com/meltano/files-docker-compose",
                "pip_url": "git+https://gitlab.com/meltano/files-docker-compose.git",
            },
            {
                "name": "airflow",
                "variant": "meltano",
                "namespace": "airflow",
                "repo": "https://gitlab.com/meltano/files-airflow",
                "pip_url": "git+https://gitlab.com/meltano/files-airflow.git",
                "update": {"orchestrate/dags/meltano.py": True},
            },
        ],
    }


@pytest.fixture(scope="class")
def locked_definition_service(project):
    return LockedDefinitionService(project)


@pytest.fixture(scope="class")
def project_init_service(request):
    return ProjectInitService(f"project_{request.node.name}")


@pytest.fixture(scope="class")
def plugin_install_service(project):
    return PluginInstallService(project)


@pytest.fixture(scope="class")
def project_add_service(project):
    return ProjectAddService(project)


@pytest.fixture(scope="class")
def plugin_settings_service_factory(project):
    def _factory(plugin, **kwargs):
        return PluginSettingsService(project, plugin, **kwargs)

    return _factory


@pytest.fixture(scope="class")
def plugin_invoker_factory(project, plugin_settings_service_factory):
    def _factory(plugin, **kwargs):
        return invoker_factory(
            project,
            plugin,
            plugin_settings_service=plugin_settings_service_factory(plugin),
            **kwargs,
        )

    return _factory


@pytest.fixture(scope="class")
def tap(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock",
            variant="meltano",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def alternative_tap(project_add_service: ProjectAddService, tap: ProjectPlugin):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock--singer-io",
            inherit_from=tap.name,
            variant="singer-io",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def inherited_tap(project_add_service: ProjectAddService, tap: ProjectPlugin):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock-inherited",
            inherit_from=tap.name,
            commands={
                "cmd": "cmd inherited",
                "cmd-inherited": "cmd-inherited",
            },
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def nonpip_tap(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(
            PluginType.EXTRACTORS,
            "tap-mock-noinstall",
            executable="tap-mock-noinstall",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def target(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(PluginType.LOADERS, "target-mock")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def alternative_target(project_add_service: ProjectAddService):
    # We don't load the `target` fixture here since this ProjectPlugin should
    # have a BasePlugin parent, not the `target` ProjectPlugin
    try:
        return project_add_service.add(
            PluginType.LOADERS,
            "target-mock-alternative",
            inherit_from="target-mock",
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def dbt(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(PluginType.TRANSFORMERS, "dbt")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def transformer(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(PluginType.TRANSFORMERS, "transformer-mock")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def utility(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(PluginType.UTILITIES, "utility-mock")
    except PluginAlreadyAddedException as err:
        return err.plugin


@pytest.fixture(scope="class")
def schedule_service(project):
    return ScheduleService(project)


@pytest.fixture(scope="class")
def task_sets_service(project):
    return TaskSetsService(project)


@pytest.fixture(scope="class")
def elt_schedule(
    project,  # noqa: ARG001
    tap,
    target,
    schedule_service,
):
    try:
        return schedule_service.add_elt(
            "elt-schedule-mock",
            extractor=tap.name,
            loader=target.name,
            transform="skip",
            interval="@daily",
        )
    except ScheduleAlreadyExistsError as err:
        return err.schedule


@pytest.fixture(scope="class")
def job_schedule(
    project,  # noqa: ARG001
    tap,  # noqa: ARG001
    target,  # noqa: ARG001
    schedule_service,
):
    try:
        return schedule_service.add(
            "job-schedule-mock",
            "mock-job",
            interval="@daily",
        )
    except ScheduleAlreadyExistsError as err:
        return err.schedule


@pytest.fixture
def environment_service(project):
    service = EnvironmentService(project)
    try:
        yield service
    finally:
        # Remove any added Environments
        for environment in service.list_environments():
            service.remove(environment.name)


@pytest.fixture(scope="class")
def elt_context_builder(project):
    return ELTContextBuilder(project)


@pytest.fixture(scope="class")
def job_logging_service(project):
    return JobLoggingService(project)


@contextmanager
def project_directory(project_init_service) -> Generator[Project, None, None]:
    project = project_init_service.init()
    logging.debug(f"Created new project at {project.root}")  # noqa: G004

    # empty out the `plugins`
    with project.meltano_update() as meltano:
        meltano.plugins = Canonical()

    ProjectSettingsService(project).set("snowplow.collector_endpoints", "[]")

    # cd into the new project root
    os.chdir(project.root)

    try:
        yield project
    finally:
        Project.deactivate()
        logging.debug(f"Cleaned project at {project.root}")  # noqa: G004


@pytest.fixture(scope="class")
def project(
    project_init_service,
    tmp_path_factory: pytest.TempPathFactory,
    hub_mock_adapter: Callable[[str], BaseAdapter],
):
    with (
        cd(tmp_path_factory.mktemp("meltano-project-dir")),
        project_directory(project_init_service) as project,
    ):
        project.hub_service.session.mount(
            project.hub_service.hub_api_url,
            hub_mock_adapter(project.hub_service.hub_api_url),
        )
        yield project


@pytest.fixture
def project_function(project_init_service, tmp_path: Path):
    with cd(tmp_path), project_directory(project_init_service) as project:
        yield project


@pytest.fixture(scope="class")
def project_files(tmp_path_factory: pytest.TempPathFactory, compatible_copy_tree):
    with (
        cd(tmp_path_factory.mktemp("meltano-project-files")),
        tmp_project(
            "a_multifile_meltano_project_core",
            current_dir / "multifile_project",
            compatible_copy_tree,
        ) as project,
    ):
        yield ProjectFiles(root=project.root, meltano_file_path=project.meltanofile)


@pytest.fixture(scope="class")
def mapper(project_add_service: ProjectAddService):
    try:
        return project_add_service.add(
            PluginType.MAPPERS,
            "mapper-mock",
            variant="meltano",
            mappings=[
                {
                    "name": "mock-mapping-0",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email",
                                "tap_stream_name": "commits",
                                "type": "MASK-HIDDEN",
                            },
                        ],
                    },
                },
                {
                    "name": "mock-mapping-1",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "given_name",
                                "tap_stream_name": "users",
                                "type": "lowercase",
                            },
                        ],
                    },
                },
            ],
        )
    except PluginAlreadyAddedException as err:
        return err.plugin


def create_state_id(description: str, env: str = "dev") -> str:
    return f"{env}:tap-{description}-to-target-{description}"


@pytest.fixture
def num_params() -> int:
    return 10


class Payloads(t.NamedTuple):
    mock_state_payloads: list[dict[str, dict]]
    mock_error_payload: dict[str, str]
    mock_empty_payload: dict[str, t.Any]


@pytest.fixture
def payloads(num_params: int) -> Payloads:
    return Payloads(
        mock_state_payloads=[
            {
                "singer_state": {
                    f"bookmark-{idx_i}": idx_i + idx_j for idx_j in range(num_params)
                },
            }
            for idx_i in range(num_params)
        ],
        mock_error_payload={"error": "failed"},
        mock_empty_payload={},
    )


class StateIds(t.NamedTuple):
    single_incomplete_state_id: str
    single_complete_state_id: str
    multiple_incompletes_state_id: str
    multiple_completes_state_id: str
    single_complete_then_multiple_incompletes_state_id: str
    single_incomplete_then_multiple_completes_state_id: str


@pytest.fixture
def state_ids():
    return StateIds(
        single_incomplete_state_id=create_state_id("single-incomplete"),
        single_complete_state_id=create_state_id("single-complete"),
        multiple_incompletes_state_id=create_state_id("multiple-incompletes"),
        multiple_completes_state_id=create_state_id("multiple-completes"),
        single_complete_then_multiple_incompletes_state_id=create_state_id(
            "single-complete-then-multiple-incompletes",
        ),
        single_incomplete_then_multiple_completes_state_id=create_state_id(
            "single-incomplete-then-multiple-completes",
        ),
    )


@pytest.fixture
def mock_time():
    def _mock_time():
        for idx in itertools.count():
            yield datetime.datetime(
                1,
                1,
                1,
                tzinfo=datetime.timezone.utc,
            ) + datetime.timedelta(hours=idx)

    return _mock_time()


class JobArgs(t.NamedTuple):
    complete_job_args: dict[str, t.Any]
    incomplete_job_args: dict[str, t.Any]


@pytest.fixture
def job_args() -> JobArgs:
    return JobArgs(
        complete_job_args={"state": State.SUCCESS, "payload_flags": Payload.STATE},
        incomplete_job_args={
            "state": State.FAIL,
            "payload_flags": Payload.INCOMPLETE_STATE,
        },
    )


@pytest.fixture
def state_ids_with_jobs(
    state_ids: StateIds,
    job_args: JobArgs,
    payloads: Payloads,
    mock_time: t.Generator[datetime.datetime, None, None],
) -> dict[str, list[Job]]:
    jobs = {
        state_ids.single_incomplete_state_id: [
            Job(
                job_name=state_ids.single_incomplete_state_id,
                **job_args.incomplete_job_args,
                payload=payloads.mock_state_payloads[0],
            ),
        ],
        state_ids.single_complete_state_id: [
            Job(
                job_name=state_ids.single_complete_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            ),
        ],
        state_ids.multiple_incompletes_state_id: [
            Job(
                job_name=state_ids.multiple_incompletes_state_id,
                **job_args.incomplete_job_args,
                payload=payload,
            )
            for payload in payloads.mock_state_payloads
        ],
        state_ids.multiple_completes_state_id: [
            Job(
                job_name=state_ids.multiple_completes_state_id,
                payload=payload,
                **job_args.complete_job_args,
            )
            for payload in payloads.mock_state_payloads
        ],
        state_ids.single_complete_then_multiple_incompletes_state_id: [
            Job(
                job_name=state_ids.single_complete_then_multiple_incompletes_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.complete_job_args,
            ),
        ]
        + [
            Job(
                job_name=state_ids.single_complete_then_multiple_incompletes_state_id,
                payload=payload,
                **job_args.incomplete_job_args,
            )
            for payload in payloads.mock_state_payloads[1:]
        ],
        state_ids.single_incomplete_then_multiple_completes_state_id: [
            Job(
                job_name=state_ids.single_incomplete_then_multiple_completes_state_id,
                payload=payloads.mock_state_payloads[0],
                **job_args.incomplete_job_args,
            ),
        ]
        + [
            Job(
                job_name=state_ids.single_incomplete_then_multiple_completes_state_id,
                payload=payload,
                **job_args.complete_job_args,
            )
            for payload in payloads.mock_state_payloads[1:]
        ],
    }
    for job_list in jobs.values():
        for job in job_list:
            job.started_at = next(mock_time)
            job.ended_at = next(mock_time)
    return jobs


@pytest.fixture
def jobs(state_ids_with_jobs):
    return [job for job_list in state_ids_with_jobs.values() for job in job_list]


@pytest.fixture
def state_ids_with_expected_states(
    state_ids: StateIds,
    payloads: Payloads,
    state_ids_with_jobs: dict[str, list[Job]],
) -> list[tuple[str, dict]]:
    final_state = {}
    for state in payloads.mock_state_payloads:
        merge(state, final_state)
    expectations = {
        state_ids.single_complete_state_id: payloads.mock_state_payloads[0],
        state_ids.single_incomplete_state_id: payloads.mock_empty_payload,
    }

    for state_id, job_list in state_ids_with_jobs.items():
        expectations[state_id] = {}
        jobs = defaultdict(list)
        # Get latest complete non-dummy job.
        for job in job_list:
            if job.state == State.STATE_EDIT:
                jobs["dummy"].append(job)
            elif job.payload_flags == Payload.STATE:
                jobs["complete"].append(job)
            elif job.payload_flags == Payload.INCOMPLETE_STATE:
                jobs["incomplete"].append(job)
        latest_job = {
            kind: (
                max(jobs[kind], key=lambda _job: _job.ended_at) if jobs[kind] else None
            )
            for kind in ("complete", "incomplete")
        }
        if latest_job["complete"]:
            expectations[state_id] = merge(
                expectations[state_id],
                latest_job["complete"].payload,
            )

        for job in jobs["incomplete"]:
            if (not latest_job["complete"]) or (
                job.ended_at > latest_job["complete"].ended_at
            ):
                expectations[state_id] = merge(expectations[state_id], job.payload)
        # Get all dummy jobs since latest non-dummy job.
        for job in jobs["dummy"]:
            if (
                not latest_job["complete"]
                or (job.ended_at > latest_job["complete"].ended_at)
            ) and (
                (not latest_job["incomplete"])
                or (job.ended_at > latest_job["incomplete"].ended_at)
            ):
                expectations[state_id] = merge(expectations[state_id], job.payload)
    return list(expectations.items())


@pytest.fixture
def job_history_session(jobs, session):
    job: Job
    job_names = set()
    for job in jobs:
        job.save(session)
        job_names.add(job.job_name)
    for job_name in job_names:
        job_state = JobState.from_job_history(session, job_name)
        session.add(job_state)
    return session


@pytest.fixture
def state_service(job_history_session, project):
    return StateService(project, session=job_history_session)


@pytest.fixture
def project_with_environment(project: Project):
    project.activate_environment("dev")
    project.environment.env["ENVIRONMENT_ENV_VAR"] = "${MELTANO_PROJECT_ROOT}/file.txt"
    try:
        yield project
    finally:
        project.deactivate_environment()


test_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "test": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": get_default_foreign_pre_chain(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "test",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


@pytest.fixture
def use_test_log_config():
    with mock.patch(
        "meltano.core.logging.utils.default_config",
        return_value=test_log_config,
    ) as patched_default_config:
        yield patched_default_config


@pytest.fixture
def reset_project_context(
    project: Project,
    project_init_service: ProjectInitService,
) -> None:
    for path in project.root.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    project_init_service.create_files(project)

    project.refresh()

    for plugin_type in PluginType:
        project.meltano.plugins[plugin_type].clear()
