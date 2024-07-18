# """
#     page_view.py

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


class PageView(Event):
    """
    Constructs a PageView event object.

    When tracked, generates a "pv" or "page_view" event.

    """

    def __init__(
        self,
        page_url: str,
        page_title: Optional[str] = None,
        referrer: Optional[str] = None,
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
        :param  event_subject:   Optional per event subject
        :type   event_subject:   subject | None
        :param  context:         Custom context for the event
        :type   context:         context_array | None
        :param  true_timestamp:          Optional event timestamp in milliseconds
        :type   true_timestamp:          int | float | None
        """
        super(PageView, self).__init__(
            event_subject=event_subject, context=context, true_timestamp=true_timestamp
        )
        self.payload.add("e", "pv")
        self.page_url = page_url
        self.page_title = page_title
        self.referrer = referrer

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
        Title of the viewed page
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
