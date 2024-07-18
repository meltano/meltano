# """
#     self_describing.py

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
from meltano._vendor.snowplow_tracker import SelfDescribingJson
from meltano._vendor.snowplow_tracker.constants import UNSTRUCT_EVENT_SCHEMA
from meltano._vendor.snowplow_tracker import payload
from meltano._vendor.snowplow_tracker.subject import Subject
from meltano._vendor.snowplow_tracker.contracts import non_empty


class SelfDescribing(Event):
    """
    Constructs a SelfDescribing event object.

    This is a customisable event type which allows you to track anything describable
    by a JsonSchema.

    When tracked, generates a self-describing event (event type "ue").
    """

    def __init__(
        self,
        event_json: SelfDescribingJson,
        event_subject: Optional[Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        true_timestamp: Optional[float] = None,
    ) -> None:
        """
        :param  event_json:      The properties of the event. Has two field:
                                 A "data" field containing the event properties and
                                 A "schema" field identifying the schema against which the data is validated
        :type   event_json:      self_describing_json
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  true_timestamp:          Optional event timestamp in milliseconds
        :type   true_timestamp:          int | float | None
        """
        super(SelfDescribing, self).__init__(
            event_subject=event_subject, context=context, true_timestamp=true_timestamp
        )
        self.payload.add("e", "ue")
        self.event_json = event_json

    @property
    def event_json(self) -> SelfDescribingJson:
        """
        The properties of the event. Has two field:
            A "data" field containing the event properties and
            A "schema" field identifying the schema against which the data is validated
        """
        return self._event_json

    @event_json.setter
    def event_json(self, value: SelfDescribingJson):
        self._event_json = value

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

        envelope = SelfDescribingJson(
            UNSTRUCT_EVENT_SCHEMA, self.event_json.to_json()
        ).to_json()
        self.payload.add_json(envelope, encode_base64, "ue_px", "ue_pr", json_encoder)

        return super(SelfDescribing, self).build_payload(
            encode_base64=encode_base64, json_encoder=json_encoder, subject=subject
        )
