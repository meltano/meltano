# """
#     event.py

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
from meltano._vendor.snowplow_tracker import payload
from meltano._vendor.snowplow_tracker.subject import Subject

from meltano._vendor.snowplow_tracker.self_describing_json import SelfDescribingJson

from meltano._vendor.snowplow_tracker.constants import CONTEXT_SCHEMA
from meltano._vendor.snowplow_tracker.typing import JsonEncoderFunction, PayloadDict


class Event(object):
    """
    Event class which contains
    elements that can be set in all events. These are context, trueTimestamp, and Subject.

    Context is a list of custom SelfDescribingJson entities.
    TrueTimestamp is a user-defined timestamp.
    Subject is an event-specific Subject. Its fields will override those of the
    Tracker-associated Subject, if present.

    """

    def __init__(
        self,
        dict_: Optional[PayloadDict] = None,
        event_subject: Optional[Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        true_timestamp: Optional[float] = None,
    ) -> None:
        """
        Constructor
        :param  dict_:              Optional Dictionary to be added to the Events Payload
        :type   dict_:              dict(string:\\*) | None
        :param  event_subject:      Optional per event subject
        :type   event_subject:      subject | None
        :param  context:            Custom context for the event
        :type   context:            context_array | None
        :param  true_timestamp:     Optional event timestamp in milliseconds
        :type   true_timestamp:     int | float | None

        """
        self.payload = payload.Payload(dict_=dict_)
        self.event_subject = event_subject
        self.context = context or []
        self.true_timestamp = true_timestamp

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
        if len(self.context) > 0:
            context_jsons = list(map(lambda c: c.to_json(), self.context))
            context_envelope = SelfDescribingJson(
                CONTEXT_SCHEMA, context_jsons
            ).to_json()
            self.payload.add_json(
                context_envelope, encode_base64, "cx", "co", json_encoder
            )

        if isinstance(
            self.true_timestamp,
            (
                int,
                float,
            ),
        ):
            self.payload.add("ttm", int(self.true_timestamp))

        if self.event_subject is not None:
            fin_payload_dict = self.event_subject.combine_subject(subject)
        else:
            fin_payload_dict = None if subject is None else subject.standard_nv_pairs

        if fin_payload_dict is not None:
            self.payload.add_dict(fin_payload_dict)
        return self.payload

    @property
    def event_subject(self) -> Optional[Subject]:
        """
        Optional per event subject
        """
        return self._event_subject

    @event_subject.setter
    def event_subject(self, value: Optional[Subject]):
        self._event_subject = value

    @property
    def context(self) -> List[SelfDescribingJson]:
        """
        Custom context for the event
        """
        return self._context

    @context.setter
    def context(self, value: List[SelfDescribingJson]):
        self._context = value

    @property
    def true_timestamp(self) -> Optional[float]:
        """
        Optional event timestamp in milliseconds
        """
        return self._true_timestamp

    @true_timestamp.setter
    def true_timestamp(self, value: Optional[float]):
        self._true_timestamp = value
