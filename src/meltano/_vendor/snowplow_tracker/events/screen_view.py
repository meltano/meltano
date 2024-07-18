# """
#     screen_view.py

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

from typing import Optional, List
from meltano._vendor.snowplow_tracker.typing import JsonEncoderFunction
from meltano._vendor.snowplow_tracker.events.event import Event
from meltano._vendor.snowplow_tracker.events.self_describing import SelfDescribing
from meltano._vendor.snowplow_tracker import SelfDescribingJson
from meltano._vendor.snowplow_tracker.constants import (
    MOBILE_SCHEMA_PATH,
    SCHEMA_TAG,
)
from meltano._vendor.snowplow_tracker import payload
from meltano._vendor.snowplow_tracker.subject import Subject
from meltano._vendor.snowplow_tracker.contracts import non_empty_string


class ScreenView(Event):
    """
    Constructs a ScreenView event object.

    When tracked, generates a SelfDescribing event (event type "ue").

    Schema: `iglu:com.snowplowanalytics.mobile/screen_view/jsonschema/1-0-0`
    """

    def __init__(
        self,
        id_: str,
        name: str,
        type: Optional[str] = None,
        previous_name: Optional[str] = None,
        previous_id: Optional[str] = None,
        previous_type: Optional[str] = None,
        transition_type: Optional[str] = None,
        event_subject: Optional[Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        true_timestamp: Optional[float] = None,
    ) -> None:
        """
        :param  id_:            Screen view ID. This must be of type UUID.
        :type   id_:            string
        :param  name:           The name of the screen view event
        :type   name:           string
        :param  type:           The type of screen that was viewed e.g feed / carousel.
        :type   type:           string | None
        :param  previous_name:  The name of the previous screen.
        :type   previous_name:  string | None
        :param  previous_id:    The screenview ID of the previous screenview.
        :type   previous_id:    string | None
        :param  previous_type   The screen type of the previous screenview
        :type   previous_type   string | None
        :param  transition_type The type of transition that led to the screen being viewed.
        :type   transition_type string | None
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  true_timestamp:  Optional event timestamp in milliseconds
        :type   true_timestamp:  int | float | None
        """
        super(ScreenView, self).__init__(
            event_subject=event_subject, context=context, true_timestamp=true_timestamp
        )
        self.screen_view_properties = {}
        self.id_ = id_
        self.name = name
        self.type = type
        self.previous_name = previous_name
        self.previous_id = previous_id
        self.previous_type = previous_type
        self.transition_type = transition_type

    @property
    def id_(self) -> str:
        """
        Screen view ID. This must be of type UUID.
        """
        return self.screen_view_properties["id"]

    @id_.setter
    def id_(self, value: str):
        non_empty_string(value)
        self.screen_view_properties["id"] = value

    @property
    def name(self) -> str:
        """
        The name of the screen view event
        """
        return self.screen_view_properties["name"]

    @name.setter
    def name(self, value: str):
        non_empty_string(value)
        self.screen_view_properties["name"] = value

    @property
    def type(self) -> Optional[str]:
        """
        The type of screen that was viewed e.g feed / carousel
        """
        return self.screen_view_properties["type"]

    @type.setter
    def type(self, value: Optional[str]):
        if value is not None:
            self.screen_view_properties["type"] = value

    @property
    def previous_name(self) -> Optional[str]:
        """
        The name of the previous screen.
        """
        return self.screen_view_properties["previousName"]

    @previous_name.setter
    def previous_name(self, value: Optional[str]):
        if value is not None:
            self.screen_view_properties["previousName"] = value

    @property
    def previous_id(self) -> Optional[str]:
        """
        The screenview ID of the previous screenview.
        """
        return self.screen_view_properties["previousId"]

    @previous_id.setter
    def previous_id(self, value: Optional[str]):
        if value is not None:
            self.screen_view_properties["previousId"] = value

    @property
    def previous_type(self) -> Optional[str]:
        """
        The screen type of the previous screenview
        """
        return self.screen_view_properties["previousType"]

    @previous_type.setter
    def previous_type(self, value: Optional[str]):
        if value is not None:
            self.screen_view_properties["previousType"] = value

    @property
    def transition_type(self) -> Optional[str]:
        """
        The type of transition that led to the screen being viewed
        """
        return self.screen_view_properties["transitionType"]

    @transition_type.setter
    def transition_type(self, value: Optional[str]):
        if value is not None:
            self.screen_view_properties["transitionType"] = value

    def build_payload(
        self,
        encode_base64: bool,
        json_encoder: Optional[JsonEncoderFunction],
        subject: Optional[Subject] = None,
    ) -> "payload.Payload":
        """
        :param encode_base64:    Whether JSONs in the payload should be base-64 encoded
        :type  encode_base64:    bool
        :param json_encoder:     Custom JSON serializer that gets called on non-serializable object
        :type  json_encoder:     function | None
        :param  subject:         Optional per event subject
        :type   subject:         subject | None
        :rtype:                  payload.Payload
        """
        event_json = SelfDescribingJson(
            "%s/screen_view/%s/1-0-0" % (MOBILE_SCHEMA_PATH, SCHEMA_TAG),
            self.screen_view_properties,
        )
        self_describing = SelfDescribing(
            event_json=event_json,
            event_subject=self.event_subject,
            context=self.context,
            true_timestamp=self.true_timestamp,
        )
        return self_describing.build_payload(
            encode_base64, json_encoder, subject=subject
        )
