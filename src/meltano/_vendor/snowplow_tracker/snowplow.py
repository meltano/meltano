# """
#     snowplow.py

#     Copyright (c) 2013-2023 Snowplow Analytics Ltd. All rights reserved.

#     This program is licensed to you under the Apache License Version 2.0,
#     and you may not use this file except in compliance with the Apache License
#     Version 2.0. You may obtain a copy of the Apache License Version 2.0 at
#     http://www.apache.org/licenses/LICENSE-2.0.

#     Unless required by applicable law or agreed to in writing,
#     software distributed under the Apache License Version 2.0 is distributed on
#     an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#     express or implied. See the Apache License Version 2.0 for the specific
#     language governing permissions and limitations there under.
# """

import logging
from typing import Optional
from meltano._vendor.snowplow_tracker import (
    Tracker,
    Emitter,
    subject,
    EmitterConfiguration,
    TrackerConfiguration,
)
from meltano._vendor.snowplow_tracker.typing import Method

# Logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

"""
Snowplow Class
"""


class Snowplow:
    _trackers = {}

    @staticmethod
    def create_tracker(
        namespace: str,
        endpoint: str,
        method: Method = "post",
        app_id: Optional[str] = None,
        subject: Optional[subject.Subject] = None,
        tracker_config: TrackerConfiguration = TrackerConfiguration(),
        emitter_config: EmitterConfiguration = EmitterConfiguration(),
    ) -> Tracker:
        """
        Create a Snowplow tracker with a namespace and collector URL

        :param  namespace:          Name of the tracker
        :type   namespace:          String
        :param  endpoint:           The collector URL
        :type   endpoint:           String
        :param  method:             The HTTP request method. Defaults to post.
        :type   method:             method
        :param  appId:              Application ID
        :type   appId:              String | None
        :param  subject:            Subject to be tracked
        :type   subject:            Subject | None
        :param  tracker_config:     Tracker configuration
        :type   tracker_config:     TrackerConfiguration
        :param  emitter_config:     Emitter configuration
        :type   emitter_config:     EmitterConfiguration
        :rtype                      Tracker
        """
        if endpoint is None:
            raise TypeError("Emitter or Collector URL must be provided")

        emitter = Emitter(
            endpoint=endpoint,
            method=method,
            batch_size=emitter_config.batch_size,
            on_success=emitter_config.on_success,
            on_failure=emitter_config.on_failure,
            byte_limit=emitter_config.byte_limit,
            request_timeout=emitter_config.request_timeout,
            custom_retry_codes=emitter_config.custom_retry_codes,
            event_store=emitter_config.event_store,
            session=emitter_config.session,
        )

        tracker = Tracker(
            namespace=namespace,
            emitters=emitter,
            app_id=app_id,
            subject=subject,
            encode_base64=tracker_config.encode_base64,
            json_encoder=tracker_config.json_encoder,
        )

        return Snowplow.add_tracker(tracker)

    @classmethod
    def add_tracker(cls, tracker: Tracker) -> Tracker:
        """
        Add a Snowplow tracker to the Snowplow object

        :param  tracker:  Tracker object to add to Snowplow
        :type   tracker:  Tracker
        :rtype            Tracker
        """
        if not isinstance(tracker, Tracker):
            logger.info("Tracker not provided.")
            return None

        namespace = tracker.get_namespace()

        if namespace in cls._trackers.keys():
            raise TypeError("Tracker with this namespace already exists")

        cls._trackers[namespace] = tracker
        logger.info("Tracker with namespace: '" + namespace + "' added to Snowplow")
        return cls._trackers[namespace]

    @classmethod
    def remove_tracker(cls, tracker: Tracker):
        """
        Remove a Snowplow tracker from the Snowplow object if it exists

        :param  tracker:        Tracker object to remove from Snowplow
        :type   tracker:        Tracker | None
        """
        namespace = tracker.get_namespace()
        cls.remove_tracker_by_namespace(namespace)

    @classmethod
    def remove_tracker_by_namespace(cls, namespace: str):
        """
        Remove a Snowplow tracker from the Snowplow object using it's namespace if it exists

        :param  namespace:      Tracker namespace to remove from Snowplow
        :type   tracker:        String | None
        """
        if not cls._trackers.pop(namespace, False):
            logger.info("Tracker with namespace: '" + namespace + "' does not exist")
            return
        logger.info("Tracker with namespace: '" + namespace + "' removed from Snowplow")

    @classmethod
    def reset(cls):
        """
        Remove all active Snowplow trackers from the Snowplow object
        """
        cls._trackers = {}

    @classmethod
    def get_tracker(cls, namespace: str) -> Tracker:
        """
        Returns a Snowplow tracker from the Snowplow object if it exists
        :param  namespace:              Snowplow tracker namespace
        :type   namespace:              string
        :rtype:                         Tracker
        """
        if namespace in cls._trackers.keys():
            return cls._trackers[namespace]
        return None
