# """
#     struct_event.py

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
from meltano._vendor.snowplow_tracker.events.event import Event
from typing import Optional, List
from meltano._vendor.snowplow_tracker.subject import Subject
from meltano._vendor.snowplow_tracker.self_describing_json import SelfDescribingJson
from meltano._vendor.snowplow_tracker.contracts import non_empty_string


class StructuredEvent(Event):
    """
    Constructs a Structured event object.

    This event type is provided to be roughly equivalent to Google Analytics-style events.
    Note that it is not automatically clear what data should be placed in what field.
    To aid data quality and modeling, agree on business-wide definitions when designing
    your tracking strategy.

    We recommend using SelfDescribing - fully custom - events instead.

    When tracked, generates a "struct" or "se" event.
    """

    def __init__(
        self,
        category: str,
        action: str,
        label: Optional[str] = None,
        property_: Optional[str] = None,
        value: Optional[int] = None,
        event_subject: Optional[Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        true_timestamp: Optional[float] = None,
    ) -> None:
        """
        :param  category:       Category of the event
        :type   category:       non_empty_string
        :param  action:         The event itself
        :type   action:         non_empty_string
        :param  label:          Refer to the object the action is
                                performed on
        :type   label:          string_or_none
        :param  property_:      Property associated with either the action
                                or the object
        :type   property_:      string_or_none
        :param  value:          A value associated with the user action
        :type   value:          int | float | None
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  true_timestamp:          Optional event timestamp in milliseconds
        :type   true_timestamp:          int | float | None
        """
        super(StructuredEvent, self).__init__(
            event_subject=event_subject, context=context, true_timestamp=true_timestamp
        )
        self.payload.add("e", "se")
        self.category = category
        self.action = action
        self.label = label
        self.property_ = property_
        self.value = value

    @property
    def category(self) -> Optional[str]:
        """
        Category of the event
        """
        return self.payload.get("se_ca")

    @category.setter
    def category(self, value: Optional[str]):
        non_empty_string(value)
        self.payload.add("se_ca", value)

    @property
    def action(self) -> Optional[str]:
        """
        The event itself
        """
        return self.payload.get("se_ac")

    @action.setter
    def action(self, value: Optional[str]):
        non_empty_string(value)
        self.payload.add("se_ac", value)

    @property
    def label(self) -> Optional[str]:
        """
        Refer to the object the action is performed on
        """
        return self.payload.get("se_la")

    @label.setter
    def label(self, value: Optional[str]):
        self.payload.add("se_la", value)

    @property
    def property_(self) -> Optional[str]:
        """
        Property associated with either the action or the object
        """
        return self.payload.get("se_pr")

    @property_.setter
    def property_(self, value: Optional[str]):
        self.payload.add("se_pr", value)

    @property
    def value(self) -> Optional[int]:
        """
        A value associated with the user action
        """
        return self.payload.get("se_va")

    @value.setter
    def value(self, value: Optional[int]):
        self.payload.add("se_va", value)
