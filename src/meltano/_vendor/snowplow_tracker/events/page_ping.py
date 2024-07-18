# """
#     page_ping.py

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
from meltano._vendor.snowplow_tracker.self_describing_json import SelfDescribingJson
from meltano._vendor.snowplow_tracker.subject import Subject
from meltano._vendor.snowplow_tracker.contracts import non_empty_string


class PagePing(Event):
    """
    Constructs a PagePing event object.

    When tracked, generates a "pp" or "page_ping" event.

    """

    def __init__(
        self,
        page_url: str,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
        min_x: Optional[int] = None,
        max_x: Optional[int] = None,
        min_y: Optional[int] = None,
        max_y: Optional[int] = None,
        event_subject: Optional[Subject] = None,
        context: Optional[List[SelfDescribingJson]] = None,
        true_timestamp: Optional[float] = None,
    ) -> None:
        """
        :param  page_url:       URL of the viewed page
        :type   page_url:       non_empty_string
        :param  page_title:     Title of the viewed page
        :type   page_title:     string_or_none
        :param  referrer:       Referrer of the page
        :type   referrer:       string_or_none
        :param  min_x:          Minimum page x offset seen in the last ping period
        :type   min_x:          int | None
        :param  max_x:          Maximum page x offset seen in the last ping period
        :type   max_x:          int | None
        :param  min_y:          Minimum page y offset seen in the last ping period
        :type   min_y:          int | None
        :param  max_y:          Maximum page y offset seen in the last ping period
        :type   max_y:          int | None
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  true_timestamp:          Optional event timestamp in milliseconds
        :type   true_timestamp:          int | float | None
        """
        super(PagePing, self).__init__(
            event_subject=event_subject, context=context, true_timestamp=true_timestamp
        )
        self.payload.add("e", "pp")
        self.page_url = page_url
        self.page_title = page_title
        self.referrer = referrer
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    @property
    def page_url(self) -> str:
        """
        URL of the viewed page
        """
        return self.payload.get("url")

    @page_url.setter
    def page_url(self, value: str):
        non_empty_string(value)
        self.payload.add("url", value)

    @property
    def page_title(self) -> Optional[str]:
        """
        URL of the viewed page
        """
        return self.payload.get("page")

    @page_title.setter
    def page_title(self, value: Optional[str]):
        self.payload.add("page", value)

    @property
    def referrer(self) -> Optional[str]:
        """
        The referrer of the page
        """
        return self.payload.get("refr")

    @referrer.setter
    def referrer(self, value: Optional[str]):
        self.payload.add("refr", value)

    @property
    def min_x(self) -> Optional[int]:
        """
        Minimum page x offset seen in the last ping period
        """
        return self.payload.get("pp_mix")

    @min_x.setter
    def min_x(self, value: Optional[int]):
        self.payload.add("pp_mix", value)

    @property
    def max_x(self) -> Optional[int]:
        """
        Maximum page x offset seen in the last ping period
        """
        return self.payload.get("pp_max")

    @max_x.setter
    def max_x(self, value: Optional[int]):
        self.payload.add("pp_max", value)

    @property
    def min_y(self) -> Optional[int]:
        """
        Minimum page y offset seen in the last ping period
        """
        return self.payload.get("pp_miy")

    @min_y.setter
    def min_y(self, value: Optional[int]):
        self.payload.add("pp_miy", value)

    @property
    def max_y(self) -> Optional[int]:
        """
        Maximum page y offset seen in the last ping period
        """
        return self.payload.get("pp_may")

    @max_y.setter
    def max_y(self, value: Optional[int]):
        self.payload.add("pp_may", value)
